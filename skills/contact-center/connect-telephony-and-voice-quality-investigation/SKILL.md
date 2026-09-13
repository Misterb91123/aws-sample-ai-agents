---
name: connect-telephony-and-voice-quality-investigation
agent_type: "Incident RCA"
description: Provides investigation procedures for Amazon Connect call setup failures
  and poor voice quality, including MissedCalls, ThrottledCalls,
  CallsBreachingConcurrencyQuota, elevated ToInstancePacketLossRate, one-way audio,
  claimed or ported phone number problems, outbound campaign call failures, and
  SIP/media issues. Use this skill when calls fail to connect, when callers report
  choppy or one-way audio, when concurrency-quota throttling appears, or when a
  specific phone number or outbound campaign stops working.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Amazon Connect Telephony and Voice Quality Investigation

Use this skill to diagnose call setup failures and voice quality degradation in
Amazon Connect. Investigation is read-only; any fix is specific and reversible.

## When to Activate

- MissedCalls (AWS/Connect) rises above baseline.
- ThrottledCalls or CallsBreachingConcurrencyQuota appears.
- ToInstancePacketLossRate is elevated.
- Callers report choppy audio, dropouts, or one-way audio.
- A claimed or ported phone number stops receiving calls.
- Outbound campaign or outbound API calls fail to place.

## Step 1: Classify Inbound vs Outbound and Setup vs Quality

| Axis | Signal | Direction |
|------|--------|-----------|
| Inbound setup | MissedCalls, ThrottledCalls | Call never establishes |
| Outbound setup | Outbound call failures, ThrottledCalls | Dial fails |
| Concurrency | CallsBreachingConcurrencyQuota, ConcurrentCallsPercentage near 100 | Either direction blocked |
| Quality | ToInstancePacketLossRate high, one-way audio | Call connects but degrades |

Separate "call cannot start" from "call starts then sounds bad"; they have
different root causes and different fixes.

## Step 2: Check Concurrency Quota Headroom

Pull AWS/Connect metrics with GetMetricDataV2:

- `ConcurrentCalls` (Maximum statistic) and `ConcurrentCallsPercentage`.
- `CallsBreachingConcurrencyQuota` (Sum) - any nonzero value means calls were
  rejected because the instance hit its concurrent active calls quota.

Compare the observed `ConcurrentCalls` peak against the Service Quota for
concurrent active calls on the instance. If `ConcurrentCallsPercentage` is
riding near 100 percent during the incident, the quota is the constraint, not
telephony health. (For sustained headroom planning, hand off to the capacity and
concurrency planning skill.)

## Step 3: Check Packet Loss and Media Quality

- `ToInstancePacketLossRate`: sustained values above roughly 1 percent correlate
  with audible degradation; higher values cause dropouts. This measures loss on
  the path toward the Connect instance.
- One-way audio typically points to network/NAT/firewall asymmetry on the agent
  side (softphone media not reaching Connect) rather than the PSTN leg.
- For agent-side voice quality, confirm the Connect softphone/CCP network meets
  the media requirements (UDP media path, low jitter, sufficient bandwidth) and
  check whether affected agents share one site or ISP.

## Step 4: Validate Phone Number Status

1. List numbers with ListPhoneNumbersV2 and confirm the affected number is
   claimed to the instance and associated with a contact flow.
2. For ported numbers, confirm the port completed and the number Type/Status is
   active, not pending.
3. Confirm the number country and the instance region are compatible and that the
   number type (DID vs toll-free) matches the intended use.
4. A number in a claimed-but-unassociated state rings nowhere; wire it to the
   inbound flow.

## Step 5: Review Outbound and Throttling

1. `ThrottledCalls` (Sum) indicates outbound dial attempts exceeded the allowed
   rate; check the outbound calls per second behavior and any campaign dialing
   rate.
2. For outbound campaigns, confirm the campaign is enabled, the source number is
   valid for the destination country, and the concurrency budget leaves room for
   inbound.
3. Confirm `CallsPerInterval` trend to see whether a traffic surge (inbound or
   outbound) is driving throttling rather than a configuration fault.

## Step 6: Remediate

Recommend specific, reversible fixes:

- If concurrency quota is the constraint, request a targeted increase to the
  concurrent active calls quota sized to the observed peak plus buffer (see the
  capacity planning skill), not an arbitrary maximum.
- For packet loss / one-way audio, correct the agent-side network path (firewall
  media ports, NAT, bandwidth); do not weaken security controls to do so.
- Associate or re-claim the affected phone number and attach the correct inbound
  flow.
- Reduce outbound dial rate or stagger campaigns to stay under throttling limits.
- Re-measure MissedCalls, ThrottledCalls, CallsBreachingConcurrencyQuota, and
  ToInstancePacketLossRate to confirm recovery.

## Output

Provide:
1. Classification (inbound vs outbound, setup vs quality, concurrency vs media).
2. Evidence (MissedCalls, ThrottledCalls, CallsBreachingConcurrencyQuota,
   ConcurrentCallsPercentage, ToInstancePacketLossRate, phone number status).
3. Root cause (quota exhaustion, network media path, number misconfiguration,
   outbound throttling).
4. Specific fix and the metrics to confirm recovery.
