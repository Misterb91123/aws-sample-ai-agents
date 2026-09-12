---
name: idle-resource-hunter
agent_type: "Generic"
description: Identifies idle and unused AWS resources that are accruing costs without
  providing value. Use this skill to find abandoned resources such as unattached EBS
  volumes, stopped instances with attached storage, unused Elastic IPs, idle load
  balancers, and orphaned snapshots that can be safely removed to reduce waste.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Idle Resource Hunter

Use this skill to find AWS resources that are idle, unused, or orphaned
and costing money without providing value.

## When to Activate

- Monthly cost optimization sweep.
- Budget exceeded and quick savings needed.
- Team is decommissioning a project and needs cleanup.
- New account onboarding - check for inherited waste.
- Triggered by cost anomaly investigation (unexpected charges from idle resources).

## Step 1: Scan for Unattached EBS Volumes

1. List all EBS volumes with state `available` (not attached to any instance).
2. For each, record:
   - Volume ID, size, type (gp2, gp3, io1, io2)
   - Creation date
   - Last attachment date (from CloudTrail)
   - Monthly cost estimate
   - Tags (to identify owner/purpose)

**Flag as waste if**: Volume has been unattached for > 7 days.
**Estimated savings**: Size x price per GB/month for the volume type.

## Step 2: Scan for Stopped EC2 Instances with Storage

1. List EC2 instances in `stopped` state.
2. For each, check:
   - How long has it been stopped? (state transition timestamp)
   - Attached EBS volumes and their sizes
   - Associated Elastic IP (still charged when instance is stopped)
   - Whether it's part of an ASG (shouldn't be stopped)

**Flag as waste if**: Stopped for > 14 days.
**Cost**: EBS storage + Elastic IP ($0.005/hr ~ $3.60/month per EIP).

## Step 3: Scan for Unused Elastic IPs

1. List all Elastic IPs (EIPs) in the account.
2. Identify EIPs not associated with a running instance or active network interface.

**Flag as waste if**: EIP is unassociated.
**Cost**: ~$3.60/month per unused EIP (plus charges per additional EIP on running instances since Feb 2024).

## Step 4: Scan for Idle Load Balancers

1. List all ALBs, NLBs, and CLBs.
2. For each, check:
   - Request count over the past 7 days (CloudWatch `RequestCount`)
   - Active connection count
   - Registered targets count (0 targets = definitely idle)
   - Healthy targets count

**Flag as waste if**: Zero requests for 7+ days OR zero registered targets.
**Cost**: ALB base cost ~$22/month + LCU charges; NLB ~$22/month + NLCU charges.

## Step 5: Scan for Orphaned Snapshots

1. List all EBS snapshots owned by the account.
2. For each, check:
   - Does the source volume still exist?
   - Is it referenced by any AMI?
   - Age (creation date)
   - Size

**Flag as waste if**: Source volume deleted AND not referenced by any AMI AND older than 30 days.
**Cost**: $0.05/GB/month for standard snapshots.

## Step 6: Scan for Idle NAT Gateways

1. List all NAT Gateways.
2. Check `BytesOutToDestination` and `ActiveConnectionCount` over 7 days.
3. Identify NAT Gateways in subnets with no running instances.

**Flag as waste if**: Zero traffic for 7+ days.
**Cost**: ~$32/month per NAT Gateway + data processing charges.

## Step 7: Scan for Unused RDS Resources

1. Check for RDS instances with zero database connections for 7+ days.
2. Check for RDS snapshots older than retention policy (manual snapshots not auto-cleaned).
3. Check for RDS instances in stopped state for > 7 days (auto-restarts after 7 days anyway).

**Flag as waste if**: Zero connections for 7+ days (not a replica, not a standby).

## Step 8: Scan for Additional Idle Resources

1. **Unused ECR repositories**: Repositories with no images or images not pulled in 90+ days.
2. **Idle Redshift clusters**: Zero queries for 7+ days.
3. **Unused S3 buckets**: Empty buckets or buckets with no access for 90+ days.
4. **Orphaned Lambda functions**: Functions not invoked in 90+ days.
5. **Unused CloudWatch Log Groups**: Log groups with no log events in 90+ days.
6. **Detached Network Interfaces**: ENIs not attached to any resource.

## Step 9: Calculate Total Waste

For each finding:
1. Calculate monthly cost of the idle resource.
2. Determine deletion risk (can data be recovered? is it backed up?).
3. Identify owner via tags or last modifier in CloudTrail.

## Safety Checks Before Recommending Deletion

Before recommending removal:
- [WARN] EBS volumes: Check if the data is backed up via snapshot.
- [WARN] Snapshots: Verify they are not the only backup of important data.
- [WARN] Stopped instances: Confirm with owner they are not paused for a reason.
- [WARN] Load balancers: Check if they are part of a disaster recovery configuration.
- [WARN] NAT Gateways: Confirm no scheduled batch jobs rely on them.

## Output

Produce a waste report:
1. **Summary**: Total monthly waste found, resource count by category, top 5 most expensive idle resources.
2. **Idle Resources Table**: Resource type, ID, account, region, idle duration, monthly cost, owner (tag), recommended action.
3. **Waste by Category Chart**: Bar chart showing cost by resource type.
4. **Safe-to-Delete List**: Resources confirmed safe for removal (no backup risk).
5. **Requires-Review List**: Resources needing owner confirmation before removal.
6. **Quick-Action Summary**: Total savings if all safe-to-delete resources are removed.