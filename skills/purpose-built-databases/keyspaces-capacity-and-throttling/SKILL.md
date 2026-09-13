---
name: keyspaces-capacity-and-throttling
agent_type: "Generic"
description: Analyzes Amazon Keyspaces (for Apache Cassandra) capacity and
  throttling by comparing read and write throttle events, consumed capacity
  against provisioned capacity, per-partition hot keys, and request latency, and
  by evaluating on-demand versus provisioned capacity mode fit. Use this skill
  when Keyspaces requests are throttled, consumed capacity nears provisioned
  limits, a hot partition drives localized throttling, or when deciding whether
  a table should run in on-demand or provisioned mode. It produces a targeted
  capacity or mode recommendation rather than a blanket maximum.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Keyspaces Capacity and Throttling

Use this skill to analyze Amazon Keyspaces (for Apache Cassandra) throttling and
capacity, distinguish global under-provisioning from per-partition hot keys, and
recommend a right-sized capacity or capacity-mode change. Keyspaces is a
serverless Cassandra-compatible engine that meters throughput in read and write
capacity units and enforces a per-partition throughput ceiling; it is distinct
from DynamoDB and self-managed Cassandra.

## When to Activate

- ReadThrottleEvents or WriteThrottleEvents rises.
- ConsumedReadCapacityUnits or ConsumedWriteCapacityUnits approaches provisioned
  capacity on a provisioned-mode table.
- SuccessfulRequestLatency climbs alongside throttling.
- A single partition appears to throttle while overall table capacity looks low.
- You need to decide between on-demand and provisioned capacity mode.

## Step 1: Inventory Keyspaces and Tables

1. `keyspaces list-keyspaces` and `keyspaces list-tables` via use_aws to
   enumerate tables.
2. `keyspaces get-table` per table of interest to read capacity mode
   (throughputMode: PAY_PER_REQUEST or PROVISIONED), and for provisioned tables
   the readCapacityUnits and writeCapacityUnits, plus any auto scaling settings.
3. Record for each table: capacity mode, provisioned RCU/WCU if applicable,
   partition key definition (drives partition distribution), and whether auto
   scaling is enabled.

## Step 2: Check Throttle Events and Consumed Capacity

Read AWS/Cassandra metrics (dimensions Keyspace, TableName) over the window.

| Metric | Meaning | Investigate |
|--------|---------|-------------|
| ReadThrottleEvents | Reads rejected for exceeding capacity | Any sustained non-zero |
| WriteThrottleEvents | Writes rejected for exceeding capacity | Any sustained non-zero |
| ConsumedReadCapacityUnits | RCU actually used | Near provisioned RCU |
| ConsumedWriteCapacityUnits | WCU actually used | Near provisioned WCU |
| SuccessfulRequestLatency | Latency of successful ops | Rising with throttles |
| SystemErrors / UserErrors | Service-side / client-side failures | Any sustained non-zero |

1. On a provisioned table, compare ConsumedReadCapacityUnits and
   ConsumedWriteCapacityUnits (as a per-second rate) against provisioned RCU and
   WCU. Throttling while consumed capacity is at or near provisioned indicates
   genuine global under-provisioning.
2. Throttling while total consumed capacity is well below provisioned is the key
   signal of a per-partition hot key, not a table-wide shortfall (see Step 3).
3. On an on-demand table, sustained throttling during rapid traffic ramps means
   the workload grew faster than on-demand can adapt, or a single partition
   exceeds the per-partition ceiling.

## Step 3: Detect Hot Partitions

Keyspaces enforces a maximum throughput per partition regardless of table-level
capacity. A single hot partition throttles even when the table is mostly idle.

1. Look for the pattern: non-zero throttle events with total consumed capacity
   far below provisioned. This is the fingerprint of a hot partition.
2. Inspect the partition key design. Low-cardinality or skewed keys (a single
   tenant, a status flag, a constant, or a monotonically increasing time bucket)
   concentrate reads or writes on one partition.
3. Confirm with the application access pattern: a single hot row or a small set
   of partitions receiving the bulk of traffic.

Decision guidance:

| Throttle events | Consumed vs provisioned | Likely cause | Direction |
|-----------------|-------------------------|--------------|-----------|
| Non-zero | Near provisioned | Global under-provisioning | Raise capacity or use auto scaling |
| Non-zero | Far below provisioned | Hot partition | Redesign partition key / add write sharding |
| Non-zero | On-demand table, ramping | On-demand adaptation lag or hot partition | Pre-warm via provisioned or fix key |

## Step 4: Evaluate Capacity Mode Fit

Choose the mode that matches the traffic shape rather than defaulting to a large
provisioned ceiling.

1. On-demand (PAY_PER_REQUEST) fits spiky, unpredictable, or new workloads. It
   scales automatically and bills per request; it is the safer default when the
   pattern is unknown or bursty.
2. Provisioned fits steady, predictable traffic where reserved RCU/WCU (ideally
   with auto scaling) is cheaper than per-request pricing at sustained volume.
3. Neither mode raises the per-partition ceiling; a hot partition must be solved
   in the data model regardless of mode.
4. If a provisioned table without auto scaling throttles during predictable
   daily peaks, enabling auto scaling with a target utilization is usually
   better than a static high ceiling.

## Step 5: Forecast Capacity

1. From ConsumedReadCapacityUnits and ConsumedWriteCapacityUnits, compute the
   sustained and peak per-second rates over a representative period.
2. For provisioned mode, size RCU/WCU to the observed peak plus modest headroom,
   or set auto scaling target utilization (for example 70 percent) so capacity
   tracks demand instead of a fixed maximum.
3. Account for growth trend; project the peak forward over the planning horizon
   rather than fitting only to today.

## Step 6: Remediate

Recommend specific, least-change actions. Do not set a blanket maximum
capacity, and never remove client authentication or expose data broadly to
work around throttling.

- Global under-provisioning: raise provisioned RCU/WCU to observed peak plus
  headroom, or enable auto scaling with a target utilization; prefer auto
  scaling over a static high ceiling.
- Hot partition: redesign the partition key for higher cardinality; add a write
  sharding suffix to spread a hot write key; distribute a hot read across
  replicas of the value where the data model allows.
- Mode mismatch: move spiky or unpredictable tables to on-demand; move steady
  high-volume tables to provisioned with auto scaling.
- Client behavior: ensure the driver retries throttled requests with
  exponential backoff and jitter so transient throttles do not amplify.

## Output

Provide an analysis summary:
1. Whether throttling is global under-provisioning or a per-partition hot key,
   per table, with the consumed-versus-provisioned evidence.
2. Metric evidence (ReadThrottleEvents/WriteThrottleEvents,
   ConsumedReadCapacityUnits/ConsumedWriteCapacityUnits, SuccessfulRequest
   Latency over the window).
3. Capacity mode recommendation (on-demand vs provisioned) with rationale.
4. A specific, right-sized capacity target or auto scaling configuration, not a
   blanket maximum, plus any partition-key change needed.
5. Recommended CloudWatch alarms (ReadThrottleEvents, WriteThrottleEvents,
   consumed-versus-provisioned ratio) to catch recurrence early.
