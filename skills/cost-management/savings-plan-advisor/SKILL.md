---
name: savings-plan-advisor
agent_type: "Generic"
description: Analyzes current compute usage patterns to recommend optimal Savings
  Plans and Reserved Instance purchases. Use this skill when evaluating commitment-based
  discount opportunities, reviewing expiring reservations, or when steady-state
  usage is identified that could benefit from 1-year or 3-year commitments.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Savings Plan Advisor

Use this skill to analyze usage and recommend the optimal mix of Savings Plans
and Reserved Instances to reduce costs while maintaining flexibility.

## When to Activate

- Annual or quarterly savings commitment review.
- Existing Reserved Instances or Savings Plans approaching expiration.
- Steady-state spend identified that could benefit from commitments.
- CFO/Finance asks "are we using our discount programs optimally?"
- After rightsizing exercise (new baseline established).

## Step 1: Analyze Current Commitment Coverage

1. List all active Savings Plans:
   - Type (Compute, EC2 Instance, SageMaker)
   - Hourly commitment amount
   - Term remaining
   - Utilization percentage (are we using what we committed to?)

2. List all active Reserved Instances:
   - Instance type, family, region
   - Term remaining
   - Utilization percentage
   - Platform (Linux/Windows)

3. Calculate current coverage:
   - Total eligible on-demand spend
   - Spend covered by commitments
   - Coverage percentage
   - Effective discount rate achieved

## Step 2: Analyze Usage Patterns

Determine which usage is steady-state (good for commitments) vs variable:

1. Retrieve hourly usage data for the past 30 days by:
   - Instance type/family
   - Region
   - Operating system
   - Service (EC2, Fargate, Lambda)

2. Calculate for each usage dimension:
   - Minimum sustained usage (floor - this is safe to commit to)
   - Average usage
   - P10 usage (nearly always running - conservative commitment target)
   - Peak usage (need on-demand headroom for this)

3. **Commitment-safe usage** = P10 or minimum sustained (whichever is more appropriate based on risk tolerance):
   - Conservative: commit to minimum sustained
   - Moderate: commit to P10
   - Aggressive: commit to P25

## Step 3: Evaluate Savings Plan Options

### Compute Savings Plans (Most Flexible)

- Covers EC2, Fargate, Lambda across ALL regions, instance types, OS.
- Discount: ~20% (1yr no upfront) to ~40% (3yr all upfront).
- Best for: dynamic workloads that change instance types, use Fargate/Lambda mix.

### EC2 Instance Savings Plans (Better Discount, Less Flexible)

- Covers specific instance family in a specific region (any size, OS, tenancy).
- Discount: ~25% (1yr no upfront) to ~45% (3yr all upfront).
- Best for: stable EC2 workloads in a known family (e.g., m6i in us-east-1).

### Reserved Instances (Legacy, Highest Discount)

- Most restrictive: specific instance type, region, platform, tenancy.
- Discount: ~30% (1yr) to ~60% (3yr all upfront).
- Best for: workloads that will NOT change for the commitment period.
- Consider only if usage is extremely predictable.

## Step 4: Model Recommendations

For the identified steady-state usage:

1. **Layer 1 - Compute SP** (covers the base across all services):
   - Hourly commitment = sum of minimum sustained usage across ALL compute x discount rate
   - Provides flexibility to shift between EC2, Fargate, Lambda

2. **Layer 2 - EC2 Instance SP** (for stable EC2 families):
   - For instance families with >90% utilization consistency
   - Layer on top of Compute SP for additional discount

3. **On-Demand remainder** (variable/peak workloads):
   - Everything above the committed amount stays on-demand
   - Use Auto Scaling for this layer

**Payment options analysis:**
| Payment | Cash Flow Impact | Total Savings |
|---------|-----------------|---------------|
| No Upfront | Lowest risk, monthly billing | Lowest savings |
| Partial Upfront | Moderate cash outlay | Moderate savings |
| All Upfront | Highest cash outlay | Highest savings |

## Step 5: Assess Risk Factors

Before recommending commitments:
1. Are there planned architecture changes? (migration to Graviton, serverless, containers)
2. Is the workload expected to shrink? (end-of-life product, customer churn)
3. Are there upcoming region migrations?
4. How confident is the usage forecast?
5. What's the break-even point? (months until commitment pays for itself)

**Break-even calculation:**
- Monthly savings from commitment vs on-demand
- Months to recover upfront payment (if applicable)
- Risk-adjusted ROI considering potential usage changes

## Step 6: Check Expiring Commitments

1. List commitments expiring in the next 90 days.
2. For each, assess:
   - Is the usage still active? (worth renewing)
   - Has the workload changed? (may need different commitment type)
   - Should we switch from RI to Savings Plan for more flexibility?
3. Recommend renewal, modification, or non-renewal for each.

## Output

Produce a savings recommendation report:
1. **Current State Summary**: Active commitments, utilization, current coverage %, effective discount rate.
2. **Expiring Commitments Table**: Commitment, expiry date, utilization, renewal recommendation.
3. **New Commitment Recommendations Table**: Type (Compute SP/EC2 SP), hourly commitment, term, payment option, estimated annual savings.
4. **Savings Projection Chart**: Monthly cost with current commitments vs recommended commitments vs full on-demand.
5. **Coverage Heatmap**: By service/region showing covered vs uncovered usage.
6. **Risk Assessment**: Factors that could reduce commitment value.
7. **Implementation Timeline**: Ordered list of commitment purchases with justification.