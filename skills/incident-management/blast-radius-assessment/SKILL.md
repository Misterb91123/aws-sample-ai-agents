---
name: blast-radius-assessment
agent_type: "Incident RCA"
description: Determines the full blast radius of an incident by mapping service
  dependencies, identifying all affected downstream systems, and quantifying
  customer impact. Use this skill when an incident is confirmed and responders
  need to understand the full scope of impact across the architecture.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Blast Radius Assessment

Use this skill when an incident has been confirmed and you need to understand
the complete scope of impact - which services, customers, and capabilities are affected.

## When to Activate

- An incident is confirmed and severity needs validation.
- Responders ask "what else is affected?"
- A core infrastructure component is impacted (database, queue, network).
- Customer reports suggest broader impact than initially detected.

## Step 1: Identify the Origin Point

Determine the source of the failure:
1. Identify the primary failing resource (EC2 instance, RDS cluster, Lambda, ECS service).
2. Determine the failure mode: is it completely unavailable, partially degraded, or intermittently failing?
3. Note the region and AZ - is this AZ-scoped or region-scoped?

## Step 2: Map Upstream Dependencies

Identify what depends on the failing component:
1. Query service topology - use service map, X-Ray traces, or resource tags to find callers.
2. Check ALB/NLB target groups - which load balancers route to this service?
3. Check API Gateway integrations - which APIs call this backend?
4. Check EventBridge rules - which event-driven workflows depend on this service?
5. Check SQS/SNS - which queues/topics does this service produce to or consume from?

## Step 3: Map Downstream Dependencies

Identify what the failing component depends on:
1. Check security group rules for outbound connections.
2. Check VPC endpoints and NAT gateways for external dependencies.
3. Check database connections (RDS, DynamoDB, ElastiCache).
4. Check secrets and parameters accessed from Secrets Manager/Parameter Store.

This helps determine if the root cause is actually downstream.

## Step 4: Assess Propagation

For each identified dependency:
1. Is the dependent service currently healthy? Check its metrics.
2. Does it have circuit breakers, retries, or fallbacks?
3. Can it tolerate the failure (graceful degradation) or will it cascade?
4. What's the timeout/retry configuration - will it exhaust resources waiting?

**Propagation Patterns:**
- **Hard dependency**: Service B cannot function without Service A -> full propagation
- **Soft dependency**: Service B degrades but continues basic operation -> partial propagation
- **Async dependency**: Service B queues work for Service A -> delayed propagation (queue backlog)
- **Cached dependency**: Service B uses cached data from Service A -> time-delayed propagation

## Step 5: Quantify Customer Impact

For each affected service in the dependency chain:
1. Is it customer-facing? (Check if it serves API endpoints, web pages, or mobile backends)
2. What percentage of traffic flows through the affected path?
3. Are there alternative paths (multi-region, failover)?
4. What customer capabilities are degraded or lost?

## Step 6: Determine Geographic and AZ Scope

1. Is the failure contained to a single AZ?
   - Check if resources are AZ-specific (single-AZ RDS, EC2 in one AZ).
   - If yes, multi-AZ services should be partially operational.
2. Is the failure region-wide?
   - Check AWS Health Dashboard for regional service issues.
   - If yes, assess cross-region failover readiness.
3. Is the failure global (IAM, Route53, CloudFront)?
   - These affect all regions simultaneously.

## Step 7: Produce Blast Radius Map

Summarize findings as:

1. **Primary failure**: The origin component and its failure mode.
2. **Directly affected services** (tier 1): Services that directly call or are called by the failing component.
3. **Indirectly affected services** (tier 2+): Services affected through the dependency chain.
4. **Customer-facing impact**: Which customer capabilities are degraded/unavailable.
5. **Unaffected services**: Explicitly note what is NOT affected (helps responders and comms).

## Output Format

Provide a topology diagram (if possible) and a summary table:

| Service | Dependency Type | Impact Level | Customer-Facing | Mitigation Available |
|---------|----------------|--------------|-----------------|---------------------|
| Example | Hard (DB) | Full outage | Yes | Failover to replica |

Include:
- Total estimated customer impact percentage
- Expected blast radius growth if not mitigated (time-based progression)
- Containment recommendations (what to isolate to prevent spread)