---
name: database-query-optimizer
agent_type: "Incident RCA"
description: Identifies and optimizes slow database queries by analyzing execution
  plans, index usage, and query patterns. Use this skill when investigating database
  performance issues, responding to RDS CPU alarms driven by query load, or when
  Performance Insights shows specific queries dominating database load.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Database Query Optimizer

Use this skill to identify slow queries and recommend optimizations for
RDS and Aurora databases.

## When to Activate

- RDS/Aurora CPU or IOPS alarm fires.
- Performance Insights shows high DB load from specific queries.
- Application latency traced to database calls.
- Post-deployment: new code introduced slow queries.
- Periodic database performance review.

## Step 1: Identify Problematic Queries

Use Performance Insights or CloudWatch to find top offenders:

1. **Top queries by load** (Average Active Sessions contribution):
   - Queries consuming the most database resources overall.
   - Even a moderately slow query called 10,000 times/minute dominates.

2. **Top queries by latency**:
   - Queries with highest p99 execution time.
   - These affect individual request experience.

3. **Top queries by call volume**:
   - Very frequently executed queries (even if fast individually).
   - Small optimizations here have large aggregate impact.

For each problematic query, capture:
- SQL text (parameterized)
- Average execution time
- Calls per minute
- Total load contribution (%)
- Wait events (CPU, IO, lock)

## Step 2: Analyze Execution Plans

For each slow query, examine the execution plan:

**Key plan elements to check:**

| Plan Element | Good | Bad |
|-------------|------|-----|
| Index usage | Index Scan / Index Only Scan | Seq Scan / Full Table Scan on large table |
| Join type | Nested Loop (small), Hash Join (large) | Nested Loop on large tables without index |
| Sort method | Index-based sort | Filesort / External sort (spills to disk) |
| Row estimates | Close to actual rows | Off by 10x+ (stale statistics) |
| Temp tables | None | Using temporary (memory exhaustion risk) |
| Filtering | Index filters rows | Post-filter after fetching all rows |

**Red flags in execution plans:**
- Full table scan on tables > 10,000 rows.
- Sort without index on large result sets.
- Nested loop join where inner table has no index on join column.
- Estimated rows vastly different from actual (stale stats).
- Temp table or filesort for ORDER BY / GROUP BY operations.

## Step 3: Evaluate Index Usage

Check existing indexes and their utilization:

1. **Missing indexes**: Queries scanning full tables that would benefit from an index on the WHERE/JOIN columns.
2. **Unused indexes**: Indexes that exist but are never used (consume write overhead and storage).
3. **Redundant indexes**: Indexes covered by other composite indexes.
4. **Index bloat**: Indexes much larger than expected (need rebuild).
5. **Covering indexes**: Can we add columns to existing indexes to enable Index Only Scans?

**Index recommendation framework:**
- Single column queries: Index on the filtered column.
- Multi-column queries: Composite index following the equality-sort-range (ESR) rule.
- Sort operations: Index on ORDER BY columns (matching direction).
- Join operations: Index on the foreign key / join column.

## Step 4: Identify Query Anti-Patterns

Look for common anti-patterns:

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| SELECT * | Fetches unnecessary columns, can't use covering index | Select only needed columns |
| N+1 queries | Loop executing query per row | Batch with IN clause or JOIN |
| OR conditions on different columns | Can't use single index efficiently | UNION of indexed queries |
| Functions on indexed columns (WHERE YEAR(date) = 2024) | Index can't be used | Rewrite as range (date >= '2024-01-01') |
| LIKE '%search%' | Leading wildcard prevents index use | Full-text search or reverse index |
| Correlated subquery | Re-executed for every row | Rewrite as JOIN |
| Missing LIMIT on large result sets | Fetches all rows when only first N needed | Add LIMIT |
| Implicit type conversion | WHERE varchar_col = 123 prevents index use | Match types explicitly |
| Large IN lists (> 1000 items) | Plan instability, memory pressure | Temp table with JOIN |
| SELECT COUNT(*) without filter | Full table scan | Maintain count in separate table or cache |

## Step 5: Analyze Wait Events

Performance Insights wait events reveal what queries are waiting for:

| Wait Event | Meaning | Solution |
|-----------|---------|----------|
| CPU | Query is compute-bound (complex calculations, parsing) | Optimize query logic, reduce rows processed |
| IO:DataFileRead | Reading data from disk (not in buffer cache) | Add memory, optimize to read fewer pages, add indexes |
| IO:DataFileWrite | Writing data to disk | Reduce write amplification, batch operations |
| Lock:Relation | Waiting for table-level lock | Reduce transaction scope, avoid long transactions |
| Lock:Tuple | Waiting for row-level lock | Reduce contention, serialize access differently |
| LWLock:BufferMapping | Buffer pool contention | Increase shared_buffers, reduce concurrent large scans |
| Client:ClientRead | Waiting for application to consume results | Application bottleneck, not DB |

## Step 6: Recommend Optimizations

Prioritize by impact (load contribution x improvement potential):

**Quick wins (minutes to implement):**
- Add a missing index for a high-load query.
- Add LIMIT to queries fetching more than needed.
- Update statistics (ANALYZE) if estimates are stale.

**Medium effort (hours):**
- Rewrite N+1 patterns to batch queries.
- Add covering indexes for Index Only Scans.
- Rewrite correlated subqueries as JOINs.
- Implement query result caching for read-heavy, rarely-changing data.

**Larger effort (days/sprints):**
- Denormalize for read-heavy access patterns.
- Partition large tables for query pruning.
- Add read replicas to offload read queries.
- Implement materialized views for complex aggregations.
- Redesign schema for better access patterns.

## Step 7: Validate Improvements

After implementing optimizations:
1. Re-run the query and compare execution plan (confirm index is used).
2. Compare execution time before/after.
3. Monitor overall DB load for improvement.
4. Watch for side effects (write performance regression from new indexes).
5. Test with production-scale data (not just dev data).

## Output

Produce a query optimization report:
1. **Top Slow Queries Table**: Query (truncated), avg time, calls/min, load %, wait type, recommended fix.
2. **Missing Indexes Table**: Table, columns, queries benefited, estimated improvement.
3. **Anti-Pattern Findings**: Query, pattern detected, rewrite recommendation.
4. **Index Health**: Unused indexes to remove, bloated indexes to rebuild.
5. **Wait Event Analysis Chart**: Distribution of wait events showing where time is spent.
6. **Optimization Priority List**: Ordered by estimated impact x ease of implementation.
7. **Before/After Projections**: Expected load reduction if top recommendations are implemented.