---
name: runbook-executor-guide
agent_type: "Incident Mitigation"
description: Guides operators through standard operational runbooks for common
  incident scenarios by providing step-by-step mitigation procedures. Use this
  skill when an incident matches a known failure pattern and the responder needs
  structured guidance on executing the appropriate runbook (database failover,
  service restart, cache flush, DNS failover, etc.).
version: "1.0.0"
last_updated: "2026-08-14"
---

# Runbook Executor Guide

Use this skill when an incident matches a known pattern and there is an
established operational procedure to follow for mitigation.

## When to Activate

- An incident root cause is identified and matches a known failure mode.
- On-call engineer requests guidance on mitigation steps.
- Automated remediation is not available and manual steps are needed.
- An incident requires a well-ordered sequence of operations to resolve.

## Common Runbook Scenarios

### Scenario: RDS Primary Failover

**Trigger**: Primary database unresponsive, high connection errors, or AZ failure.

**Pre-checks:**
1. Confirm the read replica is healthy and replication lag < 5 seconds.
2. Verify no active long-running transactions that could block failover.
3. Confirm applications have connection retry logic.

**Procedure:**
1. Initiate RDS failover via `aws rds failover-db-cluster` or `reboot-db-instance --force-failover`.
2. Monitor the event `RDS-EVENT-0049` (failover started) and `RDS-EVENT-0050` (failover complete).
3. Verify new primary is accepting connections - check `DatabaseConnections` metric.
4. Verify application recovery - check error rates returning to baseline.
5. Confirm DNS propagation (CNAME endpoint updated) - typically 30-60 seconds.

**Expected Duration**: 1-3 minutes for Multi-AZ, 5-10 minutes for Aurora.

**Rollback**: If new primary is also unhealthy, restore from latest snapshot to a new instance.

---

### Scenario: ECS Service Stuck Deployment

**Trigger**: ECS deployment stuck in PRIMARY state, new tasks failing health checks.

**Pre-checks:**
1. Check task stopped reasons: `aws ecs describe-tasks` for STOPPED tasks.
2. Check if the new task definition has an image pull error, OOM kill, or health check failure.
3. Verify the target group health check path and expected response code.

**Procedure:**
1. Roll back to previous task definition: `aws ecs update-service --task-definition <previous>`.
2. If circuit breaker is enabled, force a new deployment to trigger rollback.
3. If deployment is stuck, force a new deployment with `--force-new-deployment`.
4. Monitor: wait for running count to match desired count.
5. Verify ALB target health returns to healthy.

**Expected Duration**: 2-5 minutes.

**Rollback**: Further rollback to an even earlier task definition if previous version also fails.

---

### Scenario: ElastiCache Cluster Failover

**Trigger**: Redis primary node unreachable, connection timeouts from application.

**Pre-checks:**
1. Confirm replica nodes are healthy.
2. Check if the issue is network-related (security groups, NACLs) vs node failure.
3. Verify application uses the cluster configuration endpoint (not individual node endpoints).

**Procedure:**
1. If using Redis cluster mode: failover happens automatically.
2. If using Redis non-cluster mode: initiate `aws elasticache modify-replication-group --apply-immediately` with failover.
3. Monitor replication group status -> `available`.
4. Verify application reconnection - cache hit rate recovering.
5. Check for thundering herd (cache miss storm) - may need to warm cache.

**Expected Duration**: 1-2 minutes (automatic), 5 minutes (manual).

---

### Scenario: Lambda Throttling

**Trigger**: Lambda function returning 429 (throttled), async invocations queueing.

**Pre-checks:**
1. Check current concurrency usage vs account limit.
2. Determine if reserved concurrency is set too low.
3. Check if this is an account-wide limit or function-specific.

**Procedure:**
1. If function-specific reserved concurrency: increase the limit.
2. If account-wide: request limit increase via Service Quotas.
3. Short-term: reduce invocation rate at the source (SQS batch size, EventBridge rate).
4. Check DLQ/destination for failed async invocations - these need replay.
5. Monitor `Throttles` metric returning to zero.

**Expected Duration**: Immediate if reserved concurrency, 24-48 hours for account limit increase.

---

### Scenario: DNS/Route53 Failover

**Trigger**: Health check failing on primary endpoint, manual failover needed.

**Pre-checks:**
1. Verify the failover target (secondary region/endpoint) is healthy.
2. Confirm Route53 health check configuration (threshold, regions).
3. Check TTL on the record - clients will cache for this duration.

**Procedure:**
1. If automatic failover is configured: verify it triggered (check health check status).
2. If manual: update Route53 record to point to healthy endpoint.
3. Wait for TTL expiry (or set low TTL pre-emptively for critical records).
4. Monitor DNS resolution from multiple regions.
5. Verify traffic is flowing to the new endpoint.

**Expected Duration**: TTL-dependent (60 seconds if TTL=60, up to 5 minutes for TTL=300).

## General Runbook Execution Principles

1. **Always validate pre-conditions** before executing any mitigation.
2. **Communicate before acting** - notify the incident channel what you're about to do.
3. **One change at a time** - don't stack multiple mitigations simultaneously.
4. **Verify after each step** - confirm the step had the expected effect before proceeding.
5. **Document what you did** - log each action taken with timestamps for the post-mortem.
6. **Know your rollback** - before each step, confirm you know how to undo it.

## Output

After guiding through a runbook, provide:
1. Steps executed and their outcomes
2. Current service status
3. Any remaining follow-up actions
4. Whether the incident can be marked as mitigated