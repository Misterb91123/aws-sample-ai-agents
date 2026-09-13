---
name: memorydb-redis-cluster-health
agent_type: "Incident RCA"
description: Investigates Amazon MemoryDB for Redis cluster and shard health by
  analyzing engine CPU, database memory usage, evictions, swap, replication lag,
  connection saturation, and shard and node failover. Use this skill when a
  MemoryDB cluster shows high CPU, memory pressure, rising evictions, growing
  replication lag, connection exhaustion, or when a primary node has failed over
  or is at risk. It correlates AWS/MemoryDB CloudWatch metrics with shard
  topology to isolate the failing node and recommend targeted, read-only-safe
  remediation. This is MemoryDB, a durable multi-AZ primary datastore, not
  ElastiCache.
version: "1.0.0"
last_updated: "2026-08-14"
---

# MemoryDB for Redis Cluster Health

Use this skill to diagnose Amazon MemoryDB for Redis cluster degradation,
localize the failing shard or node, and recommend specific remediation.

Note: this skill covers MemoryDB, which is a durable, Multi-AZ primary database
that persists data via a transactional log. It is a different service from
ElastiCache (a cache), which is covered by its own skill. Metrics live under
the AWS/MemoryDB namespace, and topology is read with the memorydb API.

## When to Activate

- CPUUtilization or EngineCPUUtilization is sustained high on a node.
- DatabaseMemoryUsagePercentage is climbing toward 100 percent.
- Evictions are rising, indicating memory pressure.
- SwapUsage is non-zero, indicating the node is spilling to disk.
- ReplicationLag between a primary and its replica is growing.
- CurrConnections approaches the connection ceiling.
- A primary node failed over, or you need to confirm shards can fail over.

## Step 1: Inventory Clusters and Shards

MemoryDB partitions the keyspace across shards; each shard has one primary and
zero or more replicas. Metrics are per node, so map nodes to shards first.

1. `memorydb describe-clusters` via use_aws with node details to get shards,
   the node list per shard, node roles (primary vs replica), node type, AZ, and
   status.
2. Record for each shard: primary node, replica nodes, and AZ spread.
3. Note the number of shards and replicas per shard; a shard with zero replicas
   has no in-shard failover target.

## Step 2: Check Engine CPU and Memory Usage

Read AWS/MemoryDB metrics (dimensions ClusterName, NodeName) over the window.

| Metric | Healthy | Investigate | Meaning |
|--------|---------|-------------|---------|
| EngineCPUUtilization | < 70% | > 90% | Redis single-thread engine saturation |
| CPUUtilization | < 70% | high with low EngineCPU | Host-level work (background save, networking) |
| DatabaseMemoryUsagePercentage | < 80% | > 90% | Memory nearly full; evictions imminent |

1. EngineCPUUtilization measures the Redis engine thread specifically. Because
   Redis command execution is single-threaded, EngineCPU near 100 percent means
   the shard is command-bound even if host CPUUtilization looks moderate.
2. High EngineCPU points to expensive commands (KEYS, large SORT, big
   MGET/HGETALL, Lua scripts) or simply too many operations per second for one
   shard.
3. DatabaseMemoryUsagePercentage climbing toward 100 percent triggers the
   maxmemory policy: either evictions or write rejections, depending on policy.

## Step 3: Check Evictions and Swap

1. Read Evictions. Sustained non-zero evictions mean the dataset exceeds
   available memory and keys are being removed per the eviction policy.
   - For a cache this may be acceptable; for MemoryDB used as a primary
     datastore, evictions can mean data loss for the affected keys, so treat
     rising evictions as a capacity incident.
2. Read SwapUsage. Any meaningful swap means the node is paging memory to disk,
   which sharply degrades latency; the node is over-committed on memory.
3. Correlate Evictions and SwapUsage with DatabaseMemoryUsagePercentage to
   confirm memory pressure as the root cause.

## Step 4: Check Replication Lag

ReplicationLag measures how far a replica trails its primary.

1. Read ReplicationLag per replica.
   - Sub-second is normal.
   - Growing lag means the replica cannot apply the primary's write stream,
     usually because the replica is EngineCPU saturated or undersized relative
     to the primary.
2. High replication lag weakens durability guarantees and makes the replica a
   poor failover candidate, lengthening recovery.
3. Correlate replica lag with that replica's EngineCPUUtilization and network
   throughput.

## Step 5: Check Connections

1. Read CurrConnections per node against the node's connection ceiling.
2. Saturation causes new client connections to be refused. Common causes:
   missing client-side pooling, connection leaks, or a client storm during a
   failover as clients reconnect.
3. Correlate CurrConnections with NewConnections rate; a spike in new
   connections during an incident often indicates a reconnect storm.

## Step 6: Assess Shard and Failover Health

1. Confirm each shard has at least one replica in a different AZ from its
   primary; a shard with no replica cannot fail over within the shard.
2. Confirm replica ReplicationLag is low so promotion is fast and loses minimal
   in-flight writes.
3. If a failover occurred, identify the new primary from describe-clusters and
   verify the trigger (memory pressure, EngineCPU, host fault) is not repeating
   on the new primary.
4. Confirm keyspace balance across shards; a single hot shard (uneven key
   distribution or a hot key) saturates one node while others idle.

## Step 7: Remediate

Recommend specific, read-only-safe actions. Never disable encryption
in-transit or at-rest, never disable ACL authentication, and never expose the
cluster publicly.

- High EngineCPU: eliminate expensive commands (replace KEYS with SCAN, avoid
  large multi-key operations, review Lua scripts); if the shard is genuinely
  throughput-bound, add shards to spread the keyspace.
- Memory pressure and evictions: add shards or move to a larger node type to
  increase total memory; review TTLs and data model to shrink footprint. For a
  primary datastore, size to avoid evictions entirely.
- Swap usage: reduce memory footprint or scale the node type up; swap indicates
  over-commitment.
- Replication lag: match replica node type to the primary and reduce replica
  load; investigate network throughput.
- Connection saturation: introduce or right-size client pooling and enable
  backoff on reconnect to avoid reconnect storms.
- Hot shard: rebalance the keyspace or address a hot key with client-side
  sharding or key design; add shards to redistribute.
- Failover gap: add a replica in a second AZ for any shard that lacks one.

## Output

Provide an investigation summary:
1. Failing shard and node with its role (primary vs replica) and driving metric.
2. Root cause with evidence (EngineCPUUtilization, CPUUtilization,
   DatabaseMemoryUsagePercentage, Evictions, SwapUsage, ReplicationLag,
   CurrConnections over the incident window).
3. Specific remediation (command tuning, add shards, node type change, pooling).
4. Shard and failover health assessment and any gap (no replica, hot shard,
   lagging candidate), noting this is MemoryDB durability, not cache behavior.
5. Recommended CloudWatch alarms (EngineCPUUtilization,
   DatabaseMemoryUsagePercentage, Evictions, ReplicationLag, CurrConnections).
