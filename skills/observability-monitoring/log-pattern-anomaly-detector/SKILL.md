---
name: log-pattern-anomaly-detector
agent_type: "Generic"
description: Analyzes CloudWatch Logs to detect new error patterns, unusual log
  volume changes, and emerging issues before they trigger alarms. Use this skill
  when investigating early warning signs of service degradation, performing
  proactive log analysis, or when new error patterns appear that don't match
  existing alarm definitions.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Log Pattern Anomaly Detector

Use this skill to identify novel error patterns and log anomalies that may
indicate emerging issues before they escalate to customer-facing incidents.

## When to Activate

- Proactive daily/hourly log health check.
- Post-deployment: checking for new error patterns introduced by a release.
- When metrics show early degradation but no alarm has fired.
- Investigating "something feels off" signals from on-call.
- After log volume spikes detected in CloudWatch metrics.

## Step 1: Establish Log Baselines

For each critical service, establish normal patterns:

1. **Volume baseline**: Average log events per minute/hour for the past 7 days.
2. **Error ratio baseline**: ERROR/WARN events as a percentage of total events.
3. **Known error signatures**: Existing errors that are expected and handled.
4. **Timing patterns**: Normal volume variations by hour-of-day and day-of-week.

## Step 2: Detect Volume Anomalies

Query CloudWatch Logs Insights for volume changes:

1. **Log volume spike**: > 3x normal volume in a 5-minute window.
   - Could indicate: retry storms, debug logging left on, loop errors.
2. **Log volume drop**: < 20% of normal volume.
   - Could indicate: service stopped, logging broken, upstream traffic loss.
3. **Error ratio spike**: ERROR/WARN percentage > 2x baseline.
   - Could indicate: new bug, dependency failure, configuration error.

**Query approach:**
```
stats count(*) as total,
  count_if(@message like /ERROR/) as errors,
  (count_if(@message like /ERROR/) * 100.0 / count(*)) as error_pct
by bin(5m) as time_window
| sort time_window desc
```

## Step 3: Identify New Error Patterns

Look for errors that are NEW - not present in the baseline period:

1. Extract unique error signatures (class name, error message prefix, error code).
2. Compare against the past 7-day baseline of known errors.
3. Flag any error signature appearing now that has ZERO occurrences in baseline.

**Common new error patterns to catch:**
- New exception classes not seen before.
- New HTTP status code patterns from dependencies.
- Connection refused to a new endpoint.
- Authentication/authorization failures that weren't happening before.
- Timeout errors to a specific dependency.
- Serialization/deserialization errors (data format change).

## Step 4: Analyze Error Clustering

Group related errors to understand scope:

1. **By time**: Did errors start at a specific timestamp? (correlate with deployment)
2. **By source**: Are errors coming from all instances or just one? (infrastructure vs code)
3. **By endpoint/operation**: Is one API path affected or all?
4. **By user/request attribute**: Is it affecting a segment or everyone?
5. **By dependency**: Are errors from the same downstream service?

## Step 5: Correlate with Events

Cross-reference log anomalies with potential causes:

1. **Deployments**: Any deployment within 30 minutes before the anomaly started?
2. **Config changes**: Parameter Store, feature flags, environment variable changes?
3. **Scaling events**: Did capacity change (scale-in removing healthy instances)?
4. **Dependency changes**: Did a downstream service deploy or degrade?
5. **Traffic changes**: Unusual traffic spike (campaign launch, bot activity)?
6. **Certificate/credential expiry**: Sudden auth errors after expiration time?

## Step 6: Assess Severity

Classify the anomaly:

| Severity | Criteria |
|----------|----------|
| **Critical** | New errors AND customer-facing metrics degraded |
| **Warning** | New errors but metrics stable (internal errors, not yet customer-visible) |
| **Informational** | Volume change but no new error types (traffic pattern shift) |
| **Noise** | Known intermittent errors within expected variance |

## Step 7: Extract Actionable Context

For each significant finding, extract:
1. First occurrence timestamp (when did it start?).
2. Sample log entries (2-3 representative examples).
3. Frequency and trend (growing, stable, or resolving?).
4. Affected component (which service, function, or module?).
5. Stack trace summary (if available - root exception class and location).

## Output

Produce a log anomaly report:
1. **Summary**: Services analyzed, anomalies found, severity breakdown.
2. **New Error Patterns Table**: Error signature, first seen, frequency, affected service, sample message, severity.
3. **Volume Anomalies Table**: Log group, normal volume, current volume, deviation factor, start time.
4. **Error Ratio Trend Chart**: Line chart showing error percentage over past 24 hours with anomaly markers.
5. **Correlation Findings**: Identified triggers (deployment, config change, etc.) correlated with anomaly start.
6. **Recommended Actions**: Investigation steps for each critical/warning finding.