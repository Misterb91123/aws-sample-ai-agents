---
name: rpo-rto-gap-calculator
agent_type: "Generic"
description: Calculates and validates Recovery Point Objective (RPO) and Recovery
  Time Objective (RTO) against actual backup and restore capabilities. Use this
  skill when defining SLAs for data recovery, validating that backup configurations
  can meet stated RPO/RTO targets, or when business stakeholders need to understand
  the data loss and downtime risk for each service.
version: "1.0.0"
last_updated: "2026-08-14"
---

# RPO/RTO Gap Calculator

Use this skill to calculate actual RPO/RTO capabilities and identify gaps
against stated recovery objectives.

## When to Activate

- Defining or reviewing backup SLAs for services.
- Business stakeholder asks "how much data could we lose?"
- Validating DR plan can meet stated objectives.
- After backup configuration change - recalculating capabilities.
- Compliance audit requiring documented RPO/RTO with evidence.

## Step 1: Gather Business Requirements

For each service/data store, determine business expectations:

| Service | Business Impact of Data Loss | Acceptable Data Loss (RPO) | Acceptable Downtime (RTO) |
|---------|------------------------------|---------------------------|--------------------------|
| User database | Customer trust, legal liability | < 5 minutes | < 30 minutes |
| Payment transactions | Revenue loss, reconciliation nightmare | 0 (zero data loss) | < 15 minutes |
| Product catalog | Customer experience, sales impact | < 1 hour | < 1 hour |
| Analytics data | Reporting delay, decision impact | < 24 hours | < 4 hours |
| Logs & audit trail | Compliance risk | < 1 hour | < 24 hours |
| Session data | User inconvenience (re-login) | N/A (ephemeral) | < 5 minutes |

## Step 2: Calculate Actual RPO Capability

For each data store, determine actual RPO based on backup configuration:

**RPO = time since last successful backup (worst case)**

| Backup Method | Theoretical RPO | Actual RPO (Worst Case) |
|---------------|----------------|------------------------|
| Synchronous replication (Aurora Global, DynamoDB Global Tables) | ~0 (seconds) | Network lag (typically < 1s) |
| RDS Multi-AZ (synchronous standby) | ~0 (for AZ failure) | 0 for AZ, backup frequency for region loss |
| Continuous backup / PITR (RDS, DynamoDB) | 5 minutes | 5 minutes (guaranteed by AWS) |
| Hourly snapshots | Up to 1 hour | 1 hour + time since last successful snapshot |
| Daily snapshots / backups | Up to 24 hours | 24 hours + time since last successful backup |
| Weekly backups | Up to 7 days | 7 days |
| Cross-region replication (S3 CRR) | Minutes (replication lag) | Check actual replication lag metric |

**Actual RPO calculation:**
```
Actual RPO = backup_frequency + (time_since_last_backup - backup_frequency if backup is late)

Example: Daily backup at 2 AM, failure at 11 PM
Actual RPO = 21 hours of potential data loss
```

## Step 3: Calculate Actual RTO Capability

For each service, estimate actual recovery time:

**RTO components:**
```
Total RTO = Detection Time + Decision Time + Execution Time + Validation Time

Detection Time: How long until we know recovery is needed
- Automated monitoring: 1-5 minutes
- Human detection: 15-60 minutes

Decision Time: How long to decide to recover
- Automated failover: 0 minutes
- On-call approval: 5-30 minutes
- Management approval: 30-120 minutes

Execution Time: How long the actual recovery takes
- RDS PITR restore: 15-60 minutes (depends on size and log replay)
- RDS snapshot restore: 10-30 minutes (depends on size)
- DynamoDB PITR restore: 10-60 minutes (depends on table size)
- EBS snapshot restore: 5-10 minutes (volume available, but lazy loading)
- Aurora failover: 30-60 seconds (within region)
- Aurora Global failover: 1-5 minutes (cross-region)
- Full region failover (infrastructure rebuild): 30-120 minutes

Validation Time: How long to confirm recovery worked
- Automated health checks: 2-5 minutes
- Manual validation: 15-30 minutes
- Application smoke tests: 5-15 minutes
```

## Step 4: Identify Gaps

Compare actual capability against business requirements:

| Service | Target RPO | Actual RPO | Gap | Target RTO | Actual RTO | Gap |
|---------|-----------|-----------|-----|-----------|-----------|-----|
| User DB | 5 min | 5 min (PITR) | [PASS] None | 30 min | 45 min | [FAIL] 15 min over |
| Payments | 0 | 24 hours (daily snapshot) | [FAIL] Critical | 15 min | 60 min | [FAIL] 45 min over |
| Catalog | 1 hour | 1 hour (hourly snapshot) | [PASS] Tight | 1 hour | 30 min | [PASS] Met |

**Gap classifications:**
- [PASS] **Met**: Actual capability meets or exceeds target.
- [WARN] **Tight**: Meets target but with minimal margin (one failure = non-compliant).
- [FAIL] **Gap**: Actual capability does not meet target.
- [FAIL][FAIL] **Critical Gap**: Gap is > 5x the target (major risk).

## Step 5: Calculate Cost of Closing Gaps

For each gap, determine what's needed:

| Gap | Solution | Additional Cost | New Capability |
|-----|----------|----------------|---------------|
| RPO: 24h -> 0 | Enable PITR / synchronous replication | $X/month | RPO: 5 min or 0 |
| RPO: 1h -> 5min | Increase snapshot frequency + enable PITR | $X/month | RPO: 5 min |
| RTO: 60min -> 15min | Pre-provision standby in DR, automated failover | $X/month | RTO: 5-10 min |
| RTO: 45min -> 30min | Automate restore procedure, reduce decision time | $0 (automation effort) | RTO: 20-25 min |

**Cost vs risk trade-off:**
- What's the business cost of RPO violation? (data loss x value per hour of data)
- What's the business cost of RTO violation? (downtime x revenue per minute)
- If cost of gap > cost of solution -> invest in closing the gap.

## Step 6: Recommendations by Priority

**Priority 1 - Critical gaps (fix immediately):**
- Any service where actual RPO = 24h but target = 0 (payment systems, financial data).
- RTO gaps for revenue-critical services.

**Priority 2 - Tight margins (improve within quarter):**
- Services meeting targets but with no safety margin.
- Targets dependent on everything going perfectly (no room for error).

**Priority 3 - Optimization (plan for next review):**
- Reduce RTO through automation (faster detection, automated failover).
- Reduce cost while maintaining RPO/RTO (optimize backup frequency vs cost).

## Step 7: Document Recovery Procedures

For each service, ensure documented:
1. Step-by-step recovery procedure (reduce decision time).
2. Who can authorize recovery (reduce approval time).
3. Automated vs manual steps (reduce execution time).
4. Validation checklist (reduce validation time).
5. Communication plan during recovery.

## Output

Produce an RPO/RTO gap analysis:
1. **Summary**: Services assessed, gaps found (count by severity), critical gaps requiring immediate action.
2. **RPO/RTO Matrix Table**: Service, target RPO, actual RPO, RPO status, target RTO, actual RTO, RTO status.
3. **Gap Analysis Table**: Service, gap type (RPO/RTO), magnitude, business impact, solution, cost to fix.
4. **RTO Component Breakdown**: Service, detection time, decision time, execution time, validation time, total.
5. **Cost-Risk Analysis**: Business cost of gap vs cost of closing it (justify investment).
6. **Recommendations**: Prioritized list of improvements with expected RPO/RTO after implementation.
7. **Recovery Procedure Status**: Which services have documented and tested procedures vs undocumented.