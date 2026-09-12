---
name: cost-optimization-reviewer
agent_type: "Evaluation"
description: Evaluates infrastructure against the AWS Well-Architected Cost
  Optimization pillar, checking for right-sizing, pricing model optimization,
  demand management, and expenditure awareness. Use this skill during cost
  reviews, Well-Architected reviews, or when a service has unexpectedly high
  AWS spend.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Cost Optimization Reviewer

Use this skill to evaluate workloads against the Cost Optimization pillar
of the AWS Well-Architected Framework.

## When to Activate

- Well-Architected review session for cost pillar.
- Service spend exceeds budget and needs assessment.
- Quarterly FinOps review.
- New service being evaluated for cost efficiency.

## Step 1: Practice Cloud Financial Management (COST 1-3)

1. **Functional ownership of cost:**
   - Are cost allocation tags applied to all resources?
   - Is there a team or person responsible for service cost?
   - Are cost budgets defined per service/team?
   - Are cost reports reviewed regularly?

2. **Establish partnership between finance and technology:**
   - Is there a FinOps practice or cost review cadence?
   - Are unit economics understood (cost per transaction, cost per user)?

3. **Budgets and forecasts:**
   - AWS Budgets configured with alerts?
   - Cost Anomaly Detection enabled?
   - Is forecasting performed monthly?

## Step 2: Expenditure and Usage Awareness (COST 4-6)

1. **Governance:**
   - Are there SCPs or permission boundaries limiting expensive resource creation?
   - Is there approval required for large resource provisioning?
   - Are idle resources automatically flagged?

2. **Monitor cost and usage:**
   - Cost Explorer used regularly?
   - Are there cost-specific dashboards?
   - Is untagged spend identified and allocated?

3. **Decommission resources:**
   - Is there a process to identify and remove unused resources?
   - Are development/test resources cleaned up after use?
   - Are lifecycle policies configured for data?

## Step 3: Cost-Effective Resources (COST 7-9)

1. **Evaluate cost when selecting services:**
   - Was serverless evaluated for variable workloads?
   - Are managed services used where they reduce operational cost?
   - Is the chosen service the most cost-effective for the access pattern?

2. **Select the correct resource type and size:**
   - Are instances right-sized based on actual utilization?
   - Are current-generation instances used?
   - Is Graviton/ARM used where compatible?
   - Are burstable instances used for variable workloads?

3. **Select the best pricing model:**
   - Are Savings Plans purchased for steady-state compute?
   - Is Spot used for fault-tolerant workloads?
   - Are Reserved Instances covering predictable databases?
   - Is on-demand only used for truly variable overflow?

## Step 4: Manage Demand and Supply (COST 10)

1. **Manage demand:**
   - Is auto-scaling configured to match demand (avoid over-provisioning)?
   - Is throttling/queuing used to smooth demand spikes?
   - Are caches reducing repeated expensive compute?

2. **Supply resources dynamically:**
   - Scale-to-zero configured for non-production?
   - Scheduled scaling for predictable patterns?
   - Right-sized scaling steps (not too large, not too small)?

## Step 5: Optimize Over Time (COST 11)

1. **Evaluate new services and features:**
   - Are new AWS services evaluated when they could reduce cost?
   - Is architecture reviewed when cost grows significantly?
   - Are lifecycle policies keeping data in optimal storage tier?

## Scoring

Rate each area:
- **Optimized** (3): Best practices fully applied, continuously reviewed
- **Partial** (2): Some optimization, room for improvement
- **Gap** (1): Not optimized, significant waste
- **N/A** (0): Not applicable

## Output

Provide:
1. Per-area score with specific waste findings.
2. Overall Cost Optimization score.
3. Estimated monthly savings if gaps are addressed.
4. Top 5 cost reduction actions with effort and impact.