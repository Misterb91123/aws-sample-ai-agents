---
name: network-service-quota-guarding
agent_type: "Generic"
description: Monitors VPC, ELB, Global Accelerator, and VPN service quotas across
  all active regions - EIPs, VPCs, security groups, ENIs, rules-per-SG, NAT
  gateways, managed-prefix-list capacity and effective-rule consumption, ELB
  count, Global Accelerator accelerators, and VPN connections - and flags any at
  80 percent or higher with a recommended increase value. Use this skill to catch
  network capacity exhaustion before it blocks launches, accounting for
  prefix-list effective rules that generic quota checks miss.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Network Service Quota Guarding

Use this skill to detect network service quotas approaching exhaustion before
they cause launch, scaling, or connectivity failures. This skill is
network-scoped and differs from generic service-quota checks because it accounts
for managed-prefix-list effective-rule consumption - a prefix list referenced by
many security groups multiplies against the rules-per-SG quota - which a plain
quota read does not surface. Reason over read-only reads; never request an
increase automatically.

## Sources

Read-only.

- Service Quotas via use_aws: GetServiceQuota and ListServiceQuotas for the
  applied VPC, ELB (elasticloadbalancing), Global Accelerator, and VPN quota
  values, including any account-level applied overrides.
- EC2 via use_aws: DescribeAddresses (EIPs), DescribeVpcs, DescribeSecurityGroups
  and DescribeSecurityGroupRules (rules per SG), DescribeNetworkInterfaces (ENIs),
  DescribeNatGateways, and DescribeManagedPrefixLists with GetManagedPrefixList
  entries for capacity and effective-rule consumption.
- ELB via use_aws: DescribeLoadBalancers for ELB count; Global Accelerator
  ListAccelerators; and VPN DescribeVpnConnections.
- CloudWatch AWS/Usage metrics via query_cloudwatch_metrics for resource-count
  usage trends where the namespace exposes them.

## Method

1. Enumerate active regions and, per region, read the applied quota value for
   each tracked network quota from Service Quotas.
2. Count current usage per quota from the EC2, ELB, Global Accelerator, and VPN
   describe calls, guarding every denominator so a zero quota is a data-quality
   flag, not a division error.
3. Compute prefix-list effective rules: for each managed prefix list, multiply
   its entry count by the number of security-group rules that reference it, and
   compare against the rules-per-SG and prefix-list-entries quotas.
4. Trend usage with AWS/Usage where available to distinguish a steady value from
   one climbing toward the limit.
5. Compute utilization per quota per region and flag any at 80 percent or higher,
   ranking by how close to the limit and how fast it is rising.
6. For each flagged quota, recommend an increase value with headroom (for example
   the next sensible step above projected peak), naming the quota code and region.
7. Note that raising a quota via Service Quotas is an opt-in, human-approved
   directed action; this skill recommends only and never files the request.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Documentation MCP Server can supply current quota codes, per-quota defaults,
and which quotas are adjustable; where deeper cross-account quota rollup is
needed, recommend a custom Service-Quotas MCP server used in addition to the
Service Quotas and EC2 reads, never instead of them. AWS MCP server names and
availability evolve; verify before relying on one.

## Output

Produce a network-quota report: per region and quota, the applied limit, current
usage, utilization percent, and trend; a flagged list at 80 percent or higher
ranked by risk with a recommended increase value and quota code; a dedicated
prefix-list effective-rule section; and a note that any increase is an opt-in,
human-approved action. Reference account IDs and ARNs by identifier only.
