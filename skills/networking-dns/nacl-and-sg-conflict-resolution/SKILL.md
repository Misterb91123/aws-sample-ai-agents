---
name: nacl-and-sg-conflict-resolution
agent_type: "Incident RCA"
description: Use when resolving Network ACL and security group conflicts that cause dropped traffic. It finds ephemeral port gaps, NACL denies overriding security group allows, and misordered NACL rules, then recommends fixes. Apply when connections time out despite security group allows.
version: "1.0.0"
last_updated: "2026-08-14"
---

# NACL and Security Group Conflict Resolution

Resolve dropped traffic caused by the interaction of stateless NACLs and stateful security groups.

## When to Activate
- DescribeNetworkAcls shows no allow rule for the ephemeral port range 1024 to 65535 on return traffic.
- A NACL deny rule with a lower rule number overrides an intended allow.
- DescribeSecurityGroups allows a port but connections still time out.
- Inbound is allowed but outbound NACL rules block the response (NACLs are stateless).
- A subnet is associated with a restrictive NACL that conflicts with its security groups.

## Step 1: Map the Traffic Flow
- Identify source, destination, protocol, and port for the failing connection.
- Determine which subnets and NACLs are on each side.
- Note that security groups are stateful and NACLs are stateless.

## Step 2: Inspect Security Groups
- Call DescribeSecurityGroups and confirm inbound and outbound rules allow the flow.
- Confirm the rule references the correct source SG or CIDR.
- If security groups allow the flow, shift focus to NACLs.

## Step 3: Inspect NACL Rules
- Call DescribeNetworkAcls for the source and destination subnets.
- Evaluate rules in ascending rule number order and find the first match.
- Flag a low-numbered deny that shadows a higher-numbered allow.

## Step 4: Check Ephemeral Port Coverage
- Confirm NACLs allow the ephemeral return range 1024 to 65535 outbound on the client side and inbound on the server side.
- Flag missing ephemeral allow rules as the likely cause of one-way connectivity.
- Recommend explicit allow rules for the ephemeral range.

## Step 5: Recommend Resolution
- Reorder or renumber NACL rules so the intended allow is not shadowed by a deny.
- Add ephemeral port allow rules for return traffic.
- Prefer security groups for fine-grained control and keep NACLs as broad subnet guardrails.

## Output
Produce a titled "NACL and Security Group Conflict Report" listing missing ephemeral port allows, NACL deny rules shadowing allows, and subnet-to-NACL associations causing drops. Include a prioritized remediation list: add ephemeral return-traffic allows first, reorder shadowing NACL deny rules second, then simplify by moving fine-grained control to security groups.