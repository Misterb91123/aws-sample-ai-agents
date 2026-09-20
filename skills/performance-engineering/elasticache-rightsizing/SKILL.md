---
name: elasticache-rightsizing
agent_type: "Generic"
description: Rightsizes Amazon ElastiCache (Redis, Valkey, and Memcached)
  clusters by analyzing node utilization - memory pressure against maxmemory,
  engine and host CPU saturation, evictions, cache hit rate, connection load,
  and replication lag on read replicas - to identify over- and
  under-provisioned nodes. Use this skill to recommend an optimal node type,
  shard count, and read-replica count from observed workload patterns, distinct
  from health monitoring and serverless cost tracking. Read-only and
  recommend-only.
version: "1.0.0"
last_updated: "2026-09-12"
---

# ElastiCache Cluster Rightsizing

Use this skill to decide whether ElastiCache nodes are the right size and count
for their workload. Rightsizing differs from health monitoring: a healthy node
can still be over-provisioned (wasting spend) or under-provisioned (risking
evictions and latency). Reason over CloudWatch and ElastiCache reads; never
modify a cluster.

## Sources

Read-only.

- ElastiCache API via use_aws: DescribeCacheClusters (node type, engine, number
  of nodes), DescribeReplicationGroups (shards or node groups, replicas per
  shard, multi-AZ, automatic failover), and DescribeCacheParameters for maxmemory
  and maxmemory-policy.
- CloudWatch AWS/ElastiCache metrics: DatabaseMemoryUsagePercentage against
  maxmemory, EngineCPUUtilization and CPUUtilization, Evictions, CacheHitRate or
  CacheHits and CacheMisses, CurrConnections against the connection limit, and
  ReplicationLag on read replicas.

## Method

1. Baseline each cluster or replication group: engine, node type, shard count,
   replicas per shard, and the maxmemory and maxmemory-policy in effect.
2. Memory fit: compare DatabaseMemoryUsagePercentage against maxmemory over the
   window. Sustained high usage with Evictions indicates under-provisioned
   memory; persistently low usage indicates an oversized node type.
3. CPU fit: use EngineCPUUtilization for Redis and Valkey single-threaded engine
   load and CPUUtilization for host load. Sustained engine saturation points to
   more shards (horizontal) rather than a bigger node.
4. Eviction and hit rate: correlate Evictions and a falling CacheHitRate with
   memory pressure to separate a sizing problem from a key-expiry or access
   pattern problem.
5. Connection load: compare CurrConnections against the node limit to flag
   connection exhaustion that mimics a sizing issue.
6. Replica fit: read ReplicationLag per read replica; flag lagging replicas and
   assess whether replica count matches read throughput.
7. Recommend an optimal node type, shard count, and read-replica count from the
   observed pattern, and rank by impact (eviction and saturation first, then
   idle over-provisioning).

## MCP augmentation

Where node-type price and performance comparisons would sharpen a rightsizing
recommendation, recommend connecting the AWS Pricing MCP Server to the Agent
Space and using it in addition to the ElastiCache and CloudWatch reads, never
instead of them. Otherwise no MCP server is required. AWS MCP server names and
availability evolve; verify before relying on one.

## Output

Produce a rightsizing report: per-cluster baseline; memory, CPU, eviction, hit
rate, connection, and replication-lag findings; and a ranked, read-only-safe
recommendation list naming the target node type, shard count, and read-replica
count for each cluster with a safety rating (recommend-only). Reference clusters
by identifier and mask account IDs.
