---
name: fis-experiment-safety-audit
agent_type: "Generic"
description: Audits a proposed AWS Fault Injection Service (FIS) experiment or
  template for safety before it runs. Use this skill to check that a stop
  condition is present and bound to a real CloudWatch alarm, the target is
  scoped by tags or COUNT rather than all-resources, the experiment is
  non-production-first, blast radius is limited on the first run, rollback and
  abort are defined, timing is off-peak, and no prohibited or critical resource
  is targeted without escalation. It produces a pass/fail safety scorecard for
  a human; it does not run or modify the experiment.
version: "1.0.0"
last_updated: "2026-09-12"
---

# FIS Experiment Safety Audit

Use this skill to vet a proposed FIS experiment before any human runs it and to
produce a pass/fail safety scorecard with the required fixes before approval.
FIS injects real faults, so this skill only audits and scores; a human reviews
the scorecard and approves. Pair it with the chaos-experiment-planner skill for
the hypothesis and safety framing.

## Sources

Read-only.

- The proposed experiment or template to audit (from a report artifact, an
  investigation, or the operator), including action, target, and stop condition.
- use_aws for the affected resource's control-plane configuration (resource
  type, tags, environment, criticality) so target scope can be judged.
- list_cloudwatch_alarms to confirm the stop condition is bound to a real alarm.
- The existing chaos-experiment-planner skill for the steady-state definition,
  hypothesis, and blast-radius framing.

## Method

1. Check the stop condition: confirm one is present and, via
   list_cloudwatch_alarms, that it is bound to a real alarm on a meaningful
   metric (error rate, latency, availability). A missing or fabricated alarm is
   a fail.
2. Check the target scope with use_aws: confirm the target uses tag filters or a
   small COUNT, not an unbounded all-resources selection, and that the
   environment is non-production on the first run.
3. Check blast radius: confirm invocationPercentage or COUNT is small on the
   first run and the duration starts short. A broad first run is a fail.
4. Check rollback and abort: confirm the experiment defines how it aborts (stop
   condition) and how the system recovers, and that timing is off-peak.
5. Check for prohibited or critical targets: confirm the experiment does not
   target a prohibited or business-critical resource without a documented
   escalation and approval.
6. Check CI/CD continuous-chaos readiness: whether FIS is wired into CodePipeline
   post-deploy with error-rate stop conditions and CloudWatch Synthetics
   monitoring user experience during the experiment.
7. Score each check pass or fail, list the required fixes, and attach a safety
   rating (YELLOW at least, RED where the fault is hard to reverse). Score
   conservatively: fail on doubt when a safety-relevant field is missing.

## MCP augmentation

The awslabs Resilience guidance ships an MCP server that recommends FIS
experiments from DevOps Agent findings and generates templates
(guidance-for-enhancing-resilience-devops-agent-fis). Where available, connect
that FIS-recommender MCP server to the Agent Space and call it in addition to
the control-plane reads for a maintained safety and template rubric. The AWS
Documentation MCP Server can supply the current FIS action catalog and safety
guidance. Use any MCP in addition to the use_aws reads, never instead of them.
AWS MCP server names and availability evolve; verify before relying on one.

## Output

Produce a safety scorecard: for each audited experiment, the per-check pass or
fail result (stop condition bound to alarm, target scoped, non-production-first,
blast radius limited, rollback/abort defined, off-peak timing, no
prohibited/critical target without escalation), the CI/CD readiness gaps, the
required fixes before approval, the safety rating, and a clear statement that
this is a scorecard for a human to review and approve - not an experiment this
skill runs or modifies.
