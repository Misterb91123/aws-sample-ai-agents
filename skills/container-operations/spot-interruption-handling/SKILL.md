---
name: spot-interruption-handling
agent_type: "Generic"
description: Provides procedures for handling Spot Instance interruptions gracefully,
  designing fault-tolerant Spot architectures, and configuring proper interruption
  responses. Use this skill when Spot Instances are interrupted unexpectedly, when
  designing workloads to use Spot, or when evaluating Spot diversification strategies.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Spot Interruption Handling

Use this skill to design and troubleshoot Spot Instance strategies that
minimize interruption impact.

## When to Activate

- Spot Instances being interrupted frequently.
- Designing a new workload to use Spot capacity.
- Evaluating why a Spot fleet isn't meeting capacity targets.
- Configuring interruption handling for ECS/EKS on Spot.

## Step 1: Understand Interruption Signals

AWS provides two signals before interruption:

1. **Rebalance Recommendation** (proactive, minutes to hours before):
   - Signals that an instance is at elevated risk of interruption.
   - Gives time to proactively launch replacements.
   - Check via instance metadata or EventBridge.

2. **Two-Minute Warning** (reactive):
   - Instance WILL be terminated in 2 minutes.
   - Use for graceful shutdown (drain connections, checkpoint state, deregister from LB).
   - Check via instance metadata: `http://169.254.169.254/latest/meta-data/spot/termination-time`

## Step 2: Design for Interruption Tolerance

**Fleet diversification (most important):**
- Use 6+ instance types across 3+ AZs.
- Use `capacity-optimized` allocation strategy (selects from deepest capacity pools).
- Mix instance families (m5, m5a, m5n, m6i, m6a, c5, c5a, r5, r5a - same vCPU/memory ratio).
- Avoid relying on a single instance type (it WILL get interrupted eventually).

**Architecture patterns:**
- Stateless services: easiest Spot candidate - just replace interrupted instances.
- Batch processing: checkpoint work progress, resume on new instance.
- Queue consumers: use SQS visibility timeout > 2 minutes, messages retry on new consumer.
- Containers (ECS/EKS): use capacity providers with Spot + On-Demand mix.

## Step 3: Configure Interruption Response

**For EC2 Auto Scaling Groups:**
- Enable Capacity Rebalancing (proactively replaces at-risk instances).
- Set a mixed instances policy with On-Demand base capacity.
- Configure lifecycle hooks for graceful drain on termination.

**For ECS:**
- Use Capacity Providers with Spot + On-Demand mix.
- Set minimum On-Demand base to handle traffic during replacement.
- Configure task deregistration delay for ALB drain time.

**For EKS:**
- Use AWS Node Termination Handler (captures interruption notices).
- Configure PodDisruptionBudgets to control drain behavior.
- Taint Spot nodes so only fault-tolerant workloads schedule there.

**For application code:**
- Monitor the 2-minute warning endpoint.
- On SIGTERM: stop accepting new work, complete in-flight, exit 0.
- Save state/checkpoint to durable storage (S3, DynamoDB).
- Deregister from service discovery before shutdown.

## Step 4: Troubleshoot High Interruption Rates

| Problem | Cause | Fix |
|---------|-------|-----|
| Interruptions > 3/week | Under-diversified fleet | Add more instance types and AZs |
| Same instance type always interrupted | Popular instance, high demand | Switch allocation to capacity-optimized |
| Interruptions during business hours | Capacity competition during peak | Add On-Demand base for peak hours |
| New launches also getting interrupted | Entire AZ/type low capacity | Add different AZ or family to pool |

## Output

Provide:
1. Current Spot fleet configuration assessment (diversification score).
2. Interruption pattern analysis (which types/AZs are most interrupted).
3. Recommended fleet configuration changes.
4. Interruption handling checklist (application graceful shutdown, monitoring, replacement).