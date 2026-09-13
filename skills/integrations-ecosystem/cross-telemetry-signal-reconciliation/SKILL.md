---
name: cross-telemetry-signal-reconciliation
agent_type: "Generic"
description: >
  Reconciles health signals for the same service across CloudWatch and connected
  third-party telemetry sources (Datadog, Dynatrace, Splunk, Grafana, New Relic).
  Use this skill when different monitoring tools disagree about a service's state,
  when the team suspects coverage gaps, or when duplicate and conflicting alerting
  is creating confusion during an investigation.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Cross-Telemetry Signal Reconciliation

Large estates rarely trust a single monitoring tool. The same service is often
watched by CloudWatch and one or more third-party telemetry platforms connected
to the Agent Space. When those sources disagree, responders lose time debating
which dashboard is right instead of fixing the problem. This skill reconciles the
signals into one coherent view and names the disagreements explicitly.

## Sources

This skill reasons over data the platform surfaces from connected sources; it
does not query those tools with any dedicated tool. It reads:

- AWS-native metrics and logs through use_aws and CloudWatch reads (alarms,
  metric statistics, log groups).
- Third-party telemetry surfaced via the Agent Space one-way integrations for
  Datadog, Dynatrace, Splunk, Grafana, and New Relic.
- Webhook-triggered investigation context (list_investigations) when one of those
  tools fired the event that started this analysis.

Everything here is read-only and recommend-only. Do not create, modify, or delete
alarms, monitors, or integrations.

## Method

1. Fix the service and window. Identify the service under review and a shared time
   window. Normalize timezones so every source is compared on the same axis.
2. Inventory the signals per source. For the service, list what each connected
   source reports: alarm or monitor state, error rate, latency percentiles, and
   saturation. Note which source each number came from.
3. Align on common definitions. Confirm the sources measure the same thing. A
   CloudWatch 5xx rate at the load balancer is not the same as an APM error rate
   at the application layer. Record definitional mismatches before calling a
   disagreement.
4. Detect state disagreements. Flag cases where one source shows firing or
   degraded while another shows healthy for the same window. Classify each as
   definitional mismatch, threshold mismatch, data delay, or genuine conflict.
5. Find coverage gaps. Identify request paths or components watched by zero
   sources, and signals present in one tool but absent everywhere else.
6. Find duplicate and conflicting alerting. Identify the same condition alarmed in
   multiple tools (duplicate pages) and thresholds set inconsistently across tools
   for the same metric.
7. Establish ground truth. Where sources conflict, use the layer closest to the
   customer and the raw AWS reads to decide which signal reflects reality.

## Output

Produce a reconciliation report:

1. Signal Matrix: one row per signal, one column per source, showing state and
   value with the winning ground-truth column.
2. Disagreement List: each conflict with its classification and the likely cause.
3. Coverage Gaps: paths and signals no connected source watches.
4. Duplicate and Conflicting Alerts: overlapping alarms and inconsistent
   thresholds, with a recommended single source of truth per signal.
5. Recommendations: which source to trust per signal, thresholds to align, and
   gaps to close. All recommend-only.
