---
name: ami-and-os-lifecycle-management
agent_type: "Generic"
description: Use when managing AMI hygiene and operating system end of life across EC2 fleets. It finds stale AMIs, instances running deprecated OS releases, and unpatched launch templates, then recommends refresh and deprecation actions. Apply during patch cycles or before compliance audits.
version: "1.1.0"
last_updated: "2026-09-12"
metadata:
  version: "1.1"
  author: solair
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

## Step 6: Attribute End-of-Support Cost and Risk Correctly
- Be honest about who charges for what. AWS does not levy an operating-system "extended support" surcharge for EC2 itself, so do not imply one.
- Separate the three distinct exposures for an end-of-life OS: (a) third-party OS or database vendor extended-support and licensing cost (for example Windows Server or SQL Server end-of-support terms, RHEL and SUSE Extended Lifecycle Support), (b) security exposure from running unpatched end-of-life software, and (c) for previous-generation instance families, the price-performance premium of not moving to a current-generation or Graviton family.
- Prefer SSM DescribeInstanceInformation for the reported PlatformName and PlatformVersion; it is more reliable than inferring the OS from the AMI name. Where SSM has no record, fall back to AMI metadata and mark the OS version inferred.
- Use only published vendor and AWS lifecycle dates. If a date cannot be determined, mark it "EOS date unknown - monitor vendor lifecycle" and exclude it from deadline math. Label any dollar or effort figure an estimate.

## OS lifecycle reference

- Common end-of-support milestones to check: Windows Server 2012 and 2012 R2, older SQL Server versions, Amazon Linux 1, and CentOS and Ubuntu releases past their vendor EOL.
- An instance referencing a deregistered AMI cannot be recovered from termination; flag it distinctly from a merely stale AMI.
- SSM patch compliance state NON_COMPLIANT or a missing patch association indicates the instance is not receiving patches regardless of OS support status.

## Output
Produce a titled "AMI and OS Lifecycle Report" listing AMIs older than 180 days still in use, instances on end-of-life OS releases, launch templates and ASGs pinning stale AMIs, patch compliance gaps, and instances referencing deregistered AMIs. For each end-of-life OS finding, attribute the exposure to the correct source: third-party OS or database vendor extended-support and licensing cost, security exposure from unpatched software, or (for previous-generation families) the price-performance premium, and label dollar figures as estimates. Include a prioritized remediation list: replace end-of-life OS instances first, refresh AMIs older than 180 days in active use, update launch templates and ASGs to current images, then deprecate and deregister superseded AMIs.