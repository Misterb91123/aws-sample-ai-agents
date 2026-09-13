---
name: observability-tool-overlap-and-cost
agent_type: "Generic"
description: >
  Finds services instrumented in more than one paid telemetry or APM tool
  (Datadog, Dynatrace, Splunk, New Relic, plus CloudWatch), quantifies the
  licence and ingest waste of double-paying, and recommends consolidation. Use
  this skill during cost reviews or tool-rationalization efforts when the estate
  carries overlapping observability contracts.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Observability Tool Overlap and Cost

Teams accrete monitoring tools over time. A service picked up Datadog in one
quarter, New Relic in another, and never dropped either. The result is the same
telemetry ingested and billed twice, plus per-host or per-user licences paid to
multiple vendors for one workload. This skill maps the overlap and turns it into
a consolidation recommendation grounded in what the connected sources report.

## Sources

Read-only reasoning over data surfaced by the platform:

- Connected third-party telemetry and APM integrations (Datadog, Dynatrace,
  Splunk, New Relic) surfaced on the Agent Space, used to see which services each
  tool is instrumenting.
- CloudWatch and use_aws reads to establish the AWS-native baseline that already
  exists at no extra vendor cost.
- Cost and usage signals the platform surfaces for AWS-side ingest (CloudWatch
  metrics, logs, and traces).

This skill recommends only. It never disables agents, cancels licences, or edits
integrations.

## Method

1. Build the service-to-tool map. For each service, list every connected tool
   that instruments it. A service appearing under two or more paid tools is an
   overlap candidate.
2. Confirm true overlap. Distinguish genuine duplication (both tools collect the
   same metrics, traces, or logs) from complementary use (one for logs, one for
   APM). Only duplication is waste.
3. Estimate the waste. For each overlap, note the billing dimension that drives
   cost (hosts, ingested GB, active users, custom metrics) and describe the
   double charge in those terms using the usage the sources report.
4. Rank by savings and risk. Order overlaps by estimated recurring spend and by
   how disruptive consolidation would be, considering dashboards, alerts, and
   runbooks tied to each tool.
5. Choose a keep candidate per service. Recommend which single tool to retain
   based on existing coverage, team familiarity, and whether CloudWatch alone
   already satisfies the need.
6. Flag ingest waste inside a tool. Beyond cross-tool overlap, note high-cardinality
   custom metrics and verbose log ingest that inflate a single tool's bill.

## Output

Produce a consolidation report:

1. Overlap Map: services listed against the paid tools instrumenting them.
2. Duplication vs Complementary: which overlaps are true waste.
3. Waste Estimate: the billing dimension and approximate recurring cost per
   overlap.
4. Consolidation Plan: recommended keep tool per service, ranked by savings and
   migration risk, with dashboards and alerts to migrate first.
5. Ingest Hygiene: high-cardinality metrics and noisy log streams to trim. All
   recommend-only.
