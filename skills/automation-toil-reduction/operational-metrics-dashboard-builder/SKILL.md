---
name: operational-metrics-dashboard-builder
agent_type: "Generic"
description: Designs operational dashboards that provide actionable visibility into
  system health, team performance, and operational trends. Use this skill when
  building CloudWatch dashboards for new services, designing executive-level
  operational dashboards, or when existing dashboards are noisy and need
  restructuring to surface the right signals.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Operational Metrics Dashboard Builder

Use this skill to design dashboards that give teams actionable operational
visibility without overwhelming them with noise.

## When to Activate

- New service needs an operational dashboard.
- Existing dashboard is cluttered and people ignore it.
- Leadership wants an executive health view.
- Post-incident: "we didn't have visibility into X."
- Team wants to track operational improvement (toil reduction, MTTR, deployment frequency).

## Step 1: Define Dashboard Purpose and Audience

Different audiences need different views:

| Audience | Purpose | Detail Level | Update Frequency |
|----------|---------|-------------|-----------------|
| On-call engineer | Triage and investigate | High detail, drill-down | Real-time (1-5 min) |
| Service owner | Health overview, trends | Medium, summary + detail | 5-15 minutes |
| Engineering manager | Team operational metrics | Summary, trends | Hourly/daily |
| VP/Director | Portfolio health | Executive summary | Daily/weekly |
| Customer-facing (status page) | Availability status | Binary (up/down) per service | Real-time |

## Step 2: Select Metrics by Dashboard Type

### Service Health Dashboard (on-call focused)

**The Four Golden Signals (mandatory):**
1. **Latency**: p50, p95, p99 with threshold lines marking SLO.
2. **Traffic**: Request rate showing current vs historical pattern.
3. **Errors**: Error rate with breakdown by type (5xx, timeout, business error).
4. **Saturation**: CPU, memory, connection pool, queue depth.

**Additional operational context:**
- Deployment markers (vertical annotations showing when deploys happened).
- Active alarms (alarm status widget).
- Recent changes (deployments in last 24h).
- Dependency health (status of downstream services).

### Team Operational Metrics Dashboard (management focused)

**Reliability metrics:**
- SLO compliance per service (current period).
- Error budget remaining (% with burn rate indicator).
- Incident count (SEV1-4) over time.
- MTTR (Mean Time to Recovery) trend.
- MTTD (Mean Time to Detect) trend.

**Delivery metrics:**
- Deployment frequency (deploys per day/week).
- Change failure rate (% deployments causing incidents).
- Lead time for changes (commit to production).
- Rollback rate.

**Toil metrics:**
- Toil hours per week (trending down hopefully).
- On-call page volume and distribution.
- Alert noise ratio (alerts actioned / total alerts).
- Tickets closed vs opened.

### Executive Dashboard (VP/Director focused)

**At-a-glance health:**
- Overall platform status (Green/Yellow/Red).
- Services meeting SLO vs not meeting SLO.
- Active incidents (count and severity).
- Cost trend vs budget.

**Trends:**
- Availability trend over 90 days.
- Incident frequency trend.
- Deployment velocity trend.
- Customer-reported issues trend.

## Step 3: Design Dashboard Layout

Follow the inverted pyramid pattern:

```
+-------------------------------------------------+
| SUMMARY (top): Status indicators, key numbers |
| Answer: "Is everything OK right now?" |
+-------------------------------------------------+
| TRENDS (middle): Time-series graphs |
| Answer: "Is it getting better or worse?" |
+-------------------------------------------------+
| DETAIL (bottom): Tables, breakdowns |
| Answer: "What specifically needs attention?" |
+-------------------------------------------------+
```

**Layout principles:**
1. Most important information at the top (visible without scrolling).
2. Use consistent time ranges across related widgets.
3. Group related metrics together (don't scatter CPU across the page).
4. Use visual hierarchy: large widgets for key metrics, smaller for context.
5. Maximum 15-20 widgets per dashboard (more = ignored).
6. Include threshold lines on graphs (makes it obvious when things are bad).

## Step 4: Choose Widget Types

Match data to the right visualization:

| Data Type | Best Widget | Avoid |
|-----------|------------|-------|
| Current status (up/down) | Status indicator / colored number | Time series (too much detail) |
| Trend over time | Line chart with threshold | Single number (loses context) |
| Comparison across services | Horizontal bar chart | Multiple line charts (hard to compare) |
| Distribution / percentiles | Area chart or stacked area | Pie chart (hard to read) |
| Top N (worst performers) | Table sorted by value | Unsorted lists |
| Rate of change | Line chart with derivative | Raw counters (need rate calculation) |
| Alarm status | Alarm status widget | Buried in a table |

## Step 5: Define Alert Thresholds Visually

Every metric graph should show:
1. **Green zone**: Normal operating range.
2. **Yellow line**: Warning threshold (investigate if crossed).
3. **Red line**: Critical threshold (alarm fires, action needed).
4. **Historical band**: Normal range based on past data (e.g., p10-p90 of same day last 4 weeks).

This makes it immediately obvious when something is outside normal range without needing to remember thresholds.

## Step 6: Implement CloudWatch Dashboard

Design the dashboard JSON structure:

**Recommended widget organization:**
```
Row 1: Summary - alarm status widget + key number widgets (error rate, latency, availability)
Row 2: Traffic - request count + error count (shared time axis)
Row 3: Latency - p50/p95/p99 on same graph with SLO threshold line
Row 4: Saturation - CPU + memory + connections (per-instance breakdown)
Row 5: Dependencies - downstream service health metrics
Row 6: Recent events - deployments, scaling events, config changes
```

**Best practices:**
- Use metric math for derived metrics (error rate = errors/requests).
- Use anomaly detection bands for expected vs actual.
- Set the default time range to 3 hours (enough context, not overwhelming).
- Include a "last 24 hours" dashboard link for broader context.
- Use account/region variables for multi-account dashboards.

## Step 7: Define Dashboard SLA

A dashboard is only useful if it's maintained:

1. **Review frequency**: Quarterly review to ensure metrics are still relevant.
2. **Update triggers**: Dashboard must be updated when architecture changes.
3. **Accuracy validation**: Monthly check that all widgets are still showing data (no broken metrics).
4. **Team feedback**: Ask users if the dashboard helps them or if anything is missing.
5. **Deprecation**: Remove dashboards for decommissioned services.

## Output

Produce a dashboard design:
1. **Dashboard Specification**: Purpose, audience, metrics included, layout wireframe.
2. **Metric Definitions Table**: Metric name, source, calculation, threshold, update frequency.
3. **Widget Layout Diagram**: Visual representation of dashboard arrangement.
4. **Threshold Definitions**: Warning and critical thresholds per metric with justification.
5. **Implementation Steps**: CloudWatch dashboard JSON or Terraform/CDK code outline.
6. **Maintenance Plan**: Review schedule, update triggers, ownership.
7. **Related Dashboards**: Links between summary and detail dashboards for drill-down.