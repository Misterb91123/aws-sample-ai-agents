---
name: continuous-chaos-cicd-readiness
agent_type: "Generic"
description: Reports whether continuous chaos testing is wired into delivery for
  each application. Use this skill to check whether AWS Fault Injection Service
  (FIS) experiments are automated in CodePipeline post-deployment, gated by
  CloudWatch alarm stop conditions, monitored by CloudWatch Synthetics during
  the experiment, tracked over time, and run on a regular GameDay cadence, and
  to assign a maturity level per application with the gaps. It reports and
  recommends; it does not run or modify experiments or pipelines.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Continuous Chaos CI/CD Readiness

Use this skill to judge whether chaos testing is embedded in the delivery
pipeline rather than run ad hoc, and to assign a maturity level per application.
FIS injects real faults, so this skill only reports and recommends; a human
reviews and implements the changes. Pair it with the chaos-experiment-planner
skill for the hypothesis and safety framing.

## Sources

Read-only.

- The applications and pipelines in scope (from a report artifact, an
  investigation, or the operator).
- use_aws for CodePipeline definitions, the FIS experiment configuration, the
  bound CloudWatch alarms, and the CloudWatch Synthetics canaries.
- list_investigations for incidents a GameDay or automated experiment should
  have caught.
- The existing chaos-experiment-planner skill for the steady-state definition,
  hypothesis, and blast-radius framing.

## Method

1. Check pipeline integration with use_aws: whether each CodePipeline has a
   post-deployment stage that runs a FIS experiment after deploy, rather than
   chaos being run manually and separately.
2. Check stop-condition gating: whether the automated experiments are gated by
   CloudWatch alarm stop conditions on error rate or latency so a failing
   experiment aborts and can block the pipeline.
3. Check user-experience monitoring: whether CloudWatch Synthetics canaries run
   during the experiment window to observe the customer-facing experience, not
   just backend metrics.
4. Check results tracking: whether experiment outcomes are recorded over time (a
   history of runs, pass/fail, findings) so resilience trends are visible.
5. Check GameDay cadence: whether the team runs regular, scheduled GameDays
   rather than one-off experiments.
6. Assign a maturity level per application (for example none, ad hoc, automated,
   gated, continuous) from the observed controls, and list the specific gaps and
   the next control to add. Score conservatively when a control is unconfirmed.

## MCP augmentation

The awslabs Resilience guidance ships an MCP server that recommends FIS
experiments from DevOps Agent findings and generates templates
(guidance-for-enhancing-resilience-devops-agent-fis). Where available, connect
that FIS-recommender MCP server to the Agent Space and call it in addition to
the control-plane reads for maintained experiment and pipeline-integration
guidance. The AWS Documentation MCP Server can supply the current FIS and
CodePipeline integration patterns. Use any MCP in addition to the use_aws
reads, never instead of them. AWS MCP server names and availability evolve;
verify before relying on one.

## Output

Produce a readiness report: for each application, the observed controls
(post-deploy FIS in CodePipeline, gated by alarm stop condition, Synthetics
user-experience monitoring, results tracked over time, GameDay cadence), the
gaps, the assigned maturity level, the next control to add, and a clear
statement that this is a report and set of recommendations for a human to
review and implement - not experiments or pipeline changes this skill makes.
