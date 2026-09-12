---
name: metric-correlation-investigator
agent_type: "Incident RCA"
description: Correlates metrics across services to identify root causes by finding
  timing relationships between metric changes. Use this skill during incident
  investigation when multiple metrics are degraded and the team needs to identify
  which change came first (the root cause) vs which are symptoms of the cascade.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Metric Correlation Investigator

Use this skill to correlate metric changes across services and time to
distinguish root causes from cascading effects during investigations.

## When to Activate

- Multiple alarms firing across different services simultaneously.
- Incident under investigation with unclear root cause.
- Performance degradation with multiple potential contributing factors.
- Post-incident analysis: reconstructing the cascade sequence.
- Proactive investigation: correlating a change with downstream effects.

## Step 1: Establish the Timeline

Define the investigation window:
1. **Incident start**: When was the first anomaly detected? (earliest alarm, log error, or metric deviation)
2. **Window**: Expand to 30 minutes before the earliest signal (to catch the trigger).
3. **Resolution** (if resolved): When did metrics return to normal?
4. **Granularity**: Use 1-minute or 30-second resolution for accurate correlation.

## Step 2: Collect Metrics Across Services

For each service in the blast radius, retrieve simultaneously:

**Request path metrics:**
- Inbound request rate and error rate per service
- Response latency (p50, p95, p99)
- HTTP status code distribution (2xx, 4xx, 5xx)

**Resource metrics:**
- CPU utilization
- Memory utilization
- Network I/O (in/out bytes)
- Disk I/O (IOPS, throughput)

**Dependency metrics:**
- Connection pool utilization
- Database query latency
- Cache hit/miss rate
- Queue depth and processing latency

**Infrastructure metrics:**
- ALB healthy/unhealthy host count
- Auto Scaling group size changes
- ECS task count (running, pending, stopped)

## Step 3: Identify the Leading Indicator

Find which metric changed FIRST:

1. Align all metrics on the same time axis.
2. For each metric, identify the first deviation from baseline:
   - When did it first exceed mean + 2 standard deviations?
   - Use the earliest deviation as a candidate root cause signal.
3. Order all deviations chronologically.
4. The first metric to deviate is likely closest to the root cause.

**Common patterns:**

| First Signal | Likely Root Cause |
|-------------|------------------|
| Database latency spikes first | Database issue (slow queries, connection exhaustion) |
| One service errors first, then its callers | That service is the source |
| CPU spikes first | Resource exhaustion (traffic spike, bug, runaway process) |
| Network latency spikes first | Network issue (congestion, packet loss) |
| All services simultaneously | Shared dependency or infrastructure (DNS, IAM, networking) |
| Deployment event, then errors | Deployment-caused regression |

## Step 4: Map the Cascade

Once the leading indicator is identified, trace the propagation:

1. **T+0**: Root cause signal (first metric deviation).
2. **T+N seconds**: Direct dependents start showing errors (retry pressure).
3. **T+M seconds**: Indirect dependents degrade (cascade through dependency chain).
4. **T+X minutes**: Resource exhaustion in callers (thread pool, connection pool full from timeouts).

Build a timeline:
```
T+0s: RDS WriteLatency spikes to 500ms (root cause)
T+15s: payment-service latency increases (waiting on DB)
T+30s: payment-service errors start (timeouts on DB calls)
T+45s: order-service errors start (payment-service dependency failing)
T+60s: API Gateway 5xx spike (customer-visible impact begins)
T+90s: CloudWatch alarm fires
```

## Step 5: Validate with Supporting Evidence

Confirm the correlation isn't coincidental:

1. **Causal logic**: Does the dependency chain support this causation? (A calls B, B's failure should impact A)
2. **Timing consistency**: Is the lag between cause and effect consistent with timeout/retry configuration?
3. **Magnitude consistency**: Does the error volume upstream match the capacity lost downstream?
4. **Previous incidents**: Has this same cascade pattern occurred before?
5. **Counter-evidence**: Are there metrics that contradict this hypothesis?

## Step 6: Rule Out Red Herrings

Common misleading correlations:
- **Coincidental timing**: Two unrelated issues happening to start close together.
- **Symptom loops**: Service A fails -> Service B fails -> B's failure makes A worse (feedback loop). The first failure is the root cause.
- **Delayed detection**: The alarm fired now, but the issue actually started earlier (check metric history before the alarm time).
- **Aggregate metrics hiding specifics**: Average looks fine, but one AZ/instance is failing.

## Step 7: Summarize Findings

Present a clear causal chain:

```
Root Cause: [Component] experienced [failure mode]
Evidence: [Metric] deviated at [timestamp] - first signal by [X seconds]

Cascade:
1. [Component A] -> [Component B]: [mechanism] (latency: Xs)
2. [Component B] -> [Component C]: [mechanism] (latency: Xs)
...

Contributing Factors:
- [Missing circuit breaker on path X]
- [Aggressive retry configuration amplified load]
- [Timeout too high, caused thread pool exhaustion]
```

## Output

Produce a correlation analysis:
1. **Cascade Timeline**: Visual timeline showing metric deviations in chronological order with annotations.
2. **Root Cause Identification**: First deviating metric/service with supporting evidence.
3. **Correlation Table**: Metric pairs, time offset between deviations, causal relationship (cause/effect/unrelated).
4. **Dependency Impact Chart**: Topology showing the propagation path with timing.
5. **Contributing Factors**: Architecture or configuration issues that enabled the cascade.
6. **Recommendations**: Changes to break the cascade chain (circuit breakers, timeouts, isolation).