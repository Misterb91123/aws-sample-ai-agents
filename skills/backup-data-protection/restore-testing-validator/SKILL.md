---
name: restore-testing-validator
agent_type: "Generic"
description: Validates that backups are actually restorable by planning and assessing
  restore test procedures. Use this skill when performing periodic restore validation,
  after a backup configuration change, or when compliance requires evidence that
  backups are recoverable and meet RTO/RPO targets.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Restore Testing Validator

Use this skill to plan and validate that backups can actually be restored
successfully within required timeframes.

## When to Activate

- Periodic restore validation (quarterly recommended).
- After backup configuration changes (new plan, new vault, new region).
- Compliance requirement for restore testing evidence.
- Post-incident where restore was needed (validate before relying on it again).
- New critical data store added - verify backup is restorable.

## Step 1: Identify Critical Restore Targets

Prioritize what to test restore for:

**Must test (critical):**
- Production databases (RDS, Aurora, DynamoDB).
- Data that cannot be regenerated (customer data, financial records).
- Resources where restore failures mean extended outage.
- Data stores subject to compliance requirements.

**Should test (important):**
- Configuration data (Secrets Manager, Parameter Store).
- EBS volumes with application state.
- EFS file systems with shared data.
- ElastiCache with session or persistent data.

**Good to test (optional):**
- Development/staging databases.
- Resources fully recreatable from IaC.
- Derived data (can be rebuilt from source).

## Step 2: Define Restore Test Scenarios

For each target, define what to test:

### RDS/Aurora Restore Test
1. **Point-in-time restore**: Restore to a specific timestamp.
   - Validates that continuous backup is working.
   - Measures restoration time (contributes to RTO).
   - Verify restored data matches expectations.
2. **Snapshot restore**: Restore from latest automated snapshot.
   - Faster than PITR (fewer logs to replay).
   - Validate snapshot integrity.
3. **Cross-region restore**: Restore from cross-region backup copy.
   - Validates DR backup path.
   - Measures cross-region restore time.

### DynamoDB Restore Test
1. **PITR restore**: Restore table to a point in time.
   - Creates a new table with the restored data.
   - Validate item count and sample data.
2. **On-demand backup restore**: Restore from a named backup.
   - Validate backup completeness.
3. **Export restore**: Import from S3 export.
   - Validates long-term archival recovery path.

### EBS Restore Test
1. **Snapshot to volume**: Create a volume from snapshot.
   - Attach to a test instance and validate data.
   - Measure time to create and attach.
2. **Cross-region snapshot restore**: From DR region copy.
   - Validates DR recovery path.

### S3 Restore Test
1. **Version restore**: Restore a deleted object via version ID.
   - Validate versioning is working.
2. **Cross-region recovery**: Access CRR replica data.
   - Validate replication completeness.

## Step 3: Execute Restore Validation

For each restore test:

**Pre-test:**
1. Identify the backup to restore (latest, specific timestamp, specific snapshot ID).
2. Prepare the target environment (test VPC, isolated network, test instance).
3. Document the test procedure and expected outcome.
4. Set a time limit (if restore exceeds expected RTO, note as finding).

**During test:**
1. Start timer when restore is initiated.
2. Record each step and timestamp.
3. Note any errors or warnings during restore.
4. Record when restore completes (data available).

**Post-test validation:**
1. **Data integrity**: Does the restored data look correct?
   - Row counts match expectations.
   - Sample queries return expected results.
   - Latest transactions present (for PITR: up to specified time).
2. **Application compatibility**: Can the application connect and function with restored data?
3. **Performance**: Is restored resource performing normally? (EBS snapshot restore performance may be initially slow due to lazy loading).

## Step 4: Measure Restore Performance

For each test, record:

| Metric | Value | Target |
|--------|-------|--------|
| Restore initiation time | How long to start the restore job | < 5 minutes |
| Data availability time | When data becomes accessible | Within RTO target |
| Full performance time | When performance reaches normal (EBS: after all blocks fetched) | Within 2x RTO |
| Data completeness | Are all expected records present? | 100% |
| Data freshness | Newest record timestamp in restore | Within RPO target |

## Step 5: Validate RTO/RPO Compliance

Compare actual restore performance against requirements:

**RPO Check:**
- Newest data in backup vs stated RPO.
- If RPO = 1 hour: backup must contain data from within the last hour.
- For PITR: RPO is typically 5 minutes (continuous backup).
- For daily snapshots: RPO is up to 24 hours.

**RTO Check:**
- Time from "decision to restore" to "service operational on restored data."
- Include all steps: restore initiation, data copy, configuration, validation, DNS switch.
- If actual RTO > target RTO: flag as non-compliant.

## Step 6: Document Results

For each test, produce evidence:

```
Restore Test Record:
- Date: [test date]
- Resource: [resource name/ID]
- Backup type: [PITR / Snapshot / On-demand]
- Backup timestamp: [when backup was taken]
- Restore started: [timestamp]
- Restore completed: [timestamp]
- Restore duration: [minutes]
- Data validation: [PASS/FAIL with details]
- RTO compliance: [PASS (within target) / FAIL (exceeded by X minutes)]
- RPO compliance: [PASS (data freshness within target) / FAIL]
- Issues found: [any problems encountered]
- Tester: [who performed the test]
```

## Step 7: Clean Up Test Resources

After validation:
1. Delete restored test databases (avoid ongoing cost).
2. Remove test EBS volumes and snapshots.
3. Clean up test network resources.
4. Verify no test data leaked to production.
5. Document that cleanup was performed.

## Output

Produce a restore testing report:
1. **Test Summary**: Resources tested, pass/fail counts, overall restore readiness.
2. **Test Results Table**: Resource, backup type, restore duration, data integrity (pass/fail), RTO met (yes/no), RPO met (yes/no).
3. **RTO/RPO Compliance Matrix**: Resource, target RTO, actual RTO, target RPO, actual RPO, status.
4. **Failed Tests**: Details on any restore failures with root cause.
5. **Performance Findings**: Restore times that are close to or exceeding targets (at risk).
6. **Recommendations**: Actions to improve restore readiness (more frequent backups, faster restore procedures).
7. **Compliance Evidence**: Formatted documentation suitable for auditor review.