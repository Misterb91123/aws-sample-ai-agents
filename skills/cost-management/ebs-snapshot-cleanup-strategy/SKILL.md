---
name: ebs-snapshot-cleanup-strategy
agent_type: "Generic"
description: Use when reclaiming cost from orphaned and aged EBS snapshots. It finds snapshots whose source volumes and AMIs no longer exist, ranks them by age and size, and recommends a safe deletion and lifecycle strategy. Apply during cost optimization sweeps or storage cleanup.
version: "1.0.0"
last_updated: "2026-08-14"
---

# EBS Snapshot Cleanup Strategy

Reclaim storage cost by identifying orphaned and aged EBS snapshots and applying a lifecycle policy.

## When to Activate
- DescribeSnapshots returns snapshots whose source VolumeId no longer appears in DescribeVolumes.
- Snapshots are not referenced by any AMI returned from DescribeImages.
- Orphaned snapshots have a StartTime older than 90 days.
- No Data Lifecycle Manager policy governs snapshot retention.
- Snapshot storage growth is a rising line item in Cost Explorer for EC2-Other.

## Step 1: Inventory Snapshots
- Call DescribeSnapshots with OwnerIds self and read SnapshotId, VolumeId, VolumeSize, and StartTime.
- Sum total snapshot storage to size the opportunity.
- Compute age from StartTime for each snapshot.

## Step 2: Identify Orphaned Snapshots
- Call DescribeVolumes and build the set of existing volume IDs.
- Flag snapshots whose VolumeId is absent from that set as orphaned.
- Exclude snapshots created within the last 7 days to avoid deleting fresh backups.

## Step 3: Exclude AMI-Referenced Snapshots
- Call DescribeImages with Owners self and collect snapshot IDs from BlockDeviceMappings.
- Remove any AMI-backing snapshot from the deletion candidate list.
- Flag deregistered AMI snapshots that are now safe to delete.

## Step 4: Rank Deletion Candidates
- Rank orphaned, non-AMI snapshots older than 90 days by VolumeSize times age.
- Estimate monthly savings using the snapshot storage rate for the region.
- Separate candidates into safe-to-delete and needs-owner-confirmation.

## Step 5: Establish Ongoing Lifecycle
- Recommend a Data Lifecycle Manager policy retaining daily snapshots for 7 days and weekly for 4 weeks.
- Recommend tagging snapshots with a source and retention tag at creation.
- Propose a recurring 30 day cleanup review.

## Output
Produce a titled "EBS Snapshot Cleanup Report" listing orphaned snapshots older than 90 days with size and estimated monthly savings, AMI-referenced snapshots excluded from deletion, and total reclaimable storage. Include a prioritized remediation list: delete safe orphaned snapshots older than 90 days first (largest savings first), confirm ambiguous snapshots with owners second, then implement a Data Lifecycle Manager retention policy.