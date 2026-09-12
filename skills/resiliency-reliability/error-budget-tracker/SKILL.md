---
name: error-budget-tracker
agent_type: "Generic"
description: Tracks SLO compliance and error budget consumption across services,
  alerting when budgets are burning too fast and recommending appropriate responses.
  Use this skill when assessing service reliability posture, making release
  decisions based on remaining error budget, or when an incident consumes a
  significant portion of the error budget.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Error Budget Tracker

Use this skill to calculate, track, and act on error budget consumption for
services with defined SLOs.

## When to Activate

- Daily/weekly SLO compliance review.
- Post-incident: calculate error budget impact of an outage.
- Release decision: is there enough error budget to deploy safely?
- Error budget alert: burn rate exceeding sustainable threshold.
- Quarterly reliability planning.

## Step 1: Define SLO Context

For each service, establish the SLO framework:

| SLO Type | Example | Measurement |
|----------|---------|-------------|
| Availability | 99.9% uptime | (successful requests / total requests) x 100 |
| Latency | 95% of requests < 200ms | p95 latency distribution |
| Error rate | < 0.1% error rate | (error responses / total responses) x 100 |
| Throughput | > 1000 req/s sustained | Minimum sustained request rate |

**Error Budget = 100% - SLO target**
- 99.9% SLO -> 0.1% error budget -> 43.2 minutes/month downtime
- 99.95% SLO -> 0.05% error budget -> 21.6 minutes/month downtime
- 99.99% SLO -> 0.01% error budget -> 4.3 minutes/month downtime

## Step 2: Calculate Current Error Budget Consumption

For the current measurement window (typically 30-day rolling):

1. Retrieve availability/success metrics:
   - Total requests served
   - Failed requests (5xx, timeouts, unhealthy responses)
   - Calculate actual SLI: (total - failed) / total

2. Calculate budget consumption:
   - Total error budget (in requests or minutes)
   - Budget consumed so far this window
   - Budget remaining
   - Percentage consumed
   - Days remaining in the window

3. Calculate burn rate:
   - Current burn rate = budget consumed / time elapsed
   - Sustainable burn rate = total budget / window length
   - Burn rate ratio = current / sustainable (>1 means burning too fast)

## Step 3: Burn Rate Analysis

Classify the burn rate:

| Burn Rate Multiplier | Status | Response |
|---------------------|--------|----------|
| < 0.5x | Healthy | Budget accumulating, safe for changes |
| 0.5x - 1.0x | Normal | On track to meet SLO |
| 1.0x - 2.0x | Elevated | May exhaust budget before window resets |
| 2.0x - 5.0x | High | Will exhaust budget - reduce risk-taking |
| 5.0x - 10x | Critical | Active incident likely - investigate |
| > 10x | Emergency | Severe incident - immediate action needed |

**Multi-window burn rate (recommended):**
- Fast burn (1-hour window): detects acute incidents
- Slow burn (6-hour window): detects gradual degradation
- Alert when BOTH short and long windows exceed threshold (reduces false alerts)

## Step 4: Impact of Recent Incidents

For each incident in the current window:
1. Duration of customer impact
2. Error volume during the incident
3. Error budget consumed by this incident (minutes or request count)
4. Percentage of total budget consumed by this single event

This helps teams understand if one major incident is dominating budget consumption
vs many small issues accumulating.

## Step 5: Release Decision Guidance

Based on remaining error budget:

| Budget Remaining | Release Recommendation |
|-----------------|----------------------|
| > 75% | Green: deploy freely, normal process |
| 50-75% | Yellow: deploy with extra monitoring, prefer canary |
| 25-50% | Orange: deploy only low-risk changes, defer risky features |
| 10-25% | Red: deploy only critical fixes, freeze feature releases |
| < 10% | Frozen: emergency-only deployments until budget recovers |

## Step 6: Forecast Budget Status

Based on current trajectory:
1. If current burn rate continues, when will budget be exhausted?
2. Days until window reset (budget replenishment).
3. Will the service meet its SLO for this window? (yes/no/at risk)
4. Projected SLI at end of window based on current trend.

## Step 7: Identify Budget Consumers

Break down what is consuming error budget:
1. By error type (503s, timeouts, connection refused)
2. By endpoint (which APIs are least reliable)
3. By time period (peak hours vs off-peak)
4. By dependency (which downstream failures impact our SLI)

This helps target reliability improvements effectively.

## Output

Produce an error budget report:
1. **SLO Dashboard Table**: Service, SLO target, current SLI, budget total, budget consumed, budget remaining %, burn rate status.
2. **Budget Consumption Chart**: Line chart showing budget consumption over the rolling window with sustainable burn rate line.
3. **Incident Impact Table**: Incident, duration, budget consumed, percentage of total budget.
4. **Release Readiness**: Current release posture per service (Green/Yellow/Orange/Red/Frozen).
5. **Burn Rate Alert Status**: Services with elevated burn rates requiring attention.
6. **Forecast**: Projected SLO compliance status at end of measurement window.
7. **Top Budget Consumers**: Error types and endpoints consuming the most budget.