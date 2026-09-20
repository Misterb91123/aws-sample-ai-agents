---
name: bedrock-capacity-planning
agent_type: "Generic"
description: Plans Amazon Bedrock capacity per production model per region - pulls
  CloudWatch AWS/Bedrock Invocations, InvocationThrottles, and InvocationLatency,
  computes utilization against current Service Quotas (requests-per-minute and
  tokens-per-minute), forecasts headroom against the growth trend, classifies
  throttling as raise-quota versus fix-client-backoff-or-architecture, and
  pre-drafts justified quota-increase requests. Use this skill when a Bedrock
  workload throttles or growth threatens a quota. This is capacity and quota
  planning, not cost or token-spend tracking.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Bedrock Capacity Planning

Use this skill to plan Amazon Bedrock capacity and tell a quota shortfall apart
from a client-side throttling problem. This differs from Bedrock cost and
token-spend tracking: the concern here is CAPACITY headroom against quotas, not
dollars. Reason over the CloudWatch, Service Quotas, and usage reads the platform
surfaces; do not modify anything.

## Sources

Read-only.

- CloudWatch AWS/Bedrock metrics via query_cloudwatch_metrics: Invocations,
  InvocationThrottles, and InvocationLatency per model and region, over a window
  long enough to show the trend and peak minutes rather than only averages.
- Service Quotas via use_aws: current Bedrock quotas (requests-per-minute and
  tokens-per-minute) per model and region.
- Cost and Usage via use_aws: token-volume context for the forecast where
  available, referenced as aggregate figures only.

## Method

1. Inventory production models per region and read the current requests-per-minute
   and tokens-per-minute quotas for each.
2. Pull Invocations, InvocationThrottles, and InvocationLatency per model and
   region, capturing peak minutes, not just averages.
3. Compute utilization: peak requests-per-minute and tokens-per-minute against
   quota, and the throttle rate (throttles over total attempts).
4. Forecast headroom: fit the growth trend and estimate time-to-limit, expressing
   headroom as time remaining rather than a single instantaneous percentage.
5. Classify throttling: raise-quota when throttles rise with sustained peak usage
   near the quota; fix-client-backoff-or-architecture when throttles occur while
   utilization is well below quota (bursty retries, missing jitter, no
   exponential backoff, synchronous fan-out).
6. For raise-quota cases, add token-volume context and pre-draft a Service Quotas
   request naming the quota, current value, observed peak, forecast, and
   justification.
7. Rank findings by imminence of the limit and by customer impact, models already
   throttling in production first.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Pricing MCP Server can supply token-volume and cost context for the forecast,
and the AWS Documentation MCP Server can supply current Bedrock quota guidance;
recommend using them in addition to the CloudWatch and Service Quotas reads,
never instead of them. Where deeper client-side telemetry is needed, a custom MCP
server to the application's own metrics can corroborate the client-versus-quota
classification. AWS MCP server names and availability evolve; verify before
relying on one.

## Output

Produce a capacity-planning report: per model and region utilization (peak
requests-per-minute and tokens-per-minute against quota, throttle rate,
headroom); a forecast with time-to-limit and its assumptions; a throttling
classification (raise quota or fix client) with the observed evidence; and
pre-drafted Service Quotas requests for each raise-quota case, ranked by
imminence (recommend-only), with a GREEN, YELLOW, or RED safety rating and YELLOW
or RED flagged for human approval. Reference model identifiers and aggregate
metrics, not prompt or completion contents.
