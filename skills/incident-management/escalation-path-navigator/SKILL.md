---
name: escalation-path-navigator
agent_type: "Incident Mitigation"
description: Determines the correct escalation path during incidents based on
  affected services, severity, and time-of-day. Use this skill when an incident
  requires escalation beyond the initial responder, when response SLAs are at risk,
  or when the on-call engineer needs guidance on who to engage next.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Escalation Path Navigator

Use this skill when an incident is not being resolved within expected timeframes,
when severity increases, or when the initial responder needs to engage additional teams.

## When to Activate

- Incident has been open longer than the severity-based SLA (SEV1: 15 min, SEV2: 30 min, SEV3: 1 hour).
- Severity has been escalated (e.g., SEV3 -> SEV2).
- Multiple services are affected, requiring cross-team coordination.
- Customer-facing impact is confirmed.

## Step 1: Assess Current Incident State

Gather the following from the active investigation:
- Current severity level (SEV1-SEV4)
- Duration since detection
- Services affected and their ownership
- Current responders engaged
- Customer impact confirmed (yes/no)
- Blast radius (single service, multiple services, full platform)

## Step 2: Determine Escalation Tier

Based on severity and duration:

| Severity | Time Threshold | Escalation To |
|----------|---------------|---------------|
| SEV1 | Immediate | Engineering Manager + VP Eng + All affected service owners |
| SEV1 | > 30 min unresolved | CTO/Exec on-call |
| SEV2 | > 30 min | Engineering Manager + Service owners |
| SEV2 | > 1 hour unresolved | VP Engineering |
| SEV3 | > 2 hours | Team Lead of owning service |
| SEV4 | > 24 hours | Team Lead (async notification) |

## Step 3: Identify Service Owners

For each affected service:
1. Query resource tags for `Team` and `Service` ownership tags.
2. Check for on-call schedules (PagerDuty, OpsGenie integration if available).
3. If no tags found, use the deployment history - who last deployed to this service.

## Step 4: Compose Escalation Message

Include in the escalation:
- Incident ID and link
- Current severity and justification
- Services affected with blast radius
- Customer impact statement
- Actions taken so far
- Specific ask (what do we need from the escalated party)
- Timeline: when did it start, how long has it been going

## Step 5: Track Escalation Effectiveness

After escalation:
- Record time of escalation
- Record who was engaged
- Track time-to-acknowledge from escalated parties
- Note if escalation resolved the bottleneck

## Decision Tree: Should I Escalate?

```
Is the incident causing customer impact?
+-- YES -> Is it SEV1 or SEV2?
| +-- YES -> Escalate immediately to service owners + management
| +-- NO -> Has it been open > 1 hour? -> YES -> Escalate to Team Lead
+-- NO -> Has it exceeded the severity SLA?
    +-- YES -> Escalate one tier up
    +-- NO -> Continue current response, reassess in 15 minutes
```

## Anti-Patterns to Avoid

- **Escalating without context**: Always include what's been tried.
- **Skipping tiers**: Follow the escalation chain unless SEV1 with customer impact.
- **Delayed escalation**: When in doubt, escalate early - a false escalation is better than a late one.
- **Escalating to individuals not on-call**: Always check current on-call rotation first.