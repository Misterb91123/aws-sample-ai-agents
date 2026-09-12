---
name: data-transfer-cost-analyzer
agent_type: "Generic"
description: Analyzes AWS data transfer costs to identify expensive cross-AZ,
  cross-region, and internet egress traffic patterns. Use this skill when data
  transfer charges are unexpectedly high, when optimizing network architecture
  for cost, or when investigating NAT Gateway processing charges.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Data Transfer Cost Analyzer

Use this skill to analyze and optimize data transfer costs, which are often
the most opaque and surprising component of AWS bills.

## When to Activate

- Data transfer costs spike unexpectedly.
- NAT Gateway processing charges are higher than expected.
- Monthly cost review reveals high "EC2-Other" or data transfer line items.
- Planning architecture changes to reduce network costs.
- Cross-region replication costs need optimization.

## Step 1: Break Down Data Transfer Costs

Retrieve cost data and categorize by transfer type:

1. **Internet egress** (most expensive: $0.09/GB first 10TB):
   - Data leaving AWS to the internet
   - CloudFront may be cheaper for high-volume egress

2. **Cross-region transfer** ($0.01-0.02/GB):
   - Replication between regions
   - Cross-region API calls
   - Cross-region S3 access

3. **Cross-AZ transfer** ($0.01/GB each direction = $0.02/GB round-trip):
   - Service-to-service communication across AZs
   - RDS Multi-AZ replication
   - EBS Multi-AZ replication

4. **NAT Gateway processing** ($0.045/GB):
   - All traffic routed through NAT Gateways
   - Same-AZ vs cross-AZ NAT Gateway traffic

5. **VPC Peering / Transit Gateway** ($0.01-0.02/GB):
   - Traffic between VPCs
   - Transit Gateway attachment and data processing

## Step 2: Identify Top Data Transfer Sources

Query Cost Explorer with the following groupings:
1. By usage type (distinguishes transfer types).
2. By linked account (which account transfers most).
3. By service (which service generates the transfer).
4. By AZ (identifies cross-AZ chattiness).

**Key usage types to look for:**
- `DataTransfer-Out-Bytes` - internet egress
- `DataTransfer-Regional-Bytes` - cross-AZ
- `DataTransfer-In-Bytes` - ingress (usually free, but not via some paths)
- `NatGateway-Bytes` - NAT Gateway processing

## Step 3: Analyze NAT Gateway Costs

NAT Gateway charges are a common surprise:
1. List all NAT Gateways and their per-gateway data processing volume.
2. Identify what traffic is flowing through NAT:
   - S3/DynamoDB access (should use VPC endpoints instead - free)
   - ECR image pulls (should use VPC endpoint)
   - CloudWatch/Logs calls (should use VPC endpoint)
   - Legitimate internet-bound traffic (necessary)
3. Calculate savings from adding VPC endpoints:
   - VPC Gateway Endpoint (S3, DynamoDB): Free
   - VPC Interface Endpoint: ~$7/month/AZ + $0.01/GB (usually cheaper than NAT)

## Step 4: Analyze Cross-AZ Traffic

Cross-AZ traffic at $0.02/GB round-trip adds up:
1. Identify service pairs communicating across AZs frequently.
2. Check if services could use AZ-affinity (route to same-AZ instance first).
3. Review ECS/EKS service placement - are tasks scheduled across AZs unnecessarily?
4. Check load balancer cross-zone load balancing setting (enabled sends traffic cross-AZ).
5. Review database read replica placement.

**Optimization strategies:**
- AZ-local service discovery for internal services
- Topology-aware routing in Kubernetes
- Disable cross-zone load balancing for internal ALBs (if traffic is already balanced)

## Step 5: Analyze Internet Egress

For high internet egress:
1. Identify what is being sent out (API responses, file downloads, streaming).
2. Evaluate CloudFront for cacheable content:
   - CloudFront egress: $0.085/GB (vs $0.09/GB direct) + caching reduces origin calls
   - Regional edge caches further reduce origin fetches
3. Evaluate S3 Transfer Acceleration usage.
4. Check for uncompressed responses that could be gzip/brotli compressed.

## Step 6: Analyze Cross-Region Transfer

For cross-region costs:
1. Identify replication patterns (S3 CRR, RDS cross-region read replicas, DynamoDB global tables).
2. Evaluate necessity of each cross-region data flow.
3. Check for applications making cross-region API calls (should they be co-located?).
4. Assess if all replicated data needs cross-region (can filtering reduce volume?).

## Step 7: Calculate Optimization Impact

For each finding:
1. Current monthly cost of the transfer path.
2. Proposed optimization (VPC endpoint, CloudFront, compression, AZ affinity).
3. Cost of the optimization (endpoint pricing, CloudFront pricing).
4. Net monthly savings.
5. Implementation effort.

## Output

Produce a data transfer cost report:
1. **Summary**: Total monthly data transfer cost, breakdown by type (egress, cross-AZ, cross-region, NAT).
2. **Cost Breakdown Chart**: Pie/bar chart of data transfer costs by category.
3. **Top Transfer Paths Table**: Source, destination, transfer type, monthly GB, monthly cost, optimization available.
4. **NAT Gateway Optimization Table**: NAT Gateway, monthly processing GB, cost, traffic type, VPC endpoint savings.
5. **Cross-AZ Optimization Opportunities**: Service pairs, monthly traffic, cost, AZ-affinity recommendation.
6. **Savings Roadmap**: Prioritized list of optimizations with effort vs savings.
7. **Architecture Recommendations**: Structural changes for long-term transfer cost reduction.