---
name: opensearch-index-lifecycle-optimization
agent_type: "Generic"
description: Use when optimizing Amazon OpenSearch Service index lifecycle and storage. It finds low free storage, high JVM memory pressure, and unmanaged indices, then recommends index state management and tiering. Apply during cluster health reviews or before storage exhaustion.
version: "1.0.0"
last_updated: "2026-08-14"
---

# OpenSearch Index Lifecycle Optimization

Optimize OpenSearch storage and stability by managing index lifecycle, rollover, and tiering before capacity or memory limits are hit.

## When to Activate
- CloudWatch FreeStorageSpace is below 25 percent of allocated storage.
- CloudWatch JVMMemoryPressure is above 80 percent.
- Time-series indices have no rollover or Index State Management policy.
- ClusterStatus.yellow or ClusterStatus.red is greater than 0.
- Shard count per node is high relative to heap, causing overhead.

## Step 1: Assess Cluster Storage and Health
- Query CloudWatch FreeStorageSpace, ClusterStatus.yellow, and ClusterStatus.red per domain.
- Flag domains with free storage below 25 percent.
- Record node count, instance type, and EBS volume size.

## Step 2: Measure Memory Pressure
- Query CloudWatch JVMMemoryPressure and OldGenJVMMemoryPressure.
- Flag domains with JVMMemoryPressure above 80 percent as at risk of blocking writes.
- Correlate memory pressure with shard count and query load.

## Step 3: Inventory Indices and Shards
- Use the _cat/indices and _cat/shards APIs to list index sizes and shard distribution.
- Flag oversized shards above 50 GB and indices with excessive shard counts.
- Identify old time-series indices that are read-rarely.

## Step 4: Design Index State Management
- Recommend ISM policies to rollover indices at a size or age threshold (for example 30 GB or 1 day).
- Recommend transitions to UltraWarm after 7 days and cold storage after 30 days for logs.
- Recommend deleting indices past the retention period.

## Step 5: Right-Size and Prevent
- Recommend scaling storage or adding data nodes where free space stays below 25 percent.
- Recommend reducing shard count to keep shard size in the 10 to 50 GB range.
- Add CloudWatch alarms on FreeStorageSpace below 25 percent and JVMMemoryPressure above 80 percent.

## Output
Produce a titled "OpenSearch Index Lifecycle Report" listing domains below 25 percent free storage, JVMMemoryPressure above 80 percent, unmanaged time-series indices, and oversized shards. Include a prioritized remediation list: relieve domains near storage exhaustion or high memory pressure first, apply ISM rollover and tiering policies second, then right-size shards and nodes and add capacity alarms.