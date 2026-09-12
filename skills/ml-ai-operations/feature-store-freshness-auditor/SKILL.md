---
name: feature-store-freshness-auditor
agent_type: "Generic"
description: Audit Amazon SageMaker Feature Store for feature freshness, ingestion failures, and consistency between the online and offline stores. I use this skill to measure ingestion latency, detect stale features, diagnose PutRecord failures and throttling, and verify online/offline parity. I activate it when features are stale, ingestion pipelines fail, or the online and offline stores diverge.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Feature Store Freshness Auditor

This skill provides a procedure for auditing the health of Amazon SageMaker Feature Store. It measures how current features are, verifies that writes succeed and replicate correctly from the online store to the offline store, and identifies configuration and cost issues such as missing TTLs and unused features.

## When to Activate

- Models consume features that appear out of date relative to the source system.
- Feature ingestion jobs report errors or partial success.
- The online store and offline store return different values for the same record.
- PutRecord calls experience throttling or elevated failure rates.
- Feature Store storage cost grows without a clear driver.

## Step 1: Measure Ingestion Latency and Failures

For each feature group under audit, evaluate the ingestion path:

- Measure end-to-end ingestion latency from source event time to the record write time.
- For streaming ingestion via the PutRecord API, review CloudWatch metrics and application logs for failed writes and retries.
- For batch ingestion, confirm the ingestion job completed and compare the expected record count against the count written.

## Step 2: Detect Stale Features

Compare each feature group's most recent write timestamp against its expected refresh cadence:

- Read the record identifier and event time feature to determine the latest event time present in the online store.
- Compute staleness as current time minus latest event time.
- Flag feature groups where staleness exceeds the expected refresh interval (for example a feature expected to refresh hourly whose latest event time is more than 2 hours old).

## Step 3: Verify Online and Offline Consistency

The online store serves low-latency reads and the offline store (backed by S3) serves training and batch use. Records written to the online store replicate asynchronously to the offline store:

- Sample a set of record identifiers and read them from the online store via GetRecord.
- Read the corresponding rows from the offline store S3 location (or via Athena over the Glue table).
- Compare values and event times. Note that the offline store retains history (multiple versions), while the online store holds only the latest record; account for this when comparing.

## Step 4: Diagnose PutRecord Failures and Throttling

Investigate write reliability:

- Review PutRecord error rates and any ThrottlingException responses.
- Confirm the write throughput stays within the configured or account capacity for the feature group.
- For throttling, recommend batching, backoff with retries, or a capacity increase.
- For validation errors, confirm the record schema matches the feature definitions (feature names and types).

## Step 5: Measure Offline Store Replication Lag

Because online-to-offline replication is asynchronous, measure the lag between a record's write to the online store and its appearance in the offline S3 store. Persistent lag beyond the expected window (typically within a few minutes) indicates a replication issue that can cause training data to miss recent records. Confirm the offline store S3 bucket and Glue table are receiving new partitions on schedule.

## Step 6: Review TTL and Storage Growth

- For online stores with TTL enabled, confirm the TtlDuration is set appropriately so expired records are removed and online storage cost stays bounded.
- Track offline store S3 storage growth per feature group. Because the offline store appends historical versions, growth is expected, but unbounded growth on unused feature groups is wasteful.

## Step 7: Track Feature Usage

Identify feature groups and individual features that are ingested but rarely or never read by training jobs or endpoints. Unused features add ingestion cost, storage cost, and maintenance burden. Recommend deprecating features with no consumers over a defined observation window.

## Output

The skill produces a Feature Store audit report containing: per-feature-group ingestion latency and failure counts, a staleness assessment against expected refresh cadence, an online-versus-offline consistency comparison, a PutRecord failure and throttling diagnosis, an offline store replication lag measurement, TTL and storage-growth findings, and a list of unused features recommended for deprecation.