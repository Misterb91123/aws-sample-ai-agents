---
name: cloudfront-cache-optimization
agent_type: "Generic"
description: Use when raising CloudFront cache hit ratio and cutting origin load. It finds low CacheHitRate distributions, unnecessary cookie and query-string forwarding, and short TTLs, then recommends cache policy changes. Apply during performance reviews or when origin costs rise.
version: "1.0.0"
last_updated: "2026-08-14"
---

# CloudFront Cache Optimization

Raise CloudFront cache hit ratio by tightening cache keys and TTLs so fewer requests reach the origin.

## When to Activate
- CloudWatch CacheHitRate for a distribution is below 85 percent.
- A cache behavior forwards all cookies or all query strings in its cache policy.
- Cache policy MinTTL or DefaultTTL is set below 60 seconds for static content.
- Origin request count is high relative to viewer requests, indicating cache misses.
- Cacheable content is served without Cache-Control or with no-cache headers.

## Step 1: Measure Cache Hit Ratio
- Query CloudWatch CacheHitRate per distribution over the last 7 days.
- Flag distributions below 85 percent as optimization targets.
- Break down by cache behavior where additional metrics are enabled.

## Step 2: Inspect Cache Key Configuration
- Call GetDistributionConfig and read the attached cache policy for each behavior.
- Identify behaviors forwarding all cookies, all headers, or all query strings.
- Flag broad forwarding as a cache-fragmentation cause.

## Step 3: Review TTLs and Origin Headers
- Read MinTTL, DefaultTTL, and MaxTTL from each cache policy.
- Flag static content behaviors with DefaultTTL below 60 seconds.
- Confirm the origin sets Cache-Control max-age for cacheable objects.

## Step 4: Separate Static From Dynamic Paths
- Map path patterns to static assets versus dynamic APIs.
- Recommend a cache policy that keys only on needed query strings and no cookies for static paths.
- Recommend an origin request policy that forwards only required values to the origin.

## Step 5: Recommend Cache Policy Changes
- Propose raising DefaultTTL to at least 86400 seconds for immutable static assets.
- Propose removing cookie forwarding on static behaviors.
- Recommend Origin Shield for high-miss origins to consolidate cache fill.

## Output
Produce a titled "CloudFront Cache Optimization Report" listing distributions with CacheHitRate below 85 percent, behaviors with broad cookie or query-string forwarding, short TTLs, and origin caching header gaps. Include a prioritized remediation list: fix broad cache-key forwarding on high-traffic behaviors first, raise TTLs and add origin Cache-Control second, then enable Origin Shield for remaining high-miss origins.