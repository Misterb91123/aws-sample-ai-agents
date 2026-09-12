---
name: s3-storage-tiering-optimization
agent_type: "Generic"
description: Use this skill to optimize Amazon S3 storage classes and lifecycle policies, including Intelligent-Tiering, Glacier transitions, object expiration, and cleanup of incomplete multipart uploads. It measures storage by class and age, finds buckets lacking lifecycle rules, and recommends tiering to cut storage cost without losing data.
version: "1.0.0"
last_updated: "2026-08-14"
---

# S3 Storage Tiering Optimization

This skill analyzes S3 storage distribution by class and object age to move cold data to cheaper tiers, expire stale objects, and reclaim space from incomplete uploads.

## When to Activate

- S3 storage is a top cost line and growth is outpacing usage.
- CloudWatch BucketSizeBytes shows large STANDARD storage with little access.
- Objects remain in STANDARD older than 90 days with no lifecycle rule applied.
- Incomplete multipart uploads older than 7 days are accumulating.
- A bucket has no GetBucketLifecycleConfiguration policy at all.

## Step 1: Measure Storage by Class

- Enable or read S3 Storage Lens for account-wide storage class distribution and cold-data metrics.
- Query CloudWatch GetMetricStatistics on namespace AWS/S3, metric BucketSizeBytes, with the StorageType dimension for each class (StandardStorage, IntelligentTieringStorage, GlacierStorage).
- Rank buckets by STANDARD storage size and by growth rate.

## Step 2: Assess Lifecycle Coverage

- Call GetBucketLifecycleConfiguration on each bucket to determine whether transition, expiration, and abort-incomplete-multipart rules exist.
- Flag buckets with no lifecycle configuration and buckets missing an AbortIncompleteMultipartUpload rule.
- Note buckets where versioning is on but noncurrent-version expiration is absent.

## Step 3: Analyze Access and Age

- Use S3 Storage Lens activity metrics or S3 Inventory to identify objects in STANDARD not accessed in the last 90 days.
- Flag objects older than 90 days in STANDARD with no transition rule as tiering candidates.
- Identify incomplete multipart uploads older than 7 days for cleanup.

## Step 4: Recommend Tiering

- For buckets with unpredictable access, recommend Intelligent-Tiering to auto-move cold objects.
- For predictable cold data older than 90 days, recommend transition to Glacier Instant Retrieval or Glacier Flexible Retrieval.
- For clearly obsolete data, recommend an expiration rule with an explicit age.

## Step 5: Model Savings

- Compute current monthly cost per bucket by storage class.
- Model savings from each recommended transition and expiration rule.
- Add reclaimed cost from aborting incomplete multipart uploads.

## Output

The skill produces a titled "S3 Storage Tiering Assessment" summarizing per-bucket storage by class, lifecycle coverage gaps, the volume of cold STANDARD data older than 90 days, and the size of incomplete multipart uploads, along with modeled monthly savings for each proposed rule. It ends with a prioritized remediation list ordered by dollar savings, such as adding Intelligent-Tiering, adding Glacier transition and expiration rules, adding an AbortIncompleteMultipartUpload rule at 7 days, and enabling noncurrent-version expiration on versioned buckets.