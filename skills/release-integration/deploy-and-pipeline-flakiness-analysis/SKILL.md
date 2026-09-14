---
name: deploy-and-pipeline-flakiness-analysis
agent_type: "Generic"
description: Analyzes pipeline failure and flakiness trends across GitHub Actions,
  GitLab CI-CD, and Azure DevOps, and ties those failures to the AWS resources the
  pipelines target. Separates genuine failures from flaky, retry-passing runs and
  ranks the worst offenders by frequency and cost of lost time. Use this to make
  pipelines reliable so the release path is trusted and fast.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Deploy and Pipeline Flakiness Analysis

Use this skill to find where pipelines waste time and erode trust. A pipeline that
fails intermittently and passes on retry is flaky; one that fails consistently has
a real defect. Both slow releases, and both often trace back to the AWS resource
the pipeline touches. This skill is read-only and recommend-only: it reports
trends and likely causes, it does not modify pipelines or resources.

## Sources

- Pipeline associations (GitHub Actions, GitLab CI-CD, Azure DevOps) for run
  history: outcomes, durations, retries, and the stage where failures occur.
- Deploy-to-resource correlation the platform tracks, to map each failing stage to
  the AWS resource it targets.
- AWS-native reads (use_aws, CloudWatch) for the state of those target resources
  around the failure times (throttling, capacity, permission errors).
- Release Testing and verification history where those steps run inside the
  pipeline.
- Comms/ticketing associations only for reporting.

## Method

1. Pull pipeline run history and compute failure rate, retry rate, and duration by
   pipeline and by stage.
2. Classify failures as genuine (fails and stays failed) versus flaky (fails then
   passes on retry without a change).
3. For each recurring failure, identify the stage and the AWS resource it targets
   from the deploy-to-resource correlation.
4. Cross-check target-resource state at failure times using AWS reads to spot
   throttling, capacity limits, permission errors, or dependency outages.
5. Rank offenders by frequency and by engineering time lost to retries and waits.
6. Distinguish provider-side issues from AWS-side issues so remediation lands with
   the right owner.
7. Summarize trends and probable root causes per pipeline.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill a
custom CI MCP server that wraps the provider API (GitHub, GitLab, or Azure
DevOps) is the most relevant addition: it lets the agent read per-step logs, retry
history, and job timing at a granularity beyond the summarized run history, which
is essential to separate flaky from genuine failures. No AWS-owned MCP server is
strictly required here, though the "Agent Toolkit for AWS" can help describe the
targeted resources. To enable, connect the MCP server to the Agent Space through
the DevOps Agent MCP-server integration, after which this custom agent can call
the MCP's tools during its run. Use any MCP in addition to the regular sources -
AWS reads via use_aws/CloudWatch, deploy-to-resource correlation, and the
connected pipeline integrations - never instead of them. AWS MCP server names and
availability evolve, so verify the current server before relying on it.

## Output

Provide a flakiness report:
1. Failure and retry rates by pipeline and stage over the window.
2. Genuine-versus-flaky classification for recurring failures.
3. Failing stages mapped to their target AWS resource and resource state.
4. Ranked offenders by frequency and time lost, with owner (provider or AWS).
5. Recommendations to stabilize each top offender.
