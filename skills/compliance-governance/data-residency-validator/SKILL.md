---
name: data-residency-validator
agent_type: "Generic"
description: Validates that data storage and processing comply with geographic
  residency requirements by checking resource locations, replication configurations,
  and data flow paths. Use this skill when auditing data sovereignty compliance
  (GDPR, data localization laws), validating that sensitive data stays within
  approved regions, or when deploying to new regions.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Data Residency Validator

Use this skill to validate that data is stored and processed only in approved
geographic locations, meeting data sovereignty and residency requirements.

## When to Activate

- GDPR compliance audit - validating EU data stays in EU regions.
- New region deployment - verifying data flows respect boundaries.
- Customer contractual requirement specifying data location.
- Regulatory requirement (data localization laws by country).
- Investigating if data inadvertently crosses geographic boundaries.

## Step 1: Define Residency Requirements

Establish the data residency rules to validate against:

**Common requirements:**
| Data Type | Residency Requirement | Approved Regions |
|-----------|----------------------|-----------------|
| EU personal data (GDPR) | Must stay within EEA/EU | eu-west-1, eu-west-2, eu-central-1, eu-north-1, eu-south-1 |
| Canadian personal data (PIPEDA) | Should stay in Canada | ca-central-1 |
| Australian data (Privacy Act) | Must stay in Australia | ap-southeast-2 |
| Financial data (local regulation) | Country-specific | Varies by jurisdiction |
| Government data (FedRAMP/GovCloud) | Must stay in specific partitions | us-gov-* regions |
| Healthcare data (HIPAA) | US only (typically) | us-east-1, us-west-2, etc. |

## Step 2: Inventory Data Stores by Region

Map all data storage resources to their geographic location:

**Primary data stores:**
1. RDS instances and replicas - region and Multi-AZ configuration.
2. DynamoDB tables - region and Global Tables configuration.
3. S3 buckets - region, cross-region replication targets.
4. EFS file systems - region.
5. ElastiCache clusters - region.
6. OpenSearch domains - region.
7. Redshift clusters - region.

**Backup and replication destinations:**
1. S3 Cross-Region Replication (CRR) - where is data replicated to?
2. RDS cross-region read replicas.
3. Aurora Global Database secondary regions.
4. DynamoDB Global Tables - all replica regions.
5. EBS snapshot copy destinations.
6. AWS Backup cross-region backup vaults.

**Transient data stores:**
1. SQS queues - region.
2. Kinesis streams - region.
3. CloudWatch Logs - region.
4. Lambda /tmp storage - region of execution.

## Step 3: Trace Data Flow Paths

Identify where data travels during processing:

1. **Ingestion path**: Where does data enter AWS? (CloudFront edge -> origin region)
2. **Processing path**: Does data move between regions during processing?
3. **Analytics path**: Is data sent to a central analytics region?
4. **Backup path**: Where are backups stored?
5. **CDN path**: Is data cached at edge locations outside approved regions?
6. **Log path**: Where are access logs stored?

**Data flow violations to detect:**
- S3 CRR to a non-approved region.
- CloudFront distributing content globally (may violate residency if content is PII).
- Cross-region Lambda invocations processing resident data.
- Centralized logging sending logs outside the data region.
- Backup vaults in non-approved regions.
- Global Accelerator routing to endpoints outside approved geography.

## Step 4: Check Service-Specific Behaviors

Some AWS services have global or multi-region characteristics:

**Global services (data may exist outside selected region):**
- IAM - global (but this is metadata, not customer data)
- Route53 - global DNS
- CloudFront - edge caches worldwide (check if sensitive data is cached)
- S3 Transfer Acceleration - routes through edge locations
- WAF (Global) - logs may be stored in us-east-1

**Services with regional data guarantees:**
- Most compute and storage services keep data in the selected region.
- Check service-specific documentation for data residency commitments.

## Step 5: Validate Preventive Controls

Check that guardrails prevent residency violations:

1. **SCPs (Service Control Policies)**:
   - Is there an SCP restricting resource creation to approved regions?
   - Example: `"Condition": {"StringNotEquals": {"aws:RequestedRegion": ["eu-west-1", "eu-central-1"]}}`

2. **S3 Bucket Policies**:
   - Do policies restrict replication to approved regions?
   - Are lifecycle rules keeping data within boundaries?

3. **VPC Configuration**:
   - Is network egress restricted to prevent data flowing to non-approved regions?

4. **AWS Config Rules**:
   - Are rules configured to detect resources in non-approved regions?

5. **Tagging**:
   - Are data classification tags applied (data-residency: EU)?
   - Can tags be used to enforce policies?

## Step 6: Assess CloudFront and CDN Residency

If using CloudFront with resident data:
1. Is geographic restriction (geo-blocking) configured?
2. Are cache behaviors appropriate for sensitive content?
3. Is field-level encryption used for PII in transit?
4. Which edge locations are content cached at?
5. Consider: can CloudFront be restricted to specific PoPs?

## Step 7: Document Compliance Evidence

Generate evidence suitable for auditors:

1. **Data map**: Where each data type is stored (region, service, resource ID).
2. **Flow diagram**: How data moves between services and regions.
3. **Control evidence**: SCPs, bucket policies, Config rules preventing violations.
4. **Exception register**: Any approved exceptions to residency rules (with justification).
5. **Monitoring evidence**: Alerts configured to detect new violations.

## Output

Produce a data residency validation report:
1. **Compliance Summary**: Data types audited, approved regions, violation count, overall status.
2. **Data Location Map Table**: Data type, classification, service, resource, region, compliant (yes/no).
3. **Replication Flow Table**: Source resource, source region, destination resource, destination region, compliant (yes/no).
4. **Violations Table**: Resource, data type, current location, required location, severity, remediation.
5. **Preventive Controls Status**: Control type, configured (yes/no), coverage, gaps.
6. **Data Flow Diagram**: Visual showing data paths with compliance annotations.
7. **Remediation Plan**: Actions to resolve violations and prevent recurrence.
8. **Auditor Evidence Package**: Structured documentation for regulatory submission.