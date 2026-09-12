---
name: New agent proposal
about: Propose a new custom agent for the collection
title: "[Agent] "
labels: agent
---

## Agent purpose

One sentence describing what the agent monitors or audits and the value it provides.

## AWS services and APIs

Which AWS services and API operations does it read (for example, RDS DescribeDBInstances, CloudWatch GetMetricStatistics)?

## Key thresholds

What numeric thresholds define a finding (for example, utilization below 40 percent, expiry within 30 days)?

## Suggested schedule

For example, daily at 7 AM UTC, weekly Monday, or every 4 hours.

## Suggested skills

Which existing skills would this agent load (see skills/README.md)?

## Guardrails

Confirm the agent is read-only and produces recommendations only, in line with SECURITY.md.
