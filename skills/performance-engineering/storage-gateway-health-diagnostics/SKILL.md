---
name: storage-gateway-health-diagnostics
agent_type: "Generic"
description: Runs deep health checks on AWS Storage Gateway (File, Volume, and
  Tape) - gateway VM CPU, memory, and state; cache and upload-buffer utilization
  and eviction; network throughput to AWS against the bandwidth rate limit;
  iSCSI, NFS, and SMB mount stability; and working-storage exhaustion - and
  produces preventive maintenance recommendations before cases reopen. Use this
  skill when a Storage Gateway is degraded, slow to upload, evicting cache, or at
  risk of buffer or working-storage exhaustion.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Storage Gateway Health Diagnostics

Use this skill to assess AWS Storage Gateway health across File, Volume, and Tape
gateway types. Storage Gateway has an unusually high case-reopen rate because the
root cause is often a slow-building resource condition - cache filling, upload
buffer backing up, bandwidth rate limit too low for the change rate - that a
one-time fix does not address. This skill favors preventive findings that catch
the trend before the gateway degrades again. Reason over read-only reads; never
modify a gateway or its configuration.

## Sources

Read-only.

- Storage Gateway API via use_aws: DescribeGateway (type, state, VM CPU and
  memory, software version), DescribeCachediSCSIVolumes and
  DescribeStorediSCSIVolumes, DescribeUploadBuffer, DescribeWorkingStorage,
  DescribeBandwidthRateLimit, and DescribeSMBSettings or the NFS/SMB file-share
  describe calls where present.
- CloudWatch AWS/StorageGateway metrics via query_cloudwatch_metrics:
  CachePercentUsed, CacheHitPercent, CachePercentDirty, UploadBufferPercentUsed,
  UploadBufferUsed, CloudBytesUploaded, CloudBytesDownloaded, WorkingStoragePercentUsed,
  and the read/write throughput and latency metrics per gateway and per volume.

## Method

1. Read gateway inventory and state: type, running state, VM CPU and memory
   headroom, and software version currency.
2. Assess cache health: CachePercentUsed and CachePercentDirty trend, and
   CacheHitPercent; a rising dirty percentage with a full cache signals eviction
   pressure and impending performance loss.
3. Assess upload buffer: UploadBufferPercentUsed trend against CloudBytesUploaded;
   a buffer trending toward full with steady upload means the change rate exceeds
   what the link can drain and writes will eventually stall.
4. Assess network throughput to AWS against the configured bandwidth rate limit;
   flag a rate limit set below the sustained change rate as the buffer root cause.
5. Assess working storage (older gateway configurations) for exhaustion the same
   way as upload buffer, guarding denominators against zero.
6. Assess mount stability: iSCSI targets for Volume gateways and NFS/SMB shares
   for File gateways, plus SMB settings and any AD dependency.
7. Produce preventive recommendations: for each trending resource, the projected
   time to exhaustion and the specific corrective setting (larger cache disk,
   higher bandwidth rate limit, added upload buffer) as a read-only-safe proposal.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Documentation MCP Server can supply current Storage Gateway sizing and metric
guidance; where on-appliance detail beyond the AWS APIs is needed, recommend a
custom on-prem-appliance MCP server used in addition to the Storage Gateway and
CloudWatch reads, never instead of them. AWS MCP server names and availability
evolve; verify before relying on one.

## Output

Produce a gateway health report: per-gateway inventory and state; cache,
upload-buffer, and working-storage utilization with trend and projected time to
exhaustion; network throughput versus bandwidth rate limit; mount and share
stability; and a ranked preventive maintenance list naming the exact corrective
setting for each finding (recommend-only). Reference gateway ARNs, share names,
and account IDs by identifier only.
