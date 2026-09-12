---
name: az-failure-readiness-assessment
agent_type: "Generic"
description: Assesses the readiness of infrastructure to survive an Availability
  Zone failure by identifying single-AZ dependencies, capacity gaps, and failover
  weaknesses. Use this skill when performing resilience reviews, preparing for
  GameDays, or when an AZ impairment event requires rapid assessment of exposure.
version: "1.0.0"
last_updated: "2026-08-14"
---

# AZ Failure Readiness Assessment

Use this skill to evaluate whether your architecture can survive the loss
of a single Availability Zone without customer-facing impact.

## When to Activate

- Periodic resilience review (quarterly recommended).
- Preparing for a chaos engineering GameDay exercise.
- AWS Health reports an AZ impairment and you need rapid exposure assessment.
- New service launched and needs AZ-resilience validation.
- Post-incident where AZ failure caused unexpected impact.

## Step 1: Inventory Resources by AZ

Map all resources to their Availability Zone:

**Compute:**
1. EC2 instances - group by AZ, identify services running in each.
2. ECS tasks - check task placement and AZ distribution.
3. EKS nodes - check node group AZ spread.
4. Lambda - check VPC subnet placement (Lambda in VPCs is AZ-bound).

**Data:**
1. RDS - check Multi-AZ configuration (primary and standby AZ).
2. ElastiCache - check replica placement across AZs.
3. EBS volumes - inherently single-AZ, check critical data placement.
4. DynamoDB - inherently multi-AZ (no action needed).
5. EFS - inherently multi-AZ (no action needed).

**Networking:**
1. ALB/NLB - check enabled AZs and target distribution.
2. NAT Gateways - one per AZ? Or shared (single point of failure)?
3. VPC endpoints - check AZ coverage.
4. Direct Connect / VPN - check attachment AZs.

## Step 2: Identify Single-AZ Risks

Flag resources that create single-AZ dependencies:

**Critical (service outage if AZ fails):**
- Single EC2 instance running a critical service (not in ASG)
- RDS Single-AZ instances in production
- ElastiCache single-node cluster
- Only one NAT Gateway serving all AZs
- ECS services with all tasks in one AZ
- EBS volume with unique data and no cross-AZ backup

**High (degraded performance if AZ fails):**
- Auto Scaling group with min capacity that can't fit in N-1 AZs
- ALB targets concentrated in one AZ (imbalanced distribution)
- EKS node group in fewer AZs than the number of pod replicas

**Medium (temporary disruption, auto-recovery expected):**
- In-progress EC2 Spot instances concentrated in one AZ
- Batch processing jobs running in one AZ (will be rescheduled)

## Step 3: Validate Capacity for N-1 AZ Operation

For services using multiple AZs, validate they can operate with one AZ gone:

1. **Auto Scaling Groups:**
   - Current capacity vs minimum needed
   - Can remaining AZs absorb the lost capacity?
   - Are instance types available in all AZs?
   - Is max capacity sufficient to scale up in N-1 AZs?

2. **ECS/EKS:**
   - If one AZ's tasks/pods are lost, do remaining AZs have resource headroom?
   - Will pending tasks be schedulable on remaining nodes?
   - Check resource reservations vs available capacity per AZ.

3. **Database:**
   - Multi-AZ failover: what's the expected failover time?
   - After failover, is read capacity still sufficient? (if read replicas were in the lost AZ)

4. **Load Balancers:**
   - Cross-zone load balancing enabled? (distributes to remaining AZs)
   - Health check configuration - will unhealthy AZ targets be deregistered fast enough?

## Step 4: Validate Failover Mechanisms

For each multi-AZ service, verify failover actually works:

1. **RDS Multi-AZ:**
   - Is automatic failover enabled?
   - Has it been tested? (last failover event)
   - Application connection retry logic - will it reconnect to new primary?
   - DNS TTL on the RDS endpoint - how quickly will clients see the new IP?

2. **ElastiCache:**
   - Automatic failover enabled on replication groups?
   - Cluster mode vs non-cluster mode behavior during failover?

3. **EC2 Auto Scaling:**
   - AZ rebalancing enabled?
   - Replacement capacity will launch in healthy AZs?
   - Launch template/configuration valid in all AZs?

4. **ECS Service:**
   - Multi-AZ task placement strategy configured?
   - Will ECS reschedule tasks to healthy AZs?
   - Is there capacity in remaining AZs for rescheduled tasks?

## Step 5: Check Data Durability

Assess data loss risk during AZ failure:

1. EBS volumes in the failed AZ - are they replicated or backed up?
2. In-memory data (ElastiCache, application caches) - can it be reconstructed?
3. Local instance store data - is it ephemeral or does it contain state?
4. Queued messages - SQS is multi-AZ, but are there in-flight messages on lost instances?

## Step 6: Assess Recovery Time

Estimate recovery time for different components:

| Component | Expected Recovery | Dependencies |
|-----------|-------------------|--------------|
| ALB rerouting | 30-60 seconds | Health check interval + threshold |
| RDS failover | 60-120 seconds | DNS propagation + connection drain |
| ASG replacement instances | 3-5 minutes | Launch time + health check |
| ECS task rescheduling | 1-3 minutes | Image pull + health check |
| EKS pod rescheduling | 1-5 minutes | Node capacity + image pull |
| ElastiCache failover | 30-60 seconds | Replica promotion |

## Output

Produce a resilience assessment:
1. **AZ Readiness Score**: Per-service and overall (Ready / Partially Ready / Not Ready).
2. **Single-AZ Risk Table**: Resource, service, AZ, risk level, customer impact if AZ fails.
3. **Capacity Gap Table**: Service, current cross-AZ capacity, required capacity for N-1 operation, gap.
4. **Failover Validation Status**: Component, failover mechanism, last tested, confidence.
5. **Recovery Timeline**: Expected recovery time by component during AZ failure.
6. **Remediation Priority List**: Actions to achieve full AZ resilience, ordered by risk and effort.
7. **Architecture Diagram**: Topology showing resources per AZ with risk indicators.