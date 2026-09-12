---
name: privatelink-connectivity-troubleshooting
agent_type: "Incident RCA"
description: Use this skill when a consumer cannot reach a provider service over AWS PrivateLink, including interface endpoint connection failures, name resolution problems, or intermittent connectivity across Availability Zones. It triggers on reports of connection timeouts to a VPC endpoint, endpoint service acceptance issues, unhealthy NLB targets behind an endpoint service, or private DNS not resolving.
version: "1.0.0"
last_updated: "2026-08-14"
---

# PrivateLink Connectivity Troubleshooting

This skill diagnoses connectivity failures between a PrivateLink consumer (interface endpoint) and a provider (endpoint service backed by a Network Load Balancer). It walks the request path from the consumer endpoint through the endpoint service to the NLB targets.

## When to Activate

- Connections to an interface VPC endpoint (com.amazonaws.vpce...) time out or are refused.
- An endpoint connection is stuck in state "pendingAcceptance" or "rejected".
- Private DNS for the service name does not resolve to endpoint ENIs.
- Connectivity works in one Availability Zone but fails in another.
- The endpoint service reports connection limits reached or NLB targets unhealthy.

## Step 1: Verify endpoint and endpoint service state

- Describe the interface endpoint with describe-vpc-endpoints and confirm State is "available" and each endpoint ENI has an IP in the expected subnets.
- On the provider side, describe the endpoint service and confirm the connection appears and its state. If acceptance is required (acceptanceRequired true), a connection sits in "pendingAcceptance" until the provider accepts it. Accept it or configure allowed principals.
- Confirm the consumer principal is in the endpoint service allowlist. A missing allowed principal produces a rejected or never-completing connection.

## Step 2: Check security groups on the interface endpoint

- The interface endpoint ENIs carry their own security group. The consumer security group must allow outbound to the endpoint, and the endpoint security group must allow inbound on the application port (for example TCP 443) from the consumer source.
- A common failure is leaving the default security group that only allows the VPC CIDR, blocking traffic from other subnets or peered VPCs. Verify the inbound rules cover the actual client source range.

## Step 3: Validate NLB target health on the provider

- PrivateLink providers front their service with a Network Load Balancer. Check target group health with describe-target-health; targets must be "healthy".
- Confirm the NLB health check port and protocol match a listener the targets actually serve. NLB health checks come from within the AWS network; the target security group must allow the NLB subnet ranges or the VPC CIDR on the health check port.
- Verify the NLB has enabled the Availability Zones the consumer endpoint uses. If the consumer places an endpoint ENI in an AZ where the NLB has no node, that AZ path fails.

## Step 4: Resolve private DNS

- If the endpoint service enables private DNS, the consumer must set both enableDnsSupport and enableDnsHostnames to true on the consumer VPC, and the endpoint must have PrivateDnsEnabled true.
- Confirm the service provider has completed domain ownership verification for the private DNS name; until verified, private DNS records are not published.
- Test resolution from a consumer instance (nslookup of the service DNS name) and confirm it returns the endpoint ENI private IPs, not a public IP.

## Step 5: Investigate cross-AZ and connection limits

- Cross-AZ data flows incur charges and depend on the endpoint having an ENI in each consumed AZ. For resilience, place endpoint ENIs in every AZ the workload runs in.
- Each NLB has a per-AZ connection and new-flow rate ceiling. Under high concurrency the endpoint service can reach connection limits; check CloudWatch NLB metrics ActiveFlowCount and NewFlowCount for saturation.
- Confirm the endpoint service has not hit its maximum number of concurrent connections from a single consumer.

## Step 6: Confirm the path with Reachability Analyzer

- Run Reachability Analyzer from the consumer ENI to the endpoint ENI to confirm no NACL or route table blocks the path.
- Correlate with VPC Flow Logs on both the consumer subnet and the endpoint subnet, looking for REJECT entries on the application port.

## Output

Produce a PrivateLink Connectivity Report containing: endpoint and endpoint service state with acceptance and allowed-principal findings, security group rule validation for the endpoint ENIs, NLB target health with AZ coverage results, private DNS resolution test results, cross-AZ and connection-limit observations from CloudWatch NLB metrics, and the Reachability Analyzer path result. Include a prioritized remediation list naming the specific security group rule, target group, or DNS setting to change.