---
name: dashboard-gap-analyzer
agent_type: "Generic"
description: Identifies gaps in observability coverage by analyzing existing
  dashboards, alarms, and metrics against the services deployed in the environment.
  Use this skill when assessing monitoring maturity, onboarding new services that
  need observability, or when incidents reveal blind spots in existing monitoring.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Dashboard Gap Analyzer

Use this skill to identify services, resources, and failure modes that lack
adequate monitoring, alerting, or dashboard coverage.

## When to Activate

- New service launched - needs observability baseline.
- Post-incident review reveals monitoring gaps ("why didn't we catch this sooner?").
- Quarterly observability maturity assessment.
- Team asks "are we monitoring the right things?"
- Compliance audit requires evidence of comprehensive monitoring.

## Step 1: Inventory Deployed Services

List all production services and resources:
1. ECS services and task definitions.
2. EKS workloads (deployments, statefulsets).
3. Lambda functions.
4. EC2 instances (grouped by service).
5. RDS instances and clusters.
6. ElastiCache clusters.
7. Load balancers (ALB/NLB).
8. API Gateway stages.
9. SQS queues and SNS topics.
10. S3 buckets with active traffic.

## Step 2: Define the Observability Standard

Every production service should have (at minimum):

### The Four Golden Signals (mandatory)
| Signal | What to measure | Example metric |
|--------|----------------|----------------|
| Latency | Request duration | ALB TargetResponseTime p50, p95, p99 |
| Traffic | Request volume | ALB RequestCount, Lambda Invocations |
| Errors | Failure rate | ALB 5xx count, Lambda Errors |
| Saturation | Resource utilization | CPU%, Memory%, ConnectionCount |

### Extended Observability (recommended)
| Category | What to measure |
|----------|----------------|
| Availability | Health check pass rate, uptime percentage |
| Dependencies | Latency and errors to downstream services |
| Business metrics | Transaction success rate, user-facing SLI |
| Queue health | Queue depth, age of oldest message, DLQ size |
| Data layer | Connection pool usage, replication lag, IOPS |

## Step 3: Audit Existing Dashboards

For each deployed service, check:
1. Does a CloudWatch dashboard exist? (or Grafana, Datadog equivalent)
2. Does it cover all four golden signals?
3. Is the dashboard up-to-date (reflects current architecture)?
4. Does it show dependencies alongside the service?
5. Is there a "drill-down" path from service -> component -> individual resource?

**Gap indicators:**
- Service deployed but no dashboard exists.
- Dashboard exists but only shows CPU/memory (missing error rate, latency).
- Dashboard shows the service but not its dependencies.
- Dashboard is stale (references removed resources or old metric names).

## Step 4: Audit Alarm Coverage

For each service, check alarm coverage:

| Required Alarm | What it catches |
|---------------|-----------------|
| Error rate threshold | Service returning errors above normal |
| Latency threshold (p99) | Service slow for worst-case users |
| Health check failure | Service completely unavailable |
| Resource saturation (CPU/memory) | Approaching capacity limits |
| Queue depth growing | Consumer can't keep up with producer |
| DLQ non-empty | Messages failing processing |
| Certificate expiration | TLS cert approaching expiry |
| Disk space | Storage filling up |

**Alarm quality checks:**
- Is the threshold appropriate? (not too sensitive = noise, not too loose = misses issues)
- Does the alarm have an action? (SNS topic, auto-scaling, PagerDuty)
- Is the evaluation period appropriate? (too short = false positives)
- Is there a corresponding OK action? (to notify when resolved)

## Step 5: Audit Logging Coverage

For each service:
1. Are logs being sent to CloudWatch Logs (or equivalent)?
2. Is structured logging used? (JSON format for easy querying)
3. Are request IDs / trace IDs present for correlation?
4. Is the log retention appropriate? (not too short for investigation, not wastefully long)
5. Are error logs distinguishable from info logs? (log levels used correctly)
6. Are sensitive data fields redacted?

## Step 6: Audit Tracing Coverage

For distributed systems:
1. Is X-Ray or equivalent distributed tracing enabled?
2. Are trace IDs propagated across service boundaries?
3. Can you trace a request end-to-end from entry point to database?
4. Is the sampling rate sufficient to catch issues?
5. Are key operations annotated (business-meaningful segments)?

## Step 7: Identify Critical Gaps

Prioritize findings by risk:

**Critical gaps (fix immediately):**
- Production service with NO monitoring at all.
- Customer-facing service without error rate alarming.
- Database without connection/capacity monitoring.
- No alerting path to on-call (alarms exist but no notification action).

**High gaps (fix within sprint):**
- Service monitored but missing latency or saturation signals.
- Alarms exist but thresholds are misconfigured.
- Logs exist but not structured (can't query effectively).
- No dependency health visibility.

**Medium gaps (plan for next quarter):**
- Missing distributed tracing.
- No business metric monitoring.
- Dashboard exists but is incomplete or stale.
- Log retention too short for investigation needs.

## Output

Produce an observability gap report:
1. **Coverage Scorecard**: Per-service observability score (metrics, alarms, logs, traces, dashboard).
2. **Unmonitored Services Table**: Service, environment, last deployment, gap type, risk level.
3. **Missing Alarms Table**: Service, missing alarm type, risk if not caught, recommended threshold.
4. **Dashboard Gaps Table**: Service, what's missing from existing dashboard, priority.
5. **Observability Maturity Chart**: Radar/spider chart showing coverage across the four pillars.
6. **Implementation Roadmap**: Prioritized list of monitoring to add, grouped by effort level.