---
name: security-reviewer
agent_type: "Evaluation"
description: Evaluates infrastructure against the AWS Well-Architected Security
  pillar, checking identity management, detection, infrastructure protection,
  data protection, and incident response readiness. Use this skill during
  Well-Architected reviews, security assessments, or compliance preparation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Security Reviewer

Use this skill to evaluate workloads against the Security pillar
of the AWS Well-Architected Framework.

## When to Activate

- Well-Architected review session for security pillar.
- Security assessment of a new or existing workload.
- Compliance preparation requiring security controls evidence.
- Post-security-incident to identify prevention gaps.

## Step 1: Security Foundations (SEC 1)

1. **Account management:**
   - Is AWS Organizations used with SCPs?
   - Is the root account secured (MFA, no access keys, no daily use)?
   - Are accounts separated by environment/workload?
   - Is centralized logging configured (CloudTrail to central account)?

## Step 2: Identity and Access Management (SEC 2-4)

1. **Human identity management:**
   - Is IAM Identity Center (SSO) used for human access?
   - Is MFA enforced for all console access?
   - Are long-lived credentials (access keys) minimized?
   - Is just-in-time access implemented for elevated privileges?

2. **Machine identity management:**
   - Are IAM roles used for services (not access keys)?
   - Are roles scoped to minimum required permissions?
   - Is there a process for reviewing and rotating credentials?
   - Are cross-account roles using external IDs?

3. **Permissions management:**
   - Is least privilege enforced? (Access Advisor shows unused services)
   - Are permission boundaries used for delegated administration?
   - Are resource policies appropriate (no wildcard principals)?
   - Is there regular access review?

## Step 3: Detection (SEC 5-6)

1. **Detection controls:**
   - Is GuardDuty enabled in all accounts and regions?
   - Is Security Hub enabled with findings aggregation?
   - Is CloudTrail enabled (multi-region, integrity validation)?
   - Are VPC Flow Logs enabled?
   - Is AWS Config recording all resource types?

2. **Investigate events:**
   - Is there a process for investigating security findings?
   - Are findings auto-triaged by severity?
   - Is there integration with ticketing for tracking?
   - Are detection rules tuned to reduce false positives?

## Step 4: Infrastructure Protection (SEC 7-9)

1. **Network protection:**
   - Are VPCs segmented (public/private/isolated subnets)?
   - Are security groups following least-privilege (no 0.0.0.0/0 to sensitive ports)?
   - Is WAF protecting public endpoints?
   - Are VPC endpoints used for AWS service access?
   - Are NACLs providing defense-in-depth?

2. **Compute protection:**
   - Are instances/containers patched regularly?
   - Are container images scanned for vulnerabilities?
   - Are containers running as non-root?
   - Is host-based intrusion detection in place?

3. **Automation:**
   - Are security responses automated? (GuardDuty -> Lambda remediation)
   - Are security guardrails enforced via SCPs/Config rules?
   - Is infrastructure deployed via IaC (preventing manual insecure config)?

## Step 5: Data Protection (SEC 10-11)

1. **Data at rest:**
   - Is encryption enabled for all storage (EBS, S3, RDS, DynamoDB)?
   - Are KMS keys managed with appropriate policies?
   - Is key rotation enabled?
   - Are S3 buckets protected from public access?

2. **Data in transit:**
   - Is TLS 1.2+ enforced for all connections?
   - Are internal service communications encrypted?
   - Is certificate management automated (ACM)?
   - Are legacy protocols (TLS 1.0/1.1) disabled?

## Step 6: Incident Response (SEC 12)

1. **Preparation:**
   - Is there a documented incident response plan?
   - Are forensic capabilities available (isolated VPC, analysis tools)?
   - Are incident communication procedures defined?
   - Has the team practiced incident response?
   - Are there automated containment actions available?

## Scoring

Rate each area:
- **Secured** (3): Controls fully implemented and tested
- **Partial** (2): Some controls in place, gaps remain
- **Gap** (1): Critical control missing, creates exposure
- **N/A** (0): Not applicable

## Output

Provide:
1. Per-area score with specific security gaps identified.
2. Overall Security score.
3. Critical exposures requiring immediate attention.
4. Top 5 security improvements prioritized by risk reduction.