---
name: fis-experiment-template-design
agent_type: "Generic"
description: Turns a reviewed AWS Fault Injection Service (FIS) recommendation
  into a complete, ready-to-review FIS experiment template. Use this skill to
  assemble the action, a scoped target selection (resourceType, selectionMode
  COUNT or PERCENT or tag filters, environment), an ISO 8601 duration, stop
  conditions bound to a CloudWatch alarm, the FIS experiment IAM role
  reference, and logging configuration. It generates the template text for a
  human to review and deploy; it does not create or start the experiment.
version: "1.0.0"
last_updated: "2026-09-12"
---

# FIS Experiment Template Design

Use this skill to convert a reviewed FIS recommendation into the concrete
template a human can inspect and deploy. FIS injects real faults, so this skill
only assembles and describes the template; a human reviews it, supplies the
role and alarm, deploys it, and runs the experiment under control. Pair it with
the chaos-experiment-planner skill for the hypothesis and safety framing.

## Sources

Read-only.

- The reviewed recommendation to template (from a report artifact, an
  investigation, or the operator), including the action and target intent.
- use_aws for the affected resource's control-plane configuration (resource
  type, tags, AZ span, deployment mode) so the target selection is concrete.
- list_cloudwatch_alarms to find a real alarm to bind the stop condition to.
- The existing chaos-experiment-planner skill for the steady-state definition,
  hypothesis, and blast-radius framing.

## Method

1. Set the action from the reviewed recommendation and confirm the current
   action name against the FIS documentation, since the catalog evolves.
2. Build the target selection: set resourceType, choose selectionMode COUNT for
   a small fixed count or PERCENT for a small percentage, and prefer tag filters
   that scope to a non-production environment first. Never emit an unbounded
   all-resources target.
3. Set an ISO 8601 duration that starts short (for example PT3M for three
   minutes, PT10M for ten). Durations are ISO 8601; a human confirms the value.
4. Bind the stop condition to a real CloudWatch alarm found through
   list_cloudwatch_alarms on the metric the finding cares about (error rate,
   latency, availability). If no suitable alarm exists, mark the alarm reference
   as needs-human-input rather than inventing an alarm ARN.
5. Reference the FIS experiment IAM role by placeholder (roleArn) and state that
   the roleArn and alarm ARN must be supplied or confirmed by a human before
   deployment. Never fabricate a role ARN or account ID.
6. Add the logging configuration (CloudWatch Logs or S3 log destination) as a
   placeholder for the human to confirm so the experiment records what it did.
7. Assemble the full template, label placeholders needs-human-input, and attach
   a safety rating (YELLOW at least, RED where the fault is hard to reverse).

## MCP augmentation

The awslabs Resilience guidance ships an MCP server that recommends FIS
experiments from DevOps Agent findings and generates templates
(guidance-for-enhancing-resilience-devops-agent-fis). Where available, connect
that FIS-recommender MCP server to the Agent Space and call it in addition to
the control-plane reads for maintained template generation and the current
template schema. The AWS Documentation MCP Server can supply the current FIS
action catalog and template fields. Use any MCP in addition to the use_aws
reads, never instead of them. AWS MCP server names and availability evolve;
verify before relying on one.

## Output

Produce a template set: for each reviewed recommendation, the FIS action; the
scoped target selection (resourceType, selectionMode COUNT or PERCENT or tag
filters, environment); the ISO 8601 duration; the CloudWatch stop-condition
alarm (or needs-human-input); the roleArn reference and logging config as
placeholders; the safety rating; and a clear statement that this is a template
for a human to review, supply the role and alarm, deploy, and run - not an
experiment this skill creates or starts.
