---
name: retention-policy-optimizer
agent_type: "Generic"
description: Optimizes backup and data retention policies to balance cost, compliance
  requirements, and recovery needs. Use this skill when backup storage costs are
  growing excessively, when compliance requirements change, or when simplifying
  overlapping retention policies across different backup mechanisms.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Retention Policy Optimizer

Use this skill to optimize data retention policies that balance compliance,
recovery needs, and storage costs.

## When to Activate

- Backup storage costs growing faster than expected.
- Compliance requirement changes (new regulations, audit findings).
- Multiple overlapping retention policies need consolidation.
- Cost optimization initiative targeting storage spend.
- New data classification policy requires retention alignment.

## Step 1: Inventory Current Retention Policies

Map all active retention configurations:

**AWS Backup Plans:**
- Backup frequency (daily, weekly, monthly)
- Retention period per tier (days for recent, months/years for archival)
- Lifecycle rules (move to cold storage after N days)
- Cross-region copy retention

**Service-Native Retention:**
- RDS automated backup retention (1-35 days)
- RDS manual snapshot retention (indefinite until deleted)
- DynamoDB PITR window (35 days, fixed)
- ElastiCache snapshot retention (1-35 days)
- CloudWatch Logs retention (1 day to indefinite)
- S3 lifecycle rules (transition and expiration)
- ECR image lifecycle policies

**Custom/Manual:**
- Scripts creating and managing snapshots
- Data Lake archival policies
- Application-level data purging

## Step 2: Map Compliance Requirements

Align retention with regulatory and business requirements:

| Data Type | Typical Requirement | Minimum Retention |
|-----------|-------------------|-------------------|
| Financial records (SOX) | 7 years | 7 years |
| Healthcare data (HIPAA) | 6 years | 6 years |
| PCI transaction logs | 1 year online, 1 year archive | 1 year accessible |
| GDPR personal data | Minimum necessary | Must be deletable on request |
| Tax records | 3-7 years (varies by jurisdiction) | As required |
| Operational logs | 30-90 days (typical) | As defined by policy |
| Infrastructure backups | 30 days (typical) | Based on RTO/RPO needs |
| Audit trails (SOC2) | 1 year minimum | 1 year |

**For each data store, determine:**
1. What data classification does it hold?
2. What's the minimum legal retention?
3. What's the maximum retention (GDPR right to erasure)?
4. What's the operational retention (how far back might you need to recover)?

## Step 3: Identify Over-Retention (Cost Waste)

Find data being kept longer than necessary:

1. **RDS snapshots**: Manual snapshots accumulating indefinitely (no auto-delete).
   - Old dev/test snapshots from years ago.
   - Pre-migration snapshots that are no longer needed.
   - Calculate cost: snapshot size x $0.05/GB/month.

2. **EBS snapshots**: Old snapshots for decommissioned instances.
   - Orphaned snapshots where the source volume is deleted.
   - Check for snapshots > 90 days with no AMI reference.

3. **CloudWatch Logs**: Log groups set to "Never Expire."
   - Debug logs from years ago costing storage.
   - Calculate cost: ingestion + storage at current retention.

4. **S3 data**: Objects in Standard storage that should be archived or deleted.
   - Objects not accessed in 90+ days in Standard (should be Glacier).
   - Temporary/processed data that was never cleaned up.
   - Old log archives beyond retention requirement.

5. **AWS Backup vault**: Backups retained beyond policy due to manual overrides.

## Step 4: Identify Under-Retention (Risk)

Find data with insufficient retention:

1. **Critical database with only 1-day retention**: If corruption is discovered after 24 hours, recovery is impossible.
2. **Compliance data without required retention**: Regulatory violation risk.
3. **No archival tier**: Short-term backups exist but no long-term archive for important milestones.
4. **Single-region backup**: No cross-region copy for DR scenarios.

## Step 5: Design Optimal Retention Tiers

Recommend a tiered retention model:

```
Tier 1: Operational Recovery (1-7 days)
+-- Frequency: Every 4-6 hours or continuous (PITR)
+-- Purpose: Recover from recent errors, accidental deletion
+-- Storage: Standard (fast restore)
+-- Cost: Highest per GB but smallest volume

Tier 2: Short-Term Backup (7-35 days)
+-- Frequency: Daily
+-- Purpose: Recover from issues discovered within a month
+-- Storage: Standard
+-- Cost: Moderate

Tier 3: Monthly Milestones (3-12 months)
+-- Frequency: Weekly or monthly snapshots
+-- Purpose: Point-in-time recovery for longer incidents, audit
+-- Storage: Cold storage / Glacier Instant Retrieval
+-- Cost: Low

Tier 4: Compliance Archive (1-7 years)
+-- Frequency: Monthly or quarterly
+-- Purpose: Regulatory retention, legal hold
+-- Storage: Glacier Deep Archive
+-- Cost: Very low ($0.00099/GB/month)
```

## Step 6: Calculate Cost Impact

For each optimization recommendation:

| Change | Current Monthly Cost | Proposed Monthly Cost | Savings |
|--------|---------------------|---------------------|---------|
| Delete orphaned EBS snapshots | $X | $0 | $X |
| Set CloudWatch Logs retention to 90 days | $X | $Y | $X-Y |
| Transition S3 to Glacier after 30 days | $X | $Y | $X-Y |
| Reduce RDS retention from 35 to 14 days | $X | $Y | $X-Y |
| Delete old manual RDS snapshots | $X | $0 | $X |

## Step 7: Implementation Plan

Recommend policy changes in order:

1. **Quick wins (immediate savings, no risk):**
   - Delete confirmed orphaned snapshots.
   - Set log retention on non-production log groups.
   - Clean up old test/dev snapshots.

2. **Policy standardization (align to tiers):**
   - Consolidate backup plans to use the tiered model.
   - Configure lifecycle transitions to cold storage.
   - Set up automated cleanup of aged backups.

3. **Compliance alignment (may need legal review):**
   - Extend retention where compliance requires it.
   - Implement vault lock for immutable compliance backups.
   - Configure GDPR-compliant deletion workflows.

## Output

Produce a retention optimization report:
1. **Current State Summary**: Total backup storage, monthly cost, average retention by type.
2. **Over-Retention Findings Table**: Resource, current retention, required retention, excess cost.
3. **Under-Retention Risks Table**: Resource, current retention, required minimum, risk level.
4. **Recommended Retention Tiers**: Standardized policy with tier definitions.
5. **Cost Savings Projection**: Monthly and annual savings from recommended changes.
6. **Compliance Alignment Matrix**: Data type, regulation, required retention, current retention, status.
7. **Implementation Roadmap**: Phased plan for optimizing retention policies.