---
name: fis-experiment-result-analysis
agent_type: "Generic"
description: Analyzes AWS Fault Injection Service (FIS) experiment results after
  a run against the chaos-engineering scientific method. Use this skill to
  compare the steady-state baseline against behavior observed during the
  experiment, decide whether the hypothesis held, measure time-to-detect and
  time-to-recover, check whether stop conditions fired appropriately, compare
  observed against expected blast radius, and list the residual resilience gaps
  to fix and re-test, using CloudWatch metrics over the experiment window. It
  analyzes and recommends; it does not run or re-run experiments.
version: "1.0.0"
last_updated: "2026-09-12"
---

# FIS Experiment Result Analysis

Use this skill to learn from a FIS experiment after it has run and to name the
residual resilience gaps to fix and re-test. FIS injects real faults, so this
skill only analyzes and recommends; a human reviews and runs any re-test under
control. Pair it with the chaos-experiment-planner skill for the hypothesis and
steady-state framing.

## Sources

Read-only.

- The completed experiment record to analyze (from a report artifact, an
  investigation, or the operator), including its hypothesis, target, and window.
- query_cloudwatch_metrics for the key metrics (error rate, latency,
  availability, throughput) over both the baseline window and the experiment
  window.
- use_aws for the target resource configuration and alarm state.
- list_investigations for any incident the experiment caused or reproduced.
- The existing chaos-experiment-planner skill for the steady-state definition,
  hypothesis, and blast-radius framing.

## Method

1. Establish the steady-state baseline with query_cloudwatch_metrics: pull the
   key metrics for a comparable window before the experiment.
2. Pull the same metrics over the experiment window and compare observed
   behavior against the baseline to quantify the impact.
3. Decide whether the hypothesis held: if the hypothesis was that the system
   stays within steady state during the fault, check whether the observed
   metrics stayed within the defined bounds. Without a baseline, mark the result
   inconclusive.
4. Measure time-to-detect (fault injection to alarm or detection) and
   time-to-recover (fault end to return to steady state) from the timelines.
5. Check whether stop conditions fired appropriately: did an alarm fire when it
   should have, and did the experiment abort as designed, or did blast radius
   exceed the expected scope. Mark unknown when the alarm state cannot be read.
6. Compare observed blast radius against expected, and list the residual
   resilience gaps to fix and the re-test to run after the fix. Prefer the
   reading that a gap remains when the data is ambiguous about recovery.

## MCP augmentation

The awslabs Resilience guidance ships an MCP server that recommends FIS
experiments from DevOps Agent findings and generates templates
(guidance-for-enhancing-resilience-devops-agent-fis). Where available, connect
that FIS-recommender MCP server to the Agent Space and call it in addition to
the metric reads for maintained experiment and re-test guidance. The AWS
Documentation MCP Server can supply the current FIS action catalog and metric
interpretation guidance. Use any MCP in addition to the query_cloudwatch_metrics
and use_aws reads, never instead of them. AWS MCP server names and availability
evolve; verify before relying on one.

## Output

Produce a results analysis: for each experiment, the baseline-versus-observed
comparison; whether the hypothesis held, failed, or was inconclusive;
time-to-detect and time-to-recover; whether stop conditions fired appropriately;
observed versus expected blast radius; the residual gaps and the re-test to run;
and a clear statement that this is an analysis and set of recommendations for a
human to review, and that a human runs any re-test under control - not an action
this skill performs.
