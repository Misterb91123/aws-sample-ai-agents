---
name: post-deploy-regression-watch
agent_type: "Generic"
description: After a deployment, watches the target service's golden signals -
  latency, error rate, traffic, and saturation - for a defined window and
  attributes any regression to that specific release. Correlates the deploy marker
  with metric shifts so a bad release is caught and named quickly. Use this
  immediately after a deploy to decide whether to hold, monitor, or recommend a
  rollback.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Post-Deploy Regression Watch

Use this skill to keep an eye on a service right after it ships. The riskiest
window is the minutes and hours after a deploy; a regression that starts exactly
at the deploy marker is almost certainly the release. This skill watches the
golden signals and attributes shifts to the release. It is read-only and
recommend-only: it observes and recommends, it does not roll back or change the
service.

## Sources

- AWS-native telemetry reads (use_aws, CloudWatch) for the target service's golden
  signals: latency, error rate, request rate, and saturation.
- Connected telemetry associations (Datadog, Dynatrace, Splunk, Grafana, New
  Relic) where the service reports there, read one-way through the platform.
- Deploy markers from the pipeline association to anchor the before/after window.
- Release Testing results for the same release as corroborating signal.
- Comms/ticketing associations only to report or escalate the finding.

## Method

1. Anchor on the deploy marker for the release and define a pre-deploy baseline and
   a post-deploy watch window.
2. Track the four golden signals for the target service across the window and
   compare against the baseline and normal daily pattern.
3. Detect regressions: sustained error-rate increase, latency growth, traffic
   collapse, or saturation climbing after the marker.
4. Attribute the shift to the release by confirming timing alignment with the
   deploy marker and ruling out unrelated causes (dependency incident, traffic
   spike).
5. Check the release's Release Testing result to corroborate or contrast the live
   signal.
6. Classify severity and give a clear hold, keep-watching, or recommend-rollback
   verdict.
7. Summarize evidence so the on-call can act without re-investigating.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill no
AWS-owned MCP server is strictly needed - the golden-signal reads are telemetry
native through use_aws, CloudWatch, and the connected telemetry associations. If a
team relies on a monitoring tool that is not connected as an association, a custom
telemetry MCP server wrapping that tool's API can bring its signals into the same
analysis. To enable, connect the MCP server to the Agent Space through the DevOps
Agent MCP-server integration, after which this custom agent can call the MCP's
tools during its run. Use any such MCP in addition to the regular sources - AWS
telemetry via use_aws/CloudWatch, connected telemetry associations, deploy
markers, and Release Testing results - never instead of them. AWS MCP server
names and availability evolve, so verify the current server before relying on it.

## Output

Provide a regression-watch report:
1. Deploy marker, baseline, and watch window used.
2. Golden-signal comparison (latency, errors, traffic, saturation) before/after.
3. Detected regressions with timing alignment to the release.
4. Attribution confidence and ruled-out alternative causes.
5. Verdict - hold, keep watching, or recommend rollback - with evidence.
