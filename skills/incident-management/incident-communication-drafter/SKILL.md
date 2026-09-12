---
name: incident-communication-drafter
agent_type: "Generic"
description: Drafts internal and external incident communications including status
  page updates, stakeholder notifications, and customer-facing messages. Use this
  skill when an incident requires communication to customers, executives, or
  internal teams and the responder needs templated, professional messaging
  appropriate to the severity and audience.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Incident Communication Drafter

Use this skill to draft clear, professional incident communications for
different audiences and stages of an incident lifecycle.

## When to Activate

- A SEV1 or SEV2 incident is confirmed and customers are impacted.
- Stakeholders request an update on incident status.
- Incident is resolved and a resolution notice is needed.
- Executive briefing is required for high-severity incidents.

## Communication Types

### Type 1: Status Page Update (Customer-Facing)

Use for public-facing communications on your status page.

**Tone**: Factual, empathetic, non-technical. Never blame. Never speculate.

**Structure:**
```
Title: [Service Name] - [Impact Description]
Status: Investigating | Identified | Monitoring | Resolved

Body:
- What is affected (customer capability, not internal system names)
- Current status (are we investigating, mitigating, or monitoring)
- Workaround if available
- Next update ETA
```

**Example - Investigating:**
> We are investigating reports of increased error rates affecting the Payments API.
> Some customers may experience failed transactions. Our engineering team is
> actively investigating. We will provide an update within 30 minutes.

**Example - Identified:**
> We have identified the root cause of the Payments API errors. A fix is being
> deployed and we expect full recovery within 15 minutes. Transactions that
> failed during this window can be safely retried.

**Example - Resolved:**
> The issue affecting the Payments API has been resolved. All systems are
> operating normally. Total duration of impact was 47 minutes. We apologize
> for the inconvenience and will share a detailed post-incident review.

### Type 2: Internal Incident Channel Update

Use for updates to the internal engineering incident channel.

**Tone**: Technical, concise, actionable.

**Structure:**
```
[TIMESTAMP] [STATUS UPDATE]
Impact: <what's broken and who's affected>
Current theory: <what we think is wrong>
Actions in progress: <what's being done right now>
Next steps: <what we'll do next>
Blockers: <what's preventing progress, if anything>
Next update: <when>
```

### Type 3: Executive Briefing

Use for C-level or VP-level stakeholder updates.

**Tone**: Business impact focused, concise, no jargon.

**Structure:**
```
Subject: [SEV Level] Incident - [One-line summary]

Current Status: [Active/Mitigated/Resolved]
Duration: [How long it's been going]
Customer Impact: [What customers can't do, estimated % affected]
Business Impact: [Revenue, reputation, SLA considerations]
Root Cause: [One sentence, non-technical]
ETA to Resolution: [Best estimate]
Action Items: [What's being done, who's leading]
```

### Type 4: Post-Resolution Customer Email

Use for follow-up communications after a significant incident.

**Tone**: Transparent, accountable, forward-looking.

**Structure:**
```
Subject: Resolved - [Service] incident on [date]

Dear [Customer],

Summary of what happened (2-3 sentences, non-technical).
Duration and impact window.
What we did to resolve it.
What we're doing to prevent recurrence (without over-promising).
Apology and appreciation for patience.
Contact for questions.
```

### Type 5: Cross-Team Notification

Use when other engineering teams need to be aware of an incident affecting shared infrastructure.

**Tone**: Informational, actionable for the receiving team.

**Structure:**
```
[INCIDENT NOTIFICATION - SEV X]
Affected shared component: [name]
Impact to your service: [specific expected impact]
Action required from your team: [yes/no, what]
Workaround available: [yes/no, details]
Incident channel: [link]
```

## Communication Timing Guidelines

| Severity | First Update | Subsequent Updates | Stakeholder Alert |
|----------|-------------|-------------------|-------------------|
| SEV1 | Within 5 minutes | Every 15 minutes | Immediately |
| SEV2 | Within 15 minutes | Every 30 minutes | Within 15 minutes |
| SEV3 | Within 1 hour | Every 2 hours | Not required |
| SEV4 | Next business day | As resolved | Not required |

## Rules for Incident Communications

1. **Never speculate on root cause publicly** until confirmed.
2. **Never blame individuals or teams** in any communication.
3. **Never promise specific fix times** - use ranges or "within X minutes."
4. **Always include next update time** so stakeholders know when to expect news.
5. **Use customer-centric language** externally - describe impact in terms of what they can't do, not what's broken internally.
6. **Proofread before sending** - incident comms are high-visibility.

## Output

Produce draft communications appropriate to the incident stage and severity,
ready for the incident commander to review and send. Include:
1. The appropriate communication type based on context
2. Draft message text ready to copy/paste
3. Suggested recipients/channels
4. Recommended timing for next update