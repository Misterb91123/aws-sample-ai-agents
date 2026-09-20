---
name: fsx-ontap-diagnostics
agent_type: "Generic"
description: Diagnoses Amazon FSx for NetApp ONTAP performance and configuration
  problems - volume sizing and autosize, capacity-pool tiering policy and cooling,
  SnapMirror replication lag and health, throughput-capacity and SSD IOPS fit, and
  multi-protocol (NFS plus SMB) access and security-style conflicts. Use this
  skill when an ONTAP file system is slow, near full, rejecting or degrading
  access, or when replication is behind, to isolate the ONTAP-specific root cause
  and recommend a targeted, read-only-safe fix.
version: "1.0.0"
last_updated: "2026-09-12"
---

# FSx for NetApp ONTAP Diagnostics

Use this skill to isolate the root cause of Amazon FSx for NetApp ONTAP issues,
which differ from generic FSx because ONTAP adds volumes, storage virtual
machines (SVMs), capacity-pool tiering, SnapMirror, and multi-protocol access on
top of the file system. Reason over the FSx and CloudWatch data the platform
surfaces plus AWS-native reads; do not modify anything.

## Sources

Read-only.

- FSx API via use_aws: DescribeFileSystems (throughput capacity, SSD IOPS,
  deployment type, endpoints), DescribeVolumes (size, used, tiering policy,
  security style, junction path, snapshot policy), DescribeStorageVirtualMachines,
  DescribeSnapshots, and the SnapMirror/replication associations FSx exposes.
- CloudWatch AWS/FSx metrics: StorageCapacityUtilization, StorageCapacity vs
  StorageUsed, DataReadBytes/DataWriteBytes and IOPS, DiskThroughputUtilization,
  FileServerDiskThroughputUtilization, CPUUtilization, and the tiering metrics
  (StorageCapacityUtilizationInCapacityPool, and cold vs hot data where exposed).
- SnapMirror/replication health and lag where FSx surfaces it.

## Method

1. Establish the file system baseline: deployment type (single-AZ vs multi-AZ),
   throughput capacity, provisioned SSD IOPS, and total vs used SSD and
   capacity-pool storage.
2. Volume sizing and autosize: for each volume, compare used vs allocated,
   confirm autosize/autogrow settings, and flag volumes near full or without
   autosize where growth is trending up. Guard against a full SSD tier causing
   write failures.
3. Tiering policy and cooling: read each volume's tiering policy (auto, snapshot-
   only, all, none) and the cooling period, and compare against the hot/cold data
   split. Flag hot data stuck on SSD (tiering too conservative) or active data
   forced to the capacity pool (tiering too aggressive) hurting latency.
4. Throughput and IOPS fit: compare DiskThroughputUtilization and
   FileServerDiskThroughputUtilization and IOPS against provisioned throughput
   capacity and SSD IOPS. Sustained saturation indicates under-provisioned
   throughput capacity, not a volume problem.
5. SnapMirror replication: check each replication relationship for health, lag
   against the schedule, and last-transfer status; separate a broken relationship
   from one that is simply behind due to change rate or network.
6. Multi-protocol access: check the volume security style (unix, ntfs, mixed)
   against how it is accessed (NFS, SMB, or both), the SVM Active Directory join
   for SMB, and name-mapping. Flag a security-style vs protocol mismatch as the
   likely cause of permission-denied or inconsistent-access reports.
7. Rank findings by customer impact (write-blocking capacity and access failures
   first, then latency and replication lag) and give the specific corrective
   setting for each.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. There
is no AWS-managed ONTAP MCP server today, so where deeper ONTAP-internal data is
needed (volume efficiency, aggregate state, per-protocol latency from ONTAP
counters), recommend connecting a custom MCP server to the ONTAP management API
(ONTAP REST) and calling it in addition to the FSx and CloudWatch reads, never
instead of them. The AWS Documentation MCP Server can supply current FSx for
ONTAP guidance. AWS MCP server names and availability evolve; verify before
relying on one.

## Output

Produce an ONTAP diagnostic report: file-system baseline; per-volume sizing and
autosize findings; tiering-policy and cooling findings with the hot/cold split;
throughput/IOPS fit; SnapMirror replication health and lag; multi-protocol
security-style findings; and a ranked, read-only-safe remediation list naming the
exact setting to change for each (recommend-only). Reference identifiers, not
sensitive share or path contents.
