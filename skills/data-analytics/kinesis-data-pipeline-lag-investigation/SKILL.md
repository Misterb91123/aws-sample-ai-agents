---
name: kinesis-data-pipeline-lag-investigation
agent_type: "Incident RCA"
description: Investigates lag and throughput bottlenecks across Amazon Kinesis
  Data Streams and Kinesis Data Firehose pipelines by analyzing iterator age,
  shard-level limits, partition key distribution, consumer scaling, and delivery
  buffering. Use this skill when consumer lag grows, records are throttled with
  ProvisionedThroughputExceeded, or delivery to S3, Redshift, or OpenSearch is
  delayed.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Kinesis Data Pipeline Lag Investigation

Use this skill to locate where a Kinesis pipeline is falling behind, quantify
the gap against service limits, and recommend resharding, consumer scaling, or
buffer tuning.

## When to Activate

- GetRecords.IteratorAgeMilliseconds is rising and does not recover.
- Producers or consumers receive ProvisionedThroughputExceededException.
- Firehose DeliveryToS3, DeliveryToRedshift, or DeliveryToOpenSearch latency or
  failure metrics increase.
- Downstream consumers or dashboards report stale or delayed data.

## Step 1: Measure Consumer Lag

Establish how far behind consumers are:
1. Read GetRecords.IteratorAgeMilliseconds (Maximum) per stream and per shard.
   A value near 0 is healthy; sustained growth means consumers cannot keep up.
2. Convert to human terms: 60000 ms equals 1 minute of lag; values in the
   millions of ms indicate hours of backlog approaching the 24 hour (or up to
   365 day) retention window.
3. Identify whether all shards lag uniformly (global under-provisioning) or a
   subset lags (hot shard or slow consumer instance).

## Step 2: Compare Shard Throughput to Limits

Each shard supports fixed limits:
1. Write: 1 MB/s or 1000 records/s per shard.
2. Read (shared throughput): 2 MB/s per shard across all consumers, and
   GetRecords is capped at 5 calls/s per shard.
3. Check IncomingBytes, IncomingRecords, WriteProvisionedThroughputExceeded,
   and ReadProvisionedThroughputExceeded per shard.
4. If IncomingBytes approaches 1 MB/s per shard, the stream is write-bound and
   needs more shards.

## Step 3: Detect Hot Shards via Partition Keys

Uneven partition keys concentrate traffic on a few shards:
1. Compare IncomingRecords across shards; one shard carrying a large multiple
   of the others indicates a hot key.
2. Inspect the producer partition key strategy. Low-cardinality keys (for
   example, a single tenant id or a constant) map to one shard.
3. Confirm whether throttling is limited to the hot shard.

Remediation:
- Use a high-cardinality partition key or a random suffix to spread load.
- Reshard by splitting the hot shard (SplitShard) at the appropriate hash key.

## Step 4: Evaluate Consumer Scaling

Determine if consumers can drain the stream:
1. For shared throughput, one KCL worker per shard is the practical parallelism
   limit; fewer workers than shards means backlog.
2. If multiple consumers share 2 MB/s per shard, they contend for read
   throughput. Move latency-sensitive consumers to enhanced fan-out, which
   grants a dedicated 2 MB/s per shard per consumer.
3. Check consumer processing time per batch; slow record handling (external
   calls, large writes) inflates iterator age even when limits are not hit.

Remediation:
- Register enhanced fan-out consumers (SubscribeToShard) for isolation.
- Scale KCL instances to match shard count and enable lease balancing.
- Optimize per-record processing and batch downstream writes.

## Step 5: Analyze Firehose Delivery

For Firehose pipelines, inspect buffering and delivery:
1. Buffer hints control latency: buffer size 1 to 128 MB and buffer interval 60
   to 900 seconds. Firehose flushes when either limit is reached.
2. Check DeliveryToS3.DataFreshness (age of oldest undelivered record) and
   DeliveryToS3.Success.
3. Review ThrottledRecords and any transformation Lambda errors
   (ExecuteProcessing.Duration, ExecuteProcessing.Success).
4. For dynamic partitioning, confirm partition key count stays within limits.

## Step 6: Check Destination Backpressure

The destination may be the true bottleneck:
1. S3: normally elastic; failures usually stem from IAM, KMS, or invalid
   prefixes rather than throughput.
2. Redshift: Firehose COPY throughput depends on cluster capacity, WLM queue
   availability, and COPY frequency; check DeliveryToRedshift.Success and COPY
   errors.
3. OpenSearch: check DeliveryToOpenSearch.Success, cluster indexing rate, JVM
   memory pressure, and 429 rejections from index write queues.
4. When the destination rejects or slows, Firehose retries and DataFreshness
   climbs.

## Step 7: Produce Resharding and Scaling Recommendations

Combine findings into an action plan:
1. Compute required shard count as ceil(peak MB/s divided by 1) and
   ceil(peak records/s divided by 1000); take the larger value.
2. For on-demand streams, confirm the account is within the automatic scaling
   ceiling before assuming capacity is available.
3. Recommend SplitShard for hot shards and MergeShards where shards are idle.
4. Recommend enhanced fan-out where multiple consumers contend.

## Output

Provide an investigation summary:
1. Bottleneck location: producer, stream shards, consumer, Firehose buffer, or
   destination.
2. Quantified lag (iterator age) and throughput versus per-shard limits.
3. Hot shard or partition key findings.
4. Specific reshard, consumer scaling, or buffer configuration changes.
5. Recommended CloudWatch alarms (IteratorAgeMilliseconds threshold,
   ReadProvisionedThroughputExceeded, DataFreshness) to catch recurrence early.