---
name: cross-account-connectivity-debugger
agent_type: "Incident RCA"
description: Debugs network connectivity issues between AWS accounts including VPC
  peering, Transit Gateway, PrivateLink, and cross-account service access. Use this
  skill when resources in one account cannot reach resources in another, when
  cross-account networking is being set up, or when connectivity works in one
  direction but not the other.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Cross-Account Connectivity Debugger

Use this skill to diagnose and resolve connectivity issues between
resources in different AWS accounts.

## When to Activate

- Service in Account A cannot reach a service in Account B.
- New cross-account connectivity being established (peering, TGW, PrivateLink).
- Cross-account access works one direction but not the other.
- Intermittent connectivity failures between accounts.
- Investigating whether cross-account traffic is flowing correctly after setup.

## Step 1: Identify the Connectivity Method

Determine how the accounts are supposed to be connected:

| Method | Use Case | Characteristics |
|--------|----------|-----------------|
| VPC Peering | Direct VPC-to-VPC, 1:1 relationship | Non-transitive, no edge routing, CIDR must not overlap |
| Transit Gateway | Hub-and-spoke, multiple VPCs/accounts | Transitive, centralized routing, attachment-based |
| PrivateLink (VPC Endpoint Service) | Expose a service privately across accounts | Unidirectional (consumer -> provider), no CIDR overlap issue |
| RAM Shared Subnets | Share subnets across accounts | Resources deployed into shared VPC |
| VPN over public internet | When private connectivity isn't possible | Encrypted, but over public internet |
| Cross-account role (API-level) | AWS API access, not network-level | IAM-based, no VPC connectivity needed |

## Step 2: Validate Network Path (Layer by Layer)

Debug systematically from bottom to top:

### Layer 1: Routing
1. **Source VPC route table**: Does it have a route to the destination CIDR?
   - For peering: Route to peer VPC CIDR via pcx-xxx.
   - For TGW: Route to destination CIDR via tgw-xxx.
   - For PrivateLink: No explicit route needed (uses VPC endpoint DNS).
2. **Destination VPC route table**: Does it have a return route to the source CIDR?
   - Asymmetric routing (no return route) = connectivity fails.
3. **Transit Gateway route table**: Does the TGW have routes between the attachments?
   - Check both the source and destination TGW route table associations.

### Layer 2: Network ACLs
1. **Source subnet NACL**: Allows outbound traffic to destination port.
2. **Destination subnet NACL**: Allows inbound traffic from source CIDR.
3. **Ephemeral ports**: Both NACLs must allow ephemeral port range (1024-65535) for return traffic.
4. NACLs are stateless - both inbound and outbound rules must explicitly allow.

### Layer 3: Security Groups
1. **Source security group**: Allows outbound traffic to destination (usually all outbound is allowed).
2. **Destination security group**: Allows inbound from source. 
   - **Cannot reference cross-account security groups in peering** (must use CIDR).
   - With TGW: must use CIDR ranges.
   - With shared VPC (RAM): CAN reference security groups within the shared VPC.

### Layer 4: DNS Resolution
1. Can the source resolve the destination's hostname?
2. Private hosted zone associated with source VPC?
3. VPC peering DNS resolution enabled?
4. PrivateLink endpoint DNS configured correctly?

## Step 3: Debug VPC Peering Issues

Common peering problems:

| Issue | Cause | Fix |
|-------|-------|-----|
| Peering shows "active" but no connectivity | Missing routes in one or both VPCs | Add route to peer CIDR in both VPC route tables |
| Overlapping CIDRs | VPCs use same IP range (e.g., both 10.0.0.0/16) | Cannot peer overlapping CIDRs - redesign addressing |
| Transitive routing attempted | Trying to reach VPC C via VPC B (A->B->C) | Peering is non-transitive - use TGW or direct peering |
| DNS not resolving across peering | DNS resolution option not enabled | Enable "DNS resolution" on the peering connection |
| Works one direction only | Route or SG missing in one side | Check routes and SGs in BOTH VPCs |

## Step 4: Debug Transit Gateway Issues

Common TGW problems:

| Issue | Cause | Fix |
|-------|-------|-----|
| Attachment in "pending" state | Cross-account attachment not accepted | Accept the attachment in the resource owner account |
| No connectivity after attachment | Missing TGW route table entries | Add routes in TGW route table for destination CIDR |
| Wrong route table association | Attachment associated with wrong TGW RT | Re-associate to correct route table |
| Blackhole routes | Route points to deleted or failed attachment | Remove blackhole route, fix attachment |
| Cross-region TGW peering | Peering not established or routes missing | Create TGW peering, add static routes for remote CIDRs |
| MTU issues (packet loss for large packets) | TGW reduces MTU to 8500 bytes | Enable jumbo frames awareness or reduce application MTU |

## Step 5: Debug PrivateLink Issues

Common VPC Endpoint Service (PrivateLink) problems:

| Issue | Cause | Fix |
|-------|-------|-----|
| Endpoint in "rejected" state | Service provider didn't accept the request | Provider must accept in their endpoint service config |
| DNS not resolving to endpoint | Private DNS not enabled or not propagated | Enable private DNS on the endpoint; verify hosted zone |
| Connection timeout | NLB in provider account not healthy | Check NLB targets and health checks |
| Permission denied creating endpoint | Missing permissions in endpoint policy | Update VPC endpoint policy to allow the principal |
| Endpoint shows available but can't connect | Security group on endpoint interface too restrictive | Allow inbound from consumer CIDR on endpoint SG |

## Step 6: Validate with VPC Reachability Analyzer

Use VPC Reachability Analyzer to trace the path:
1. Create an analysis between source and destination.
2. Specify protocol and ports.
3. Analyzer checks all routing, SGs, NACLs, peering, and TGW configuration.
4. Returns either "reachable" or the specific hop where connectivity fails.

This is the fastest way to identify exactly which layer is blocking traffic.

## Step 7: Verify End-to-End

After fixing the identified issue:
1. Test connectivity from source to destination (telnet, curl, nmap).
2. Verify bidirectional if needed (can destination also reach source?).
3. Check VPC Flow Logs for accepted traffic.
4. Monitor for intermittent issues (connection resets, timeouts).
5. Document the connectivity for future reference.

## Output

Produce a connectivity debug report:
1. **Connectivity Summary**: Source, destination, expected path, current status (working/broken/partial).
2. **Layer-by-Layer Analysis**: Routing [PASS]/[FAIL], NACLs [PASS]/[FAIL], Security Groups [PASS]/[FAIL], DNS [PASS]/[FAIL].
3. **Root Cause**: Specific misconfiguration identified with affected resource.
4. **Fix Applied/Recommended**: Configuration change to establish connectivity.
5. **Connectivity Diagram**: Visual showing the network path between accounts.
6. **Verification Results**: Proof that connectivity works after fix.