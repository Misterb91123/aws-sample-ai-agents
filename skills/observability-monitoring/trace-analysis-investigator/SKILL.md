---
name: trace-analysis-investigator
agent_type: "Incident RCA"
description: Analyzes distributed traces from AWS X-Ray to identify performance
  bottlenecks, error sources, and latency contributors across microservice
  architectures. Use this skill when investigating slow API responses, intermittent
  failures in distributed systems, or when tracing the path of a specific failed
  request through the service mesh.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Trace Analysis Investigator

Use this skill to analyze distributed traces and identify performance
bottlenecks, error propagation, and latency contributors across services.

## When to Activate

- Investigating slow API responses that span multiple services.
- Tracking a specific failed request through the service architecture.
- Identifying which service in a chain is causing latency.
- Post-deployment: checking if new code introduced latency regression.
- Capacity planning: understanding where time is spent in critical paths.

## Step 1: Define the Investigation Scope

Determine what to trace:
1. **Specific request**: Trace ID from a customer report or error log.
2. **Slow endpoint**: Traces for a specific API path with p99 latency > threshold.
3. **Error traces**: Traces that resulted in 5xx or failed operations.
4. **Time window**: Recent traces matching specific criteria.

## Step 2: Retrieve Traces from X-Ray

Query X-Ray for relevant traces:

**Filter expressions:**
- By latency: `responsetime > 5` (requests taking > 5 seconds)
- By status: `http.status = 500` (failed requests)
- By service: `service("payment-service")` (specific service involvement)
- By annotation: `annotation.user_id = "123"` (specific user/request attribute)
- By error: `fault = true` (any 5xx response in the trace)
- Combined: `service("api-gateway") AND responsetime > 3 AND fault = true`

## Step 3: Analyze Trace Structure

For each trace, decompose into segments:

```
[Client Request - 2500ms total]
+-- [API Gateway - 50ms]
+-- [Auth Lambda - 200ms]
+-- [Order Service - 2100ms] <- bottleneck
| +-- [DynamoDB GetItem - 15ms]
| +-- [Payment Service - 1800ms] <- deeper bottleneck
| | +-- [RDS Query - 1500ms] <- ROOT CAUSE
| | +-- [Stripe API - 250ms]
| +-- [Notification Service (async) - 0ms]
+-- [Response serialization - 50ms]
```

**Key analysis:**
1. **Critical path**: The longest chain of sequential segments (determines total latency).
2. **Bottleneck segment**: The single segment contributing most to total latency.
3. **Parallelization opportunities**: Sequential calls that could be made concurrent.
4. **Unnecessary calls**: Segments that could be eliminated (redundant lookups, unused data fetch).

## Step 4: Identify Performance Patterns

Look for these common issues in traces:

### N+1 Query Pattern
- Multiple sequential database calls for individual items.
- **Symptom**: Many short DB segments adding up to high total.
- **Fix**: Batch query or data loader pattern.

### Chatty Service Calls
- Many sequential calls between the same two services.
- **Symptom**: Repeated segments to same downstream.
- **Fix**: Batch API, reduce round trips.

### Missing Caching
- Same data fetched from database on every request.
- **Symptom**: Identical DB queries across multiple traces.
- **Fix**: Add caching layer (ElastiCache, local cache).

### Sequential When Parallel Is Possible
- Independent operations executed one after another.
- **Symptom**: Long trace with segments that have no data dependency.
- **Fix**: Parallelize independent operations.

### Long Tail Latency
- p50 is fast but p99 is very slow.
- **Symptom**: Most traces are short, but occasional traces are 10x+ longer.
- **Causes**: GC pauses, cold starts, connection pool exhaustion, lock contention, slow replica reads.

### Retry Amplification
- Failed requests being retried multiple times.
- **Symptom**: Trace shows 3 attempts to the same downstream service.
- **Impact**: 3x load on an already struggling service.

## Step 5: Analyze Error Traces

For traces with errors:
1. **Error origin**: Which segment threw the error first?
2. **Error type**: Timeout? Connection refused? Business logic error? Data validation?
3. **Error propagation**: How did the error cascade upstream?
4. **Error handling**: Did upstream services handle it gracefully or pass it through?
5. **Retry behavior**: Were retries attempted? How many? Did they succeed?

## Step 6: Statistical Trace Analysis

Beyond individual traces, analyze patterns across many traces:

1. **Latency distribution by segment**: Which segment has the most variance?
2. **Error rate by segment**: Which downstream service fails most often?
3. **Segment frequency**: Are some services called more often than expected?
4. **Correlation**: When segment X is slow, is segment Y also slow? (shared resource contention)

## Step 7: Generate Optimization Recommendations

Based on trace analysis:

| Finding | Impact | Recommendation | Effort |
|---------|--------|----------------|--------|
| N+1 queries to DynamoDB | +800ms latency | Implement BatchGetItem | Medium |
| Sequential auth + profile fetch | +200ms latency | Parallelize calls | Low |
| No cache on user preferences | +150ms per request | Add ElastiCache | Medium |
| Retry storm to payment API | 3x load on degraded service | Add circuit breaker | Medium |

## Output

Produce a trace analysis report:
1. **Summary**: Traces analyzed, average vs p99 latency, primary bottleneck identified.
2. **Critical Path Visualization**: Segment-by-segment breakdown of the slowest path.
3. **Bottleneck Table**: Segment, service, avg duration, contribution to total latency, optimization available.
4. **Error Trace Summary**: Error origin, type, propagation path, handling quality.
5. **Pattern Findings**: N+1 queries, missing caches, parallelization opportunities found.
6. **Latency Budget Breakdown Chart**: Where time is spent across services (waterfall or pie chart).
7. **Optimization Roadmap**: Prioritized improvements with estimated latency reduction.