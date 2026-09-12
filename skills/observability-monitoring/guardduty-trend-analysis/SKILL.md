---
name: guardduty-trend-analysis
agent_type: "Incident RCA"
description: Use when analyzing Amazon GuardDuty severity trends and recurring finding types. It aggregates finding statistics, flags rising HIGH severity and stale unresolved findings, and prioritizes response. Apply during security operations reviews or weekly threat triage.
version: "1.0.0"
last_updated: "2026-08-14"
---

# GuardDuty Trend Analysis

Analyze GuardDuty findings over time to surface rising threats, recurring types, and unresolved findings that need action.

## When to Activate
- GetFindingsStatistics shows HIGH severity findings (7.0 to 8.9) rising week over week.
- Findings remain in an unresolved state for more than 14 days.
- A single finding type recurs repeatedly across accounts or resources.
- CRITICAL or HIGH findings appear for the first time in an account.
- The detector has findings that were never triaged or archived.

## Step 1: Aggregate Finding Statistics
- Call GetFindingsStatistics grouped by severity and by finding type per detector.
- Compare current period counts against the prior 7 and 30 day periods.
- Flag any increase in HIGH severity findings.

## Step 2: Identify Recurring Types
- List the top finding types by count using ListFindings with type filters.
- Flag types that recur more than 3 times as systemic issues.
- Group recurring types by root cause (for example exposed credentials or reconnaissance).

## Step 3: Age Unresolved Findings
- Filter findings by service.archived false and compute age from updatedAt.
- Flag findings unresolved for more than 14 days.
- Separate suppressed and false-positive findings via existing suppression rules.

## Step 4: Assess Severity and Blast Radius
- For each HIGH and CRITICAL finding read the resource and affected account.
- Prioritize findings on production and internet-facing resources.
- Correlate related findings that indicate a multi-step attack.

## Step 5: Recommend Response and Tuning
- Recommend containment actions for active HIGH and CRITICAL findings.
- Recommend suppression rules for confirmed benign recurring findings to reduce noise.
- Recommend an SLA of triage within 24 hours for HIGH and 72 hours for MEDIUM.

## Output
Produce a titled "GuardDuty Trend Analysis Report" containing severity counts with week-over-week trend, top recurring finding types, findings unresolved longer than 14 days, and affected accounts and resources. Include a prioritized remediation list: contain active HIGH and CRITICAL findings first, address recurring systemic types second, then close stale unresolved findings and add suppression rules for confirmed benign noise.