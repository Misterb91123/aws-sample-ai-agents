---
name: redshift-query-tuning-advisor
agent_type: "Generic"
description: Tunes Amazon Redshift query performance by analyzing distribution
  styles, sort keys, disk-based (spilled) operations, workload management queue
  behavior, vacuum and analyze staleness, and concurrency features. Use this
  skill when Redshift queries are slow, steps spill to disk, table statistics
  are stale, or WLM queues back up with high queue wait time.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Redshift Query Tuning Advisor

Use this skill to diagnose slow Amazon Redshift queries, tie the slowness to
distribution, sort, statistics, or workload management, and recommend concrete
schema and configuration changes.

## When to Activate

- Query execution time regresses or exceeds SLA.
- Query steps report disk-based (spilled) operations.
- WLM queues show high queue wait time or queries queue behind long runners.
- Uneven data distribution across compute slices is suspected.

## Step 1: Identify the Slowest Queries

Establish which queries to tune:
1. Query SVL_QUERY_REPORT, STL_QUERY, and SYS_QUERY_HISTORY (RA3 / serverless)
   for the longest-running and most frequent statements.
2. Separate execution time from queue wait time so you tune the correct layer.
3. Capture the query plan with EXPLAIN and the actual steps from
   SVL_QUERY_SUMMARY.

## Step 2: Analyze Distribution Style and Skew

Distribution controls how much data moves between nodes:
1. For each large table, check the distribution style (KEY, EVEN, ALL, AUTO).
2. Detect slice-level skew by comparing row counts per slice in
   SVV_TABLE_INFO (skew_rows) and STV_BLOCKLIST; a skew ratio above 4x is a
   concern.
3. Look for DS_BCAST_INNER or DS_DIST_BOTH in query plans, which indicate
   costly redistribution or broadcasting during joins.

Remediation:
- Use DISTKEY on the common join column of large fact-to-fact or fact-to-large
  dimension joins to enable co-located joins.
- Use DISTSTYLE ALL for small dimension tables so they exist on every node.
- Use EVEN when there is no dominant join key and skew must be avoided.

## Step 3: Evaluate Sort Keys

Sort keys enable zone-map range restriction:
1. Confirm frequently filtered columns (dates, ids) are sort keys.
2. Compare rows scanned to rows returned; scanning far more than returned means
   the sort key is unused or ineffective.
3. Check unsorted region percentage in SVV_TABLE_INFO; a high unsorted
   percentage weakens sort key benefits.

Remediation:
- Set a compound sort key leading with the most selective filter column.
- Use time-series ordering for append-mostly tables.

## Step 4: Detect Disk-Based Operations

Spilling to disk slows queries sharply:
1. In SVL_QUERY_SUMMARY, find steps where is_diskbased is true (hashes, sorts,
   aggregations).
2. Correlate with insufficient memory per WLM slot for the query.

Remediation:
- Increase memory for the queue or reduce concurrency so each slot gets more
  memory.
- Reduce intermediate result size (filter earlier, avoid unnecessary DISTINCT
  and wide GROUP BY).

## Step 5: Review Workload Management

Queue configuration governs concurrency and wait time:
1. Inspect WLM queues (manual or Auto WLM) in STV_WLM_QUERY_STATE and
   STL_WLM_QUERY for queue wait time.
2. Identify queues where short queries wait behind long-running statements.
3. Confirm Short Query Acceleration (SQA) is enabled to fast-track brief
   queries.
4. Check whether Concurrency Scaling is enabled and how many usage seconds are
   consumed for read-heavy bursts.

Remediation:
- Prefer Auto WLM with query priorities for mixed workloads.
- Enable SQA and Concurrency Scaling for spiky read concurrency.
- Separate ETL and BI workloads into distinct queues.

## Step 6: Check Vacuum and Analyze Staleness

Stale maintenance degrades plans and scans:
1. Check last vacuum and unsorted percentage in SVV_TABLE_INFO; heavily
   updated or deleted tables accumulate unsorted rows and dead space.
2. Check statistics freshness (stats_off in SVV_TABLE_INFO); values above 10
   percent mean the planner may choose poor plans.

Remediation:
- Run VACUUM (or VACUUM DELETE ONLY / SORT ONLY) on high-churn tables.
- Run ANALYZE after large loads so the optimizer has current statistics.
- Rely on automatic table optimization where appropriate.

## Step 7: Rank Top Queries by Impact

Prioritize tuning effort:
1. Rank by total execution time (average duration multiplied by frequency).
2. Note which fixes are schema changes (DISTKEY, SORTKEY, needing a rebuild)
   versus configuration changes (WLM, SQA, Concurrency Scaling).

## Output

Provide a tuning report:
1. Top queries by total impact with execution versus queue time split.
2. Distribution findings: skew ratios and redistribution or broadcast steps.
3. Sort key effectiveness and unsorted region percentages.
4. Disk-based step locations and the memory or concurrency fix.
5. WLM, SQA, and Concurrency Scaling recommendations.
6. Vacuum and analyze actions with target tables.
7. Prioritized change list separating schema rebuilds from configuration
   adjustments.