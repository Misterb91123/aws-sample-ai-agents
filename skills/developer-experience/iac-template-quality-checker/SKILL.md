---
name: iac-template-quality-checker
agent_type: "Generic"
description: Use this skill when I need to review AWS CloudFormation and CDK-generated templates for quality issues, anti-patterns, and missing best practices before deployment. Activate it when reviewing infrastructure code, before a production deployment, or when standardizing IaC practices across teams. It inspects template resources for hardcoded values, weak security defaults, and missing operational safeguards.
version: "1.0.0"
last_updated: "2026-08-14"
---

# IaC Template Quality Checker

This skill reviews CloudFormation and CDK-synthesized templates before they reach an environment. It checks for hardcoded configuration, permissive security settings, missing operational safeguards, and race conditions, then returns specific remediation for each finding so the template meets a consistent quality bar.

## When to Activate

- An infrastructure change is up for review before merge.
- A stack is about to be deployed to production for the first time.
- A team is standardizing IaC practices and needs a baseline check.
- A CDK app was synthesized and the resulting template needs inspection.
- A prior deployment failed on a race condition or a security control gap.

## Step 1: Detect Hardcoded Values That Should Be Parameters

Find brittle inline configuration:

- Scan for hardcoded account IDs, region strings, AMI IDs, ARNs, CIDR blocks, and instance sizes embedded in resource properties.
- Recommend moving them to Parameters, Mappings, or SSM Parameter Store references so the template is portable across environments.
- Flag hardcoded endpoint URLs and bucket names that break reuse.

## Step 2: Flag Hardcoded Secrets

Catch credentials in the template:

- Scan for inline passwords, access keys, tokens, and connection strings in properties, Metadata, and user data.
- Report any match as critical and recommend Secrets Manager with a dynamic reference (resolve at deploy time) instead of literal values.
- Never echo the matched secret value in the finding; reference it by property path only.

## Step 3: Check Resource Tagging

Verify governance tags are present:

- Confirm each taggable resource carries required tags, for example Owner, Environment, and CostCenter.
- Report resources missing required tags and recommend a stack-level tag strategy or CDK Tags to apply them uniformly.

## Step 4: Verify Protection on Stateful Resources

Guard against accidental data loss:

- Check that RDS, DynamoDB, and S3 stateful resources set DeletionPolicy and UpdateReplacePolicy to Retain or Snapshot as appropriate.
- Confirm RDS DeletionProtection is enabled for production stacks.
- Flag any stateful resource that would be destroyed on stack update or delete.

## Step 5: Review IAM for Least Privilege

Find overly permissive grants:

- Flag IAM policies using Action wildcard star or Resource star.
- Flag inline policies that grant iam:PassRole without a resource condition and administrative actions granted broadly.
- Recommend scoping actions and resources, and using conditions to constrain grants.

## Step 6: Check Encryption Configuration

Confirm data is protected at rest:

- Verify S3 bucket encryption, EBS volume encryption, RDS StorageEncrypted, and SQS and SNS encryption are set.
- Flag any storage or messaging resource missing encryption and recommend a customer-managed KMS key where policy requires it.
- Confirm S3 buckets also block public access.

## Step 7: Verify Observability and Operational Safeguards

Ensure resources are monitored and safe to change:

- Flag critical resources (databases, load balancers, queues) with no associated CloudWatch alarms.
- Report missing stack policies that would otherwise protect resources from unintended updates.
- Report that drift detection is not configured or scheduled for the stack.

## Step 8: Detect Race Conditions From Missing Dependencies

Prevent flaky deployments:

- Identify resources that depend on another resource being ready but lack an explicit DependsOn or an implicit reference.
- Flag cases where creation order is not guaranteed, for example an ECS service referencing a target group that may not be attached to a listener yet.
- Recommend adding DependsOn or restructuring references so ordering is deterministic.

## Output

The skill produces a template review report containing: hardcoded values that should be parameterized, any hardcoded secrets marked critical with the property path, missing required tags per resource, stateful resources lacking retention or deletion protection, overly permissive IAM statements, resources missing encryption or public-access blocks, critical resources without CloudWatch alarms, missing stack policy and drift-detection gaps, and missing DependsOn relationships that risk race conditions. Each finding lists the resource logical ID, the issue, its severity, and concrete remediation guidance, so the template can be corrected before deployment.