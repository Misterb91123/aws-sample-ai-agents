---
name: data-lifecycle-manager
agent_type: "Generic"
description: Designs and validates data lifecycle policies for transitioning data
  between storage tiers based on access patterns, age, and value. Use this skill
  when optimizing S3 storage costs through lifecycle rules, managing EBS snapshot
  lifecycles, or designing end-to-end data lifecycle strategies from creation
  through archival to deletion.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Data Lifecycle Manager

Use this skill to design efficient data lifecycle policies that automatically
move data to the most cost-effective storage tier.

## When to Activate

- S3 storage costs growing linearly despite stable data value.
- No lifecycle rules configured on S3 buckets.
- EBS snapshots accumulating without cleanup.
- Designing storage architecture for a new application.
- Compliance requires data deletion after retention period.
- Evaluating S3 Intelligent-Tiering vs manual lifecycle rules.

## Step 1: Analyze Data Access Patterns

For each data store, characterize access patterns:

**S3 Object Access Analysis:**
1. Enable S3 Storage Lens or S3 Analytics for access pattern reports.
2. Determine for each prefix/bucket:
   - Percentage of objects accessed in last 30/60/90/180 days.
   - Access frequency distribution (hot objects vs cold).
   - Object age distribution.
   - Object size distribution.

**Access Pattern Categories:**
| Pattern | Description | Optimal Tier |
|---------|-------------|-------------|
| Hot | Accessed multiple times per day | S3 Standard |
| Warm | Accessed weekly-monthly | S3 Standard-IA or One Zone-IA |
| Cold | Accessed quarterly or less | S3 Glacier Instant Retrieval |
| Archive | Accessed rarely (compliance/legal) | S3 Glacier Flexible / Deep Archive |
| Write-once-read-many | Written once, read infrequently | S3 One Zone-IA (if non-critical) |
| Unpredictable | Can't predict access pattern | S3 Intelligent-Tiering |

## Step 2: Design S3 Lifecycle Rules

Create rules based on access analysis:

**Standard lifecycle progression:**
```
Day 0: Object created in S3 Standard
Day 30: Transition to Standard-IA (if not accessed in 30 days)
Day 90: Transition to Glacier Instant Retrieval
Day 365:  Transition to Glacier Flexible Retrieval
Day 730:  Transition to Glacier Deep Archive
Day 2555: Expire (delete) - 7 year compliance retention met
```

**Key considerations:**
- Minimum storage duration charges: Standard-IA (30 days), Glacier IR (90 days), Glacier (90 days), Deep Archive (180 days).
- Object size minimum: Standard-IA charges minimum 128KB (small objects may be cheaper in Standard).
- Retrieval costs: Glacier has per-GB retrieval fees + request fees.
- Transition costs: $0.01 per 1,000 objects transitioned.

**When to use Intelligent-Tiering instead:**
- Access patterns are unpredictable.
- Don't want to manage lifecycle rules.
- Willing to pay the monitoring fee ($0.0025 per 1,000 objects/month).
- Objects are > 128KB (monitoring fee makes small objects expensive).

## Step 3: Design EBS Snapshot Lifecycle

Use Data Lifecycle Manager (DLM) policies:

**Standard EBS lifecycle:**
```
Snapshot Creation:
- Frequency: Daily for production, weekly for non-production
- Retention: 7 daily, 4 weekly, 12 monthly (Grandfather-Father-Son)
- Time: During low-I/O period
- Tags: Inherit from source volume

Snapshot Archiving:
- Move to archive tier after 90 days (for long-term retention snapshots)
- Archive tier: 75% cheaper but 24-72 hour restore time

Cross-Region Copy:
- Critical volumes: Copy latest daily snapshot to DR region
- Retention in DR region: 7 days (enough for failover + rebuild)
```

## Step 4: Design Log Data Lifecycle

Logs have predictable lifecycle:

```
Stage 1: Active (0-7 days)
- CloudWatch Logs: searchable, queryable
- Use: Active debugging, real-time monitoring

Stage 2: Recent Archive (7-30 days)
- CloudWatch Logs: still queryable but less frequently
- Use: Incident investigation, trend analysis

Stage 3: Long-term Archive (30-365 days)
- Export to S3 (Glacier class)
- Use: Compliance, rare investigation

Stage 4: Deletion (365+ days, unless compliance requires longer)
- Automatic expiration
```

**Implementation:**
- CloudWatch Logs retention: Set to 30-90 days (not "Never Expire").
- S3 export: Subscription filter or scheduled export for long-term.
- S3 lifecycle: Transition exported logs to Glacier -> Deep Archive -> Delete.

## Step 5: Design Application Data Lifecycle

For application-generated data:

**Transactional data:**
- Active: In primary database (30-90 days).
- Archive: Move to archive table or S3 after activity period.
- Delete: After compliance retention period.

**Media/uploads:**
- Active: S3 Standard while user is active.
- Warm: S3-IA after 90 days of no access.
- Archive: Glacier after account deactivation.
- Delete: 30 days after account deletion request (GDPR).

**Analytics/reporting data:**
- Raw: S3 Standard during processing window.
- Processed: S3-IA after aggregation complete.
- Archive: Glacier after reporting period.
- Delete: Based on data value and compliance.

## Step 6: Implement Deletion Policies

Data deletion is part of the lifecycle:

1. **Compliance-driven deletion**: Data must be deleted after retention period (GDPR, internal policy).
2. **Cost-driven deletion**: Data has no value after a period.
3. **Request-driven deletion**: Customer requests data deletion (right to erasure).

**Deletion safeguards:**
- S3 versioning + MFA Delete: prevents accidental deletion.
- S3 Object Lock (Governance mode): requires special permissions to delete.
- S3 Object Lock (Compliance mode): no one can delete until retention expires.
- Confirmation workflow before bulk deletions.

## Step 7: Monitor and Optimize

After implementing lifecycle policies:

1. **S3 Storage Lens**: Monitor storage distribution across tiers over time.
2. **Cost tracking**: Verify cost is decreasing as data transitions to cheaper tiers.
3. **Access pattern validation**: Confirm data in cold tiers isn't being frequently accessed (retrieval costs).
4. **Policy drift**: Ensure new data is being created with appropriate lifecycle tags.

## Output

Produce a data lifecycle management plan:
1. **Current State**: Storage distribution by tier, total cost, growth rate.
2. **Access Pattern Analysis**: Hot/warm/cold/archive percentages by bucket/prefix.
3. **Recommended Lifecycle Rules Table**: Bucket/prefix, transition schedule, deletion schedule, expected savings.
4. **EBS Snapshot Policy**: DLM configuration for creation, retention, archival, cross-region copy.
5. **Log Lifecycle Design**: Retention settings and archival path for each log type.
6. **Cost Projection Chart**: Current vs optimized monthly cost over 12 months.
7. **Implementation Priority**: Ordered list of lifecycle rules to implement by savings impact.