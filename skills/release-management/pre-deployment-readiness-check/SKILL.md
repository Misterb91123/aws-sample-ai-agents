---
name: pre-deployment-readiness-check
agent_type: "Generic"
description: Validates that all preconditions are met before a deployment proceeds,
  including environment health, dependency availability, feature flags, and change
  approval status. Use this skill before initiating a production deployment to
  catch blockers early and prevent failed releases.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Pre-Deployment Readiness Check

Use this skill before initiating a production deployment to validate all
preconditions and reduce the risk of a failed release.

## When to Activate

- A deployment is scheduled and approaching its execution window.
- An engineer asks "is it safe to deploy?"
- A release pipeline is about to enter the production stage.
- Change advisory board (CAB) approval is pending validation.

## Step 1: Validate Environment Health

Before deploying, confirm the target environment is stable:

1. Check CloudWatch alarms - are any currently in ALARM state for the target service or its dependencies?
2. Check active investigations - is there an ongoing incident affecting the target environment?
3. Verify baseline metrics for the target service:
   - Error rate < 1% (or below normal threshold)
   - Latency p99 within acceptable range
   - No recent OOM kills or task restarts
4. Check infrastructure capacity:
   - ECS/EKS cluster has headroom for blue/green or rolling deployment
   - ALB target group can handle additional targets during deployment

**Blocker if**: Any active SEV1/SEV2 incident, alarm in ALARM state on target service, or resource capacity insufficient.

## Step 2: Validate Dependencies

Confirm downstream dependencies are healthy:

1. Database health - RDS/DynamoDB not in maintenance, replication healthy.
2. Cache layer - ElastiCache cluster healthy, no ongoing failovers.
3. Message queues - SQS queues not experiencing DLQ growth.
4. External APIs - third-party dependencies responding within SLA.
5. Shared services - auth, config, secrets services all healthy.

**Blocker if**: Any critical dependency is degraded or in maintenance.

## Step 3: Validate Change Approval

Confirm governance requirements are met:

1. Change ticket exists and is approved (ServiceNow, Jira, or equivalent).
2. Deployment window is valid (not during freeze period or outside approved window).
3. Rollback plan documented in the change ticket.
4. Required approvals obtained (peer review, QA sign-off, security review if needed).

**Blocker if**: Missing approvals, outside change window, or during a deployment freeze.

## Step 4: Validate Artifact Readiness

Confirm the deployment artifact is ready:

1. Container image or artifact exists and is tagged correctly.
2. Image has passed all CI pipeline stages (build, unit test, integration test, security scan).
3. Image vulnerability scan completed with no critical/high findings (or waiver documented).
4. Configuration changes (environment variables, secrets) are staged and validated.
5. Database migrations (if any) are tested and reversible.

**Blocker if**: Artifact not found, CI pipeline failed, critical vulnerabilities unwaived.

## Step 5: Validate Deployment Guardrails

Confirm safety mechanisms are in place:

1. Canary/blue-green deployment strategy configured (not raw rolling update for production).
2. Health check endpoints configured and tested.
3. Rollback mechanism verified - can we roll back within 5 minutes?
4. CloudWatch alarms configured to detect deployment failure.
5. Feature flags in correct state for new functionality.

**Warning if**: Missing canary stage or automated rollback - deployment can proceed but with elevated risk.

## Step 6: Validate Observability

Confirm you can detect problems post-deployment:

1. Dashboards exist for the deploying service.
2. Log groups configured and accessible.
3. Deployment markers/annotations will be created for correlation.
4. Team is available to monitor post-deployment (not deploying and walking away).

## Readiness Verdict

Produce a clear go/no-go decision:

| Status | Criteria |
|--------|----------|
| [PASS] GO | All checks pass, no active blockers |
| [WARN] CONDITIONAL GO | Minor warnings only, proceed with extra monitoring |
| [FAIL] NO-GO | One or more blockers present, must resolve before deploying |

## Output

Provide a deployment readiness summary:
1. Go/No-Go verdict with justification
2. Blocker list (if any) with remediation steps
3. Warning list with risk acceptance notes
4. Recommended deployment time window
5. Post-deployment monitoring checklist