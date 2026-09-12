---
name: waf-blocked-traffic-analysis
agent_type: "Incident RCA"
description: Use this skill to analyze AWS WAF blocked-request trends and separate genuine attacks from false positives so rules can be tuned. It correlates blocked and allowed request metrics, samples matched requests, and inspects WAF logs to find noisy rules and attack sources, then recommends rule and rate-limit changes.
version: "1.0.0"
last_updated: "2026-08-14"
---

# WAF Blocked Traffic Analysis

This skill examines AWS WAF block activity per WebACL and rule to tell real attacks from over-blocking, then tunes rules to protect the app without dropping legitimate users.

## When to Activate

- CloudWatch BlockedRequests for a WebACL spikes more than 3x its trailing baseline.
- A single rule is blocking more than 90% of traffic that looks legitimate.
- Users report 403 responses after a rule or managed rule group update.
- A rate-based rule is triggering during normal traffic peaks.
- A new managed rule group was deployed and needs validation.

## Step 1: Establish Baseline

- Query CloudWatch GetMetricStatistics on namespace AWS/WAFV2, metrics BlockedRequests and AllowedRequests, per WebACL and per Rule over the last 14 days.
- Compute the trailing baseline block rate and the current block rate.
- Flag a SPIKE when current BlockedRequests exceeds 3x the baseline.

## Step 2: Attribute Blocks to Rules

- Break BlockedRequests down by the Rule dimension to rank the rules causing the most blocks.
- Flag any single rule responsible for more than 90% of blocks as a false-positive candidate.
- Separate managed rule group blocks from custom rule blocks.

## Step 3: Sample and Inspect Requests

- Call WAF GetSampledRequests for the top blocking rules to retrieve matched request details (URI, headers, source IP, country).
- Query WAF logs in CloudWatch Logs or S3 to profile source IPs, user agents, and URIs at scale.
- Classify traffic as attack (concentrated sources, malicious payloads) or legitimate (broad sources, normal paths).

## Step 4: Distinguish Attack From False Positive

- For attack traffic, confirm concentration by source IP or ASN and align with an IP set or rate-based rule.
- For false positives, identify the specific rule and match condition causing legitimate blocks.
- Quantify the share of blocked requests that appear legitimate.

## Step 5: Tune Rules

- For confirmed attacks, recommend an IP set block, a tighter rate-based limit, or a scope-down on the target URI.
- For false positives, recommend moving the offending managed rule to COUNT, adding a scope-down statement, or excluding a rule action override.
- Recommend a rate-based rule threshold aligned to peak legitimate request rate plus headroom.

## Output

The skill produces a titled "WAF Blocked Traffic Analysis" summarizing per-WebACL and per-rule block and allow counts, the baseline versus current block rate, sampled evidence for the top blocking rules, and a classification of each spike as attack or false positive with the legitimate-block share. It ends with a prioritized remediation list ordered by user impact and attack severity, such as setting noisy rules to COUNT, adding scope-down statements, adjusting rate-based thresholds, and blocking confirmed attack sources via IP sets.