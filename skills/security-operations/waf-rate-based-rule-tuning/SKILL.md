---
name: waf-rate-based-rule-tuning
agent_type: "Generic"
description: Use when tuning AWS WAF rate-based rules to match real attack volume. It finds limits set too high to stop abuse or too low to allow legitimate traffic, then recommends calibrated thresholds and scope. Apply during edge security reviews or after DDoS or scraping incidents.
version: "1.0.0"
last_updated: "2026-08-14"
---

# WAF Rate-Based Rule Tuning

Calibrate WAF rate-based rule limits so they block abusive clients without throttling legitimate users.

## When to Activate
- GetRateBasedStatementManagedKeys shows few or no IPs being rate limited during a known attack.
- CloudWatch BlockedRequests stays at 0 while AllowedRequests spikes from a small set of IPs.
- A rate-based rule limit is set far above observed per-IP request rates (too permissive).
- A rate-based rule limit is below normal per-IP traffic and blocks real users (too strict).
- No rate-based rule exists on a public endpoint exposed to scraping or credential stuffing.

## Step 1: Establish Baseline Traffic
- Query CloudWatch AllowedRequests and BlockedRequests for the web ACL over 7 days.
- Use WAF logs or sampled requests to compute per-IP request rates.
- Record the normal 95th percentile requests per IP over the rule evaluation window.

## Step 2: Read Current Rules
- Call GetWebACL and inspect RateBasedStatement Limit, AggregateKeyType, and EvaluationWindowSec.
- Call GetRateBasedStatementManagedKeys to see which IPs are currently limited.
- Flag limits far above or below the observed per-IP rate.

## Step 3: Analyze Attack Patterns
- Correlate spikes in AllowedRequests with source IPs, URIs, and user agents.
- Distinguish distributed attacks from single-source abuse.
- Choose AggregateKeyType (IP, forwarded IP, or custom key) that matches the pattern.

## Step 4: Calibrate the Limit
- Set the limit above the 95th percentile legitimate per-IP rate with headroom (for example 1.5 times).
- Set it low enough to catch abusive bursts observed in logs.
- Tune EvaluationWindowSec (60 to 600 seconds) to the attack cadence.

## Step 5: Recommend Scope and Action
- Scope the rule with a scope-down statement to protect only sensitive paths where needed.
- Choose Block or CAPTCHA action based on false-positive tolerance.
- Add alarms on BlockedRequests and monitor for legitimate users being caught.

## Output
Produce a titled "WAF Rate-Based Rule Tuning Report" listing rules with limits that are too high or too low relative to baseline per-IP traffic, currently limited IPs, and unprotected public endpoints. Include a prioritized remediation list: add rate-based rules to unprotected sensitive endpoints first, lower over-permissive limits toward the calibrated value second, then raise over-strict limits and add scope-down statements and alarms.