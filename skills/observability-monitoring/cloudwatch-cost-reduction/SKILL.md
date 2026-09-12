---
name: cloudwatch-cost-reduction
agent_type: "Generic"
description: Use this skill when Amazon CloudWatch spend is high and needs reduction across custom metrics, log ingestion and storage, and API calls. It triggers on rising CloudWatch charges in Cost Explorer, high-cardinality custom metrics, large log ingestion volumes, or frequent GetMetricData and API usage, and it guides safe cost cuts without losing needed visibility.
version: "1.0.0"
last_updated: "2026-08-14"
---

# CloudWatch Cost Reduction

This skill reduces Amazon CloudWatch cost across its main billing dimensions: custom metrics, log ingestion and storage, and API requests. It identifies the largest drivers first and applies changes that preserve the visibility teams actually use.

## When to Activate

- CloudWatch charges are rising in Cost Explorer and need attribution and reduction.
- A service publishes high-cardinality custom metrics (many unique dimension combinations).
- Log ingestion volume (GB ingested) is a large line item.
- GetMetricData or PutMetricData API charges are significant.
- Dashboards or Contributor Insights are driving unexpected cost.

## Step 1: Attribute the cost

- In Cost Explorer, filter to the CloudWatch service and group by Usage Type to split cost across metrics, logs (ingestion, storage, and analysis), dashboards, alarms, and API requests.
- Identify the top one or two usage types by cost. Custom metrics are billed per metric per month; logs are billed per GB ingested and per GB stored; API calls (GetMetricData, GetMetricStatistics) are billed per 1,000 requests.

## Step 2: Reduce custom metric cardinality

- Enumerate custom metrics and their dimensions. Each unique combination of metric name and dimension values is a separate billable custom metric, so high-cardinality dimensions (request ID, user ID, instance ID at scale) multiply cost quickly.
- Remove high-cardinality dimensions that are not used in alarms or dashboards. Aggregate at a coarser dimension (per service or per fleet rather than per instance) where per-instance detail is not needed.
- Consolidate near-duplicate metrics and delete metrics no longer referenced by any alarm or dashboard.

## Step 3: Adopt embedded metric format for logs-derived metrics

- Where an application emits many custom metrics via PutMetricData, consider the Embedded Metric Format (EMF): the app writes structured logs and CloudWatch extracts metrics from them, avoiding per-call PutMetricData charges and letting you keep the underlying log detail.
- Weigh the tradeoff: EMF shifts cost toward log ingestion, so it wins when you already ingest the logs or when it collapses many PutMetricData calls.

## Step 4: Tune log retention and ingestion

- Set retention on every log group. Logs default to never expire, so storage accumulates indefinitely. Set retention to the actual requirement (for example 30, 90, or 365 days) per log group.
- Reduce ingestion volume by lowering verbose log levels in production, dropping health-check and noise lines at the source, and sampling high-volume debug logs.
- For logs needed long term but rarely queried, export to S3 (and optionally Glacier) where storage is far cheaper than CloudWatch Logs storage, and query with Athena when needed.
- Review Logs Insights query usage, which is billed per GB of data scanned; narrow time ranges and add filters early in queries to scan less data.

## Step 5: Batch and reduce API calls

- Replace many GetMetricStatistics calls with GetMetricData, which retrieves up to 500 metrics in a single request and supports metric math, cutting request count.
- Increase polling intervals for dashboards and pollers that do not need sub-minute refresh, since each refresh issues metric-read API calls.
- Cache metric reads in downstream tooling rather than re-querying the same data repeatedly.

## Step 6: Optimize dashboards and Contributor Insights

- Dashboards are billed per dashboard per month above the free allotment, and each auto-refresh issues API calls. Consolidate redundant dashboards and reduce auto-refresh frequency.
- Contributor Insights rules are billed per rule and per matched log event; disable rules that are no longer investigated and scope rules narrowly so they match fewer events.

## Output

Produce a CloudWatch Cost Reduction Report containing: the cost breakdown by usage type with the top drivers, the high-cardinality custom metrics identified and the dimensions to remove or aggregate, an EMF recommendation where PutMetricData volume is high, per-log-group retention and ingestion-reduction actions with estimated GB savings, API-call batching opportunities (GetMetricData consolidation), and dashboard and Contributor Insights cleanup. Include an estimated monthly savings per action and a note confirming no in-use alarm or dashboard loses its source data.