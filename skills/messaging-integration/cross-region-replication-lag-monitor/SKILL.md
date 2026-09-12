---
name: cross-region-replication-lag-monitor
agent_type: "Generic"
description: Monitors cross-region replication lag across Amazon S3
  Cross-Region Replication, DynamoDB global tables, and Aurora global databases
  to confirm disaster recovery readiness and protect RPO targets. Use this skill
  when replication falls behind, RPO targets are at risk, or failover readiness
  is in question.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Cross-Region Replication Lag Monitor

Use this skill to measure replication lag on each replicated data service,
translate lag into an actual recovery point objective (RPO), and assess whether
a region failover would meet recovery targets.

## When to Activate

- Replication metrics show a growing backlog of pending objects, items, or
  changes.
- The measured lag exceeds the RPO target for the workload.
- A failover drill or a real incident requires a readiness assessment.
- Replication failures appear for a bucket, table, or database.

## Step 1: Measure S3 Cross-Region Replication Lag

S3 CRR exposes replication progress through CloudWatch metrics:
1. Read ReplicationLatency (seconds), the maximum time objects have been waiting
   to replicate to the destination bucket.
2. Read BytesPendingReplication (total bytes not yet replicated) and
   OperationsPendingReplication (count of objects not yet replicated) to size
   the backlog.
3. These metrics require S3 Replication metrics (and optionally S3 Replication
   Time Control, RTC) to be enabled. RTC commits to replicating 99.99 percent of
   objects within 15 minutes.
4. A rising ReplicationLatency with a growing pending count indicates the
   destination cannot keep pace or replication is blocked.

## Step 2: Measure DynamoDB Global Table Lag

Global tables replicate item changes across regions:
1. Read the ReplicationLatency metric per source-and-destination region pair
   (milliseconds). Typical healthy latency is under 1 second.
2. Read PendingReplicationCount, the number of item updates not yet propagated
   to a replica region.
3. Sustained growth in either metric means the replica is falling behind, often
   due to insufficient write capacity on the replica or a throttled region.

## Step 3: Measure Aurora Global Database Lag

Aurora global databases replicate the storage layer across regions:
1. Read AuroraGlobalDBReplicationLag (milliseconds), the delay between a write
   committing in the primary region and being available in the secondary region.
2. The target is under 1 second under normal conditions; this value directly
   defines the achievable RPO for the database.
3. Also read AuroraGlobalDBReplicatedWriteIO and, where relevant, the data
   transfer metrics to confirm replication is actively flowing.
4. A spike in replication lag under heavy write load signals the secondary
   cannot apply changes as fast as the primary produces them.

## Step 4: Investigate Replication Failures

Distinguish lag from outright failure:
1. S3: replication can fail or skip objects due to missing IAM permissions on
   the replication role, KMS key access on the destination, object size or
   storage class rules, or objects that predate replication being enabled. Check
   the replication status of sample objects and CloudTrail for access errors.
2. DynamoDB: replica write throttling (insufficient capacity or a hot
   partition) stalls propagation; check ThrottledRequests on the replica.
3. Aurora: a secondary region outage, network disruption, or storage pressure
   halts apply; check the cluster events and region health.

## Step 5: Calculate RPO from Actual Lag

Convert measured lag into a recovery point objective:
1. RPO is the maximum data loss window on failover. It equals the replication
   lag at the moment of the primary region loss.
2. For S3, RPO is approximated by ReplicationLatency plus the time to drain
   OperationsPendingReplication at the current replication rate.
3. For DynamoDB, RPO is approximated by ReplicationLatency plus the time to
   propagate PendingReplicationCount.
4. For Aurora, RPO is approximated directly by AuroraGlobalDBReplicationLag.
5. Compare each computed RPO against the documented target (for example, under
   1 second, under 5 minutes, or under 15 minutes) and flag any breach.

## Step 6: Assess Failover Readiness

Determine whether a failover would meet recovery targets now:
1. Confirm current lag is within the RPO target for every replicated service in
   the workload; the workload RPO is the worst case across all services.
2. Confirm the secondary region has capacity (compute, read and write capacity,
   connections) to take over primary traffic, not just to receive replication.
3. Confirm any dependent configuration (Route 53 records, endpoints, secrets,
   IAM) exists in the secondary region so promotion is not blocked.
4. Record the readiness verdict: ready, degraded (within tolerance but at risk),
   or not ready (RPO breached).

## Step 7: Set Alerting Thresholds by Service

Alarm before lag threatens the RPO target:
1. S3: alarm when ReplicationLatency exceeds 900 seconds (the RTC 15 minute
   commitment) or when OperationsPendingReplication grows without draining.
2. DynamoDB: alarm when ReplicationLatency exceeds 1000 milliseconds sustained
   or PendingReplicationCount grows steadily.
3. Aurora: alarm when AuroraGlobalDBReplicationLag exceeds 1000 milliseconds
   sustained, tightening the threshold for stricter RPO targets.
4. Set thresholds below the RPO target so alarms leave time to act before the
   objective is breached.

## Output

Provide a monitoring summary:
1. Current lag per service: S3 ReplicationLatency and pending backlog, DynamoDB
   ReplicationLatency and PendingReplicationCount, and Aurora
   AuroraGlobalDBReplicationLag.
2. Computed RPO per service and the worst-case workload RPO, each compared
   against its target.
3. Any replication failures with root cause (permissions, KMS, throttling, or
   region health).
4. Failover readiness verdict: ready, degraded, or not ready, with the limiting
   service.
5. Recommended CloudWatch alarms and thresholds per service to catch lag before
   it breaches the RPO target.