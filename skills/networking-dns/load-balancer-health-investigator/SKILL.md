---
name: load-balancer-health-investigator
agent_type: "Incident RCA"
description: Investigates load balancer health issues including unhealthy targets,
  5xx errors, connection timeouts, and uneven traffic distribution. Use this skill
  when ALB/NLB targets are failing health checks, when 502/503/504 errors originate
  from the load balancer, or when traffic is not distributing evenly across targets.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Load Balancer Health Investigator

Use this skill to diagnose ALB and NLB health issues, unhealthy targets,
and error patterns.

## When to Activate

- ALB/NLB HealthyHostCount drops or UnHealthyHostCount increases.
- HTTP 502, 503, or 504 errors from the load balancer.
- Target group shows targets in "unhealthy" state.
- Latency from load balancer is unexpectedly high.
- Uneven traffic distribution across targets.
- Connection draining or deregistration issues during deployments.

## Step 1: Identify the Problem Type

| Symptom | Category |
|---------|----------|
| Targets marked unhealthy | Health check failure |
| HTTP 502 Bad Gateway | Target closed connection / not responding |
| HTTP 503 Service Unavailable | No healthy targets available |
| HTTP 504 Gateway Timeout | Target did not respond within timeout |
| High latency (TargetResponseTime) | Target slow to respond |
| Uneven RequestCount across targets | Sticky sessions or imbalanced routing |
| Connection errors (ELB 5xx) | Load balancer internal issue or limit |

## Step 2: Diagnose Health Check Failures

If targets are unhealthy:

1. **Check health check configuration:**
   - Path: Does the health check URL exist and return 200? (common: `/health`, `/ping`)
   - Port: Is the health check port correct? (matches application listen port)
   - Protocol: HTTP vs HTTPS - does the target support it?
   - Matcher: Expected response code (default 200 - does the app return something else?)
   - Timeout: Is it shorter than the application's response time for the health path?
   - Interval: Time between checks.
   - Threshold: How many consecutive failures before marking unhealthy?

2. **Test the health check manually:**
   - From within the VPC: `curl -v http://<target-ip>:<port>/<health-path>`
   - Does it respond? With what status code? Within the timeout?

3. **Common health check failures:**
   | Cause | Evidence | Fix |
   |-------|----------|-----|
   | Application not started yet | Target unhealthy immediately after registration | Increase health check grace period |
   | Wrong port | Connection refused in target logs | Fix health check port configuration |
   | Application returns non-200 | 302 redirect to login, 404 not found | Fix path or change matcher codes |
   | Security group blocks health check | No traffic reaching target | Allow ALB security group inbound on health check port |
   | Application crash loop | Alternating healthy/unhealthy | Fix application stability issue |
   | Resource exhaustion | Healthy initially, then fails under load | Fix resource limits (memory, connections) |

## Step 3: Diagnose 502 Errors

HTTP 502 from ALB means the target sent an invalid response or closed the connection:

1. **Target closed connection before responding:**
   - Application crashed mid-request.
   - Application's keep-alive timeout is shorter than ALB's idle timeout.
   - **Fix:** Set application keep-alive > ALB idle timeout (default 60s).

2. **Target responded with malformed HTTP:**
   - Application sent non-HTTP response on HTTP listener.
   - Binary protocol on HTTP port.

3. **Target unreachable after being marked healthy:**
   - Race condition between health check passing and actual request failing.
   - Happens during deployments (old task draining).

## Step 4: Diagnose 504 Errors

HTTP 504 means the target didn't respond within the timeout:

1. **Check ALB idle timeout** (default 60s):
   - If application takes > 60s to respond -> 504.
   - **Fix:** Increase ALB idle timeout OR optimize the slow endpoint.

2. **Target overloaded:**
   - All threads busy, request queued beyond timeout.
   - Check target CPU, connection count, thread pool metrics.

3. **Downstream dependency slow:**
   - Target waiting on database or external API that's slow.
   - Check target's outbound connection metrics.

## Step 5: Diagnose Uneven Distribution

If traffic isn't balanced across targets:

1. **Sticky sessions enabled:**
   - Cookie-based affinity sends same user to same target.
   - One target may accumulate more long-lived sessions.
   - **Check:** Target group stickiness settings.

2. **Cross-zone load balancing:**
   - Disabled: traffic stays within AZ (imbalanced if AZs have different target counts).
   - Enabled: distributes evenly across all targets in all AZs.

3. **Least outstanding requests algorithm:**
   - Sends to target with fewest in-flight requests.
   - May appear "unfair" if targets have different processing speeds.

4. **Slow-start mode:**
   - Newly registered targets receive gradually increasing traffic.
   - May look imbalanced during scale-out events.

5. **Long-lived connections (WebSocket, gRPC):**
   - Once established, connection stays on one target.
   - New targets don't receive existing connections.
   - **Fix:** Connection draining with periodic reconnection.

## Step 6: Diagnose NLB-Specific Issues

NLB (Layer 4) has different failure modes:

1. **TCP connection timeout:**
   - NLB idle timeout is 350 seconds (fixed, not configurable).
   - If client or target has shorter keepalive -> connection reset.

2. **Target health check with TCP:**
   - NLB TCP health check only verifies port is open (SYN-ACK).
   - Application may be "up" but not "ready" (passes TCP check, fails HTTP).
   - **Fix:** Use HTTP/HTTPS health check on NLB for application-level validation.

3. **Source IP preservation:**
   - NLB preserves client source IP (unlike ALB which substitutes its own).
   - Target security groups must allow client IPs, not just NLB IPs.

4. **Cross-zone disabled by default:**
   - NLB cross-zone is disabled by default (unlike ALB).
   - Targets in AZ with less traffic are under-utilized.

## Step 7: Deployment-Related Issues

During rolling deployments:

1. **Deregistration delay:** Default 300s. Too short -> in-flight requests terminated. Too long -> slow deployments.
2. **Health check grace period:** New targets need time to start before being checked.
3. **Connection draining:** Existing connections completed before target removed.
4. **Blue/green routing:** Ensure new target group is healthy BEFORE switching.

## Output

Produce a load balancer health report:
1. **Current Status**: Healthy/unhealthy target counts, error rates, latency summary.
2. **Health Check Analysis**: Configuration review, failure reasons per target.
3. **Error Breakdown Table**: Error type (502/503/504), count, affected targets, likely cause.
4. **Traffic Distribution Analysis**: Per-target request count, showing imbalance if present.
5. **Root Cause**: Identified issue with supporting evidence.
6. **Fix Recommendation**: Configuration or application change to resolve.
7. **Monitoring Improvements**: Alarms to add for catching similar issues earlier.