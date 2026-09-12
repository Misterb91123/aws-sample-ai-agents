---
name: operational-excellence-reviewer
agent_type: "Evaluation"
description: Evaluates infrastructure against the AWS Well-Architected Operational
  Excellence pillar, checking IaC adoption, monitoring coverage, runbook maturity,
  and deployment automation. Use this skill when performing Well-Architected reviews,
  assessing operational maturity of a service, or when preparing for an AWS
  Well-Architected Tool review session.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Operational Excellence Reviewer

Use this skill to evaluate workloads against the Operational Excellence pillar
of the AWS Well-Architected Framework.

## When to Activate

- Formal Well-Architected review session.
- New service being assessed for operational readiness.
- Post-incident: checking if operational gaps contributed.
- Quarterly maturity assessment.

## Step 1: Organization (OPS 1-4)

Evaluate how teams manage operational priorities:

1. **How do you determine priorities?**
   - Are there defined SLOs for services?
   - Is there an error budget policy?
   - Are there escalation procedures?

2. **How do you structure your organization?**
   - Is there clear ownership of services (tags, service catalog)?
   - Are on-call rotations defined?
   - Is there separation between product teams and platform?

## Step 2: Prepare (OPS 5-7)

Check preparation for operations:

1. **Design for operations:**
   - Is workload deployed via IaC (CloudFormation, Terraform, CDK)?
   - Are there multiple environments (dev, staging, prod)?
   - Is configuration externalized (Parameter Store, AppConfig)?

2. **Mitigate deployment risk:**
   - Is deployment automated via pipeline?
   - Are canary/blue-green deployments configured?
   - Is there automated rollback on failure?
   - Are feature flags available for risky changes?

3. **Operational readiness:**
   - Is there a runbook for common operational tasks?
   - Have failure modes been identified?
   - Has the team conducted pre-mortems?

## Step 3: Operate (OPS 8-10)

Evaluate day-to-day operations:

1. **Understanding workload health:**
   - Are the four golden signals monitored (latency, traffic, errors, saturation)?
   - Are dashboards available and current?
   - Are SLIs/SLOs defined and tracked?
   - Are alerts actionable (low noise)?

2. **Understanding operational health:**
   - Is on-call burden tracked?
   - Is toil measured?
   - Are operational metrics reported (MTTR, deployment frequency)?

3. **Responding to events:**
   - Are incident response procedures defined?
   - Is there an escalation path?
   - Are post-incident reviews conducted?
   - Are action items tracked to completion?

## Step 4: Evolve (OPS 11)

Check continuous improvement:

1. **Learning from experience:**
   - Are post-mortems blameless?
   - Are lessons shared across teams?
   - Are recurring issues being automated away?
   - Is toil trending down over time?

## Scoring

For each question, rate:
- **Best Practice** (3): Fully implemented and regularly reviewed
- **Partial** (2): Partially implemented or not consistently followed
- **Gap** (1): Not implemented
- **Not Applicable** (0): Doesn't apply to this workload

## Output

Provide:
1. Per-question score with evidence and gap description.
2. Overall Operational Excellence score (sum / max possible x 100).
3. Top 3 high-risk gaps to address first.
4. Remediation recommendations with effort estimates.