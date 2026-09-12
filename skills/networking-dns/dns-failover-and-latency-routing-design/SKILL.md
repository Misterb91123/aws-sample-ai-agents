---
name: dns-failover-and-latency-routing-design
agent_type: "Generic"
description: Use this skill when designing or validating Amazon Route 53 routing policies for resilience and performance, including failover, latency-based, geolocation, and multivalue answer routing. It triggers on requests to build DNS-level high availability, reduce user latency by region, configure health checks, or diagnose why failover or latency routing is not behaving as expected.
version: "1.0.0"
last_updated: "2026-08-14"
---

# DNS Failover and Latency Routing Design

This skill designs and validates Amazon Route 53 routing policies that keep applications reachable and fast during regional failures. It covers health check configuration, failover records, latency and geolocation routing, TTL tuning, and multivalue answer routing.

## When to Activate

- A team needs DNS-level failover between a primary region and a standby region.
- Users in different geographies should be routed to the nearest healthy endpoint.
- Route 53 failover is not switching to the secondary, or latency routing sends users to the wrong region.
- Health checks are flapping or reporting an endpoint unhealthy when it is serving.
- A design review requires validating TTLs, record types, and failover behavior.

## Step 1: Design health checks

- Choose the health check type: endpoint (HTTP, HTTPS, or TCP against an IP or domain), calculated (combine child checks), or CloudWatch alarm based (drive health from a metric).
- Configure request interval and failure threshold. Standard checks use a 30-second interval; fast checks use 10 seconds. Route 53 uses a default failure threshold of 3 consecutive failures, so a fast check detects failure in roughly 30 seconds and a standard check in roughly 90 seconds.
- For HTTPS checks, enable string matching on a lightweight health endpoint that reflects real dependency health rather than a static 200 page, so a degraded backend is detected.
- Health checkers query from multiple global locations; an endpoint is considered unhealthy only when more than 18 percent of checkers report failure, which avoids single-region false alarms.

## Step 2: Configure failover routing

- Create a primary failover record associated with a health check and a secondary failover record (which may point to a static site, another region, or an S3 or CloudFront origin).
- Route 53 returns the primary while its health check is healthy and returns the secondary when the primary is unhealthy. Confirm the secondary is either always healthy or has its own health check.
- For active-active designs, use weighted or latency records with health checks on each so an unhealthy endpoint is simply omitted from answers.

## Step 3: Design latency and geolocation routing

- Latency-based routing directs each resolver to the region with the lowest measured network latency to that resolver, not necessarily the geographically closest. Create one latency record per region with the region attribute set.
- Geolocation routing directs by the user's location (continent, country, or subdivision). Always configure a default (no-location) record to answer queries that do not match any location; without it, unmatched queries receive no answer.
- Do not mix incompatible policies on the same name. Combine health checks with latency records so an unhealthy region is excluded and the resolver falls back to the next lowest-latency healthy region.

## Step 4: Tune TTL

- Set TTL to balance failover speed against query volume and cost. A lower TTL (for example 60 seconds) makes clients revalidate sooner and speeds observed failover, at the cost of more queries.
- For records fronting failover, use 30 to 60 seconds. For stable records that rarely change, use 300 seconds or higher to reduce query cost.
- Remember that failover speed at the client is bounded by both the health check detection time and the TTL, plus resolver and client caching that may ignore low TTLs.

## Step 5: Configure multivalue answer routing

- Multivalue answer routing returns up to 8 healthy records in response to a query, each optionally associated with a health check, giving simple client-side load spreading with health awareness.
- Use it when you want DNS to return several healthy IPs and let clients pick, without a load balancer. Confirm each value has a health check so unhealthy IPs are omitted.

## Step 6: Validate propagation and behavior

- Validate resolution from multiple regions (using resolvers in different geographies) to confirm latency and geolocation routing returns the expected endpoint per location.
- Test failover by marking the primary health check unhealthy (or failing the endpoint) and confirm the secondary is returned within the expected detection-plus-TTL window.
- Account for negative caching and client caching; observed switch time can exceed the configured TTL depending on the resolver.

## Output

Produce a DNS Routing Design document containing: the health check configuration per endpoint (type, interval, threshold, expected detection time), the record set layout for failover and latency or geolocation with the default record noted, TTL recommendations per record with the rationale, multivalue answer configuration where applicable, and a validation plan with the expected end-to-end failover time. Include any findings where the current configuration would not fail over as intended and the specific record or health check to change.