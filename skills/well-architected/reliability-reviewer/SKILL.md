---
name: reliability-reviewer
agent_type: "Evaluation"
description: Evaluates infrastructure against the AWS Well-Architected Reliability
  pillar, checking workload architecture for fault tolerance, recovery planning,
  change management, and failure isolation. Use this skill during Well-Architected
  reviews, resilience assessments, or when designing for high availability.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Reliability Reviewer

Use this skill to evaluate workloads against the Reliability pillar
of the AWS Well-Architected Framework.

## When to Activate

- Well-Architected review session for reliability pillar.
- New service being assessed for production readiness.
- Post-incident where reliability gaps contributed.
- Designing architecture for high-availability requirements.

## Step 1: Foundations (REL 1-2)

1. **Manage service quotas and constraints:**
   - Are service quotas monitored and proactively increased?
   - Is capacity planning performed for growth?
   - Are fixed limits (VPC CIDRs, AZ capacity) accounted for?

2. **Plan network topology:**
   - Is the VPC designed with proper subnet segmentation?
   - Are there multiple AZs used?
   - Is connectivity redundant (multiple NAT GWs, redundant VPN/DX)?
   - Is IP addressing planned for future growth?

## Step 2: Workload Architecture (REL 3-5)

1. **Design for distributed systems:**
   - Is the architecture decomposed into independent components?
   - Are service-to-service calls resilient (timeouts, retries, circuit breakers)?
   - Is there graceful degradation when dependencies fail?

2. **Design interactions to prevent failures:**
   - Are queues used to decouple producers from consumers?
   - Is back-pressure implemented for overload protection?
   - Are idempotency tokens used for retry safety?
   - Are there rate limits to protect backend services?

3. **Design interactions to mitigate failures:**
   - Is load shedding implemented for overload?
   - Are circuit breakers configured on downstream calls?
   - Are fallback responses available (cached data, default values)?

## Step 3: Change Management (REL 6-8)

1. **Monitor workload resources:**
   - Are all components monitored (compute, data, network)?
   - Are alarms configured for anomalous behavior?
   - Are health checks properly defined?
   - Is distributed tracing enabled for cross-service visibility?

2. **Design for auto-scaling:**
   - Is auto-scaling configured for variable demand?
   - Is the scaling policy responsive enough (not too slow)?
   - Is there sufficient maximum capacity for peak?
   - Is scale-in safe (graceful connection draining)?

3. **Deploy changes safely:**
   - Are deployments automated with health check validation?
   - Is there automated rollback on failure?
   - Are changes deployed incrementally (canary, rolling)?
   - Can deployments be reversed quickly?

## Step 4: Failure Management (REL 9-13)

1. **Back up data:**
   - Is backup configured for all data stores?
   - Is backup recovery tested regularly?
   - Are backups stored in a separate region?

2. **Use fault isolation:**
   - Is the workload deployed across multiple AZs?
   - Are there bulkheads between failure domains?
   - Is each AZ independently capable of serving traffic?

3. **Design to withstand component failures:**
   - Can the workload survive one AZ failure?
   - Are single points of failure eliminated?
   - Is data replicated synchronously (RDS Multi-AZ, Aurora multi-writer)?

4. **Test reliability:**
   - Has the workload been chaos-tested?
   - Are failover mechanisms tested regularly?
   - Are game days conducted?

5. **Plan for disaster recovery:**
   - Is there a defined DR strategy (active-active, active-passive, backup-restore)?
   - Are RTO/RPO targets documented and tested?
   - Is DR infrastructure kept in sync with primary?

## Scoring

Rate each area:
- **Resilient** (3): Fully implemented and tested
- **Partial** (2): Implemented but not tested or incomplete
- **Gap** (1): Not implemented, creates availability risk
- **N/A** (0): Not applicable

## Output

Provide:
1. Per-area score with specific single-points-of-failure identified.
2. Overall Reliability score.
3. Blast radius assessment for each identified gap.
4. Top 5 reliability improvements prioritized by impact.