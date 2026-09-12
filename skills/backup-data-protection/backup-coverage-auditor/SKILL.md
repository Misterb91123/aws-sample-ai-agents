---
name: backup-coverage-auditor
agent_type: "Generic"
description: Audits backup coverage across all AWS resources to identify unprotected
  data stores, misconfigured backup schedules, and gaps in backup policies. Use
  this skill when validating that all critical data is backed up, preparing for
  compliance audits requiring backup evidence, or after discovering a data loss
  event that backups should have prevented.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Backup Coverage Auditor

Use this skill to identify resources that lack backup protection and
validate that backup configurations meet organizational requirements.

## When to Activate

- Periodic backup compliance audit (monthly/quarterly).
- After a data loss event - checking what was or wasn't backed up.
- New service deployed - verify backups are configured.
- Compliance audit requiring backup coverage evidence.
- AWS Backup health check reveals gaps.

## Step 1: Inventory Backupable Resources

List all resources that should have backup protection:

**Databases:**
- RDS instances and clusters (automated backups + snapshots)
- Aurora clusters (continuous backup + snapshots)
- DynamoDB tables (point-in-time recovery + on-demand backups)
- ElastiCache Redis clusters (snapshots)
- DocumentDB clusters
- Neptune clusters
- Redshift clusters

**Storage:**
- EBS volumes (snapshots)
- EFS file systems (AWS Backup)
- S3 buckets (versioning + cross-region replication for critical data)
- FSx file systems

**Compute State:**
- EC2 instances with important local data (AMIs + EBS snapshots)
- ECS task definitions and service configurations (IaC is the backup)
- Lambda function code versions

**Configuration:**
- Secrets Manager secrets
- Parameter Store values
- CloudFormation templates (source control)
- Route53 hosted zone records

## Step 2: Check AWS Backup Configuration

For each resource, verify backup via AWS Backup:

1. **Backup plan assignment:**
   - Is the resource assigned to a backup plan?
   - Check via tags (AWS Backup uses tag-based resource selection).
   - Check via resource ARN in backup plan selections.

2. **Backup plan details:**
   - Schedule (frequency): daily, weekly, monthly?
   - Retention period: how long are backups kept?
   - Lifecycle: transition to cold storage?
   - Copy to another region: cross-region backup?
   - Backup vault: where are backups stored?
   - Vault lock: immutable backups for compliance?

3. **Backup job history:**
   - When was the last successful backup?
   - Are there any failed backup jobs?
   - What's the typical backup completion time?

## Step 3: Check Service-Native Backup

Some services have their own backup mechanisms:

### RDS/Aurora
- [ ] Automated backups enabled (retention period > 0).
- [ ] Retention period meets requirement (1-35 days).
- [ ] Backup window configured (low-traffic period).
- [ ] Manual snapshots for important milestones.
- [ ] Cross-region automated backups (if DR required).
- [ ] Point-in-time recovery functional.

### DynamoDB
- [ ] Point-in-time recovery (PITR) enabled.
- [ ] On-demand backups for critical state.
- [ ] Global tables (if cross-region backup needed).
- [ ] Export to S3 for long-term archival.

### S3
- [ ] Versioning enabled (protects against accidental deletion/overwrite).
- [ ] MFA Delete enabled for critical buckets.
- [ ] Cross-region replication for disaster recovery.
- [ ] Object Lock for immutable compliance data.
- [ ] Lifecycle rules don't delete critical data prematurely.

### EBS
- [ ] Snapshot schedule (DLM or AWS Backup).
- [ ] Snapshots copied to DR region.
- [ ] Old snapshots cleaned up (retention policy).

### ElastiCache Redis
- [ ] Automatic snapshots enabled.
- [ ] Snapshot retention period appropriate.
- [ ] Manual snapshot before maintenance/upgrades.

## Step 4: Identify Unprotected Resources

Flag resources with NO backup:

| Priority | Criteria |
|----------|----------|
| Critical | Production database with no backup (RDS automated backups disabled, DynamoDB PITR off) |
| Critical | EBS volume with unique data and no snapshots |
| High | S3 bucket with non-versioned critical data |
| High | ElastiCache with persistent data and no snapshots |
| Medium | Development database with important test data |
| Medium | EC2 instance with local state not captured in AMI |
| Low | Resources fully managed by IaC (can be recreated) |
| Low | Ephemeral/derived data that can be regenerated |

## Step 5: Validate Backup Freshness

For protected resources, verify backups are current:

1. **Last successful backup timestamp** vs expected frequency.
   - Daily backup plan but last backup 3 days ago = problem.
2. **Backup job failures** in the past 7 days.
3. **Backup size anomalies** - sudden zero-size backup may indicate failure.
4. **Backup window violations** - backup didn't complete before production hours.

## Step 6: Check Backup Security

Verify backups are protected:

1. **Encryption**: Are backups encrypted at rest?
2. **Access control**: Who can delete backups? (principle of least privilege)
3. **Vault lock**: For compliance, are backup vaults locked (immutable)?
4. **Cross-account backup**: Copy to a separate backup account? (protects against account compromise)
5. **Deletion protection**: Is accidental deletion of backup plans prevented?

## Step 7: Calculate Coverage Score

Compute an overall backup coverage metric:

```
Coverage Score = (resources with valid backup / total backupable resources) x 100
```

**Breakdown by:**
- Per service type (RDS: 95%, EBS: 80%, DynamoDB: 60%)
- Per account
- Per environment (production should be 100%)
- Per data classification (confidential data should be 100%)

## Output

Produce a backup coverage report:
1. **Coverage Summary**: Total resources, protected count, unprotected count, coverage percentage.
2. **Unprotected Resources Table**: Resource, type, account, region, data classification, owner, risk level.
3. **Backup Health Table**: Resource, backup method, last successful backup, frequency, retention, issues.
4. **Failed Backup Jobs Table**: Resource, job ID, failure time, error reason, impact.
5. **Coverage by Service Type Chart**: Bar chart showing backup coverage per AWS service.
6. **Security Assessment**: Encryption status, access controls, vault lock configuration.
7. **Recommendations**: Prioritized list of resources needing backup with recommended configuration.