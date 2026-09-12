---
name: sli-measurement-validator
agent_type: "Generic"
description: Validates that Service Level Indicators (SLIs) are correctly defined,
  accurately measured, and truly represent the customer experience. Use this skill
  when setting up new SLIs, auditing existing SLO definitions for accuracy, or
  when SLO reports don't match customer-reported experience.
version: "1.0.0"
last_updated: "2026-08-14"
---

# SLI Measurement Validator

Use this skill to validate that SLI definitions accurately capture customer
experience and that the measurement implementation is correct.

## When to Activate

- Setting up SLOs for a new service.
- SLO reports show "healthy" but customers are complaining (measurement gap).
- Annual SLO review - are we measuring the right things?
- After architecture changes that may affect how SLIs are captured.
- Investigating discrepancy between internal SLI and external monitoring (synthetic checks).

## Step 1: Review Current SLI Definitions

For each service's SLI, document:
1. **What is being measured**: The specific metric or calculation.
2. **Where it's measured**: The data source (ALB metrics, application metrics, synthetic checks).
3. **The formula**: Exact calculation (e.g., successful requests / total requests).
4. **What counts as "good"**: Definition of a successful event.
5. **What counts as "total"**: All events in the denominator.
6. **Exclusions**: Any events explicitly excluded from the calculation.

## Step 2: Validate "Good Event" Definition

The most common SLI error is an incorrect definition of "good":

**Availability SLI pitfalls:**
| Issue | Problem | Fix |
|-------|---------|-----|
| Only counting 5xx as bad | 4xx from server bugs counted as "good" | Include server-caused 4xx |
| Measuring at ALB only | Doesn't capture connection refused (instance dead) | Include health check failures |
| Excluding timeouts | Client-side timeouts not counted | Include requests that never complete |
| Counting health checks | Health check traffic inflates "good" count | Exclude synthetic/internal traffic |
| Counting non-customer traffic | Bot traffic inflates availability | Consider filtering to real users |

**Latency SLI pitfalls:**
| Issue | Problem | Fix |
|-------|---------|-----|
| Measuring server-side only | Ignores network latency to customer | Measure client-side or edge |
| Using average latency | Hides tail latency issues | Use percentile (p95, p99) |
| Measuring only successful requests | Failed fast requests make latency look good | Include all requests |
| Including cached responses | Cache hits hide backend latency issues | Measure by response type |

## Step 3: Validate Measurement Point

Where you measure determines what you see:

```
Customer -> CDN -> Load Balancer -> Application -> Database
   | | | |
   | | | +-- DB latency only (too narrow)
   | | +-- Server processing time (missing network)
   | +-- Infrastructure latency (good proxy for availability)
   +-- True customer experience (ideal but hard to measure)
```

**Validation checklist:**
- Is the measurement point as close to the customer as possible?
- Does it capture failures that happen BETWEEN measurement points?
- Can a request fail without being counted? (e.g., DNS failure, TCP connection refused)
- Are there paths that bypass the measurement point? (direct API calls, WebSockets)

## Step 4: Validate Denominator Accuracy

The "total events" denominator is often wrong:

1. **Missing events**: Requests that timeout before reaching the measurement point are never counted.
2. **Inflated denominator**: Health checks, internal traffic, or monitoring probes included.
3. **Double counting**: Retried requests counted multiple times (should count user-intent once).
4. **Stale denominator**: Service receives zero traffic at night - 0/0 = undefined, not 100%.

**Questions to ask:**
- During the last outage, did the SLI correctly reflect the customer experience?
- If the service returns errors for 5 minutes, what does the SLI show?
- If the service is completely unreachable, what does the SLI show? (If it shows 100% because no requests were measured, the SLI is broken.)

## Step 5: Cross-Validate with External Signals

Compare internal SLI against external truth:
1. **Synthetic monitoring**: Do synthetic checks agree with the SLI?
2. **Customer reports**: During reported outages, did the SLI reflect impact?
3. **Status page incidents**: Does incident history align with SLI dips?
4. **Support tickets**: Correlation between SLI dips and ticket volume.

**Red flags:**
- SLI never drops below target but customers regularly report issues -> measurement gap.
- SLI shows brief dips but customers report prolonged issues -> resolution detection is wrong.
- SLI varies wildly but no customer impact -> measuring the wrong thing.

## Step 6: Validate Window and Aggregation

How the SLI is aggregated matters:

1. **Window size**: 30-day rolling window is standard. Calendar month can hide end-of-month issues.
2. **Aggregation method**: Request-based (every request is an event) vs time-based (every minute is good/bad).
3. **Time-based pitfall**: A 1-minute outage during peak traffic is worse than during low traffic, but time-based SLI treats them equally.
4. **Request-based advantage**: Naturally weights by traffic volume - busy periods matter more.

## Step 7: Produce Validation Report

For each SLI, assess:

| Aspect | Status | Finding |
|--------|--------|---------|
| Definition clarity | [PASS]/[WARN]/[FAIL] | Is it unambiguous? |
| Measurement point | [PASS]/[WARN]/[FAIL] | Close enough to customer? |
| Good event definition | [PASS]/[WARN]/[FAIL] | Captures all failure modes? |
| Denominator accuracy | [PASS]/[WARN]/[FAIL] | Includes all relevant events? |
| External correlation | [PASS]/[WARN]/[FAIL] | Matches customer experience? |
| Edge cases handled | [PASS]/[WARN]/[FAIL] | Zero traffic, partial failures? |

## Output

Produce an SLI validation report:
1. **SLI Health Summary**: Each SLI with validation status (Valid / Needs Adjustment / Broken).
2. **Measurement Gap Analysis**: Where internal SLI diverges from customer experience.
3. **Definition Issues Table**: SLI, issue found, impact on accuracy, recommended fix.
4. **Cross-Validation Results**: Comparison of SLI vs synthetic checks vs customer reports.
5. **Recommended SLI Improvements**: Specific changes to definitions, measurement points, or formulas.
6. **Implementation Checklist**: Steps to correct each identified issue.