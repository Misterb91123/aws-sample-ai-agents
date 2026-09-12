---
name: dynamodb-hot-partition-remediation
agent_type: "Incident RCA"
description: Use when remediating Amazon DynamoDB hot partitions and throttling. It uses Contributor Insights and throttling metrics to find skewed keys, then recommends key design and capacity changes. Apply during performance reviews or when tables throttle under uneven access.
version: "1.0.0"
last_updated: "2026-08-14"
---

# DynamoDB Hot Partition Remediation

Diagnose and remediate DynamoDB hot partitions where uneven key access causes throttling and latency.

## When to Activate
- CloudWatch ThrottledRequests or ReadThrottleEvents and WriteThrottleEvents are greater than 0.
- Contributor Insights shows a single partition key receiving more than 3 times the average key traffic.
- ConsumedReadCapacityUnits or ConsumedWriteCapacityUnits spikes on a subset of keys.
- A global secondary index throttles independently of the base table.
- SuccessfulRequestLatency rises during peak access to a specific key.

## Step 1: Confirm Throttling
- Query CloudWatch ThrottledRequests, ReadThrottleEvents, and WriteThrottleEvents per table and GSI.
- Flag any table or index with throttle events greater than 0.
- Record whether the table is provisioned or on-demand.

## Step 2: Identify Hot Keys
- Enable and read DynamoDB Contributor Insights to find the most accessed partition keys.
- Flag any key receiving more than 3 times the average per-key request rate.
- Distinguish read hot keys from write hot keys.

## Step 3: Analyze Key Design
- Review the partition key cardinality and access distribution.
- Flag low-cardinality keys (for example a status field) driving concentration.
- Recommend a composite or write-sharded key to spread load.

## Step 4: Evaluate Capacity and Caching
- For provisioned tables confirm auto scaling target utilization near 70 percent.
- Recommend DAX for read-heavy hot keys to absorb repeated reads.
- Recommend switching to on-demand where traffic is spiky and unpredictable.

## Step 5: Recommend Remediation
- Propose adding a random or calculated suffix to shard hot write keys.
- Propose an alternate access pattern using a GSI with a higher-cardinality key.
- Add CloudWatch alarms on ThrottledRequests greater than 0.

## Output
Produce a titled "DynamoDB Hot Partition Remediation Report" listing tables and indexes with throttle events, hot keys exceeding 3 times average traffic, key design issues, and capacity settings. Include a prioritized remediation list: relieve immediate throttling via capacity or on-demand first, shard or redesign hot keys second, then add DAX caching for read hot keys and alarms on throttling.