---
name: apigateway-throttling-tuning
agent_type: "Incident RCA"
description: Use when tuning Amazon API Gateway throttling limits and usage plan quotas. It finds high 429 rates, misaligned burst and rate limits, and undersized usage plans, then recommends limit changes. Apply during performance reviews or after traffic growth causes client throttling.
version: "1.0.0"
last_updated: "2026-08-14"
---

# API Gateway Throttling Tuning

Tune API Gateway rate and burst limits and usage plan quotas so legitimate traffic is not throttled while abuse is contained.

## When to Activate
- CloudWatch 4XXError or the 429 count relative to Count is greater than 1 percent.
- Account or stage rate and burst limits are set below observed peak request rates.
- A usage plan quota is exhausted before the billing period ends per GetUsage.
- Latency spikes correlate with throttling during traffic bursts.
- A single API key consumes a disproportionate share of the shared throttle.

## Step 1: Measure Throttling
- Query CloudWatch Count and 4XXError for each stage over the last 7 days.
- Compute the 429 throttled percentage and flag anything above 1 percent.
- Identify the times of day when throttling peaks.

## Step 2: Read Current Limits
- Call GetStage and GetMethod to read throttlingRateLimit and throttlingBurstLimit at stage and method levels.
- Read account level limits and compare to peak observed request rate.
- Flag limits set below the observed 95th percentile request rate.

## Step 3: Analyze Usage Plans and Quotas
- Call GetUsagePlans and GetUsage to read quota limit, period, and consumption per API key.
- Flag keys that hit their quota before the period ends.
- Flag any single key consuming more than 50 percent of the shared throttle.

## Step 4: Model Right-Sized Limits
- Set rate limit to peak sustained rate plus a 20 percent headroom buffer.
- Set burst limit to cover the highest observed short spike.
- Recommend per-method throttles for expensive endpoints.

## Step 5: Recommend Changes and Guardrails
- Propose updated stage and method throttle values.
- Recommend usage plan quota increases for legitimate high-volume keys.
- Recommend a WAF rate-based rule for abusive clients rather than lowering the shared throttle.

## Output
Produce a titled "API Gateway Throttling Tuning Report" listing stages with 429 rate above 1 percent, current versus recommended rate and burst limits, and usage plans hitting quota early. Include a prioritized remediation list: raise limits for stages throttling legitimate traffic first, right-size usage plan quotas for high-volume keys second, then add per-method throttles and WAF rate rules for abusive clients.