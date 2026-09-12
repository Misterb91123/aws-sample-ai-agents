---
name: runbook-to-automation-converter
agent_type: "Generic"
description: Converts manual runbook procedures into automated workflows by analyzing
  runbook steps, identifying automation building blocks, and designing implementation
  using AWS services (Lambda, Step Functions, Systems Manager, EventBridge). Use
  this skill when a frequently-executed runbook should be automated, when building
  self-service automation for developer teams, or when converting incident response
  procedures into automated remediation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Runbook to Automation Converter

Use this skill to transform manual operational runbooks into automated
workflows using AWS services.

## When to Activate

- A runbook is executed more than once per week (high-value automation target).
- On-call engineer requests "can we automate this?"
- Post-incident action item: "automate the remediation for this failure mode."
- Building a self-service catalog for developer teams.
- Reducing after-hours pages by automating routine remediations.

## Step 1: Analyze the Runbook

Break down the manual procedure:

For each step in the runbook, classify:

| Step Type | Description | Automation Approach |
|-----------|------------|-------------------|
| **Data gathering** | Query metrics, check status, read logs | API calls (CloudWatch, describe-*) |
| **Decision** | If/then logic based on gathered data | Conditional branching (Step Functions Choice) |
| **Action** | Modify a resource, restart, scale | API call (modify, update, reboot) |
| **Verification** | Confirm action succeeded | Poll for status, check metrics |
| **Notification** | Tell someone what happened | SNS, Slack webhook, ticket creation |
| **Judgment call** | Human decision that varies | Human approval step or escalation |
| **Wait** | Pause for propagation or effect | Step Functions Wait, polling loop |

**Key questions for each step:**
1. Can this be done via an API? (Yes -> automate directly)
2. Is the decision deterministic? (Yes -> code it. No -> add human approval gate)
3. What could go wrong? (Error handling needed)
4. Is the step idempotent? (Can be safely retried?)

## Step 2: Identify Automation Boundaries

Determine how far to automate:

**Full automation (no human in loop):**
- All steps are API-callable.
- All decisions are rule-based.
- Blast radius is limited (affects one service/instance).
- Action is reversible or low-risk.
- Has been performed manually many times with consistent outcome.

**Semi-automation (human approval gate):**
- Most steps automated but one decision requires human judgment.
- Action has broad impact (multiple services, customer-facing).
- Action is irreversible (data deletion, failover).
- First time automating this (build trust gradually).

**Assisted automation (automation prepares, human executes):**
- Automation gathers all information and presents options.
- Human makes the final call and triggers the action.
- Good for complex scenarios or when learning the automation's behavior.

## Step 3: Select AWS Services for Implementation

Map runbook patterns to AWS services:

| Pattern | AWS Service | Use Case |
|---------|-------------|----------|
| Sequential steps with error handling | Step Functions (Standard) | Multi-step workflows with retries |
| Simple event -> action | Lambda + EventBridge | React to a CloudWatch alarm or event |
| Run command on EC2 | Systems Manager Run Command | Execute scripts on instances |
| Multi-step with human approval | Step Functions + callback task | Approval gate before risky action |
| Scheduled procedure | EventBridge Scheduler + Lambda | Daily/weekly automated checks |
| Long-running with waits | Step Functions (with Wait states) | Procedures with polling or delays |
| Cross-account actions | Lambda + cross-account role | Actions in multiple AWS accounts |
| Self-service portal | Service Catalog / Step Functions + API Gateway | Developer-triggered automations |

## Step 4: Design the Automation Workflow

Convert the runbook into a workflow specification:

```
Workflow: [Runbook Name] Automation
Trigger: [CloudWatch Alarm / Schedule / Manual / Event]

Steps:
1. [Gather Context]
   - Action: Query CloudWatch for {metric}
   - Input: {alarm details from trigger}
   - Output: {current_metric_value}
   - Error: Log error, notify, abort

2. [Evaluate Condition]
   - Decision: Is {current_metric_value} > {threshold}?
   - Yes -> Continue to Step 3
   - No -> Log "no action needed", end

3. [Execute Remediation]
   - Action: Call {AWS API} with {parameters}
   - Retry: 3 times with exponential backoff
   - Timeout: 60 seconds
   - Error: Notify on-call, log failure

4. [Verify Success]
   - Action: Wait 60 seconds, then check {metric} again
   - Success: {metric} returned to normal -> Step 5
   - Failure: {metric} still bad -> Escalate to human

5. [Notify]
   - Action: Send notification (Slack/SNS)
   - Content: What was detected, what was done, current status
```

## Step 5: Add Safety Guardrails

Every automation needs safety controls:

1. **Rate limiting**: Don't execute more than N times per hour (prevent automation loops).
2. **Circuit breaker**: If automation has failed 3 times in a row, stop and alert a human.
3. **Dry run mode**: First deploy in "report only" mode to build confidence.
4. **Scope limitation**: Restrict to specific resources (tag-based targeting).
5. **Undo capability**: Log what was done so it can be reversed.
6. **Notification on every execution**: Always inform the team what automation did.
7. **Time boundaries**: Don't run during deployment freezes or maintenance windows.
8. **Concurrency limit**: Only one execution at a time (prevent conflicting actions).

## Step 6: Design Error Handling

For each step, define failure behavior:

| Failure Type | Response |
|-------------|----------|
| API timeout | Retry with backoff (max 3 retries) |
| API error (4xx) | Log error, don't retry (permanent failure) |
| API error (5xx) | Retry with backoff |
| Unexpected state | Abort, notify on-call, log full context |
| Partial completion | Record what succeeded, alert for manual completion |
| Guardrail triggered | Abort, notify, log why guardrail fired |

## Step 7: Plan Rollout

Deploy automation gradually:

**Phase 1: Shadow mode (1-2 weeks)**
- Automation runs but only LOGS what it would do.
- Human continues to execute the runbook manually.
- Compare automation's decisions with human decisions.
- Build confidence that automation makes correct choices.

**Phase 2: Approval mode (2-4 weeks)**
- Automation prepares and proposes actions.
- Human approves before execution.
- Track approval rate (>95% approval -> ready for full auto).

**Phase 3: Full automation (ongoing)**
- Automation executes without human approval.
- Notifications sent post-execution.
- Regular review of automation logs (weekly for first month).

**Phase 4: Refinement (continuous)**
- Handle edge cases discovered in production.
- Expand scope gradually.
- Reduce noise in notifications.

## Output

Produce an automation design document:
1. **Runbook Analysis**: Original steps classified by type with automation mapping.
2. **Automation Architecture**: AWS services selected, workflow diagram.
3. **Workflow Specification**: Step-by-step automation design with inputs, outputs, error handling.
4. **Safety Controls**: Guardrails, rate limits, circuit breakers designed.
5. **Implementation Estimate**: Development effort, testing effort, rollout timeline.
6. **Rollout Plan**: Shadow -> Approval -> Full automation phases.
7. **Success Metrics**: How to measure automation effectiveness (execution count, success rate, time saved).