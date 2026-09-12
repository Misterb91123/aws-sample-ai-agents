---
name: load-test-results-analyzer
agent_type: "Generic"
description: Analyzes load test results to identify performance bottlenecks,
  determine system breaking points, and validate capacity readiness. Use this
  skill when interpreting results from load testing tools (k6, Locust, JMeter,
  Artillery), determining if a service can handle expected traffic, or when
  performance regressions are detected between test runs.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Load Test Results Analyzer

Use this skill to interpret load test results, identify bottlenecks, and
make capacity and performance recommendations.

## When to Activate

- Load test completed and results need interpretation.
- Comparing load test results before and after a change (regression detection).
- Validating service readiness for an upcoming traffic event.
- Determining the breaking point and maximum safe operating capacity.
- Post-incident: validating the fix under load.

## Step 1: Gather Test Context

Before analyzing results, understand the test:

1. **Test type**: What kind of load test was run?
   - Smoke test (minimal load, validate functionality)
   - Load test (expected production traffic)
   - Stress test (beyond expected, find breaking point)
   - Soak test (sustained load over long period, find leaks)
   - Spike test (sudden traffic increase)

2. **Test parameters**:
   - Virtual users / concurrent connections (ramp pattern)
   - Duration of the test
   - Target endpoint(s) and request mix
   - Think time and pacing between requests
   - Test data variety (single user vs diverse)

3. **Environment**:
   - Target environment (production-like? scaled down?)
   - Auto-scaling enabled? Fixed capacity?
   - Database seeded with production-scale data?
   - CDN/cache warmed or cold?

## Step 2: Analyze Response Time Distribution

Evaluate latency across the test:

| Metric | What It Tells You |
|--------|-------------------|
| p50 (median) | Typical user experience |
| p95 | Worst case for most users |
| p99 | Worst case (tail latency) |
| Max | Extreme outliers (often timeout) |
| Standard deviation | Consistency of response times |

**Red flags:**
- p99 > 5x p50: High variance, likely resource contention at load.
- p50 increasing over time: Gradual degradation (memory leak, connection exhaustion, GC pressure).
- p99 spikes correlating with specific concurrency level: Found the saturation point.
- Bimodal distribution (two clusters of response times): Some requests hit cache, others don't.

## Step 3: Analyze Throughput

Evaluate system capacity:

1. **Peak throughput achieved**: Maximum requests/second sustained for > 1 minute.
2. **Throughput ceiling**: Did throughput plateau while VUs continued increasing?
   - If yes: system is saturated at that throughput.
   - If no: test may not have pushed hard enough.
3. **Throughput degradation**: Did throughput decrease at high concurrency?
   - Indicates resource exhaustion or queuing.
4. **Throughput vs latency curve**: Plot both. Ideal is flat latency until a knee point, then rapid increase.

**The knee point** is your safe operating capacity: the concurrency level where latency starts increasing non-linearly. Operate below this.

## Step 4: Analyze Error Rates

Categorize errors during the test:

| Error Type | Likely Cause |
|-----------|--------------|
| HTTP 429 (Too Many Requests) | Rate limiting triggered - expected behavior |
| HTTP 503 (Service Unavailable) | Server overloaded, upstream circuit breaker |
| HTTP 502 (Bad Gateway) | Backend crashed or unresponsive |
| Connection refused | All connections in use, no capacity for new |
| Timeout | Request took too long, client gave up |
| Connection reset | Server crashed mid-request |

**Acceptable error rate**: < 0.1% during expected load, < 1% during stress test.
**Breaking point**: Error rate where the system becomes unusable (typically > 5%).

## Step 5: Correlate with Infrastructure Metrics

Map performance results to resource utilization:

1. **CPU**: Did it hit 80%+ on any component? (saturation point)
2. **Memory**: Increasing trend? (leak). Hitting limits? (OOM risk)
3. **Network**: Bandwidth maxed on any instance?
4. **Disk I/O**: IOPS maxed? High queue depth?
5. **Connection pools**: Database connections exhausted?
6. **Thread pools**: Application threads all busy (thread starvation)?
7. **Queue depth**: Messages backing up in SQS/internal queues?

**The first resource to saturate is your bottleneck.** Performance cannot improve until that bottleneck is resolved.

## Step 6: Identify the Bottleneck

Common bottleneck patterns:

| Symptom | Bottleneck | Solution |
|---------|-----------|----------|
| CPU 100% on app server, DB is fine | Compute-bound application | Optimize code, add instances, or bigger instance |
| DB CPU 100%, app CPU low | Database queries inefficient or too many | Query optimization, read replicas, caching |
| App threads all waiting, CPU low | I/O bound (waiting on DB or external call) | Connection pooling, async processing, caching |
| Memory growing throughout test | Memory leak | Fix leak, add memory as temporary measure |
| Errors start at specific concurrency | Connection pool exhausted | Increase pool size, or reduce connection hold time |
| Latency spikes every few minutes | Garbage collection (JVM, .NET) | Tune GC, reduce object allocation, increase heap |
| Throughput constant despite more VUs | Single-threaded bottleneck or lock contention | Identify the lock, redesign for concurrency |

## Step 7: Compare Against Previous Results

If historical results exist:

1. **Regression detection**: Is p95 latency > 10% worse than previous run at same load?
2. **Capacity change**: Has maximum throughput decreased?
3. **Efficiency change**: Same throughput but requiring more resources?
4. **Error threshold shift**: Errors appearing at lower concurrency than before?

Any regression should be correlated with recent changes (deployments, config changes, data growth).

## Step 8: Generate Recommendations

Based on analysis:

**Capacity recommendations:**
- Maximum safe operating concurrency: [knee point x 0.8]
- Current production traffic headroom: [max capacity / current peak traffic]
- Scale-out trigger: Add capacity at [X% of knee point concurrency]

**Performance fixes (prioritized by impact):**
1. [Bottleneck #1]: Description, expected improvement if fixed.
2. [Bottleneck #2]: Description, expected improvement if fixed.
3. [Optimization opportunity]: Low-effort improvement available.

## Output

Produce a load test analysis:
1. **Summary**: Test type, peak VUs, peak throughput, p95 latency, error rate, verdict (PASS/FAIL/MARGINAL).
2. **Latency Distribution Table**: p50, p75, p90, p95, p99, max - with pass/fail against SLO.
3. **Throughput vs Latency Chart**: Line chart showing the knee point.
4. **Error Analysis Table**: Error type, count, percentage, first occurrence (at what concurrency).
5. **Bottleneck Identification**: Primary bottleneck with evidence and fix recommendation.
6. **Capacity Assessment**: Safe operating limit, current headroom, scaling recommendations.
7. **Comparison to Previous Run** (if available): Regression/improvement with delta percentages.