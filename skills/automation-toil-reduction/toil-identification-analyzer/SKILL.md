---
name: toil-identification-analyzer
agent_type: "Generic"
description: Identifies and quantifies operational toil by analyzing repetitive manual
  tasks, interrupt-driven work, and automation gaps. Use this skill when assessing
  team operational burden, justifying automation investments, or during quarterly
  planning to identify high-ROI automation targets that free up engineering capacity.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Toil Identification Analyzer

Use this skill to systematically identify, measure, and prioritize toil
within SRE and operations workflows.

## When to Activate

- Quarterly toil assessment for the team.
- Team burnout or ticket backlog growing - need to identify what's consuming time.
- Justifying headcount or automation investment to leadership.
- New team member onboarding - documenting what tasks consume team time.
- SRE engagement model review - what should be automated vs delegated.

## Step 1: Define Toil Characteristics

Toil is work that is:

| Characteristic | Definition | Example |
|---------------|-----------|---------|
| **Manual** | Requires a human to execute steps | SSH into server, run script, verify output |
| **Repetitive** | Done more than once (will happen again) | Weekly certificate rotation, daily report generation |
| **Automatable** | Could be done by a machine/script | Restarting a service when health check fails |
| **Tactical** | Reactive, interrupt-driven, not strategic | Responding to the same alarm every day |
| **No lasting value** | Doesn't improve the system for next time | Manually scaling during peak, then scaling back |
| **Scales linearly** | Grows with service size (O(n) work) | Adding DNS records per customer manually |

**Not toil:**
- Strategic project work (building automation).
- Learning and development.
- Design and architecture work.
- On-call response to novel incidents (first time = learning, nth time = toil).

## Step 2: Gather Toil Data Sources

Collect evidence of toil from multiple sources:

1. **Ticketing system analysis:**
   - Recurring ticket types (same category appearing weekly).
   - Time-to-close patterns (quick fixes suggest repetitive manual steps).
   - Ticket volume by category over 90 days.
   - Tickets that reference "manual steps" or specific runbooks.

2. **On-call data:**
   - Alert frequency by alert type.
   - Alerts that are acknowledged but require no investigation (noise or routine action).
   - Pages that lead to the same remediation every time.
   - Off-hours pages for non-critical issues.

3. **Runbook usage:**
   - Which runbooks are executed most frequently?
   - Runbooks with "repeat weekly/daily" in their notes.
   - Runbooks that are purely mechanical (no judgment calls).

4. **Time tracking / stand-ups:**
   - What do team members report doing repeatedly?
   - Tasks that appear in stand-ups multiple times a week.
   - Work described as "I have to do X again."

5. **Deployment and change logs:**
   - Manual deployment steps (should be automated).
   - Manual scaling events.
   - Manual certificate rotations.
   - Manual DNS changes.

## Step 3: Categorize Toil

Group identified toil by category:

### Infrastructure Toil
- Manual scaling (adding/removing instances for traffic patterns).
- Manual certificate renewal and rotation.
- Manual security group updates for new IPs.
- Manual DNS record management.
- Instance patching and reboots during maintenance windows.

### Operational Toil
- Responding to the same alarm with the same fix.
- Restarting services that crash periodically.
- Clearing disk space when logs fill up.
- Resetting stuck jobs or queues.
- Manual data fixes/corrections.

### Access & Provisioning Toil
- Granting/revoking access manually.
- Setting up new environments manually.
- Creating accounts and permissions for new team members.
- Provisioning resources for new services.

### Deployment Toil
- Manual deployment steps (even partially manual).
- Post-deployment verification done manually.
- Rolling back deployments manually.
- Updating configuration across multiple services.

### Reporting & Communication Toil
- Manually gathering metrics for reports.
- Writing the same status update format every week.
- Manually checking compliance status.
- Generating on-call handoff reports.

## Step 4: Quantify Toil

For each identified toil item:

| Metric | How to Measure |
|--------|---------------|
| Frequency | How often (times per day/week/month) |
| Duration | How long each occurrence takes (minutes/hours) |
| People required | How many people needed (1 person, requires coordination) |
| Monthly toil hours | Frequency x duration x people |
| Annual toil hours | Monthly x 12 |
| Toil growth rate | Is frequency increasing with scale? |
| Interruption cost | Does it interrupt focus work? (context switch penalty) |

**Toil budget calculation:**
```
Total team capacity: N engineers x 40 hours/week = X hours/week
Current toil: sum of all toil hours/week
Toil percentage: toil hours / total capacity x 100

Target: Toil should be < 50% of team capacity (Google SRE recommendation)
Healthy: < 30%
At risk: 30-50%
Unsustainable: > 50%
```

## Step 5: Prioritize Automation Opportunities

Rank toil items by automation ROI:

**ROI Score = (Hours saved per year x cost per hour) / (Automation effort in hours x cost per hour)**

Simplified: **ROI = Annual toil hours / Automation effort hours**

| Priority | Criteria |
|----------|----------|
| P1 (automate now) | High frequency + easy to automate + growing with scale |
| P2 (automate soon) | High frequency + moderate effort OR medium frequency + easy |
| P3 (plan for future) | Medium frequency + high effort OR low frequency + easy |
| P4 (accept for now) | Low frequency + high effort (automation costs more than toil) |

## Step 6: Estimate Automation Impact

For top opportunities, project the impact:

```
If we automate [task]:
- Current time spent: X hours/month
- Automation development effort: Y hours (one-time)
- Automation maintenance: Z hours/month (ongoing)
- Net savings/month: X - Z hours/month
- Break-even: Y / (X - Z) months
- Annual ROI after break-even: (X - Z) x (12 - break-even months)
```

## Step 7: Track Toil Trends

Establish ongoing measurement:

1. **Toil percentage per quarter**: Is it decreasing over time?
2. **Top toil items**: Are the biggest items getting automated?
3. **New toil introduced**: Are new services creating new toil?
4. **Team satisfaction**: Is the team feeling less burdened?
5. **Incident-driven toil**: Is incident frequency decreasing?

## Output

Produce a toil assessment report:
1. **Summary**: Total toil hours/month, toil percentage, trend vs previous quarter.
2. **Toil Inventory Table**: Task, category, frequency, duration, monthly hours, automatable (yes/no), ROI score.
3. **Toil by Category Chart**: Pie chart showing where time goes.
4. **Top 10 Automation Targets**: Ranked by ROI with estimated effort and savings.
5. **Toil Growth Projection**: If no action taken, projected toil in 6/12 months.
6. **Team Capacity Impact**: How much engineering capacity is freed by top 5 automations.
7. **Quarterly Roadmap**: Recommended automation projects for next quarter.