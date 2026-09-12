---
name: observability-cost-optimization
agent_type: "Generic"
description: Use this skill to reduce CloudWatch and X-Ray spend driven by custom metrics, log ingestion and storage, dashboards, high-cardinality dimensions, and trace sampling. It quantifies the cost of each observability component and recommends retention, sampling, and cardinality changes without losing needed signal.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Observability Cost Optimization

This skill audits CloudWatch and X-Ray usage to find the highest-cost observability components and trims spend while preserving the metrics, logs, and traces teams actually use.

## When to Activate

- CloudWatch or X-Ray appears among the top services in a Cost Anomaly or Cost Explorer report.
- A log group ingests more than 50 GB per month.
- Custom metric count is high enough that per-metric cost exceeds $0.30 each per month.
- Log groups have no retention set (retention is Never Expire).
- Dashboards or high-cardinality metric dimensions are proliferating without ownership.

## Step 1: Inventory Log Ingestion and Storage

- Call CloudWatch Logs DescribeLogGroups and read storedBytes and retentionInDays for every log group.
- Call GetMetricStatistics on namespace AWS/Logs, metric IncomingBytes, per log group to measure monthly ingestion.
- Flag any log group ingesting more than 50 GB per month or with retentionInDays unset.

## Step 2: Audit Custom Metrics

- Call ListMetrics to count custom metrics per namespace and identify high-cardinality dimensions.
- Estimate monthly cost per metric and flag namespaces where individual metrics cost more than $0.30 each.
- Identify metrics with cardinality driven by unbounded dimensions such as request id or user id.

## Step 3: Review Dashboards and Alarms

- Call ListDashboards and GetDashboard to count widgets and API-driven metric queries.
- Call DescribeAlarms to find alarms on unused or duplicate metrics.
- Flag dashboards not viewed and alarms in INSUFFICIENT_DATA for more than 30 days.

## Step 4: Examine X-Ray Sampling

- Call X-Ray GetSamplingRules and GetSamplingStatisticSummaries to read the effective sampling rate.
- Flag services sampling more than 5% of traces where 1 to 2% would preserve signal.
- Identify traces retained beyond the value needed for debugging.

## Step 5: Model Savings

- For each flagged log group, model the savings from setting retention (for example 30 or 90 days) and moving cold logs to S3.
- For custom metrics, model savings from dropping high-cardinality dimensions or aggregating at the source.
- For X-Ray, model savings from lowering the sampling rate to the recommended target.

## Output

The skill produces a titled "Observability Cost Optimization Assessment" summarizing monthly CloudWatch Logs, custom metrics, dashboards, and X-Ray spend, the highest-cost components with their measured ingestion, cardinality, and sampling rates, and modeled monthly savings for each recommended change. It concludes with a prioritized remediation list ordered by dollar savings, such as setting retention on unbounded log groups, exporting cold logs to S3, removing high-cardinality dimensions, deleting unused dashboards and alarms, and lowering X-Ray sampling to the target rate.