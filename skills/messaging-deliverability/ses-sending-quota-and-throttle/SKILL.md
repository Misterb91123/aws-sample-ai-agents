---
name: ses-sending-quota-and-throttle
agent_type: "Generic"
description: Provides analysis procedures for Amazon SES sending quota and
  throttling limits including daily sending cap utilization, maximum send rate
  throttling, sandbox restrictions, and volume growth forecasting. Use this
  skill when SES rejects or throttles messages near the daily cap or send rate,
  when an account is still in the sandbox, or when you need to size a targeted
  quota increase ahead of a campaign. All steps are read-only analysis and the
  recommendation is a specific, justified increase rather than a maximum grab.

version: "1.0.0"
last_updated: "2026-08-14"
---

# SES Sending Quota and Throttle

Use this skill to analyze Amazon SES quota utilization and throttling, then
recommend a targeted quota increase sized to real demand.

## When to Activate

- Messages are throttled or rejected as the daily cap approaches.
- Send attempts exceed MaxSendRate and produce throttling errors.
- The account is in the sandbox and cannot reach unverified recipients.
- A campaign or seasonal peak is coming and headroom is unknown.
- You need to justify a Service Quotas increase request with data.

## Step 1: Read the Current Quota

Retrieve the account quota via use_aws (read-only): SES GetSendQuota returns:

| Field | Meaning |
|-------|---------|
| Max24HourSend | Maximum messages allowed in a rolling 24-hour window |
| MaxSendRate | Maximum messages per second SES will accept |
| SentLast24Hours | Messages sent in the trailing 24 hours |

Also read SES GetAccount for ProductionAccessEnabled and SendingEnabled to
confirm sandbox versus production and that sending is not paused. In the
sandbox, Max24HourSend is 200 and MaxSendRate is 1 per second, and recipients
must be verified.

## Step 2: Compute Utilization and Headroom

Daily utilization:

- Daily utilization percent = SentLast24Hours / Max24HourSend * 100.
- Daily headroom = Max24HourSend - SentLast24Hours.

Rate utilization (from CloudWatch AWS/SES Send at 1-minute resolution):

- Observed peak rate = max(Send per minute) / 60 messages per second.
- Rate headroom = MaxSendRate - observed peak rate.

Decision table:

| Daily utilization | Interpretation |
|-------------------|----------------|
| less than 60 percent | Comfortable headroom |
| 60 to 80 percent | Monitor; plan increase before next peak |
| greater than 80 percent | Constrained; increase likely needed soon |
| greater than 95 percent | Imminent throttling risk |

## Step 3: Detect Throttling

Distinguish the two throttle types:

1. Daily cap throttle: sends fail once SentLast24Hours reaches Max24HourSend.
   SES returns a throttling error and the sender must wait for the rolling
   window to free capacity.
2. Rate throttle: sends fail transiently when instantaneous throughput exceeds
   MaxSendRate. This appears as bursty throttling errors while daily headroom
   still exists.

Evidence:

- CloudWatch AWS/SES Reject can rise when messages are refused pre-send, though
  Reject also covers content and virus rejects, so correlate with send errors.
- Application logs showing Throttling or a 454 style deferral at the SMTP layer
  indicate rate throttling.
- If SentLast24Hours is at or near Max24HourSend, the daily cap is the cause.

Classification:

| Symptom | Daily headroom | Cause |
|---------|----------------|-------|
| Errors only during bursts | Positive | Rate throttle (MaxSendRate) |
| Errors sustained near cap | Near zero | Daily cap throttle (Max24HourSend) |
| All sends to unverified fail | Any | Sandbox restriction |

## Step 4: Forecast Against Volume Growth

Project demand and compare with current limits.

1. Trend SentLast24Hours over the last 14 to 30 days to derive a daily growth
   rate.
2. Layer known events (a scheduled campaign of N recipients, expected retries,
   and transactional baseline) onto the trend to get a projected peak daily
   volume.
3. Convert the campaign burst to a required rate: if a campaign of N messages
   must complete in T seconds, required rate = N / T messages per second.
4. Compare projected daily volume with Max24HourSend and required rate with
   MaxSendRate.

## Step 5: Recommend a Targeted Increase

Size the request to projected demand plus a safety margin, not the maximum.

- Recommended Max24HourSend = projected peak daily volume * 1.3 (about 30
  percent buffer for retries and variance).
- Recommended MaxSendRate = required peak rate * 1.5, rounded to a sensible
  value, so short bursts do not throttle.

For sandbox accounts, the primary recommendation is to request production
access and verify the sending domain rather than to request large numeric
limits before demonstrating good sending behavior.

Submit through Service Quotas or the SES account details request, and include:
the current values from GetSendQuota, the utilization and forecast from Steps 2
and 4, the use case, and the authentication and list hygiene practices in place.

## Output

Provide:
1. Current quota snapshot (Max24HourSend, MaxSendRate, SentLast24Hours,
   sandbox or production).
2. Utilization and headroom for both daily cap and send rate.
3. Throttle classification with evidence (daily cap, rate, or sandbox).
4. Volume forecast and the required daily volume and peak rate.
5. A specific, justified increase recommendation with target numbers and the
   supporting data for the request.
