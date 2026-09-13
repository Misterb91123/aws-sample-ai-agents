---
name: connect-capacity-and-concurrency-planning
agent_type: "Generic"
description: Provides procedures to forecast and right-size Amazon Connect capacity
  against Service Quotas, including ConcurrentCalls versus the concurrent active calls
  quota, CallsBreachingConcurrencyQuota, phone numbers per instance, and queues,
  routing profiles, and contact flows per instance, plus seasonal and peak
  forecasting. Use this skill when planning for growth or seasonal peaks, when
  concurrency headroom is shrinking, or when deciding whether and by how much to
  request a Service Quota increase for a Connect instance.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Amazon Connect Capacity and Concurrency Planning

Use this skill to forecast Amazon Connect demand and right-size the instance
against Service Quotas. Investigation is read-only; recommendations are specific
quota targets, never blanket maximums.

## When to Activate

- Planning for a seasonal peak, launch, or expected growth.
- ConcurrentCallsPercentage regularly approaches 100 percent.
- CallsBreachingConcurrencyQuota is nonzero or trending up.
- Approaching limits on phone numbers, queues, routing profiles, or flows.
- Deciding whether to request a Service Quota increase and by how much.

## Step 1: Gather Current Quota Values

Use the Service Quotas API (service-quotas GetServiceQuota / ListServiceQuotas for
the `connect` service) plus Connect describe/list APIs:

- Concurrent active calls per instance.
- Phone numbers per instance (ListPhoneNumbersV2 for current count).
- Queues per instance (ListQueues), routing profiles per instance
  (ListRoutingProfiles), contact flows per instance (ListContactFlows).
- Users/agents and security profiles as needed (ListSecurityProfiles).

Record each quota's current value and the currently consumed count.

## Step 2: Gather Observed Peaks

Use GetMetricDataV2 over a representative window (at least the last 4-8 weeks, or
the last comparable season):

- `ConcurrentCalls` with the Maximum statistic to find the true peak concurrency.
- `ConcurrentCallsPercentage` to see how close peaks ran to the quota.
- `CallsPerInterval` and `CallsBreachingConcurrencyQuota` to catch prior rejections.

Note the peak value, the time of peak, and whether any breach already occurred.

## Step 3: Compute Headroom

For each dimension:

```
headroom_percent = (quota - observed_peak) / quota * 100
```

Decision table:

| Headroom | Status | Action |
|----------|--------|--------|
| >= 40% | Healthy | Monitor only |
| 20-40% | Watch | Plan increase before next peak |
| 10-20% | Tight | Request increase now |
| < 10% | Critical | Request increase immediately |
| any breach | Breached | Increase already overdue |

Apply the same computation to phone numbers, queues, routing profiles, and flows
using current consumed counts.

## Step 4: Forecast Against Growth

1. Establish a growth rate from historical peaks (month-over-month or
   year-over-year contact volume and concurrency).
2. Project the peak concurrency for the target horizon:
   `projected_peak = observed_peak * (1 + growth_rate) ^ periods`.
3. Add a seasonal multiplier for known spikes (holiday, launch, billing cycle).
4. Compare the projected peak against current quotas to find which dimension
   breaches first and when.

## Step 5: Recommend Targeted Quota Increases

1. Set each target quota to `projected_peak * (1 + buffer)`, using a buffer of
   roughly 20-30 percent, rounded to a sensible value.
2. Never request the theoretical maximum "to be safe"; request the computed target
   with the forecast as justification.
3. Sequence requests by which dimension breaches first, and submit early because
   concurrent-call quota increases require AWS review lead time.
4. Note any dimensions where the fix is design change rather than a quota bump (for
   example consolidating flows or queues instead of raising the per-instance count).

## Step 6: Remediate and Track

Recommend specific, reversible actions:

- Submit Service Quota increase requests with exact target values and the forecast.
- Add CloudWatch alarms on ConcurrentCallsPercentage (for example warn at 70,
  alert at 85) and on CallsBreachingConcurrencyQuota > 0.
- Re-run this analysis after each peak to recalibrate growth and buffers.

## Output

Provide:
1. Current quota and consumed count per dimension (concurrency, phone numbers,
   queues, routing profiles, flows).
2. Observed peaks and computed headroom percent with status.
3. Forecast to the target horizon and the first dimension to breach.
4. Specific quota target values (peak plus buffer, not maximum) and the monitoring
   alarms to add.
