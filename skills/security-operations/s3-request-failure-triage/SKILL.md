---
name: s3-request-failure-triage
agent_type: "Generic"
description: Triages the highest-volume Amazon S3 failure modes - 403
  access-denied across bucket policy, IAM, Block Public Access, VPC endpoint
  policy, KMS, and Object Ownership or ACL; replication stalls; lifecycle rule
  conflicts; and 503 SlowDown request-rate throttling from prefix fan-out - and
  produces a triage decision tree per failure class with self-service
  resolution guidance. Use this skill to isolate which control denied or
  throttled a request without changing anything. Read-only and recommend-only.
version: "1.0.0"
last_updated: "2026-09-12"
---

# S3 Request Failure Triage

Use this skill to diagnose why S3 requests fail and route each to a self-service
fix. S3 access is decided by several layers that can each deny independently, so
a 403 is only actionable once you know which layer denied it. Reason over S3
configuration and log reads; never modify a bucket or policy.

## Sources

Read-only.

- S3 API via use_aws: GetBucketPolicy, GetBucketReplication,
  GetBucketLifecycleConfiguration, GetBucketOwnershipControls, and
  GetPublicAccessBlock.
- CloudTrail via query_cloudwatch_logs where trail data lands in CloudWatch
  Logs: AccessDenied events with the errorCode, the principal, and the
  requested action.
- CloudWatch S3 request metrics: 4xxErrors and 5xxErrors to size the failure
  volume and detect 503 SlowDown throttling trends.

## Method

1. Classify the failure: 403 access-denied, replication stall, lifecycle
   conflict, or 503 SlowDown throttling, using CloudTrail error codes and
   request metrics.
2. For 403, walk the decision tree in order: identity-based IAM deny, bucket
   policy explicit deny, Block Public Access, VPC endpoint policy, KMS key
   policy or grant for SSE-KMS objects, then Object Ownership and ACL settings.
   Name the single layer that denied.
3. For replication, read the replication configuration and status to separate a
   misconfigured rule or missing role permission from a destination or KMS
   problem, and identify stalled objects.
4. For lifecycle, compare rules for overlapping prefixes and conflicting
   transition or expiration actions that produce unexpected deletes or no-ops.
5. For 503 SlowDown, correlate the throttling trend with prefix fan-out and
   request rate to recommend a key-prefix distribution change.
6. Emit a decision tree per failure class with the observed evidence at each
   branch and the self-service resolution.

## MCP augmentation

Where precise S3 error semantics or current control-precedence guidance would
sharpen the triage, recommend connecting the AWS Documentation MCP Server to the
Agent Space and using it in addition to the S3 and log reads, never instead of
them. Otherwise no MCP server is required. AWS MCP server names and availability
evolve; verify before relying on one.

## Output

Produce a triage report: per failure class a decision tree with the observed
evidence at each branch, the identified failing control, and a read-only-safe
self-service resolution with a safety rating (recommend-only). Reference buckets
and principals by identifier and mask account IDs; never reproduce object
contents.
