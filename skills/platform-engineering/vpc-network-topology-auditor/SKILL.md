---
name: vpc-network-topology-auditor
agent_type: "Generic"
description: Audits VPC network topology for misconfigurations, routing issues, and
  connectivity problems. Use this skill when troubleshooting network connectivity
  between services, validating network architecture after changes, or performing
  periodic security reviews of VPC configurations including subnets, route tables,
  NACLs, and peering connections.
version: "1.0.0"
last_updated: "2026-08-14"
---

# VPC Network Topology Auditor

Use this skill to audit and validate VPC network configurations, identify
misconfigurations, and troubleshoot connectivity issues.

## When to Activate

- Service cannot reach another service (connectivity issue).
- New VPC or subnet provisioned and needs validation.
- Network architecture review (security audit, compliance).
- Post-incident where network was a contributing factor.
- Evaluating network design for a new multi-account architecture.

## Step 1: Map VPC Topology

For each VPC in scope, enumerate:

**Subnets:**
1. List all subnets with their CIDR blocks, AZ, and type (public/private).
2. Verify naming convention compliance.
3. Check available IP count in each subnet (flag if < 20% available).
4. Identify subnet purpose: public (internet-facing), private (application), isolated (data).

**Route Tables:**
1. List all route tables and their subnet associations.
2. For each route table, list all routes:
   - Default route (0.0.0.0/0) destination: IGW (public), NAT (private), or none (isolated).
   - VPC peering routes
   - Transit Gateway routes
   - VPC endpoint routes
   - VPN/Direct Connect routes
3. Verify every subnet has a route table association (not using main by default).

**Internet Connectivity:**
1. Internet Gateway attached and routes configured for public subnets.
2. NAT Gateways deployed (one per AZ for resilience?).
3. Egress-only Internet Gateway for IPv6 (if applicable).

## Step 2: Validate Security Controls

**Network ACLs:**
1. For each subnet, check the associated NACL rules.
2. Verify NACLs are not overly permissive (allow all inbound/outbound).
3. Check for deny rules that may block legitimate traffic.
4. Verify ephemeral port ranges are allowed for return traffic (1024-65535).
5. Flag NACLs that differ from the expected baseline.

**Security Group Architecture:**
1. Map security group references (which SGs reference other SGs).
2. Verify tier isolation (web -> app -> data, not web -> data directly).
3. Check for SGs allowing 0.0.0.0/0 on non-public-facing resources.
4. Identify unused security groups (no ENIs attached).

## Step 3: Validate VPC Connectivity

**VPC Peering:**
1. List all peering connections and their status (active, pending, expired).
2. Verify route tables in both VPCs have routes to the peer's CIDR.
3. Check for overlapping CIDRs between peered VPCs (this breaks routing).
4. Verify DNS resolution across peering (if needed).

**Transit Gateway:**
1. List all TGW attachments (VPCs, VPNs, Direct Connect).
2. Verify TGW route tables have correct routes.
3. Check for blackhole routes (routes to non-existent attachments).
4. Validate route propagation settings.

**VPC Endpoints:**
1. List all VPC endpoints (Interface and Gateway).
2. Verify Gateway endpoints exist for S3 and DynamoDB (cost optimization).
3. Check Interface endpoints have appropriate security groups.
4. Verify endpoint policies are not overly restrictive.
5. Check Interface endpoints are deployed in multiple AZs.

## Step 4: Identify Misconfigurations

Common network misconfigurations to detect:

| Issue | Symptom | Check |
|-------|---------|-------|
| Missing NAT Gateway route | Private subnet can't reach internet | Route table for private subnet has no 0.0.0.0/0 route |
| Single NAT Gateway | AZ failure breaks outbound connectivity | Only one NAT GW for all AZs |
| Subnet IP exhaustion | New resources can't launch | Available IPs < 10 |
| Overlapping CIDRs | Routing conflicts | CIDR ranges overlap between VPCs/subnets |
| Missing return route | Asymmetric routing | VPC peering route exists one way but not the other |
| Wrong route table association | Resources in wrong network tier | Subnet associated with wrong route table |
| Blocked ephemeral ports | TCP connections timeout | NACL missing outbound ephemeral port rule |
| DNS resolution disabled | Can't resolve private hostnames | VPC DNS settings disabled |

## Step 5: Assess Connectivity Matrix

Validate that expected connectivity works:

Build a connectivity matrix:
```
From \ To | Internet | VPC-A Private | VPC-B Private | On-Prem |
Public Subnet | [PASS] IGW | [PASS] Local | [PASS] Peering | [PASS] VPN  |
Private Subnet| [PASS] NAT | [PASS] Local | [PASS] Peering | [PASS] VPN  |
Isolated Sub  | [FAIL] None | [PASS] Local | [FAIL] None | [FAIL] None |
```

For each expected path:
1. Verify route exists in route table.
2. Verify NACL allows traffic.
3. Verify security groups allow traffic.
4. Verify no conflicting rules at any layer.

## Step 6: Check IPv4 Exhaustion Planning

Assess subnet IP address capacity:
1. Current available IPs per subnet.
2. Growth rate of IP consumption.
3. Projected exhaustion date.
4. Secondary CIDR options if needed.
5. IPv6 readiness for future migration.

## Output

Produce a network topology audit:
1. **Topology Diagram**: Visual map of VPCs, subnets, connectivity, and traffic flow.
2. **Subnet Inventory Table**: Subnet, VPC, AZ, CIDR, available IPs, type, route table, NACL.
3. **Connectivity Matrix**: Expected vs actual connectivity between network segments.
4. **Misconfiguration Findings Table**: Issue, affected resource, severity, impact, remediation.
5. **IP Capacity Table**: Subnet, total IPs, used, available, utilization %, projected exhaustion.
6. **VPC Endpoint Coverage**: Services accessed, endpoint type, cost savings vs NAT Gateway.
7. **Recommendations**: Network architecture improvements prioritized by risk.