---
name: release-testing-coverage-and-outcomes
agent_type: "Generic"
description: Reports which deployed web applications and REST APIs are covered by
  the AWS DevOps Agent's autonomous Release Testing, and analyzes pass/fail and
  flaky-test trends over time. Identifies coverage gaps where deployed services
  receive no functional regression, user-journey, integration, or edge-case
  testing. Use this to understand how much of the fleet is actually being
  exercised after deploy and where confidence is missing.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Release Testing Coverage and Outcomes

Use this skill to answer two questions: what is Release Testing actually covering,
and how are those tests trending. Release Testing runs autonomous UAT and
regression - functional regression, user-journey, integration, and edge-case
checks - against deployed web apps and REST APIs. This skill is read-only and
recommend-only: it summarizes coverage and outcomes and highlights gaps, it does
not change any test configuration.

## Sources

- Release Testing run history the platform surfaces: which targets were tested,
  when, and the pass/fail result per run.
- The aws-actions/devops-agent-qa trigger presence in deploy pipelines, from the
  connected pipeline integrations, to map deploys to expected test runs.
- Deployed service inventory from AWS-native reads (use_aws, CloudWatch) plus
  connected telemetry to know the full set of web apps and REST APIs that exist.
- Pipeline/deploy correlation data to align each test run with the release it
  validated.
- Comms/ticketing associations only to see where results were reported.

## Method

1. Enumerate all deployed web applications and REST APIs from AWS reads and
   telemetry to establish the denominator of testable targets.
2. Pull Release Testing run history and map each run to a target and a release.
3. Compute coverage: which targets have recent test runs and which have none.
   Flag deployed targets with zero coverage.
4. For covered targets, compute pass/fail rates over the trailing window and by
   test category (functional regression, user-journey, integration, edge cases).
5. Detect flakiness: targets or scenarios that alternate pass/fail without a code
   change, and rank by flake frequency.
6. Correlate failures and flakes with the deploys or resources they touch to
   suggest likely causes.
7. Summarize coverage gaps and outcome trends into a single fleet view.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill,
connecting a custom MCP server to the team's test or CI system (for example the
CI provider API or a dedicated test-reporting service) lets the agent read
detailed per-scenario results, historical suites, and quarantine lists that are
richer than the summarized run history. The general "Agent Toolkit for AWS" can
help the agent enumerate and describe AWS-hosted targets while assembling the
coverage denominator. To enable, connect the MCP server to the Agent Space
through the DevOps Agent MCP-server integration, after which this custom agent can
call the MCP's tools during its run. Use any MCP in addition to the regular
sources - Release Testing history, AWS reads via use_aws/CloudWatch, connected
telemetry, and pipeline integrations - never instead of them. AWS MCP server
names and availability evolve, so verify the current server before relying on it.

## Output

Provide a coverage and outcomes report:
1. Fleet coverage summary: covered vs uncovered deployed web apps and REST APIs.
2. Pass/fail trend per covered target and per test category over the window.
3. Ranked flaky-test list with frequency and suspected cause.
4. Coverage-gap list prioritized by service criticality and recent deploy rate.
5. Recommendations for closing gaps and stabilizing flaky scenarios.
