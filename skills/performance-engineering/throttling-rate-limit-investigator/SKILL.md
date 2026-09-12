---
name: throttling-rate-limit-investigator
agent_type: "Incident RCA"
description: Investigates throttling and rate limiting issues across AWS services
  and application APIs. Use this skill when requests are being throttled (429 errors),
  AWS API calls are hitting rate limits, or when diagnosing why capacity exists
  but requests are being rejected due to rate/concurrency limits.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Throttling & Rate Limit Investigator

Use this skill to diagnose and resolve throttling issues across AWS services
and application-level rate limiting.

## When to Activate

- HTTP 429 (Too Many Requests) errors appearing in application or AWS API calls.
- AWS SDK retry metrics show throttling.
- Lambda functions being throttled (ConcurrentExecutions at limit).
- DynamoDB returning ProvisionedThroughputExceededException.
- API Gateway returning 429 to clients.
- Application performance degraded due to upstream throttling.

## Step 1: Identify the Throttling Source

Determine what is being throttled:

### AWS Service API Throttling
- **CloudTrail indicator**: Events with `errorCode: Throttling` or `TooManyRequestsException`.
- **Common throttled APIs**: EC2 Describe*, S3 PUT/GET, CloudWatch PutMetricData, SSM GetParameter.
- **Service-specific limits**: Each AWS service has per-account API rate limits.

### AWS Resource Throttling
- **DynamoDB**: ProvisionedThroughputExceededException (RCU/WCU exceeded).
- **Lambda**: Throttled invocations (ConcurrentExecutions at limit).
- **Kinesis**: WriteProvisionedThroughputExceeded (shard write limit).
- **SQS**: ReceiveMessage rate limit or SendMessage rate limit per queue.
- **SNS**: PublishMessageRate limit.

### Application-Level Rate Limiting
- **API Gateway**: Account or stage-level throttle, per-method throttle, usage plan limits.
- **WAF**: Rate-based rules blocking high-frequency callers.
- **Application code**: Custom rate limiters (token bucket, sliding window).

### Third-Party API Throttling
- External APIs returning 429 or Retry-After headers.
- Payment gateways, SaaS integrations, partner APIs.

## Step 2: Quantify the Throttling

Measure the scope and impact:

1. **Throttle rate**: What percentage of requests are being throttled?
   - < 1%: Mild, likely burst patterns. Retries usually handle it.
   - 1-5%: Moderate, causing noticeable latency from retries.
   - > 5%: Severe, requests failing even after retries.

2. **Pattern**:
   - Constant throttling (sustained over-limit traffic).
   - Burst throttling (short spikes exceed burst quota).
   - Periodic (every hour/day at specific times - correlate with cron jobs).
   - After deployment (new code makes more API calls).

3. **Retry behavior**:
   - Are SDK retries handling the throttling transparently?
   - Are retries amplifying the problem (retry storm)?
   - Is exponential backoff configured with jitter?

## Step 3: AWS Service-Specific Investigation

### DynamoDB Throttling
1. Check: ProvisionedReadCapacityUnits and ProvisionedWriteCapacityUnits metrics.
2. Check: ConsumedReadCapacityUnits / ConsumedWriteCapacityUnits vs provisioned.
3. Hot partition detection: Is one partition key receiving disproportionate traffic?
4. Burst capacity: DynamoDB provides 300 seconds of unused capacity as burst - is burst exhausted?
5. **Fix options**: Increase provisioned capacity, switch to on-demand, redesign partition key, add DAX cache.

### Lambda Throttling
1. Check: ConcurrentExecutions metric vs account/function reserved limit.
2. Check: Throttles metric (count of throttled invocations).
3. Is it account-level (1000 default) or function reserved concurrency limit?
4. Are other functions in the account consuming the concurrency pool?
5. **Fix options**: Request limit increase, set reserved concurrency, optimize function duration (frees up concurrency faster).

### API Gateway Throttling
1. Check account-level limit: 10,000 req/s (default, can be increased).
2. Check stage-level throttle settings.
3. Check usage plan limits (per API key).
4. Check per-method throttle overrides.
5. **Fix options**: Request account limit increase, adjust stage limits, optimize usage plans, add caching.

### Kinesis Throttling
1. Check: WriteProvisionedThroughputExceeded per shard.
2. Check: ReadProvisionedThroughputExceeded (5 reads/sec per shard).
3. Are records distributed evenly across shards? (partition key design)
4. **Fix options**: Add shards (reshard), better partition key distribution, batch records.

### EC2/General AWS API Throttling
1. Check: API call volume in CloudTrail.
2. Identify the specific API being throttled.
3. Check if multiple automation scripts are hitting the same API.
4. **Fix options**: Implement caching of describe results, reduce polling frequency, use EventBridge for state changes instead of polling, request limit increase.

## Step 4: Analyze Client Behavior

Is the client contributing to throttling?

| Problem | Symptom | Solution |
|---------|---------|----------|
| No exponential backoff | Retries at fixed rate hammer the service | Implement exponential backoff with jitter |
| Retry amplification | Cascade of retries from multiple layers | Limit total retries, add circuit breaker |
| Polling too aggressively | Describe calls every second | Use longer intervals, switch to event-driven |
| Missing caching | Same data fetched from API every request | Cache API responses locally |
| Bulk operations serialized | 1000 sequential API calls | Batch APIs where available, parallelize with rate control |
| Multiple scripts/services same limit | Different automation competing for same quota | Coordinate, implement shared rate limiter |

## Step 5: Design Rate Limit Mitigation

Based on findings, implement mitigations:

**Immediate (reduce throttling now):**
- Add/fix exponential backoff with jitter in client code.
- Cache AWS API responses that are called repeatedly.
- Stagger cron jobs (don't run all at :00 of the hour).
- Reduce polling frequency.

**Short-term (prevent recurrence):**
- Request service limit increases via Service Quotas.
- Implement token-bucket rate limiter in client.
- Switch from polling to event-driven (EventBridge).
- Add circuit breakers to prevent retry storms.

**Architecture-level:**
- Implement request queuing with controlled drain rate.
- Use SQS as a buffer between producers and rate-limited consumers.
- Implement API Gateway caching to reduce backend calls.
- Federate across multiple accounts for higher aggregate limits.

## Step 6: Monitor After Resolution

Set up monitoring to catch future throttling:

1. CloudWatch alarm on DynamoDB ThrottledRequests > 0.
2. CloudWatch alarm on Lambda Throttles > 0.
3. Custom metric for application-level 429s received from dependencies.
4. Dashboard showing API call volumes vs known limits.
5. Cost anomaly detection (throttling often corresponds with retries increasing costs).

## Output

Produce a throttling investigation report:
1. **Throttling Summary**: Source, affected service, throttle rate, duration, customer impact.
2. **Root Cause**: What is being throttled and why (limit hit, hot partition, burst exhaustion).
3. **Current Limits Table**: Service, current limit, current usage, headroom, limit type (soft/hard).
4. **Client Behavior Assessment**: Retry configuration, caching, polling patterns - issues found.
5. **Mitigation Recommendations**: Immediate fixes + long-term architecture changes.
6. **Limit Increase Requests**: Which Service Quotas to request increases for (with justification).
7. **Monitoring Setup**: Alarms and dashboards to detect future throttling early.