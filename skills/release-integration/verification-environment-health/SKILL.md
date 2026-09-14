---
name: verification-environment-health
agent_type: "Generic"
description: Reports on the health, duration, and cost of the agent-managed
  verification environments that Release Readiness Reviews use to build, run, and
  test changes. Surfaces build/test success rates, provisioning failures, run
  durations, and the spend attributable to these environments. Use this to keep
  the automated verification step fast, reliable, and cost-aware so it stays a
  trusted gate rather than a bottleneck.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Verification Environment Health

Use this skill to keep the automated verification testing behind Release Readiness
Reviews healthy. Each review can build, run, and test the change in an
agent-managed verification environment; this skill watches how well that machinery
runs and what it costs. It is read-only and recommend-only: it reports health and
spend and suggests improvements, it does not resize or reconfigure anything.

## Sources

- Verification run history the platform surfaces from Release Readiness Reviews:
  provisioning outcome, build result, test result, and duration per run.
- AWS-native reads (use_aws, CloudWatch) for the compute and supporting resources
  the verification environments consume and their utilization.
- Cost and usage data the platform surfaces for the account, to attribute spend
  to verification activity.
- Pipeline correlation to align verification runs with the PRs and repos that
  triggered them.
- Comms/ticketing associations only to see where failures were escalated.

## Method

1. Pull verification run history and compute provisioning success rate, build
   success rate, and test success rate over the window.
2. Measure run duration distribution (median and tail) and flag environments or
   repos with slow or timing-out runs.
3. Identify recurring provisioning failures and group them by cause (quota,
   dependency fetch, image pull, permission).
4. Attribute cost to verification activity using account cost/usage data and the
   underlying compute reads, and compute cost per run and per repo.
5. Correlate expensive or failing runs with the repositories and change types that
   trigger them.
6. Flag trends: rising duration, rising failure rate, or rising spend.
7. Summarize health and cost into a single scorecard with the worst offenders.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For the spend
angle of this skill, the "AWS Billing and Cost Management MCP Server" and the
"AWS Pricing MCP Server" (both from the awslabs/mcp project) are the most
relevant: the billing server helps attribute actual verification spend and the
pricing server helps model the rate of the compute the environments use. To
enable, connect the MCP server to the Agent Space through the DevOps Agent
MCP-server integration, after which this custom agent can call the MCP's tools
during its run. Use these in addition to the regular sources - verification run
history, AWS reads via use_aws/CloudWatch, and connected pipeline integrations -
never instead of them. AWS MCP server names and availability evolve, so verify
the current server before relying on it.

## Output

Provide a verification health report:
1. Provisioning, build, and test success rates over the window.
2. Duration distribution with slow-run and timeout offenders.
3. Provisioning failure causes grouped and ranked.
4. Cost per run and per repo, with the top spend contributors.
5. Trend flags and recommendations to improve reliability and reduce spend.
