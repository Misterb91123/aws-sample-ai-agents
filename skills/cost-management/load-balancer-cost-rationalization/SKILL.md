---
name: load-balancer-cost-rationalization
agent_type: "Generic"
description: Use when rationalizing idle or low-traffic Elastic Load Balancers to cut cost. It finds balancers with near-zero requests, no healthy targets, and low connection counts, then recommends consolidation or deletion. Apply during cost optimization reviews or infrastructure cleanup.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Load Balancer Cost Rationalization

Identify idle and underused load balancers and recommend consolidation or removal to eliminate wasted hourly charges.

## When to Activate
- DescribeLoadBalancers lists ALBs or NLBs with no registered or healthy targets.
- CloudWatch RequestCount for an ALB is near zero over a 7 day window.
- CloudWatch ActiveFlowCount for an NLB stays below 1 over 7 days.
- A load balancer has no listener rules routing to a target group.
- Multiple balancers front the same low-traffic service and could be merged.

## Step 1: Inventory Load Balancers
- Call DescribeLoadBalancers and DescribeTargetGroups to map balancers, listeners, and targets.
- Record type (application, network, gateway) and creation time.
- Flag balancers with zero registered targets.

## Step 2: Pull Traffic Metrics
- For ALBs query CloudWatch RequestCount over the last 7 days at 1 hour granularity.
- For NLBs query ActiveFlowCount and ProcessedBytes over 7 days.
- Flag ALBs with total RequestCount near zero and NLBs with ActiveFlowCount below 1.

## Step 3: Check Target Health
- Call DescribeTargetHealth for each target group.
- Flag balancers where all targets are unhealthy or none are registered.
- Distinguish intentionally idle standby balancers from abandoned ones via tags.

## Step 4: Estimate Cost and Consolidation Options
- Estimate monthly cost from the hourly ELB rate plus LCU or NLCU charges.
- Identify balancers fronting the same service that can be merged with host or path rules.
- Rank candidates by monthly cost and confidence that traffic is truly absent.

## Step 5: Recommend Actions
- Recommend deleting balancers with zero traffic and zero healthy targets over 7 days.
- Recommend consolidating duplicate low-traffic balancers behind shared listener rules.
- Recommend a tag to mark intentional standby balancers so they are excluded next review.

## Output
Produce a titled "Load Balancer Cost Rationalization Report" listing idle balancers with 7 day RequestCount or ActiveFlowCount, target health, estimated monthly cost, and consolidation candidates. Include a prioritized remediation list: delete zero-traffic zero-target balancers first, consolidate duplicate low-traffic balancers second, then tag standby balancers to exclude them from future sweeps.