---
name: api-gateway-troubleshooting
agent_type: "Incident RCA"
description: Provides investigation procedures for API Gateway issues including
  5xx errors, high latency, throttling, authorization failures, and CORS problems.
  Use this skill when API Gateway returns errors to clients, latency spikes from
  the API layer, or when APIs are being throttled unexpectedly.
version: "1.0.0"
last_updated: "2026-08-14"
---

# API Gateway Troubleshooting

Use this skill to diagnose and resolve API Gateway issues affecting
client requests.

## When to Activate

- API returning 5xx errors to clients.
- API latency exceeds SLO targets.
- Clients receiving 429 throttle responses.
- Authorization/authentication failures.
- CORS errors reported by frontend applications.
- WebSocket connections dropping.

## Step 1: Classify the Error

| Status Code | Origin | Investigation |
|-------------|--------|--------------|
| 401 | API Gateway | Authorizer rejecting the request (bad token, expired) |
| 403 | API Gateway | IAM auth failed, resource policy denied, WAF blocked |
| 404 | API Gateway | Route not found (wrong path, wrong stage) |
| 429 | API Gateway | Throttle limit exceeded (account, stage, or usage plan) |
| 500 | API Gateway | Internal error (misconfigured integration, mapping template error) |
| 502 | Backend | Backend returned invalid response or connection failed |
| 503 | Backend | Backend overloaded or unhealthy |
| 504 | Backend | Backend timed out (exceeded integration timeout) |

## Step 2: Diagnose 5xx Errors

**502 Bad Gateway:**
1. Backend (Lambda/ECS/HTTP) returned a non-HTTP-compliant response.
2. Lambda: function error (check CloudWatch Logs for the Lambda function).
3. HTTP integration: target returned malformed response or connection reset.
4. VPC link: backend is unreachable from API Gateway's VPC link.
5. Fix: Check backend logs, ensure proper JSON response format.

**503 Service Unavailable:**
1. Backend is overwhelmed (all connections busy).
2. Lambda throttled (concurrent execution limit reached).
3. Integration endpoint returning 503.
4. Fix: Scale backend, increase Lambda concurrency, add caching.

**504 Timeout:**
1. Backend processing exceeds API Gateway timeout.
   - REST API: max 29 seconds (hard limit).
   - HTTP API: max 30 seconds.
2. Backend might be waiting on a downstream dependency.
3. Fix: Optimize backend, increase timeout (up to limit), or go async (return 202 + poll/webhook).

## Step 3: Diagnose Throttling

**Account-level throttle (10,000 req/s default):**
- All APIs in the account share this limit.
- Request a limit increase via Service Quotas.

**Stage-level throttle:**
- Configured per stage (default: account limit).
- Check stage settings: method-level overrides may be lower.

**Usage plan throttle:**
- API keys associated with usage plans have their own limits.
- Check which usage plan the client's API key belongs to.
- Check burst vs rate limit (burst handles spikes, rate is sustained).

**Lambda concurrency throttle:**
- Lambda backend hits its concurrency limit -> API Gateway returns 502 or 429.
- Solution: increase reserved/unreserved concurrency or add provisioned concurrency.

## Step 4: Diagnose Authorization Issues

**401 Unauthorized:**
1. Cognito/JWT authorizer: token expired, wrong audience, wrong issuer.
2. Lambda authorizer: returned Deny or threw an error.
3. Missing Authorization header entirely.
4. Fix: Check token claims, verify authorizer configuration.

**403 Forbidden:**
1. IAM authorization: caller doesn't have execute-api:Invoke permission.
2. Resource policy: denying the source IP or VPC.
3. WAF rule blocking the request.
4. API key required but not provided.
5. Fix: Check IAM policy, resource policy conditions, WAF logs.

## Step 5: Diagnose CORS Issues

CORS errors come from the browser (not API Gateway directly):

1. **Missing CORS headers**: OPTIONS method not configured or not returning headers.
2. **Wrong origin**: `Access-Control-Allow-Origin` doesn't match the requesting origin.
3. **Missing method**: `Access-Control-Allow-Methods` doesn't include the request method.
4. **Credentials issue**: `Access-Control-Allow-Credentials: true` needed but not set.

**For HTTP APIs**: Enable CORS in the API configuration (automatic OPTIONS handling).
**For REST APIs**: Configure OPTIONS method with proper mock integration response headers.

## Step 6: Performance Optimization

If latency is the issue:
1. Enable caching (REST API only) for cacheable GET requests.
2. Use HTTP API instead of REST API (lower overhead, faster).
3. Deploy API in the same region as the backend.
4. Use CloudFront in front of API Gateway for edge caching.
5. Optimize Lambda cold starts (for Lambda backends).
6. Enable payload compression.

## Output

Provide:
1. Error classification (API Gateway vs backend, configuration vs runtime).
2. Root cause with evidence (logs, metrics, request/response samples).
3. Specific fix with configuration change or backend modification.
4. Prevention steps (monitoring, testing, documentation).