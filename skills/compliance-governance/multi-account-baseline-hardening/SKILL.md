---
name: multi-account-baseline-hardening
agent_type: "Generic"
description: Use this skill when hardening a new or existing AWS account to an organizational security baseline. It triggers on account onboarding, security review findings, or requests to enable foundational controls such as CloudTrail, AWS Config, GuardDuty, Security Hub, IAM password policy, S3 public access block, and default EBS encryption, and it guides delegated administration across the Organization.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Multi-Account Baseline Hardening

This skill brings an AWS account up to an organizational security baseline by enabling foundational logging, detection, and data-protection controls. It prefers organization-wide, delegated-admin configuration so the baseline is consistent and centrally managed.

## When to Activate

- A new account is being onboarded and must meet the security baseline.
- A security review finds an existing account missing foundational controls.
- CloudTrail, Config, GuardDuty, or Security Hub is not enabled or not centralized.
- Account-level data protections (S3 public access block, default EBS encryption) are missing.
- A team wants to standardize delegated administration for security services.

## Step 1: Enable CloudTrail

- Confirm an organization trail exists (created from the management account or delegated administrator) that logs management events for all accounts and regions, is multi-region, and delivers to a centralized, access-restricted S3 bucket in the log archive account.
- Enable log file validation and encrypt the trail with a KMS key. Add data events for sensitive S3 buckets and Lambda functions where required, noting the added cost.

## Step 2: Enable AWS Config

- Enable AWS Config in every region in use with a configuration recorder that records all supported resource types plus global resources, delivering to the centralized S3 bucket.
- Deploy the baseline Config rules (or a conformance pack) that back the organization's detective controls. Set up an aggregator in the security account so compliance is visible across all accounts and regions.

## Step 3: Enable GuardDuty

- Enable Amazon GuardDuty and designate a delegated administrator (the security account) so member accounts are auto-enrolled and findings aggregate centrally.
- Enable the relevant protection plans (for example S3 protection, EKS protection, malware protection, RDS protection) per the baseline, and route findings to Security Hub and an alerting pipeline.

## Step 4: Enable Security Hub

- Enable AWS Security Hub with a delegated administrator and auto-enable for new accounts, so findings from GuardDuty, Config, Inspector, and others are normalized in one place.
- Turn on the required standards (for example AWS Foundational Security Best Practices and CIS AWS Foundations Benchmark) and set up cross-region aggregation to a single home region.

## Step 5: Set IAM and data-protection defaults

- Configure the IAM account password policy to the baseline: minimum length of at least 14 characters, require uppercase, lowercase, number, and symbol, prevent reuse of the last 24 passwords, and set a maximum age where required by policy.
- Enable the S3 Block Public Access setting at the account level so no bucket can be made public regardless of bucket policy.
- Enable default EBS encryption in every region so new volumes and snapshots are encrypted with a KMS key by default.
- Confirm the account root user has MFA enabled and no active access keys.

## Step 6: Centralize with delegated administration

- Where a service supports it, delegate administration to the dedicated security account rather than operating from the management account, reducing blast radius on the management account.
- Deliver the baseline as code (a StackSet or the organization's landing zone) so it applies consistently and drift can be detected. Confirm each control reports healthy in Security Hub after enablement.

## Output

Produce an Account Baseline Hardening Report containing: the enablement status of CloudTrail, Config, GuardDuty, and Security Hub with their delegated-admin and centralization details, the IAM password policy and root user findings, S3 public access block and default EBS encryption status per region, and any gaps against the baseline with the specific remediation. Note which controls were applied organization-wide versus per-account, and confirm each control reports healthy after enablement.