---
name: fsx-windows-sla-diagnostics
agent_type: "Generic"
description: Diagnoses Amazon FSx for Windows File Server SLA and reopen problems -
  DFS namespace resolution failures, Active Directory trust and authentication
  errors, shadow-copy (VSS) storage exhaustion and scheduling conflicts, and
  repeating throughput-capacity warnings. Use this skill when a Windows file
  system misses first-response SLA or a ticket keeps reopening, to isolate the
  Windows-and-Active-Directory root cause that generic FSx and ONTAP diagnostics
  do not cover, and to recommend a targeted, read-only-safe fix.
version: "1.0.0"
last_updated: "2026-09-12"
---

# FSx for Windows File Server SLA Diagnostics

Use this skill to isolate the root cause of Amazon FSx for Windows File Server
SLA breaches and repeat tickets. These problems differ from generic FSx and from
FSx for NetApp ONTAP because they live in the Windows and Active Directory layer:
DFS namespaces, AD trust and authentication, shadow copies (VSS), and repeating
throughput warnings. Reason over the FSx and CloudWatch data the platform
surfaces plus AWS-native reads; do not modify anything.

## Sources

Read-only.

- FSx API via use_aws: DescribeFileSystems (deployment type, throughput capacity,
  storage capacity and type, WindowsConfiguration including Active Directory or
  self-managed AD, DNS, preferred file server IPs, and audit-log settings) and
  DescribeBackups (backup cadence to correlate with contention).
- CloudWatch AWS/FSx metrics: FreeStorageCapacity, throughput and IOPS metrics,
  and any repeating throughput-capacity warning signals, over a window long
  enough to distinguish a recurring warning from a transient spike.
- FSx audit logging (Windows file-access auditing) where enabled, referenced by
  identifier only.

## Method

1. Establish the file system baseline: deployment type, throughput capacity,
   storage capacity versus FreeStorageCapacity, and the AD or DFS configuration
   summary from WindowsConfiguration.
2. DFS namespace resolution: compare the AD DNS settings and preferred file
   server IPs against the namespace target; flag stale or missing DNS records and
   unresolved referral targets as the resolution root cause.
3. Active Directory trust and authentication: check the AD join state, domain and
   organizational-unit configuration, and trust or service-account status; flag a
   broken trust, an expired join, or a DNS-to-domain-controller failure as the
   authentication root cause.
4. Shadow-copy (VSS) exhaustion and scheduling: assess the shadow-copy storage
   allocation against FreeStorageCapacity and the snapshot schedule; flag
   exhaustion that silently drops the oldest copies and schedules that overlap
   backup or peak-throughput windows.
5. Repeating throughput-capacity warnings: correlate throughput and IOPS
   saturation with provisioned throughput capacity across the window; a warning
   that recurs indicates sustained under-provisioning, not a transient spike.
6. Rank findings by customer impact: authentication and namespace failures that
   block access first, then VSS data-loss risk, then repeating throughput
   warnings, and give the specific corrective setting for each.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Documentation MCP Server can supply current FSx for Windows File Server
guidance. Where deeper Windows-internal or directory data is needed (Windows
event logs, DFS referral state, or AD trust detail not surfaced by FSx),
recommend connecting a custom MCP server to Windows event logs or the Active
Directory management interface and calling it in addition to the FSx and
CloudWatch reads, never instead of them. AWS MCP server names and availability
evolve; verify before relying on one.

## Output

Produce a Windows SLA diagnostic report: file-system baseline; DFS namespace
resolution findings; AD trust and authentication findings; shadow-copy (VSS)
storage and schedule findings; repeating throughput-capacity findings; and a
ranked, read-only-safe remediation list naming the exact setting to change for
each (recommend-only), with a GREEN, YELLOW, or RED safety rating and YELLOW or
RED flagged for human approval. Reference identifiers, not sensitive share, DFS
path, or AD domain contents.
