---
name: s3-bucket-hygiene-cleanup
agent_type: "Generic"
description: Finds Amazon S3 bucket hygiene debt - noncurrent object versions,
  delete markers, and incomplete multipart uploads that block bucket deletion or
  inflate cost and object count - and generates the exact lifecycle rule or S3
  Batch Operations job to remediate, plus a lint of the bucket policy against the
  20 KB size limit. Use this skill for version, delete-marker, and multipart
  cleanup and policy-size linting, distinct from storage-class tiering. Read-only
  and recommend-only.
version: "1.0.0"
last_updated: "2026-09-12"
---

# S3 Bucket Hygiene Cleanup

Use this skill to surface the hidden debt inside S3 buckets: noncurrent versions,
delete markers, and incomplete multipart uploads accumulate silently, block
bucket deletion, and inflate cost and object count. This is cleanup of versions,
markers, and multipart uploads plus a policy-size lint, not storage-class
tiering. Reason over S3 and CloudWatch reads; never delete or modify anything.

## Sources

Read-only.

- S3 API via use_aws: ListObjectVersions (noncurrent versions and delete
  markers), ListMultipartUploads (incomplete uploads and their age),
  GetBucketLifecycleConfiguration (existing rules), and GetBucketPolicy (policy
  document for size linting).
- CloudWatch S3 storage metrics: BucketSizeBytes by storage type and
  NumberOfObjects to quantify the cost and object-count impact.

## Method

1. Enumerate noncurrent versions and delete markers with ListObjectVersions and
   estimate their share of BucketSizeBytes and NumberOfObjects.
2. Enumerate incomplete multipart uploads with ListMultipartUploads and flag
   those older than a threshold that consume storage without a completed object.
3. Detect buckets where these artifacts block deletion (a versioned bucket
   cannot be deleted while versions or markers remain).
4. Compare against the existing lifecycle configuration to see whether a
   NoncurrentVersionExpiration or AbortIncompleteMultipartUpload rule is missing.
5. Generate the exact remediation: a lifecycle rule to expire noncurrent
   versions and abort incomplete uploads, or an S3 Batch Operations job for a
   one-time cleanup where lifecycle timing is too slow.
6. Lint the bucket policy against the 20 KB (20480 byte) size limit and flag
   policies near or over the limit with the current byte size.
7. Rank by cost and by deletion-blocking impact.

## MCP augmentation

Where current lifecycle, Batch Operations, or bucket-policy-limit semantics would
sharpen a recommendation, recommend connecting the AWS Documentation MCP Server
to the Agent Space and using it in addition to the S3 and CloudWatch reads, never
instead of them. Otherwise no MCP server is required. AWS MCP server names and
availability evolve; verify before relying on one.

## Output

Produce a hygiene report: per bucket the counts and estimated size of noncurrent
versions, delete markers, and incomplete multipart uploads; the generated
lifecycle rule or Batch Operations job; the bucket-policy byte size against the
20 KB limit; and a ranked, read-only-safe remediation list with a safety rating
(recommend-only). Reference buckets by identifier and mask account IDs.
