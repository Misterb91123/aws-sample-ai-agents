---
name: automation-opportunity-scorer
agent_type: "Generic"
description: Scores and ranks automation opportunities by evaluating feasibility,
  ROI, risk, and maintainability. Use this skill when deciding which operational
  tasks to automate next, when building an automation backlog, or when justifying
  automation projects to stakeholders with data-driven prioritization.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Automation Opportunity Scorer

Use this skill to evaluate and rank automation candidates using a structured
scoring framework that balances value, feasibility, and risk.

## When to Activate

- Backlog of automation ideas needs prioritization.
- Team has automation sprint capacity and needs to choose the highest-value work.
- Business case needed for an automation project.
- Comparing two automation approaches for the same problem.
- Quarterly planning - selecting automation initiatives.

## Step 1: Define the Automation Candidate

For each candidate, document:

1. **What**: Specific task or process to automate.
2. **Who**: Who currently does this work (SRE, DevOps, developers, support).
3. **When**: How often and under what conditions.
4. **Current process**: Step-by-step manual procedure.
5. **Trigger**: What initiates the task (alert, schedule, request, event).
6. **Decision points**: Does the task require human judgment? Where?
7. **Success criteria**: How do you know it was done correctly?

## Step 2: Score Value (Weight: 40%)

How much value does automating this deliver?

| Factor | Score 1-5 | Description |
|--------|-----------|-------------|
| Time savings | 1=minutes/month, 5=>40 hours/month | Total time reclaimed |
| Frequency | 1=monthly, 3=weekly, 5=multiple/day | How often it occurs |
| Scale sensitivity | 1=constant, 5=grows linearly+ with infrastructure | Does toil grow with scale |
| Reliability improvement | 1=rarely fails manually, 5=frequently errors | Human error reduction |
| Speed improvement | 1=manual is fast enough, 5=automation is 10x+ faster | Time to complete |
| Interrupt reduction | 1=scheduled work, 5=interrupts focus work randomly | Cognitive load removed |

**Value Score** = weighted average of above factors.

## Step 3: Score Feasibility (Weight: 30%)

How practical is the automation to build?

| Factor | Score 1-5 | Description |
|--------|-----------|-------------|
| Technical complexity | 1=complex stateful logic, 5=simple sequential steps | Ease of implementation |
| API/tool availability | 1=no APIs available, 5=full API coverage | Everything accessible programmatically |
| Deterministic | 1=requires judgment calls, 5=rules-based decisions | Can logic be codified |
| Testing ease | 1=hard to test safely, 5=easy to test in isolation | Can you validate without risk |
| Existing patterns | 1=novel, 5=similar automation exists to copy | Prior art available |
| Dependencies | 1=many external dependencies, 5=self-contained | Fewer moving parts |

**Feasibility Score** = weighted average of above factors.

## Step 4: Score Risk (Weight: 20%)

What can go wrong if automation has a bug?

| Factor | Score 1-5 | Description |
|--------|-----------|-------------|
| Blast radius | 5=limited scope, 1=affects all customers | Impact if automation goes wrong |
| Reversibility | 5=easily undone, 1=irreversible actions | Can mistakes be rolled back |
| Safety controls | 5=can add guardrails easily, 1=hard to limit | Ability to add circuit breakers |
| Data sensitivity | 5=non-sensitive, 1=handles PII/financial/credentials | Risk of data exposure |
| Failure mode | 5=fails safe (does nothing), 1=fails dangerous | What happens when automation breaks |

**Risk Score** = weighted average (higher is safer = better).

## Step 5: Score Maintainability (Weight: 10%)

How much ongoing effort does the automation need?

| Factor | Score 1-5 | Description |
|--------|-----------|-------------|
| Stability of inputs | 5=inputs rarely change, 1=APIs/formats change often | How often will it break |
| Team ownership clarity | 5=clear owner, 1=orphan risk | Who maintains it long-term |
| Complexity of logic | 5=simple, 1=complex branching and edge cases | Ease of understanding |
| Monitoring feasibility | 5=easy to monitor success/failure, 1=silent failures likely | Observability of automation |
| Documentation needs | 5=self-explanatory, 1=requires extensive docs | Knowledge transfer burden |

**Maintainability Score** = weighted average.

## Step 6: Calculate Composite Score

```
Final Score = (Value x 0.40) + (Feasibility x 0.30) + (Risk x 0.20) + (Maintainability x 0.10)
```

| Score Range | Recommendation |
|-------------|---------------|
| 4.0-5.0 | Automate immediately - high value, low risk, easy to build |
| 3.0-3.9 | Strong candidate - plan for next sprint/quarter |
| 2.0-2.9 | Moderate candidate - consider when capacity allows |
| 1.0-1.9 | Poor candidate - reconsider approach or defer indefinitely |

## Step 7: Build the Prioritized Backlog

Rank all scored candidates and present:

| Rank | Automation | Value | Feasibility | Risk | Maintain | Total | Effort (days) | Annual Savings (hrs) |
|------|-----------|-------|-------------|------|----------|-------|--------------|---------------------|
| 1 | Auto-scale on schedule | 4.5 | 4.8 | 4.2 | 4.0 | 4.45 | 3 | 200 |
| 2 | Cert rotation | 4.2 | 4.0 | 3.5 | 4.5 | 4.05 | 5 | 150 |
| 3 | Access provisioning | 3.8 | 3.5 | 3.0 | 3.2 | 3.48 | 10 | 300 |

**Implementation recommendation:**
- Sprint 1: Top 2-3 items (quick wins with highest composite score).
- Sprint 2: Next 3-5 items.
- Backlog: Remaining items for future sprints.
- Rejected: Items scoring < 2.0 (document why, revisit in 6 months).

## Step 8: Build the Business Case

For the top candidates, produce executive-friendly justification:

```
Automation: [Name]
Problem: [Current manual process and its cost]
Solution: [What the automation will do]
Investment: [Development effort in person-days]
Returns:
  - Time saved: X hours/month
  - Cost saved: $X/year (time x loaded cost per hour)
  - Risk reduction: [fewer human errors, faster MTTR]
  - Scale enablement: [supports N% growth without adding headcount]
Break-even: [X weeks/months]
```

## Output

Produce an automation priority report:
1. **Scored Candidate Table**: All candidates with per-dimension scores and composite score.
2. **Top 5 Recommendations**: Detailed cards with value, effort, timeline, and business case.
3. **Priority Matrix Chart**: Plot of Value vs Feasibility with candidates as points (bubble size = time savings).
4. **Quick Wins**: Candidates with score > 4.0 and effort < 5 days.
5. **Deferred Items**: Low-score candidates with explanation of why.
6. **Capacity Plan**: How many automation items can be delivered per quarter with available capacity.
7. **Expected Toil Reduction**: Projected toil percentage after implementing top N automations.