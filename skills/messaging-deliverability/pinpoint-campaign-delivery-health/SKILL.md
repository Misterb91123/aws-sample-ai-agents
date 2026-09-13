---
name: pinpoint-campaign-delivery-health
agent_type: "Incident RCA"
description: Provides investigation procedures for Amazon Pinpoint campaign and
  channel delivery incidents including high per-channel failure rates, endpoint
  opt-out surges, and channel throttling across email, SMS, and push. Use this
  skill when a campaign shows low delivery or high failure rates, when opt-outs
  spike, or when one channel underperforms while others are healthy. All steps
  are read-only investigation and remediation isolates the failing channel with
  targeted fixes that never disable logging, consent handling, or protections.

version: "1.0.0"
last_updated: "2026-08-14"
---

# Pinpoint Campaign Delivery Health

Use this skill to diagnose Amazon Pinpoint campaign and channel delivery
failures, isolate the failing channel, and recommend safe remediation.

## When to Activate

- A campaign reports low delivery relative to messages sent.
- Per-channel failure rate (email, SMS, or push) rises above baseline.
- Endpoint opt-out counts surge after a send.
- Messages are throttled or deferred for a specific channel.
- One channel fails while others in the same application stay healthy.

## Step 1: Enumerate Campaigns and Channels

Establish scope before measuring rates.

- use_aws (read-only) Pinpoint GetCampaign for the affected campaign returns the
  schedule, segment, message configuration, and per-channel setup.
- Pinpoint GetCampaignActivities returns activity execution results including
  SuccessfulEndpointCount, TotalEndpointCount, and State per activity.
- Pinpoint GetApplicationSettings returns the application default limits
  (MessagesPerSecond, Daily, Total, MaximumDuration) that can constrain a
  campaign.
- Confirm which channels are enabled: GetEmailChannel, GetSmsChannel,
  GetApnsChannel, GetGcmChannel. Each returns Enabled and channel-specific
  attributes.

## Step 2: Compute Per-Channel Delivery vs Failure Rate

For each channel compute rates from campaign activity counts and channel
delivery data.

- Delivery rate = delivered / attempted for the channel.
- Failure rate = failed / attempted for the channel.

Channel-specific failure signals:

| Channel | Common failure signal | Underlying source |
|---------|-----------------------|-------------------|
| Email | Bounce, complaint, rendering failure | Backed by SES; check SES metrics |
| SMS | Failed carrier delivery, invalid number | Backed by SNS/SMS; check delivery status |
| Push (APNs) | InvalidToken, Unregistered | Stale or revoked device tokens |
| Push (FCM) | NotRegistered, MismatchSenderId | Stale tokens or credential mismatch |

Because the Pinpoint email channel sends through SES, correlate email failures
with AWS/SES Bounce, Complaint, and Rendering Failures metrics for the sending
identity.

## Step 3: Check Opt-Out and Quota Health

1. Opt-out surge: a rising opt-out count reduces the addressable segment and
   signals content or frequency problems. Endpoints with OptOut set to ALL are
   excluded from future sends. Compare opt-out count for this campaign with the
   channel baseline.
2. Channel throttling: compare the campaign send rate with
   GetApplicationSettings MessagesPerSecond and any per-channel rate. SMS is
   also constrained by the account spend limit and per-number throughput; email
   is constrained by the underlying SES MaxSendRate and Max24HourSend.
3. Quota exhaustion: if the daily or total message limit for the application is
   reached, remaining endpoints are not sent to and the campaign reports lower
   delivery even without per-message errors.

## Step 4: Isolate the Failing Channel

Use the per-channel rates and signals to localize the fault.

| Pattern | Likely cause |
|---------|--------------|
| Only email fails; SES Bounce high | Recipient list quality or SES reputation |
| Only SMS fails; invalid-number errors | Bad number formatting or unsupported region |
| Only push fails; InvalidToken high | Stale device tokens, expired credentials |
| All channels fail near a limit | Application-level quota or throttle |
| Delivery low, no per-message errors | Segment shrinkage from opt-outs or quota cap |

Confirm the isolation by checking whether other campaigns on the same channel
share the symptom (channel-wide) or whether only this campaign is affected
(campaign or segment specific).

## Step 5: Remediate the Failing Channel

Apply targeted fixes. Never disable consent handling, opt-out processing, or
delivery logging.

Email channel:
1. Address SES reputation and list hygiene using the SES deliverability
   procedures; suppress repeat bounces and honor complaints.
2. Verify DKIM and custom MAIL FROM for the sending identity.

SMS channel:
1. Normalize numbers to E.164 and validate country support before sending.
2. Confirm the account SMS spend limit and originating number throughput are
   sufficient; request a targeted increase if throttled.

Push channels:
1. Remove or refresh stale tokens flagged InvalidToken, Unregistered, or
   NotRegistered; update endpoints after each send.
2. Re-verify APNs certificate or key and FCM credentials for validity.

Opt-out or quota driven:
1. Reduce frequency and improve targeting to slow opt-out growth.
2. Raise application message limits only to the level the forecast requires, or
   spread the campaign over a longer MaximumDuration.

## Output

Provide:
1. The failing channel identified and its delivery and failure rates versus
   baseline.
2. Root cause with evidence (campaign activity counts, per-channel error
   signals, opt-out trend, quota or throttle state, correlated SES metrics for
   email).
3. Specific per-channel remediation steps.
4. Prevention recommendations (token refresh cadence, list validation, opt-out
   monitoring, alarms on per-channel failure rate).
