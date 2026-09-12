---
name: rds-snapshot-security-review
agent_type: "Evaluation"
description: Use when reviewing Amazon RDS snapshot sharing and encryption posture. It detects publicly shared snapshots, unencrypted snapshots, and overly broad account sharing, then recommends encryption and access remediation. Apply during data protection audits or after RDS configuration changes.
version: "1.0.0"
last_updated: "2026-08-14"
---

# RDS Snapshot Security Review

Review RDS and Aurora snapshot sharing and encryption to prevent data exposure through misconfigured snapshots.

## When to Activate
- DescribeDBSnapshotAttributes shows a snapshot with the restore attribute value set to all (public sharing).
- DescribeDBSnapshots reports snapshots with Encrypted false.
- Snapshots are shared with AWS account IDs outside the approved organization list.
- Cluster snapshots via DescribeDBClusterSnapshotAttributes are shared publicly.
- Automated snapshots inherit an instance that lacks StorageEncrypted true.

## Step 1: Inventory Snapshots
- Call DescribeDBSnapshots and DescribeDBClusterSnapshots to list manual and automated snapshots.
- Record Encrypted, KmsKeyId, and SnapshotType for each.
- Flag any snapshot with Encrypted false.

## Step 2: Evaluate Sharing Attributes
- Call DescribeDBSnapshotAttributes and DescribeDBClusterSnapshotAttributes for each manual snapshot.
- Inspect the restore attribute values for the literal all, which indicates public sharing.
- Flag any snapshot shared with all as critical.

## Step 3: Validate Cross-Account Sharing
- Compare shared account IDs against the approved organization account list.
- Flag any account ID not on the approved list as unauthorized sharing.
- Recommend removing unknown accounts via ModifyDBSnapshotAttribute with ValuesToRemove.

## Step 4: Assess Encryption Coverage
- Confirm KmsKeyId is a customer managed key where policy requires it.
- Flag unencrypted snapshots and their source instances (StorageEncrypted false).
- Recommend copying unencrypted snapshots to encrypted copies via CopyDBSnapshot with a KMS key.

## Step 5: Remediate and Prevent
- Revoke public sharing immediately by removing the all value from restore attributes.
- Recommend an SCP or Config rule to block public snapshot sharing going forward.
- Recommend enabling encryption at rest for all new instances.

## Output
Produce a titled "RDS Snapshot Security Review" listing publicly shared snapshots, snapshots shared with unapproved accounts, unencrypted snapshots, and their source instances. Include a prioritized remediation list: revoke public sharing on all snapshots first (critical), remove unapproved account sharing second, then create encrypted copies of unencrypted snapshots and add preventive guardrails.