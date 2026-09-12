---
name: athena-query-performance-optimizer
agent_type: "Generic"
description: Optimizes Amazon Athena query performance and cost by analyzing data
  scanned per query, partition pruning, file formats, small-file overhead,
  partition projection, result caching, and workgroup controls. Use this skill
  when Athena queries are slow, scan large volumes of data, or cost more than
  expected under the per-terabyte scanned pricing model.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Athena Query Performance Optimizer

Use this skill to reduce Athena query latency and cost, since Athena bills on
data scanned (about 5 USD per TB scanned for standard on-demand queries).
Scanning less data is the primary lever for both speed and cost.

## When to Activate

- Query latency is high or inconsistent.
- QueryExecution reports large DataScannedInBytes relative to result size.
- Athena spend rises without a matching increase in useful output.
- A table is queried frequently but stored as raw CSV or JSON.

## Step 1: Measure Data Scanned per Query

Establish the cost baseline:
1. From GetQueryExecution, read Statistics.DataScannedInBytes and
   EngineExecutionTimeInMillis.
2. Estimate cost: DataScannedInBytes divided by 1,099,511,627,776 (bytes per
   TB), multiplied by 5 USD.
3. Rank the most expensive and most frequent queries; optimize those first.
4. Flag any query scanning more than roughly 100 GB where the result is small,
   which signals missing pruning or full-table scans.

## Step 2: Assess Partition Pruning

Confirm queries only scan relevant partitions:
1. Verify the table is partitioned on columns used in WHERE filters (for
   example, year, month, day, or region).
2. Compare DataScannedInBytes for a filtered query against an unfiltered one;
   little difference means pruning is not happening.
3. Check that filter predicates reference partition columns directly rather
   than wrapping them in functions that block pruning.
4. Confirm partitions are registered via MSCK REPAIR TABLE, ALTER TABLE ADD
   PARTITION, or partition projection.

## Step 3: Analyze File Format

Columnar formats scan far less data than row formats:
1. Identify the current storage format (CSV, JSON, Parquet, ORC).
2. For analytical queries selecting a subset of columns, Parquet or ORC read
   only the needed columns and apply compression, commonly cutting scanned
   bytes by 80 to 90 percent versus CSV or JSON.
3. Recommend converting hot tables to Parquet (Snappy compression is a good
   default).

## Step 4: Address the Small File Problem

Many tiny files add per-object overhead and hurt throughput:
1. Inspect object counts and sizes under table prefixes.
2. Thousands of files well below 128 MB indicate fragmentation, common with
   streaming or frequent micro-batch writes.
3. Target file sizes in the range of 128 MB to 512 MB.

Remediation:
- Compact small files using CTAS or INSERT INTO with bucketing or a periodic
  compaction job.
- Tune upstream producers (for example, Firehose buffer size) to write larger
  objects.

## Step 5: Evaluate Partition Projection

For high-cardinality, predictable partitions:
1. Where partitions follow a regular pattern (dates, integer ranges,
   enumerated values), enable partition projection to skip metastore partition
   lookups.
2. Configure projection properties (projection.enabled, per-column type,
   range, format, and interval) so Athena computes partitions at query time.
3. This removes the need for MSCK REPAIR TABLE and speeds planning on tables
   with very large partition counts.

## Step 6: Use Result Caching

Avoid rescanning for repeated queries:
1. Confirm the workgroup has query result reuse enabled and set a reuse age
   (up to 7 days / 10080 minutes) appropriate to data freshness needs.
2. Identical queries within the reuse window return cached results and scan 0
   bytes, eliminating cost for dashboard refreshes.

## Step 7: Apply Workgroup Cost Controls

Prevent runaway scans:
1. Set a per-query data scan limit on the workgroup to cancel queries that
   exceed a byte threshold.
2. Set per-workgroup limits to isolate teams or workloads.
3. Enforce a results output location and consider requiring CTAS or Parquet for
   frequently queried datasets.

## Output

Provide an optimization report:
1. Top queries by data scanned and estimated cost.
2. Pruning effectiveness and any missing or unused partitioning.
3. File format and small-file findings with a conversion or compaction plan.
4. Partition projection and result caching opportunities.
5. Recommended workgroup data scan limits.
6. Estimated cost reduction (for example, format conversion cutting scanned
   bytes by 80 to 90 percent) and specific CTAS or DDL statements to apply.