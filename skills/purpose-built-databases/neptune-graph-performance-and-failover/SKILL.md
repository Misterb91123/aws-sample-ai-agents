---
name: neptune-graph-performance-and-failover
agent_type: "Incident RCA"
description: Investigates Amazon Neptune graph database performance by analyzing
  Gremlin and SPARQL request rates and errors, main request queue backlog, query
  latency, reader replica lag, and failover readiness. Use this skill when graph
  queries slow down, the request queue backs up, Gremlin or SPARQL error counts
  rise, a replica falls behind, or a primary failover has occurred or is at
  risk. It correlates AWS/Neptune CloudWatch metrics with cluster topology to
  find whether the writer or a reader is saturated and recommends targeted,
  read-only-safe remediation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Neptune Graph Performance and Failover

Use this skill to diagnose Amazon Neptune query slowdowns and failover risk,
localize the failing instance, and recommend specific remediation. Neptune is a
purpose-built graph engine with its own request queue and per-language
(Gremlin, SPARQL, openCypher) metrics; it is distinct from RDS and Aurora.

## When to Activate

- Graph query latency exceeds application SLO.
- MainRequestQueuePendingRequests is rising, indicating queued work.
- GremlinErrors or SparqlErrors counts increase.
- ClusterReplicaLagMaximum is rising and does not recover.
- CPUUtilization on the writer or a reader is sustained high.
- A failover occurred, or you need to confirm the cluster can fail over safely.

## Step 1: Inventory the Cluster

Neptune metrics are per instance, so identify the writer first.

1. `neptune describe-db-clusters` via use_aws to get the member list with the
   writer flag, engine version, and reader endpoints.
2. Record each instance: role (writer vs reader), instance class, AZ, status,
   and promotion tier.
3. Note whether the application uses the cluster (writer) endpoint, the reader
   endpoint, or instance endpoints; routing determines which instance absorbs
   load.

## Step 2: Check Request Rate and Errors

Read AWS/Neptune metrics (dimension DBInstanceIdentifier) over the incident
window.

| Metric | Meaning | Investigate |
|--------|---------|-------------|
| TotalRequestsPerSec | Overall request throughput | Sudden change vs baseline |
| GremlinRequestsPerSec | Gremlin traversal rate | Spike aligned with latency |
| SparqlRequestsPerSec | SPARQL query rate | Spike aligned with latency |
| GremlinErrors | Failed Gremlin requests | Any sustained non-zero |
| SparqlErrors | Failed SPARQL requests | Any sustained non-zero |

1. Compare current request rate to baseline. A traffic surge that tracks the
   latency rise points to load, not a defect.
2. Rising GremlinErrors or SparqlErrors indicates rejected or failing queries.
   Common causes: malformed queries, timeouts, memory limits on a single query,
   or the queue rejecting requests once full.
3. Split traffic by language; a Gremlin-only regression narrows the search to
   Gremlin traversals and their indexes.

## Step 3: Check Queue Backlog and Latency

Neptune serves requests through a bounded main request queue. Backlog here is
the clearest signal that the instance cannot keep up.

1. Read MainRequestQueuePendingRequests per instance.
   - Near 0 is healthy.
   - Sustained growth means arrivals exceed the instance's processing rate;
     the queue can hold a bounded number of requests and rejects new ones once
     full, surfacing as errors to clients.
2. Correlate queue growth with CPUUtilization. A full queue plus high CPU means
   the instance is compute bound on query evaluation.
3. Identify expensive traversals: unbounded or high-fan-out Gremlin traversals
   and Cartesian SPARQL patterns consume disproportionate CPU and hold queue
   slots, starving cheap queries.
4. Check BufferCacheHitRatio; a low ratio forces reads from storage and slows
   every query, indirectly growing the queue.

## Step 4: Check Reader Replica Lag

ClusterReplicaLagMaximum reports the largest reader lag behind the writer, in
milliseconds.

1. Read ClusterReplicaLagMaximum over the window.
   - Low tens of ms is normal.
   - Sustained hundreds of ms or more means readers serve stale graph state and
     are weak failover candidates.
2. Correlate reader lag with reader CPUUtilization and MainRequestQueuePending
   Requests; a saturated reader lags because it cannot both serve reads and
   apply the write stream.
3. If the application reads through the reader endpoint, high lag can present as
   inconsistent results after a write.

## Step 5: Assess Failover Readiness

1. Confirm at least one reader exists in a different AZ from the writer.
2. Confirm reader promotion tiers; the lowest-numbered tier with a healthy,
   low-lag reader is promoted first.
3. Confirm candidate readers are not queue-saturated and have low
   ClusterReplicaLagMaximum, so promotion is fast and the promoted instance can
   immediately absorb write traffic.
4. If a failover already occurred, identify the new writer from
   describe-db-clusters and verify the original trigger (CPU, queue backlog,
   hardware) is not repeating on the new writer.

## Step 6: Remediate

Recommend specific, read-only-safe actions. Never open the cluster to public
access, and never disable IAM database authentication or audit logging.

- Queue backlog with high writer CPU: optimize the hot traversals (add range
  filters, cap fan-out, use indexed property lookups); scale the writer class
  up only if the workload is genuinely compute bound after tuning.
- Read-heavy backlog: add reader instances and route read-only queries to the
  reader endpoint to offload the writer.
- Rising errors: capture failing queries and fix query shape or raise the
  per-query timeout deliberately rather than globally; ensure clients retry
  with backoff on transient queue-full rejections.
- Reader lag: match reader instance class to the writer and reduce read load on
  the lagging reader.
- Low cache hit ratio: scale the instance class up so the working graph fits in
  memory.
- Failover gap: add a reader in a second AZ and set promotion tiers so a
  healthy reader is the preferred target.

## Output

Provide an investigation summary:
1. Failing instance and role (writer vs reader) with the driving signal.
2. Root cause with evidence (TotalRequestsPerSec, GremlinRequestsPerSec/
   SparqlRequestsPerSec, GremlinErrors/SparqlErrors,
   MainRequestQueuePendingRequests, ClusterReplicaLagMaximum, CPUUtilization,
   BufferCacheHitRatio over the incident window).
3. Specific remediation (query tuning, reader scaling, routing, class change).
4. Failover readiness assessment and any gap.
5. Recommended CloudWatch alarms (MainRequestQueuePendingRequests,
   GremlinErrors/SparqlErrors, ClusterReplicaLagMaximum, CPUUtilization).
