---
name: documentdb-cluster-health
agent_type: "Incident RCA"
description: Investigates Amazon DocumentDB (with MongoDB compatibility) cluster
  and instance health by analyzing CPU saturation, connection limits, replica
  lag, buffer cache hit ratio, read/write latency, and storage volume growth.
  Use this skill when a DocumentDB cluster shows high CPU, connection
  exhaustion, rising replica lag, slow queries, or when a primary failover has
  occurred or is at risk. It correlates AWS/DocDB CloudWatch metrics with
  cluster topology to isolate whether the primary or a replica is the source of
  degradation and recommends targeted, read-only-safe remediation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# DocumentDB Cluster Health

Use this skill to diagnose Amazon DocumentDB cluster and instance degradation,
localize the failing instance, and recommend specific remediation. DocumentDB
is a distinct engine from RDS and Aurora: it separates compute instances from a
shared cluster storage volume, and each instance reports its own AWS/DocDB
CloudWatch metrics.

## When to Activate

- CPUUtilization on the primary or a replica is sustained above 80 percent.
- DatabaseConnections approaches the instance connection ceiling.
- DBInstanceReplicaLag is rising and does not recover.
- BufferCacheHitRatio drops below 95 percent, driving read latency up.
- ReadLatency or WriteLatency exceeds application SLO.
- VolumeBytesUsed is growing faster than expected or nearing budget.
- A failover occurred, or you need to confirm the cluster can fail over safely.

## Step 1: Inventory the Cluster and Instances

Establish the topology before reading metrics. Metrics are per instance, so you
must know which instance is the writer.

1. List clusters and members with use_aws:
   `docdb describe-db-clusters` to get the cluster, engine version, and the
   member list with `IsClusterWriter` per instance.
2. `docdb describe-db-instances` to get instance class, AZ, status, and
   `PromotionTier` for each member.
3. Record for each instance: role (writer vs reader), instance class (drives
   vCPU, RAM, and the connection ceiling), AZ placement, and status.
4. Note the cluster parameter group; connection and TLS settings live there.

A single-instance cluster has no failover target; flag that immediately.

## Step 2: Check CPU and Connections

Read the following AWS/DocDB metrics per instance (dimension
DBInstanceIdentifier) over the incident window:

| Metric | Healthy | Investigate | Meaning |
|--------|---------|-------------|---------|
| CPUUtilization | < 70% | > 80% sustained | Compute bound: heavy queries, missing indexes, or undersized class |
| DatabaseConnections | < 80% of max | near max | Connection saturation; new clients rejected |
| FreeableMemory | stable | trending to 0 | Memory pressure; cache thrash and possible instance restart |

1. If CPUUtilization is high on the writer only, suspect write-heavy load,
   unindexed queries, or aggregation pipelines. Correlate with the slow query
   profiler (profiler logs to CloudWatch Logs when enabled).
2. If DatabaseConnections is near the ceiling, check for connection leaks or a
   missing connection pool. The per-instance connection limit scales with
   instance class RAM; smaller classes cap lower.
3. If FreeableMemory trends toward zero while connections climb, each
   connection consumes memory; connection growth can force cache eviction.

## Step 3: Check Replica Lag

DBInstanceReplicaLag measures how far a reader trails the writer, in
milliseconds.

1. Read DBInstanceReplicaLag (Maximum) per replica.
2. Interpretation:
   - Under 100 ms is normal for a healthy cluster.
   - Hundreds of ms to seconds indicates the replica cannot apply the write
     stream fast enough, usually due to replica CPU saturation or a replica
     running a smaller instance class than the writer.
3. High replica lag risks stale reads for readers using a secondary read
   preference, and it lengthens failover recovery because a lagging replica is
   a poor promotion candidate.
4. Correlate replica lag with that replica's CPUUtilization and read workload.

## Step 4: Check Buffer Cache Hit Ratio and Latency

BufferCacheHitRatio is the percentage of reads served from memory rather than
storage. Low values are the most common cause of read latency in DocumentDB.

1. Read BufferCacheHitRatio per instance.
   - 99 percent or higher is healthy.
   - Below 95 percent means the working set no longer fits in memory; reads
     fall through to the cluster volume and ReadLatency climbs.
2. Correlate with ReadLatency and WriteLatency (seconds per operation). A cache
   ratio drop that coincides with a ReadLatency spike confirms cache pressure.
3. Root causes of a falling cache ratio: working set larger than instance RAM,
   a new query scanning cold collections, or an index dropped so queries now
   scan documents.

Decision guidance:

| BufferCacheHitRatio | ReadLatency | Likely cause | Direction |
|---------------------|-------------|--------------|-----------|
| >= 99% | low | Healthy | No action |
| 95-99% | slightly elevated | Working set near memory limit | Add indexes or plan scale-up |
| < 95% | high | Working set exceeds RAM or missing index | Add index, or scale instance class up |

## Step 5: Check Storage Growth

DocumentDB storage is a shared cluster volume that grows automatically and does
not shrink when data is deleted.

1. Read VolumeBytesUsed at the cluster level and compute the growth rate over
   the trailing days.
2. Confirm whether growth matches expected ingestion. Unexpected growth can
   come from an index build, large TTL backlog, or oversized documents.
3. Because the volume does not auto-shrink, deleting data reclaims logical
   space for reuse but does not reduce VolumeBytesUsed. Plan capacity against
   the high-water mark.

## Step 6: Assess Failover Readiness

Before recommending any change, confirm the cluster can survive a primary loss.

1. Confirm at least one replica exists in a different AZ from the writer.
2. Confirm each replica's PromotionTier; the lowest-numbered tier with a
   healthy, low-lag replica is promoted first.
3. Confirm candidate replicas have low DBInstanceReplicaLag and are not CPU
   saturated; a lagging or saturated replica extends recovery time.
4. If a failover already occurred, identify the new writer from
   describe-db-clusters and check whether the trigger (CPU, memory, hardware)
   persists on the new writer.

## Step 7: Remediate

Recommend specific, read-only-safe actions matched to the finding. Never
disable TLS, auditing, or the profiler, and never open the cluster to public
access.

- High CPU from queries: add or correct indexes so queries stop scanning
  collections; use explain to confirm index use. Scale the instance class up
  only if the workload is genuinely compute bound after indexing.
- Connection saturation: introduce or right-size a client-side connection pool;
  do not raise limits by moving to a larger class before fixing leaks.
- Replica lag: match replica instance class to the writer, or reduce read load
  on the lagging replica; add a replica to spread reads.
- Low cache hit ratio: add indexes to shrink the scanned working set, or scale
  the instance class up to fit the working set in RAM.
- Storage growth: verify TTL indexes are pruning as intended and confirm
  document sizes; plan capacity to the high-water mark.
- Failover readiness: add a replica in a second AZ and set PromotionTier so a
  healthy replica is the preferred target.

## Output

Provide an investigation summary:
1. Failing instance and its role (writer vs reader) with the driving metric.
2. Root cause with evidence (CPUUtilization, DatabaseConnections,
   DBInstanceReplicaLag, BufferCacheHitRatio, ReadLatency/WriteLatency,
   VolumeBytesUsed values over the incident window).
3. Specific remediation (indexing, pooling, replica sizing, or scale-up).
4. Failover readiness assessment and any gap (single AZ, lagging candidate).
5. Recommended CloudWatch alarms (CPUUtilization, DatabaseConnections,
   DBInstanceReplicaLag, BufferCacheHitRatio) to catch recurrence early.
