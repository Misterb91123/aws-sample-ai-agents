---
name: caching-strategy-advisor
agent_type: "Generic"
description: Designs and optimizes caching strategies for AWS applications by
  analyzing access patterns, cache hit rates, and invalidation needs. Use this
  skill when evaluating whether to add caching, troubleshooting low cache hit
  rates, choosing between caching solutions (ElastiCache, CloudFront, DAX,
  API Gateway caching), or designing cache invalidation strategies.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Caching Strategy Advisor

Use this skill to design, optimize, and troubleshoot caching strategies
for AWS applications.

## When to Activate

- Application has latency issues that caching could solve.
- Existing cache has low hit rate and needs optimization.
- Database is overloaded and reads need offloading.
- Evaluating which caching solution to use (ElastiCache, CloudFront, DAX, local).
- Cache inconsistency issues causing stale data bugs.
- Cost optimization: reducing repeated API calls or database queries.

## Step 1: Analyze Access Patterns

Characterize the data access to determine cacheability:

| Factor | High Cacheability | Low Cacheability |
|--------|-------------------|------------------|
| Read/write ratio | 90%+ reads | Write-heavy (< 50% reads) |
| Data freshness requirement | Stale for seconds/minutes OK | Must always be latest |
| Access distribution | Hot keys (few items accessed often) | Uniform (all items equally) |
| Data size | Small per-item (< 1MB) | Large per-item (> 10MB) |
| Computation cost | Expensive to generate (complex query, aggregation) | Cheap to recompute |
| Request volume | High (thousands per minute) | Low (< 10 per minute) |

**Cache value formula**:
Cache value = (requests/sec) x (origin latency - cache latency) x (1 - miss rate)

## Step 2: Select Cache Layer

Choose the appropriate caching layer:

### Browser/Client Cache
- **Use for**: Static assets, API responses that don't change per-user.
- **Mechanism**: HTTP Cache-Control headers (max-age, s-maxage, stale-while-revalidate).
- **Invalidation**: Time-based (TTL) or versioned URLs (cache busting).
- **Cost**: Zero (uses client resources).

### CDN Cache (CloudFront)
- **Use for**: Static content, API responses, media files.
- **Mechanism**: CloudFront cache behaviors with TTL policies.
- **Invalidation**: Invalidation requests, versioned paths, TTL.
- **Benefit**: Geographic distribution, reduces origin load.

### API Gateway Cache
- **Use for**: REST API responses that are same for all callers.
- **Mechanism**: Per-stage cache with configurable TTL (0.5-3600 seconds).
- **Invalidation**: TTL-based, manual flush, Cache-Control headers.
- **Limitation**: Request-level only, shared across all clients for same parameters.

### Application Cache (ElastiCache Redis/Valkey)
- **Use for**: Database query results, session data, computed values, rate limiting.
- **Mechanism**: Application code reads/writes to Redis.
- **Invalidation**: TTL, explicit delete on write, pub/sub for distributed invalidation.
- **Benefit**: Sub-millisecond access, rich data structures.

### Database Cache (DAX for DynamoDB)
- **Use for**: DynamoDB read-heavy workloads.
- **Mechanism**: Transparent drop-in cache in front of DynamoDB.
- **Invalidation**: Write-through (automatic on writes) + TTL.
- **Benefit**: No application code changes needed.

### Local In-Process Cache
- **Use for**: Extremely hot data accessed per-request (config, feature flags).
- **Mechanism**: In-memory hashmap refreshed on interval.
- **Invalidation**: Time-based refresh (every 30s-5min).
- **Limitation**: Not shared across instances, stale between refresh intervals.

## Step 3: Design Cache Key Strategy

Effective cache keys determine hit rate:

**Principles:**
1. Key should uniquely identify the cached data.
2. Include all request parameters that affect the response.
3. Exclude parameters that don't affect the response (request ID, timestamp).
4. Keep keys short (memory efficient, fast lookup).

**Common patterns:**
```
# Database query cache
cache_key = f"users:{user_id}:profile"

# API response cache
cache_key = f"api:v2:products:{category}:page:{page}:sort:{sort}"

# Computed result cache
cache_key = f"reports:daily:{date}:{account_id}"

# Session cache
cache_key = f"session:{session_token}"
```

**Cache key pitfalls:**
- Including timestamps in keys -> every request is a miss.
- Not including all varying parameters -> serving wrong data.
- Keys too broad -> low hit rate (too specific to match).
- Keys too narrow -> stale data served to wrong user.

## Step 4: Design Invalidation Strategy

Choose based on consistency requirements:

| Strategy | Consistency | Complexity | Use Case |
|----------|------------|-----------|----------|
| TTL-only | Eventually consistent (TTL delay) | Low | Read-heavy, stale data is acceptable |
| Write-through | Strong (writes update cache) | Medium | Critical data that must be fresh |
| Write-behind (write-back) | Eventually consistent | High | High-write volume, can tolerate brief staleness |
| Cache-aside (lazy) | Eventually consistent (first miss) | Low | Most common pattern, simple implementation |
| Event-driven invalidation | Near real-time | Medium-High | Multi-service, DynamoDB streams or SNS triggers |

**Recommended patterns:**
- Default: Cache-aside with TTL (simplest, works for most cases).
- For critical data: Write-through (update cache on every write).
- For multi-service: Event-driven (SNS/EventBridge notifies when source data changes).

## Step 5: Diagnose Low Hit Rate

If existing cache has poor hit rate:

1. **Cache is too small**: Evictions happening before items are re-requested.
   - Check: ElastiCache `Evictions` metric > 0.
   - Fix: Increase cache size or reduce data cached.

2. **TTL too short**: Items expire before being re-requested.
   - Check: High miss rate with zero evictions (items timing out).
   - Fix: Increase TTL (if data freshness allows).

3. **Key cardinality too high**: Too many unique keys, few repeated.
   - Check: Large number of keys with low access count per key.
   - Fix: Generalize keys (cache at a higher level of granularity).

4. **Cache warming missing**: Empty cache after restart serves all misses.
   - Fix: Pre-warm cache on startup from database or previous snapshot.

5. **Thundering herd**: Many requests for same expired key simultaneously.
   - Fix: Stale-while-revalidate pattern, distributed locks on cache fill.

## Step 6: Estimate Cache Sizing

Calculate required cache capacity:

1. **Working set size**: Number of unique items accessed in a typical TTL period x item size.
2. **Memory requirement**: Working set size x 1.3 (overhead for Redis data structures).
3. **Node selection**: Choose ElastiCache node type that fits the memory requirement.
4. **Replica strategy**: Add replicas for read scaling and HA (failover).

**Cost calculation:**
- Monthly cache cost (node hours).
- Compare to: reduced RDS costs (smaller instance possible) + improved latency value.

## Output

Produce a caching strategy report:
1. **Access Pattern Summary**: Read/write ratio, request volume, latency requirements, data freshness needs.
2. **Recommended Cache Layers**: Which cache types to implement with justification.
3. **Cache Key Design**: Proposed key patterns for top access patterns.
4. **Invalidation Strategy**: Selected approach per data type with consistency trade-offs.
5. **Sizing Recommendation**: Cache node type, size, replicas, estimated cost.
6. **Hit Rate Projections**: Expected hit rate and latency improvement.
7. **Implementation Priority**: Ordered list of caching to add, highest impact first.