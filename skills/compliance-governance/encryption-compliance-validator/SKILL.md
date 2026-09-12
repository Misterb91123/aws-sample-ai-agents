---
name: encryption-compliance-validator
agent_type: "Generic"
description: Validates encryption-at-rest and encryption-in-transit configurations
  across all AWS services to ensure data protection compliance. Use this skill
  when auditing encryption posture, preparing for compliance certifications,
  or when validating that data classification policies are enforced through
  appropriate encryption controls.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Encryption Compliance Validator

Use this skill to validate that all data stores and communication channels
are encrypted in accordance with organizational data protection policies.

## When to Activate

- Data protection audit (SOC2, PCI-DSS, HIPAA, GDPR).
- New service deployed that handles sensitive data.
- Compliance team requests encryption posture report.
- After discovering an unencrypted resource in production.
- KMS key management review.

## Step 1: Audit Encryption at Rest

For each data storage service, verify encryption:

### S3 Buckets
- [ ] Default encryption enabled (SSE-S3, SSE-KMS, or DSSE-KMS).
- [ ] Bucket policy enforces encrypted uploads (`x-amz-server-side-encryption` condition).
- [ ] For sensitive data: KMS CMK used (not default aws/s3 key) for key rotation control.
- [ ] Versioning-enabled buckets: older versions also encrypted.

### RDS / Aurora
- [ ] Storage encryption enabled (cannot be enabled post-creation without migration).
- [ ] KMS key identified and accessible.
- [ ] Automated backups encrypted.
- [ ] Snapshots encrypted.
- [ ] Read replicas encrypted (they inherit from source).
- [ ] Performance Insights encrypted.

### DynamoDB
- [ ] Encryption at rest enabled (default since 2018, but verify CMK vs AWS-owned).
- [ ] For compliance: Customer-managed CMK used (supports key rotation auditing).
- [ ] DAX cluster encrypted.
- [ ] DynamoDB Streams encrypted.
- [ ] Backups (on-demand and PITR) encrypted.

### EBS Volumes
- [ ] All volumes encrypted.
- [ ] Default encryption enabled at account level.
- [ ] Snapshots encrypted.
- [ ] AMIs created from encrypted volumes.

### EFS
- [ ] Encryption at rest enabled (set at creation, cannot change after).
- [ ] KMS key identified.

### ElastiCache
- [ ] At-rest encryption enabled (set at creation for Redis).
- [ ] In-transit encryption enabled (Redis AUTH or TLS).

### SQS / SNS
- [ ] Server-side encryption enabled (SSE-SQS or SSE-KMS).
- [ ] KMS key specified for sensitive message content.

### CloudWatch Logs
- [ ] Log group encryption with KMS CMK (for sensitive logs).

### Secrets Manager / Parameter Store
- [ ] All secrets encrypted with KMS (default for Secrets Manager).
- [ ] SecureString used for sensitive Parameter Store values.

## Step 2: Audit Encryption in Transit

Verify all network communication is encrypted:

### Load Balancers
- [ ] ALB/NLB listeners use HTTPS/TLS (not HTTP for production).
- [ ] TLS policy is current (ELBSecurityPolicy-TLS13-* or at minimum TLS 1.2).
- [ ] Redirect HTTP -> HTTPS configured.
- [ ] Backend connections encrypted (ALB -> target over HTTPS).

### API Gateway
- [ ] Custom domain uses TLS 1.2 minimum.
- [ ] Mutual TLS configured where required.
- [ ] Backend integration uses HTTPS.

### Internal Service Communication
- [ ] Service mesh or mTLS for service-to-service.
- [ ] Database connections over TLS (RDS `require_ssl` parameter).
- [ ] Redis connections over TLS (in-transit encryption enabled).
- [ ] Elasticsearch/OpenSearch connections over HTTPS.

### VPN / Direct Connect
- [ ] Site-to-site VPN uses strong encryption (IKEv2, AES-256).
- [ ] Direct Connect has MACsec encryption or VPN overlay.

## Step 3: Validate KMS Key Management

Audit KMS key hygiene:

1. **Key inventory**: List all CMKs, their aliases, and usage.
2. **Key rotation**: Is automatic rotation enabled for symmetric CMKs?
3. **Key policy**: Who has access? Is the policy least-privilege?
4. **Key usage audit**: CloudTrail events for Decrypt/Encrypt calls - any unexpected principals?
5. **Key deletion protection**: Are production keys protected from accidental deletion?
6. **Cross-account access**: Are key policies granting access to other accounts? Is that intended?
7. **Orphaned keys**: Keys with no current usage that could be scheduled for deletion.

## Step 4: Validate Data Classification Alignment

Ensure encryption strength matches data classification:

| Data Classification | Encryption Requirement |
|--------------------|----------------------|
| Public | Encryption at rest recommended, in transit required |
| Internal | Encryption at rest and in transit required (AWS-managed key OK) |
| Confidential | CMK encryption required, key access audited, in-transit TLS 1.2+ |
| Restricted (PII, PHI, PCI) | CMK with restricted key policy, envelope encryption, full audit trail |

For each data store:
1. What data classification does it hold?
2. Does the encryption configuration meet the requirement?
3. Is the KMS key policy appropriate for the classification?

## Step 5: Check for Encryption Gaps

Common encryption gaps:

| Gap | Risk | Detection |
|-----|------|-----------|
| Unencrypted EBS volume | Data at rest exposure | AWS Config rule: `encrypted-volumes` |
| HTTP endpoint (no TLS) | Data in transit exposure | ALB listener on port 80 without redirect |
| Old TLS policy | Weak cipher vulnerability | ALB/NLB using deprecated policy |
| Default AWS key | No key rotation audit trail | CMK alias is `aws/service` |
| Unencrypted snapshot shared | Data exposure to other accounts | Snapshot permissions check |
| Backup not encrypted | Offline data exposure | AWS Backup vault encryption check |

## Step 6: Compliance Framework Mapping

Map findings to specific compliance requirements:

**PCI-DSS:**
- Requirement 3: Protect stored cardholder data (encryption at rest with CMK).
- Requirement 4: Encrypt transmission of cardholder data (TLS 1.2+).

**HIPAA:**
- Section 164.312(a)(2)(iv): Encryption of ePHI at rest.
- Section 164.312(e)(2)(ii): Encryption of ePHI in transit.

**SOC2 (CC6.1):**
- Logical and physical access controls, encryption as safeguard.

## Output

Produce an encryption compliance report:
1. **Summary**: Total resources audited, encrypted percentage, gaps found, compliance status per framework.
2. **Encryption Coverage Chart**: Pie/bar chart showing encrypted vs unencrypted by service type.
3. **Unencrypted Resources Table**: Resource, type, account, data classification, risk level, remediation action.
4. **Weak Encryption Table**: Resource, current config (old TLS, AWS-managed key), recommended config.
5. **KMS Key Health Table**: Key alias, rotation status, policy scope, usage count, health status.
6. **Compliance Gap Mapping**: Finding, affected framework requirement, remediation priority.
7. **Recommendations**: Prioritized actions to achieve full encryption coverage.