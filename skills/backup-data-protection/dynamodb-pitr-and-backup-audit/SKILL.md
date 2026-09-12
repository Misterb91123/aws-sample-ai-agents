---
name: dynamodb-pitr-and-backup-audit
agent_type: "Generic"
description: Use this skill to audit DynamoDB point-in-time recovery and on-demand or continuous backup coverage across tables. It finds production tables with PITR disabled or without a recent on-demand backup, then recommends enabling PITR and establishing a backup schedule to meet recovery objectives.
version: "1.0.0"
last_updated: "2026-08-14"
---

# DynamoDB PITR and Backup Audit

This skill checks every DynamoDB table for point-in-time recovery status and backup recency so production data is protected against corruption and accidental deletion.

## When to Activate

- A DynamoDB table is tagged or named as production with unknown backup posture.
- DescribeContinuousBackups shows PITR PointInTimeRecoveryStatus DISABLED.
- No on-demand backup exists for a table in the last 30 days.
- A new table was created without backup configuration in the deployment pipeline.
- A compliance review requires evidence of DynamoDB recoverability.

## Step 1: Enumerate Tables

- Call DynamoDB ListTables to enumerate all tables in each region.
- Call DescribeTable to read TableStatus, item count, table size, and tags identifying environment.
- Classify each table as production or non-production from tags and naming.

## Step 2: Check PITR

- Call DescribeContinuousBackups and read ContinuousBackupsStatus and PointInTimeRecoveryDescription.PointInTimeRecoveryStatus.
- Flag CRITICAL for any production table where PointInTimeRecoveryStatus is DISABLED.
- Record EarliestRestorableDateTime and LatestRestorableDateTime for enabled tables.

## Step 3: Audit On-Demand Backups

- Call ListBackups per table and read the most recent BackupCreationDateTime.
- Flag WARNING when no on-demand or AWS Backup recovery point exists in the last 30 days.
- Note tables relying only on PITR where policy also requires periodic snapshots.

## Step 4: Verify Backup Plan Coverage

- Cross-reference AWS Backup selections to confirm DynamoDB tables are included in a backup plan.
- Flag tables not covered by any backup plan selection.
- Confirm backup vault retention meets the required retention window.

## Step 5: Recommend Remediation

- Recommend enabling PITR via UpdateContinuousBackups on every production table where it is disabled.
- Recommend adding uncovered tables to an AWS Backup plan with an appropriate schedule and retention.
- Recommend an on-demand backup cadence for tables that require periodic point-in-time snapshots.

## Output

The skill produces a titled "DynamoDB Backup and PITR Audit" listing each table with its environment classification, PITR status, latest on-demand backup date, backup-plan coverage, and a CRITICAL, WARNING, or OK verdict. It ends with a prioritized remediation list ordered by data criticality, such as enabling PITR on unprotected production tables, adding uncovered tables to a backup plan, establishing a 30-day on-demand backup cadence, and aligning vault retention with policy.