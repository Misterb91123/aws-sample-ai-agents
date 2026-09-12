---
name: deployment-freeze-enforcer
agent_type: "Generic"
description: Enforces deployment freeze windows by validating deployment requests
  against freeze schedules, exception policies, and change management rules. Use
  this skill when deployments are requested during restricted periods (holidays,
  major events, quarter-end) to determine if the deployment should proceed, require
  exception approval, or be blocked.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Deployment Freeze Enforcer

Use this skill to validate whether a deployment should proceed based on
current freeze windows, exception policies, and risk assessment.

## When to Activate

- A deployment is requested and needs freeze validation.
- During known freeze periods (holidays, major events, quarter-end, peak traffic).
- When a hotfix deployment is needed during a freeze and exception handling is required.
- Evaluating whether a scheduled deployment will conflict with an upcoming freeze.

## Step 1: Check Active Freeze Windows

Determine if a freeze is currently active:

**Standard Freeze Types:**

| Freeze Type | Typical Duration | Strictness |
|-------------|-----------------|------------|
| Holiday freeze | Dec 15 - Jan 5 | Hard (no exceptions without VP approval) |
| Quarter-end freeze | Last 3 days of quarter | Medium (exceptions with manager approval) |
| Major event freeze | Event day +/- 1 day | Hard (company-defined events) |
| Peak traffic freeze | Black Friday/Cyber Monday +/- 2 days | Hard |
| Maintenance window conflict | During scheduled maintenance | Soft (reschedule preferred) |
| Incident freeze | During active SEV1/SEV2 | Hard (only related fixes) |

**Check:**
1. Is the current date/time within any defined freeze window?
2. Is the target deployment time within a freeze window?
3. Are there upcoming freezes within 24 hours that should affect planning?

## Step 2: Classify the Deployment

Determine what type of deployment is being requested:

| Deployment Type | Definition | Freeze Behavior |
|----------------|------------|-----------------|
| Standard release | New features, planned changes | BLOCKED during all freezes |
| Bug fix | Non-critical fix, can wait | BLOCKED during hard freezes, allowed during soft |
| Hotfix | Critical production fix for active issue | EXCEPTION process required |
| Security patch | Critical CVE, active exploitation | EXCEPTION fast-track |
| Rollback | Reverting a bad deployment | ALWAYS ALLOWED |
| Config change | Feature flag, parameter update | Depends on risk level |

## Step 3: Evaluate Exception Request

If deployment is blocked but an exception is requested:

**Exception Criteria (ALL must be met):**
1. There is a documented business justification.
2. The deployment addresses an active production issue OR critical security vulnerability.
3. Delaying the fix would cause greater risk than deploying during the freeze.
4. A rollback plan exists and has been validated.
5. The appropriate approval has been obtained:
   - Soft freeze: Team lead approval
   - Medium freeze: Engineering manager approval
   - Hard freeze: VP Engineering or equivalent approval

**Exception Documentation Required:**
- Ticket/issue reference
- Impact if not deployed (quantified: revenue, users, SLA)
- Risk assessment of deploying during freeze
- Approver name and timestamp
- Monitoring plan post-deployment

## Step 4: Validate Freeze-Safe Deployments

Some deployments may be safe even during freezes. Evaluate:

**Likely safe (soft allow):**
- Feature flag toggles (disable new code, not enable)
- Read-only configuration changes
- Monitoring/alerting changes
- Documentation-only deployments

**Likely unsafe (block):**
- Any deployment that changes runtime behavior
- Database migrations
- Infrastructure scaling changes (may mask capacity issues)
- New service deployments

## Step 5: Produce Verdict

| Verdict | Condition |
|---------|-----------|
| [PASS] ALLOWED | No freeze active, or deployment is a rollback |
| [WARN] EXCEPTION REQUIRED | Freeze active, but deployment qualifies for exception |
| [FAIL] BLOCKED | Freeze active, no valid exception, must wait |
| [INFO] UPCOMING FREEZE | No freeze now, but one starts within 24 hours - deploy with caution |

## Step 6: Provide Guidance

**If BLOCKED:**
- State which freeze is active and when it ends.
- Provide the next available deployment window.
- If urgent, outline the exception approval process.

**If EXCEPTION REQUIRED:**
- List the required approvals.
- Provide the exception request template.
- Recommend enhanced monitoring for the deployment.
- Require explicit rollback plan documentation.

**If ALLOWED but near a freeze:**
- Recommend completing deployment well before freeze starts.
- Ensure rollback is possible before freeze begins.
- Flag increased monitoring during early freeze period.

## Freeze Calendar Template

Provide teams with visibility into upcoming freezes:

```
Current Status: [NO FREEZE ACTIVE / FREEZE ACTIVE: {type}]
Next Freeze: {type} starting {date} at {time}
Freeze Ends: {date} at {time}
Exception Contact: {role/person}
```

## Output

Provide a freeze validation result:
1. Current freeze status (active/inactive/upcoming)
2. Deployment verdict: ALLOWED / EXCEPTION REQUIRED / BLOCKED
3. If blocked: when the freeze ends and next deployment window
4. If exception needed: approval requirements and process
5. Risk assessment for deployments near freeze boundaries