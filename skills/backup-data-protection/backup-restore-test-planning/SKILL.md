---
name: backup-restore-test-planning
agent_type: "Generic"
description: Use this skill to plan and validate periodic restore tests for AWS Backup recovery points so RTO and RPO commitments are proven, not assumed. It finds vaults and resources lacking a recent restore test, runs or schedules test restores to isolated targets, and measures restore duration against the stated RTO.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Backup Restore Test Planning

This skill verifies that AWS Backup recovery points can actually be restored within RTO by planning, running, and measuring test restores rather than trusting that backups succeed.

## When to Activate

- No restore test has been performed for a backup vault in the last 90 days.
- A resource has a defined RTO or RPO that has never been validated by an actual restore.
- AWS Backup CompletionTime for jobs is unknown or unmeasured against the RTO.
- A compliance or DR review requires evidence of a successful restore.
- Backup plan lifecycle or vault contents changed and need revalidation.

## Step 1: Inventory Recovery Points

- Call AWS Backup ListBackupVaults and ListRecoveryPointsByBackupVault to enumerate recovery points per resource.
- Read CreationDate and Status to confirm the most recent COMPLETED recovery point per resource.
- Compute backup recency and flag resources whose newest recovery point is older than the stated RPO.

## Step 2: Identify Untested Resources

- Call ListRestoreJobs and correlate by ResourceArn to find the last successful test restore per resource.
- Flag any resource with no successful restore job in the last 90 days.
- Prioritize tier-1 resources with an RTO of 4 hours or less.

## Step 3: Execute Test Restores

- Call StartRestoreJob targeting an isolated account, VPC, or renamed resource so production is untouched.
- Poll DescribeRestoreJob for Status and record CreationDate and CompletionTime.
- Verify restored data integrity (row counts, checksums, or application smoke test) before tearing down.

## Step 4: Measure Against RTO and RPO

- Compute restore duration as CompletionTime minus CreationDate.
- Flag FAIL when restore duration exceeds the stated RTO.
- Flag RPO_GAP when the recovery point age at restore exceeds the stated RPO.

## Step 5: Schedule Recurring Tests

- Recommend a recurring restore-test cadence (for example every 30 days for tier-1, 90 days for tier-2).
- Propose an EventBridge schedule or runbook to trigger StartRestoreJob automatically.
- Define cleanup steps to delete restored test resources and avoid extra cost.

## Output

The skill produces a titled "Backup Restore Test Plan and Results" listing each resource with its newest recovery point date, last successful restore-test date, measured restore duration, and a PASS, FAIL, or RPO_GAP verdict against the stated RTO and RPO. It closes with a prioritized remediation list ordered by tier and gap severity, such as running immediate test restores for untested tier-1 resources, adjusting backup frequency where RPO is missed, tuning restore procedures where RTO is exceeded, and scheduling recurring automated restore tests with cleanup.