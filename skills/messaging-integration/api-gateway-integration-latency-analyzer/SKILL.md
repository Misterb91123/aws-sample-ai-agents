---
name: api-gateway-integration-latency-analyzer
agent_type: "Incident RCA"
description: Analyzes Amazon API Gateway latency to separate gateway overhead
  from backend integration latency, isolating slow endpoints, Lambda cold
  starts, VPC link delays, and cache misses. Use this skill when API responses
  are slow, p99 latency is high, or specific resources and methods lag behind
  the rest of the API.
version: "1.0.0"
last_updated: "2026-08-14"
---

# API Gateway Integration Latency Analyzer

Use this skill to decompose API Gateway response time into gateway overhead and
backend integration time, locate the slow endpoint or dependency, and recommend
caching, timeout, and integration changes.

## When to Activate

- Overall API p99 or p50 Latency is high or trending up.
- Specific resources or methods respond slowly while others are fast.
- Clients report timeouts near the integration timeout limit.
- Cache hit ratio is low or the cache appears ineffective.

## Step 1: Decompose Latency Metrics

Separate gateway overhead from backend time:
1. Read the Latency metric (total time API Gateway takes to respond to the
   caller) and the IntegrationLatency metric (time the backend takes to respond
   to API Gateway).
2. Compute gateway overhead as Latency minus IntegrationLatency. This overhead
   covers mapping templates, authorization, throttling checks, and caching
   logic.
3. If IntegrationLatency dominates, the backend is slow. If gateway overhead
   dominates, focus on mapping templates, authorizers, or caching.
4. Evaluate at p50, p90, and p99 rather than average; tail latency reveals cold
   starts and intermittent backend stalls that averages hide.

## Step 2: Break Down Latency Per Resource and Method

Find the specific slow endpoint:
1. Enable detailed CloudWatch metrics for the stage so metrics are emitted per
   resource and per method (GET, POST) rather than only at the API level.
2. Compare Latency and IntegrationLatency across endpoints to isolate the one
   or two that drive the tail.
3. Enable access logging and, where deeper tracing is needed, AWS X-Ray to
   trace individual requests through the integration.

## Step 3: Investigate Lambda Integration Cold Starts

Lambda-backed integrations add cold start time:
1. High p99 IntegrationLatency with a low p50 on a Lambda integration is a
   classic cold start signature; the tail requests initialize a new execution
   environment.
2. Check the function Init Duration and the ratio of cold to warm invocations.
3. Reduce cold starts with provisioned concurrency, a smaller deployment
   package, and lighter initialization code. Cross-reference the
   lambda-cold-start-investigator skill for deeper analysis.

## Step 4: Measure VPC Link Latency

Private backends reached through a VPC link add network hops:
1. For private integrations, confirm the VPC link and the target Network Load
   Balancer or ALB are healthy.
2. Elevated IntegrationLatency with a healthy backend points to the link path:
   cross-AZ traffic, unhealthy targets increasing retries, or an
   under-provisioned load balancer.
3. Confirm backend targets are spread across the same AZs as the API to avoid
   cross-AZ round trips.

## Step 5: Evaluate Caching Effectiveness

Caching cuts both backend calls and latency when tuned correctly:
1. Enable stage caching and read CacheHitCount and CacheMissCount. Cache hit
   ratio equals CacheHitCount divided by (CacheHitCount plus CacheMissCount).
2. A low hit ratio means the cache key varies too much (unnecessary query
   strings or headers in the key) or the TTL is too short (default 300 seconds,
   range 0 to 3600 seconds).
3. Size the cache appropriately (0.5 GB up to 237 GB) and scope the cache key
   to only the parameters that affect the response.

## Step 6: Check Throttling and Burst Limits

Throttling adds latency and 429 errors under load:
1. Read the 4XXError metric for 429 responses caused by exceeding the account
   or stage rate and burst limits (default 10000 requests/s steady, 5000 burst
   at the account level).
2. Review usage plan and per-method throttle settings; a tight per-method limit
   can throttle a hot endpoint even when the account has headroom.
3. Raise limits or add usage plans as appropriate, and confirm clients
   implement backoff.

## Step 7: Reduce Mapping Template and Timeout Overhead

Request and response transformation and timeouts affect latency and failures:
1. Complex Velocity (VTL) mapping templates add gateway overhead; simplify or
   remove transformations where a proxy integration can pass through directly.
2. Confirm the integration timeout is set correctly: REST APIs allow a maximum
   integration timeout of 29 seconds; HTTP APIs allow up to 30 seconds. Backends
   slower than the timeout return 504 errors.
3. Enable backend connection reuse (keep-alive) so integrations do not pay TLS
   and TCP setup cost on every request.

## Output

Provide an analysis summary:
1. Latency decomposition: total Latency, IntegrationLatency, and computed
   gateway overhead at p50, p90, and p99.
2. The slowest resources and methods and whether the delay is gateway-side or
   backend-side.
3. Root cause: Lambda cold starts, VPC link path, cache misses, throttling,
   mapping template overhead, or an undersized timeout.
4. Specific fixes: caching key and TTL changes, provisioned concurrency,
   throttle limit adjustments, template simplification, or timeout correction.
5. Recommended CloudWatch alarms (p99 Latency threshold, IntegrationLatency
   threshold, 5XXError and 429 count) to catch recurrence early.