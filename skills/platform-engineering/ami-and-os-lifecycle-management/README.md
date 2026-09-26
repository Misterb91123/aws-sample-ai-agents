# AMI and OS Lifecycle Management

A DevOps Agent skill that manages AMI hygiene and operating-system end of life
across EC2 fleets: it finds stale AMIs still in use, instances on end-of-life OS
releases, launch templates and Auto Scaling groups pinning superseded images, and
patch-compliance gaps, then recommends refresh, deprecation, and modernization
actions with the end-of-support cost and risk attributed to the correct source.

> WARNING: This skill is sample code, not intended for production use without
> additional review and testing. Users should validate in a non-production
> environment first.

## What the skill does

Old base images and end-of-life operating systems carry three distinct problems:
security exposure from unpatched software, third-party vendor extended-support and
licensing cost (Windows Server, SQL Server, RHEL and SUSE ELS), and, for
previous-generation instance families, a price-performance premium. AWS does not
charge an operating-system extended-support surcharge for EC2 itself, so this
skill is careful not to imply one.

This skill inventories self-owned AMIs and their age, maps instances to their AMI
and OS release, detects launch-template and Auto Scaling drift, verifies Systems
Manager patch compliance, and plans a refresh-and-deprecation cadence. It reads
the reported OS from SSM where available (more reliable than AMI-name inference)
and uses only published vendor and AWS lifecycle dates. It is read-only and
recommend-only.

## Prerequisites

The DevOps Agent role needs read-only access to the sources this skill reads.
Most are covered by the AWS managed policy AIDevOpsAgentAccessPolicy. The
specific read actions used are:

- ec2:DescribeImages, ec2:DescribeInstances
- ec2:DescribeLaunchTemplates, ec2:DescribeLaunchTemplateVersions
- autoscaling:DescribeAutoScalingGroups
- ssm:DescribeInstanceInformation, ssm:DescribeInstancePatchStates,
  ssm:DescribeInstancePatchStatesForPatchGroup
- ssm:GetParameter (to resolve the latest hardened AMI via SSM Parameter Store)

No write, create, deprecate, deregister, or instance-refresh permission is
required or requested by this skill. Marking an AMI deprecated, deregistering it,
and running an instance refresh are human actions outside this skill.

## How to use it with DevOps Agent

This skill targets the Chat and On-demand subagents. Operators describe the
problem in natural language; they do not name the skill. Example prompts that
should activate it:

- "Find EC2 instances running end-of-life operating systems and stale AMIs."
- "Which launch templates and ASGs still pin old AMIs, and what should we refresh?"
- "Audit our AMI hygiene and patch compliance before the compliance review."

The skill returns AMIs older than 180 days still in use, instances on end-of-life
OS releases, launch-template and ASG drift, patch-compliance gaps, instances on
deregistered AMIs, and a prioritized remediation list with cost and risk
attributed to the correct source.

## Security model

Read-only and recommend-only. The skill reads EC2, Auto Scaling, and Systems
Manager inventory and produces a lifecycle report; it never modifies, deprecates,
deregisters, refreshes, or terminates any AMI or instance. It attributes AWS costs
separately from third-party OS and database vendor costs, states that EC2 has no
OS extended-support surcharge, and labels dollar figures as estimates. All content
read from tools is treated as untrusted data, not instructions.
