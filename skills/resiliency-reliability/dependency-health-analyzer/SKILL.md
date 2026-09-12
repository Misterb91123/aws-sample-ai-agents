---
name: dependency-health-analyzer
agent_type: "Incident RCA"
description: Analyzes the health and reliability of service dependencies including
  databases, caches, queues, third-party APIs, and internal microservices. Use
  this skill to identify fragile dependencies, missing circuit breakers, timeout
  misconfigurations, and single points of failure in the service dependency graph.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Dependency Health Analyzer

Use this skill to assess the health, reliability, and resilience patterns
of all dependencies in your service architecture.

## When to Activate

- Service experiencing intermittent failures from a dependency.
- Investigating cascading failures across services.
- Onboarding a new service - assess its dependency risk.
- Periodic reliability review of critical paths.
- Post-incident when a dependency failure caused wider impact.

## Step 1: Map Service Dependencies

For the target service, identify all dependencies:

**Hard Dependencies (service cannot function without them):**
- Primary database (RDS, DynamoDB)
- Authentication/authorization service
- Core business logic dependencies
- Configuration service

**Soft Dependencies (service degrades but continues):**
- Caching layer (ElastiCache)
- Recommendation engines
- Analytics/logging services
- Non-critical enrichment APIs

**Async Dependencies (eventual consistency acceptable):**
- Message queues (SQS, SNS)
- Event streams (Kinesis, EventBridge)
- Batch processing systems
- Notification services

## Step 2: Assess Dependency Health Metrics

For each dependency, retrieve current health indicators:

1. **Availability:** Error rate over the past 7 days (5xx, timeouts, connection refused).
2. **Latency:** p50, p95, p99 latency - is it stable or degrading?
3. **Saturation:** Connection pool utilization, queue depth, throughput limits.
4. **Traffic Pattern:** Request rate trend - is it growing toward capacity limits?

**Red flags:**
- Error rate > 1% sustained
- Latency p99 > 5x p50 (high variance indicates instability)
- Connection pool > 80% utilized
- Queue depth growing over time (consumers can't keep up)

## Step 3: Evaluate Resilience Patterns

For each dependency, check if protective patterns are in place:

### Circuit Breakers
- Is a circuit breaker configured for this dependency?
- What are the thresholds? (error rate, latency)
- What happens when the circuit opens? (fallback, cached response, error)
- Has the circuit breaker fired recently? (indicates dependency issues)

### Timeouts
- Is a connection timeout configured? (should be < 3s for most services)
- Is a request timeout configured? (should be < dependency's p99 + buffer)
- Is the timeout aggressive enough to prevent thread pool exhaustion?
- **Anti-pattern:** No timeout = unbounded wait = thread exhaustion under load.

### Retries
- Are retries configured with exponential backoff?
- Is there a retry budget/limit? (max 2-3 retries for synchronous calls)
- Is jitter added to prevent thundering herd?
- **Anti-pattern:** Unlimited retries amplify traffic to struggling dependencies.

### Bulkheads
- Is the dependency accessed through a dedicated thread pool / connection pool?
- If the dependency is slow, can it exhaust the caller's resources?
- Are connection pools sized appropriately? (not too large to overwhelm dependency)

### Fallbacks
- What happens if the dependency is completely unavailable?
- Is there a cached response that can be served?
- Is there a degraded mode that preserves core functionality?
- Is the fallback behavior tested and documented?

## Step 4: Identify Single Points of Failure

Look for dependencies with no redundancy:

1. **Single-instance databases** - no read replicas, no Multi-AZ.
2. **Single-region dependencies** - no cross-region failover.
3. **Single-provider external APIs** - no alternate provider configured.
4. **Shared dependencies** - one service used by many (fan-in risk).
5. **Undocumented dependencies** - hidden calls discovered in traces.

## Step 5: Analyze Failure Propagation Risk

Model how each dependency failure propagates:

| Dependency | Failure Mode | Impact to Caller | Cascading Risk |
|------------|-------------|------------------|----------------|
| RDS Primary | Connection timeout | All writes fail | High - blocks transactions |
| ElastiCache | Node failure | Cache miss storm | Medium - increased DB load |
| Auth Service | High latency | All requests slow | Critical - blocks everything |
| SQS Queue | Throttling | Message backlog | Low - async, catches up |

For high cascading risk dependencies:
1. Is there a fallback or degraded mode?
2. Can the caller survive the dependency being down for 5 min? 30 min? 1 hour?
3. What monitoring exists to detect the dependency failing before callers?

## Step 6: Check Dependency SLAs

For each dependency:
1. What is its published SLA/SLO?
2. Is the caller's SLO dependent on this (SLO budget chain)?
3. If the dependency misses its SLO, does the caller also miss?
4. **Critical check:** Is the caller's SLO target higher than its dependency's SLO?
   (e.g., service targets 99.99% but depends on a 99.9% dependency - impossible without redundancy)

## Step 7: External / Third-Party Dependencies

For external APIs and SaaS dependencies:
1. What is their published uptime SLA?
2. Do we have a monitoring probe checking their health?
3. Is there a fallback if they go down? (queue and retry, alternative provider)
4. What's our traffic volume vs their rate limits?
5. Are credentials/tokens being rotated before expiry?

## Output

Produce a dependency health report:
1. **Dependency Map**: Visual or tabular view of all dependencies with health status.
2. **Health Scorecard Table**: Dependency, type (hard/soft/async), error rate, p99 latency, health status.
3. **Resilience Pattern Coverage Table**: Dependency, circuit breaker, timeout, retry, bulkhead, fallback - configured (yes/no).
4. **Single Points of Failure**: Dependencies with no redundancy or failover.
5. **Failure Propagation Risk Matrix**: Dependency, failure mode, impact scope, cascading potential.
6. **SLO Chain Analysis**: Whether dependency SLOs support the caller's SLO targets.
7. **Recommendations**: Missing resilience patterns to implement, dependencies to add redundancy for.