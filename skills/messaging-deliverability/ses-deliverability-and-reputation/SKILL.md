---
name: ses-deliverability-and-reputation
agent_type: "Incident RCA"
description: Provides investigation procedures for Amazon SES deliverability
  incidents including bounce and complaint spikes, reputation metrics trending
  toward at-risk, DKIM/SPF/DMARC misalignment, and dedicated IP warmup or
  reputation problems. Use this skill when bounce or complaint rates cross
  warning or at-risk thresholds, when the account is at risk of a sending
  pause, or when authentication failures reduce inbox placement. All steps are
  read-only investigation; remediation focuses on list hygiene, authentication,
  and controlled warmup and never disables encryption, logging, or protections.

version: "1.0.0"
last_updated: "2026-08-14"
---

# SES Deliverability and Reputation

Use this skill to diagnose Amazon SES deliverability incidents and reputation
degradation, then recommend safe remediation that protects the account from a
sending pause.

## When to Activate

- CloudWatch AWS/SES Bounce or Complaint counts spike relative to Send volume.
- ReputationBounceRate or ReputationComplaintRate trends toward at-risk levels.
- Account sending is paused or flagged, or a review notification arrives.
- Inbox placement drops and DKIM, SPF, or DMARC alignment is suspected.
- A dedicated IP shows rising bounces during or after warmup.
- Suppression list grows rapidly, indicating repeated hard bounces or complaints.

## Step 1: Pull Send, Delivery, Bounce, and Complaint Volumes

Read CloudWatch AWS/SES metrics over the incident window and a 14-day baseline.

Key metrics (namespace AWS/SES):

| Metric | Meaning | Use |
|--------|---------|-----|
| Send | Messages accepted by SES | Denominator for rates |
| Delivery | Messages delivered to the recipient MTA | Delivery success |
| Bounce | Hard and soft bounces | Numerator for bounce rate |
| Complaint | Recipient spam complaints | Numerator for complaint rate |
| Reject | Messages rejected by SES pre-send | Content or virus rejects |
| Rendering Failures | Template rendering errors | Template data mismatch |

Retrieve via use_aws (read-only): CloudWatch GetMetricData for Send, Bounce,
Complaint, Delivery, Reject over 5-minute periods for the incident window and
daily periods for the baseline. Scope by configuration set dimension when a
specific sending stream is suspected.

## Step 2: Compute Bounce Rate and Complaint Rate Against Thresholds

SES evaluates account-level rates over a representative rolling volume, not a
single minute. Compute rates over trailing sent volume.

- Bounce rate = Bounce / Send over the trailing window.
- Complaint rate = Complaint / Send over the trailing window.

Decision table:

| Signal | Warning | At-risk / pause risk |
|--------|---------|----------------------|
| Bounce rate | greater than 5 percent | greater than 10 percent |
| Complaint rate | greater than 0.1 percent | greater than 0.5 percent |

Classify the incident:

1. Bounce-driven: bounce rate is the metric crossing thresholds. Likely list
   quality, invalid domains, or spamtrap hits.
2. Complaint-driven: complaint rate is crossing. Likely consent, frequency, or
   content and expectation mismatch.
3. Mixed: both elevated. Treat as high severity and prioritize a sending
   slowdown recommendation.

## Step 3: Check Reputation Metrics and Account Sending Status

Read account-level reputation and status.

- CloudWatch AWS/SES ReputationBounceRate and ReputationComplaintRate are the
  values SES itself tracks against enforcement thresholds. Compare with the
  raw rates from Step 2 to confirm the trend.
- use_aws SES GetAccount returns SendingEnabled, ProductionAccessEnabled,
  EnforcementStatus, and the reputation object. EnforcementStatus values such
  as UNDER_REVIEW, PENDING_END_OF_REVIEW, or SHUTDOWN indicate active
  enforcement.
- use_aws SES GetAccountSendingEnabled confirms whether sending is currently
  permitted at the account level.

If EnforcementStatus is not HEALTHY, treat the incident as pause-risk and make
the slowdown and hygiene recommendation the primary action.

## Step 4: Check Authentication Alignment (DKIM, SPF, DMARC)

Authentication misalignment lowers inbox placement and can inflate complaints.

1. DKIM: confirm the sending identity uses Easy DKIM or BYODKIM and that the
   CNAME or TXT records resolve. use_aws SESv2 GetEmailIdentity returns
   DkimAttributes.Status (expect SUCCESS) and SigningEnabled true.
2. SPF: confirm the MAIL FROM domain is configured (custom MAIL FROM) and the
   SPF record includes the SES include mechanism. GetEmailIdentity returns
   MailFromAttributes with MailFromDomainStatus SUCCESS.
3. DMARC: confirm a DMARC TXT record exists at _dmarc for the domain and that
   alignment passes on either DKIM or SPF. A DMARC policy of quarantine or
   reject with failing alignment explains sudden placement loss.

Alignment decision:

| Finding | Impact | Action |
|---------|--------|--------|
| DKIM status not SUCCESS | Signature failures, placement drop | Republish DKIM records, re-verify identity |
| Custom MAIL FROM missing | SPF not aligned | Configure custom MAIL FROM and SPF record |
| DMARC absent | No alignment enforcement, spoofing risk | Add DMARC record starting at p=none for monitoring |

## Step 5: Inspect Suppression List and Configuration Sets

1. Suppression list growth: use_aws SESv2 ListSuppressedDestinations filtered by
   Reason BOUNCE and COMPLAINT over the incident window. Rapid growth confirms
   list quality problems and identifies specific recipients or domains.
2. Configuration sets: use_aws SESv2 ListConfigurationSets and
   GetConfigurationSet to confirm event destinations capture bounces and
   complaints and that the reputation options and suppression options are
   enabled for the sending stream. Missing event destinations mean you are
   blind to the failure signal.
3. Dedicated IPs: use_aws SESv2 GetDedicatedIps to review WarmupStatus and
   WarmupPercentage per IP. A high bounce rate on a specific IP during warmup
   means the warmup schedule is being outpaced by volume.

## Step 6: Remediate Safely

Match remediation to the classification. Never disable authentication, logging,
event destinations, or suppression protections.

Bounce-driven:
1. Enable and honor the account-level suppression list so repeat hard bounces
   are not resent.
2. Remove or re-verify invalid recipient domains; segment recently bounced
   addresses out of the next send.
3. Add double opt-in and list validation at capture time.

Complaint-driven:
1. Add a visible unsubscribe and honor opt-outs immediately.
2. Reduce frequency and target only engaged recipients.
3. Align content and sender name with the recipient expectation set at signup.

Reputation at-risk or pause-risk:
1. Recommend an immediate reduction in send rate and volume to let rates recover
   over the rolling window.
2. Keep sending only to highly engaged, recently validated recipients.
3. Prepare a remediation summary for the SES review process describing the
   hygiene and authentication changes made.

Dedicated IP warmup:
1. Slow volume to fit the warmup schedule and WarmupPercentage rather than
   forcing traffic onto a cold IP.
2. Route non-warmed volume to the shared pool temporarily where appropriate.

## Output

Provide:
1. Incident classification (bounce-driven, complaint-driven, mixed, or
   reputation-at-risk) with the computed rates and the thresholds crossed.
2. Root cause with evidence (metric values, GetAccount EnforcementStatus,
   authentication status, suppression growth, dedicated IP warmup state).
3. Specific safe remediation steps tied to the classification.
4. Pause-risk assessment and monitoring recommendations (CloudWatch alarms on
   ReputationBounceRate and ReputationComplaintRate, Virtual Deliverability
   Manager dashboards for ongoing visibility).
