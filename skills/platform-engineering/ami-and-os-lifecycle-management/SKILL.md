---
name: ami-and-os-lifecycle-management
agent_type: "Generic"
description: Use when managing AMI hygiene and operating system end of life across EC2 fleets. It finds stale AMIs, instances running deprecated OS releases, and unpatched launch templates, then recommends refresh and deprecation actions. Apply during patch cycles or before compliance audits.
version: "1.0.0"
last_updated: "2026-08-14"
---

# AMI and OS Lifecycle Management

Manage AMI freshness and OS lifecycle so instances run supported, patched base images.

## When to Activate
- DescribeImages shows self-owned AMIs with a CreationDate older than 180 days still referenced by launch templates.
- DescribeInstances reveals instances running an OS release past vendor end of life.
- Launch templates or Auto Scaling groups pin an AMI that has been superseded by a newer build.
- AMIs are not marked deprecated with DeprecationTime despite being replaced.
- Instances have no recent patch baseline association in Systems Manager.

## Step 1: Inventory AMIs and Age
- Call DescribeImages with Owners self and read CreationDate and DeprecationTime.
- Compute AMI age and flag any AMI older than 180 days still in active use.
- Identify AMIs with no deprecation date set.

## Step 2: Map Instances to AMIs and OS
- Call DescribeInstances and read ImageId, PlatformDetails, and platform for each instance.
- Correlate each instance to its source AMI and OS release.
- Flag instances whose OS release is past vendor end of life.

## Step 3: Detect Launch Template and ASG Drift
- Call DescribeLaunchTemplateVersions and DescribeAutoScalingGroups to find pinned ImageIds.
- Flag templates or groups referencing AMIs older than 180 days or superseded builds.
- Recommend updating to the latest hardened AMI via SSM Parameter reference.

## Step 4: Verify Patch Baselines
- Check Systems Manager patch compliance and last patch scan time for each instance.
- Flag instances with no patch association or a compliance state of NON_COMPLIANT.
- Recommend a maintenance window to remediate missing patches.

## Step 5: Plan Refresh and Deprecation
- Recommend rebuilding golden AMIs on a 90 day cadence.
- Mark superseded AMIs deprecated with a DeprecationTime and schedule deregistration after grace period.
- Sequence instance refresh via Auto Scaling instance refresh to avoid downtime.

## Output
Produce a titled "AMI and OS Lifecycle Report" listing AMIs older than 180 days still in use, instances on end-of-life OS releases, launch templates and ASGs pinning stale AMIs, and patch compliance gaps. Include a prioritized remediation list: replace end-of-life OS instances first, refresh AMIs older than 180 days in active use, update launch templates and ASGs to current images, then deprecate and deregister superseded AMIs.