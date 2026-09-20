---
name: athena-partition-projection-advisory
agent_type: "Generic"
description: Finds Amazon Athena and Glue tables that scan far more S3 data than
  needed - unpartitioned tables over log-shaped prefixes correlated with recent
  high-ProcessedBytes queries - and emits ready-to-run partition-projection DDL,
  an optional partitioned-CTAS reorg, and a Parquet-conversion recommendation,
  with a projected bytes-scanned reduction. Use this skill for the automated
  partition-projection-DDL angle, distinct from general query tuning and
  scan-limit governance. Read-only and recommend-only.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Athena Partition Projection Advisory

Use this skill to cut Athena bytes-scanned by fixing missing or inefficient
partitioning. The high-value pattern is an unpartitioned Glue table sitting over
log-shaped S3 prefixes (date or hour paths) that recent queries scan in full.
The remedy is partition projection DDL that maps predicates to prefixes without a
metastore crawl. Reason over Glue, Athena, and S3 reads; never modify a table.

## Sources

Read-only.

- Glue API via use_aws: GetTables and GetPartitions to read table schema,
  StorageDescriptor location, partition keys, and current partition count.
- Athena via use_aws: GetQueryExecution statistics for DataScannedInBytes to
  identify high-ProcessedBytes queries against each table.
- S3 prefix listing via use_aws: ListObjectsV2 with a delimiter to detect
  log-shaped date or hour prefix structure under the table location.
- CloudWatch Athena metrics: ProcessedBytes to size the scan trend over time.

## Method

1. Enumerate Glue tables and read partition keys, location, and format.
2. Flag unpartitioned or lightly partitioned tables whose S3 location shows a
   log-shaped prefix structure (for example year/month/day or hourly paths).
3. Correlate each flagged table with recent high-DataScannedInBytes Athena
   queries to confirm the table drives real scan cost, not just theoretical risk.
4. Emit ready-to-run partition-projection DDL (projection type, range, format,
   and the storage location template) matching the observed prefix layout.
5. Offer an optional partitioned-CTAS reorg where the existing layout does not
   map cleanly to projection, and a Parquet-conversion recommendation where data
   is row-oriented (CSV or JSON).
6. Quantify the projected bytes-scanned reduction from the observed query
   predicates and prefix selectivity, and rank tables by that saving.

## MCP augmentation

Where current partition-projection syntax, supported projection types, or CTAS
semantics would sharpen the emitted DDL, recommend connecting the AWS
Documentation MCP Server to the Agent Space and using it in addition to the Glue,
Athena, and S3 reads, never instead of them. Otherwise no MCP server is required.
AWS MCP server names and availability evolve; verify before relying on one.

## Output

Produce a partition advisory report: per flagged table the current layout, the
correlated high-scan queries, the ready-to-run partition-projection DDL, the
optional CTAS reorg and Parquet recommendation, and the projected bytes-scanned
reduction, ranked by saving, each read-only-safe with a safety rating
(recommend-only). Reference tables and buckets by identifier and mask account
IDs.
