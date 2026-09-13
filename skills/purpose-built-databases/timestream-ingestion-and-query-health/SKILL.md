---
name: timestream-ingestion-and-query-health
agent_type: "Incident RCA"
description: Investigates Amazon Timestream ingestion and query health by
  analyzing write success versus system and user errors, request throttling,
  magnetic store write rejections, request latency, and query scanned-bytes
  cost. Use this skill when writes are throttled or rejected, records fail to
  land in the magnetic store, query latency climbs, or query cost rises from
  large scanned-bytes. It correlates AWS/Timestream CloudWatch metrics with
  memory-to-magnetic store tiering and retention settings to isolate the cause
  and recommend targeted, read-only-safe remediation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Timestream Ingestion and Query Health

Use this skill to diagnose Amazon Timestream write and query problems, separate
ingestion failures from query cost issues, and recommend specific remediation.
Timestream is a purpose-built time-series engine with a two-tier store: a
fast in-memory store for recent data and a magnetic store for historical data.
It is distinct from RDS, DynamoDB, and other engines.

## When to Activate

- Writes return ThrottlingException or ThrottledRequests rises.
- SystemErrors or UserErrors on write or query increases.
- Records fail to persist to the magnetic store (magnetic store write errors).
- SuccessfulRequestLatency for queries or writes exceeds SLO.
- Query cost is rising, driven by large scanned-bytes on queries.

## Step 1: Inventory Databases and Tables

Establish the tiering and retention configuration first, because most write
rejections trace back to retention boundaries.

1. `timestream-write describe-database` via use_aws for the database and KMS
   key.
2. `timestream-write list-tables` and `describe-table` per table to read
   RetentionProperties: MemoryStoreRetentionPeriodInHours and
   MagneticStoreRetentionPeriodInDays, plus MagneticStoreWriteProperties
   (whether magnetic store writes and the rejected-data-location are enabled).
3. Record for each table: memory store window, magnetic store window, and
   whether magnetic store writes are enabled.

## Step 2: Check Write Success, Errors, and Throttling

Read AWS/Timestream metrics (dimensions DatabaseName, TableName, Operation)
over the incident window.

| Metric | Meaning | Investigate |
|--------|---------|-------------|
| SuccessfulRequestLatency | Latency of successful requests | Rising p99 |
| ThrottledRequests | Requests rejected for exceeding throughput | Any sustained non-zero |
| UserErrors | Client-side 4xx (bad data, validation) | Any sustained non-zero |
| SystemErrors | Service-side 5xx | Any sustained non-zero |

1. Split UserErrors from SystemErrors. UserErrors are the client's
   responsibility: malformed records, wrong data types, timestamps outside the
   retention window, or duplicate dimensions. SystemErrors are service-side and
   should be retried with backoff.
2. ThrottledRequests means write throughput exceeded the current partition
   capacity. Timestream partitions by the combination of dimensions and time;
   throttling usually points to a hot partition (many writes sharing the same
   dimension values) rather than a global limit.
3. Correlate ThrottledRequests with the write client's batch size and retry
   behavior; WriteRecords should batch up to the per-request record limit and
   retry throttles with exponential backoff.

## Step 3: Check Magnetic Store Write Rejections

Late-arriving data is the most common cause of silent magnetic store write
failures.

1. Records whose timestamp falls outside the memory store window but inside the
   magnetic store window are written directly to the magnetic store (when
   magnetic store writes are enabled). Records older than the magnetic store
   retention are rejected.
2. When MagneticStoreWriteProperties enables the rejected-data-location, review
   the configured S3 bucket for rejected-record reports; each report names the
   reason (for example, timestamp outside retention, schema mismatch).
3. Confirm the writer's clock and the timestamp field: batches with stale or
   misparsed timestamps land as magnetic store rejections rather than throttles.

Decision guidance:

| Symptom | Likely cause | Direction |
|---------|--------------|-----------|
| UserErrors on write, no throttle | Bad records or timestamp outside retention | Fix client data/timestamps |
| ThrottledRequests rising | Hot partition / write burst | Spread dimensions, batch, backoff |
| Records missing, no visible error | Magnetic store rejection (late data) | Check rejected-data-location reports |
| SystemErrors | Service-side transient | Retry with backoff |

## Step 4: Check Query Latency and Scanned-Bytes Cost

Timestream query cost is driven by the volume of data scanned, so an
inefficient query is both slow and expensive.

1. Read SuccessfulRequestLatency for the Query operation; a rising p99 signals
   heavy scans or contention.
2. Query cost is proportional to bytes scanned. Queries without a time-range
   predicate scan the full retention; queries selecting all measures or all
   dimensions scan more than needed.
3. Reduce scanned bytes by:
   - Always constraining the time range in the WHERE clause.
   - Filtering on dimensions early to prune partitions.
   - Selecting only the required measures rather than the whole record.
4. Data in the memory store is faster and cheaper to scan than the magnetic
   store; queries reaching far back into the magnetic store are inherently
   heavier.

## Step 5: Validate Tiering and Retention

1. Confirm MemoryStoreRetentionPeriodInHours covers the freshest-query window
   the application needs; queries within this window are fastest.
2. Confirm MagneticStoreRetentionPeriodInDays covers the longest historical
   query and matches how late data can arrive; too short a magnetic window
   turns late writes into rejections.
3. Verify that the memory-to-magnetic boundary matches the ingestion pattern:
   if data routinely arrives later than the memory window, magnetic store
   writes must be enabled or those records are rejected.

## Step 6: Remediate

Recommend specific, read-only-safe actions. Never disable the KMS encryption on
a table and never disable the rejected-data-location that provides failure
visibility.

- Throttling: spread writes across dimension values to avoid a hot partition,
  batch records per WriteRecords call, and implement exponential backoff on the
  client rather than raising write rate blindly.
- UserErrors: fix client record schema and ensure timestamps fall within the
  configured retention windows.
- Magnetic store rejections: enable magnetic store writes if late data is
  expected, extend MagneticStoreRetentionPeriodInDays to cover arrival lag, and
  fix the writer clock or timestamp parsing.
- Query cost and latency: add time-range and dimension predicates, select only
  needed measures, and pre-aggregate high-frequency series where feasible.
- Tiering: align MemoryStoreRetentionPeriodInHours with the hot-query window so
  common queries stay in the fast tier.

## Output

Provide an investigation summary:
1. Whether the incident is ingestion (throttle, error, magnetic rejection) or
   query (latency, scanned-bytes cost), per table.
2. Root cause with evidence (ThrottledRequests, UserErrors, SystemErrors,
   SuccessfulRequestLatency, magnetic store rejection reports, retention
   settings over the incident window).
3. Specific remediation (batching/backoff, dimension spread, retention change,
   query predicate changes).
4. Tiering and retention assessment and any gap.
5. Recommended CloudWatch alarms (ThrottledRequests, SystemErrors, UserErrors,
   SuccessfulRequestLatency) to catch recurrence early.
