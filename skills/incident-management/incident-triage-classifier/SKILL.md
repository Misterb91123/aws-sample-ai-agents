---
name: incident-triage-classifier
agent_type: "Incident Triage"
description: Classifies and triages incoming incidents by analyzing alarm patterns,
  affected services, and customer impact to assign appropriate severity levels.
  Use this skill when a new incident is detected and needs initial assessment,
  severity classification, or when determining whether an alert constitutes a
  real incident vs transient noise.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Incident Triage Classifier

Use this skill to perform initial incident triage - determining severity,
ownership, and immediate response actions when a new incident arrives.

## When to Activate

- A new alarm or alert fires that may indicate an incident.
- Multiple related alarms fire in quick succession.
- A customer report comes in indicating service degradation.
- An investigation is created and needs initial classification.

## Step 1: Gather Initial Signal

Collect the triggering information:
1. Query the alarm or alert details - metric name, threshold breached, duration.
2. Check if related alarms are also firing (correlate within a 5-minute window).
3. Determine the affected service(s) from alarm dimensions (namespace, resource tags).
4. Check if this is a known pattern (similar alarm fired recently and auto-resolved).

## Step 2: Assess Customer Impact

Determine whether customers are affected:
1. Check external-facing metrics: HTTP 5xx rates, API error rates, latency p99.
2. If the affected service is internal-only (batch processing, internal tooling), note reduced impact.
3. Check if the service has active traffic (time-of-day matters - low traffic overnight may indicate lower urgency).
4. Look for customer-reported issues (support tickets, status page reports).

**Impact Classification:**
- **Full outage**: Service completely unavailable to all customers
- **Partial degradation**: Service slow or erroring for a subset of customers/features
- **Internal only**: No customer-facing impact, internal systems affected
- **Potential**: Metrics trending toward impact but not yet customer-visible

## Step 3: Classify Severity

| Severity | Criteria |
|----------|----------|
| SEV1 - Critical | Full customer-facing outage OR data loss/corruption OR security breach active |
| SEV2 - High | Partial customer degradation OR complete loss of non-critical feature OR internal service critical to operations |
| SEV3 - Medium | Minor degradation noticed by some customers OR internal service degraded but workarounds exist |
| SEV4 - Low | No current impact, but condition may worsen if not addressed OR cosmetic issues |

## Step 4: Determine Ownership

Assign the incident to the correct team:
1. Map the affected AWS resource to a service using resource tags (`Team`, `Service`).
2. If multiple services affected, assign to the team owning the upstream/root service.
3. If unclear, assign to the platform/SRE team for initial investigation.

## Step 5: Define Initial Response Actions

Based on severity:

**SEV1:**
- Page on-call immediately
- Open incident channel (Slack/Teams)
- Begin customer communication within 5 minutes
- All hands on deck for owning team

**SEV2:**
- Page on-call
- Open incident channel
- Begin investigation immediately
- Prepare customer communication draft

**SEV3:**
- Notify on-call (non-page)
- Investigate within 30 minutes
- No immediate customer communication needed

**SEV4:**
- Create ticket for next business day
- No immediate response required

## Step 6: Check for False Positives

Before confirming the incident, rule out:
- Scheduled maintenance (check change calendar)
- Known deployment in progress (check recent deployments in the past 30 minutes)
- Transient spike that self-resolved (check if metric has recovered)
- Alarm misconfiguration (has this alarm flapped recently?)

If determined to be a false positive, mark as "Skipped" with clear reasoning.

## Output

Provide a triage summary:
1. Severity classification with justification
2. Affected services and ownership
3. Customer impact assessment
4. Recommended immediate actions
5. Whether this is a confirmed incident or potential false positive