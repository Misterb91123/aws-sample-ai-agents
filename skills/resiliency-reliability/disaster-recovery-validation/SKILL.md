---
name: disaster-recovery-validation
agent_type: "Generic"
description: Validates disaster recovery configurations and readiness across AWS
  infrastructure including cross-region failover, backup integrity, and RTO/RPO
  compliance. Use this skill when performing DR drills, auditing backup health,
  or when assessing recovery capabilities for compliance requirements.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Disaster Recovery Validation

Use this skill to validate that disaster recovery configurations are functional,
backups are recoverable, and RTO/RPO commitments can be met.

## When to Activate

- Scheduled DR drill (quarterly/annual).
- Compliance audit requiring DR evidence.
- After significant architecture changes that may affect DR posture.
- Post-incident where DR failover was needed (or should have been).
- New service deployed that needs DR configuration validated.

## Step 1: Inventory DR Configuration

Map all services and their DR strategies:

| DR Strategy | RTO | RPO | AWS Services |
|-------------|-----|-----|--------------|
| Active-Active | ~0 | ~0 | DynamoDB Global Tables, Aurora Global, CloudFront |
| Active-Passive (hot standby) | Minutes | Seconds | RDS Multi-Region read replica, ECS in standby region |
| Active-Passive (pilot light) | 10-30 min | Minutes | AMIs replicated, infra defined but not running |
| Backup & Restore | Hours | Hours-Days | S3 cross-region replication, EBS snapshot copy |

For each service, document:
1. Current DR strategy
2. Target RTO (Recovery Time Objective)
3. Target RPO (Recovery Point Objective)
4. DR region
5. Last successful DR test date

## Step 2: Validate Backup Integrity

For each backup mechanism, verify:

**RDS Automated Backups:**
1. Backup retention period (meets RPO?)
2. Most recent automated backup timestamp
3. Cross-region backup replication enabled and current
4. Point-in-time recovery window

**EBS Snapshots:**
1. Snapshot schedule running (AWS Backup, DLM)
2. Most recent snapshot for critical volumes
3. Snapshots copied to DR region
4. Snapshot lifecycle - are old snapshots being cleaned up?

**S3 Cross-Region Replication:**
1. Replication status for critical buckets
2. Replication lag (pending objects, pending size)
3. Replication rules covering all necessary prefixes
4. Failed replication objects (if any)

**DynamoDB Backups:**
1. Point-in-time recovery enabled on production tables
2. On-demand backups for critical state
3. Global tables replication lag

**Aurora Global Database:**
1. Replication lag to secondary region
2. Secondary cluster health
3. Managed failover configuration

## Step 3: Validate Failover Readiness

For cross-region failover, verify:

1. **DNS Configuration:**
   - Route53 health checks configured for primary region endpoints
   - Failover routing policies in place
   - Health check is actually testing the critical path (not just a /ping)
   - TTL appropriate for failover speed requirements

2. **Secondary Region Infrastructure:**
   - VPCs, subnets, security groups mirrored in DR region
   - IAM roles and policies replicated (IAM is global, but verify)
   - Secrets and configuration available in DR region
   - SSL certificates valid in DR region
   - AMIs / container images available in DR region

3. **Data Synchronization:**
   - Database replication lag within RPO tolerance
   - S3 replication current
   - State stores synchronized
   - Message queues: strategy for in-flight messages during failover

4. **Application Configuration:**
   - DR region connection strings and endpoints configured
   - Feature flags and configuration accessible from DR region
   - Third-party integrations configured for DR endpoints

## Step 4: RTO/RPO Compliance Check

Validate theoretical vs actual recovery capabilities:

**RPO Validation:**
- For each data store: latest replication timestamp vs current time
- If gap > RPO target: flag as non-compliant
- Account for replication lag under load (may be higher during peak)

**RTO Validation:**
- For each service: estimated recovery time components:
  - Detection time (how long until we know we need to failover)
  - Decision time (how long to decide to failover)
  - Execution time (how long the failover takes)
  - Validation time (how long to confirm DR is working)
- Sum of components = estimated actual RTO
- If estimated RTO > target RTO: flag and identify bottleneck

## Step 5: Check for DR Drift

DR configurations often drift from their intended state:

1. Infrastructure-as-code drift - is DR region IaC still in sync?
2. New services added to primary without DR equivalent.
3. Capacity changes in primary not reflected in DR.
4. Schema changes applied to primary but not DR replicas.
5. New secrets or configs added to primary but not DR region.
6. Network ACLs or security groups modified in primary only.

## Step 6: DR Test Recommendations

Based on findings, recommend test procedures:

**Tabletop Exercise (low risk):**
- Walk through the failover procedure on paper
- Identify gaps in documentation
- Verify team knows their roles

**Component Test (medium risk):**
- Test individual failover mechanisms (RDS failover, DNS switch)
- Validate backup restoration to a test environment
- Time the recovery for RTO measurement

**Full Failover Test (higher risk):**
- Redirect production traffic to DR region
- Operate from DR for a defined period
- Fail back to primary after validation
- Measure actual RTO/RPO achieved

## Output

Produce a DR readiness report:
1. **DR Coverage Summary**: Services with DR configured vs without, overall readiness score.
2. **RTO/RPO Compliance Table**: Service, target RTO, estimated RTO, target RPO, current RPO, status (compliant/gap).
3. **Backup Health Table**: Backup type, resource, latest backup, age, DR region copy status.
4. **Replication Lag Table**: Data store, replication type, current lag, RPO threshold, status.
5. **DR Drift Findings**: Components out of sync between primary and DR regions.
6. **Last Test Date Table**: Service, DR strategy, last tested, days since test, recommended next test.
7. **Recommendations**: Prioritized list of gaps to close and tests to schedule.