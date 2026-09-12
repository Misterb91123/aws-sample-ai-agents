---
name: aws-config-compliance-assessor
agent_type: "Generic"
description: Assesses compliance status of AWS resources against AWS Config rules
  and conformance packs, identifies non-compliant resources, and provides remediation
  guidance. Use this skill when performing compliance audits, responding to Config
  rule violations, or when validating that infrastructure changes maintain compliance
  with organizational policies.
version: "1.0.0"
last_updated: "2026-08-14"
---

# AWS Config Compliance Assessor

Use this skill to assess and report on compliance posture across AWS accounts
using AWS Config rules and conformance packs.

## When to Activate

- Scheduled compliance assessment (weekly/monthly/quarterly).
- AWS Config reports new non-compliant resources.
- Pre-audit preparation (SOC2, PCI, HIPAA, ISO 27001).
- After infrastructure changes, validate continued compliance.
- Management requests compliance status summary.

## Step 1: Retrieve Config Compliance Status

For each connected AWS account:

1. List all AWS Config rules and their compliance status:
   - COMPLIANT: All evaluated resources pass the rule.
   - NON_COMPLIANT: One or more resources fail the rule.
   - NOT_APPLICABLE: Rule doesn't apply to any resources in the account.
   - INSUFFICIENT_DATA: Not enough data to evaluate.

2. List all conformance packs and their compliance scores:
   - Pack name (e.g., "Operational Best Practices for CIS")
   - Rules within the pack
   - Overall compliance percentage

3. Aggregate compliance metrics:
   - Total rules evaluated
   - Compliant rules count
   - Non-compliant rules count
   - Overall compliance percentage

## Step 2: Identify Non-Compliant Resources

For each non-compliant rule:

1. List all resources failing the rule.
2. For each resource, capture:
   - Resource type and identifier
   - Account and region
   - Rule name and description
   - Compliance timeline (when did it become non-compliant?)
   - Resource owner (via tags)

3. Group non-compliant resources by:
   - Severity (critical/high/medium/low based on rule importance)
   - Resource type
   - Account/team ownership
   - Time non-compliant (new vs chronic)

## Step 3: Classify Findings by Framework

Map Config rule violations to compliance frameworks:

**CIS AWS Foundations Benchmark:**
- Root account MFA not enabled
- CloudTrail not enabled in all regions
- S3 buckets without access logging
- Security groups allowing 0.0.0.0/0 ingress
- VPC flow logs not enabled

**AWS Security Best Practices:**
- EBS volumes not encrypted
- RDS instances not encrypted at rest
- S3 buckets without default encryption
- IAM users without MFA
- Access keys not rotated within 90 days

**Operational Excellence:**
- EC2 instances not managed by Systems Manager
- Auto Scaling groups without multiple AZs
- ELB access logging not enabled
- CloudWatch log groups without retention policy

**Data Protection:**
- S3 buckets with public access
- SNS topics without encryption
- SQS queues without encryption
- Backup policies not configured

## Step 4: Assess Compliance Trends

Track compliance over time:
1. Compare current compliance percentage to previous assessment.
2. Identify improvements (newly compliant resources).
3. Identify regressions (newly non-compliant resources).
4. Calculate mean-time-to-remediate for non-compliant findings.
5. Identify chronic non-compliance (resources non-compliant for > 30 days).

## Step 5: Prioritize Remediation

Order findings by risk and effort:

| Priority | Criteria |
|----------|----------|
| P1 - Immediate | Security-critical violations (public data exposure, missing encryption, no MFA) |
| P2 - This week | Compliance framework violations that affect audit readiness |
| P3 - This month | Operational best practice gaps with clear remediation path |
| P4 - Backlog | Low-risk informational findings or accepted exceptions |

**Remediation complexity:**
- **Auto-remediable**: AWS Config can auto-remediate (SSM Automation documents available).
- **Simple fix**: One API call or IaC change (enable encryption, add tag, enable logging).
- **Moderate fix**: Requires downtime or data migration (encrypt existing volume).
- **Complex fix**: Architecture change needed (redesign for compliance).

## Step 6: Check Exception Management

Review existing compliance exceptions:
1. Resources tagged with `compliance:exception` or `config:suppress`.
2. Is the exception still valid? (check expiration date if set)
3. Is there a documented justification?
4. Is there a remediation plan with a target date?
5. Flag expired exceptions that are still non-compliant.

## Step 7: Audit Readiness Assessment

For a specific compliance framework, assess readiness:

| Area | Evidence Required | Status |
|------|-------------------|--------|
| Access Control | IAM policies, MFA enforcement, access reviews | [PASS]/[WARN]/[FAIL] |
| Data Protection | Encryption at rest and in transit, key management | [PASS]/[WARN]/[FAIL] |
| Logging & Monitoring | CloudTrail, VPC Flow Logs, access logs | [PASS]/[WARN]/[FAIL] |
| Network Security | Security groups, NACLs, WAF | [PASS]/[WARN]/[FAIL] |
| Incident Response | Detection, alerting, response procedures | [PASS]/[WARN]/[FAIL] |
| Change Management | IaC, approval workflows, audit trail | [PASS]/[WARN]/[FAIL] |
| Backup & Recovery | Backup schedules, retention, tested restore | [PASS]/[WARN]/[FAIL] |

## Output

Produce a compliance assessment report:
1. **Executive Summary**: Overall compliance score, trend vs previous assessment, critical gaps count.
2. **Compliance by Framework Chart**: Bar chart showing compliance percentage per framework/conformance pack.
3. **Non-Compliant Resources Table**: Resource, rule violated, severity, account, duration non-compliant, remediation action.
4. **Compliance Trend Chart**: Line chart showing compliance percentage over time (improving or degrading).
5. **Top Non-Compliant Rules Table**: Rule name, non-compliant resource count, severity, auto-remediable (yes/no).
6. **Account Compliance Scorecard**: Per-account compliance percentage and top gaps.
7. **Remediation Roadmap**: Prioritized action plan with effort estimates and ownership.
8. **Audit Readiness Assessment**: Framework-specific readiness status.