---
name: monitor-root-cause-recall
agent_type: "Generic"
description: Summarizes the recurring root-cause history AWS DevOps Agent keeps
  per monitor (the managed monitors memory store) to identify repeat-offender
  alarms, dominant cause categories, and alarms whose incidents cluster on one
  fixable cause. Use this skill to turn per-alarm incident history into a
  prioritized list of the alarms worth fixing at the source and the alarms that
  are chronically noisy. It reads memory and live alarm state; it does not modify
  alarms or memory.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Monitor Root-Cause Recall

Use this skill to read the per-monitor root-cause history the platform builds and
turn it into a prioritized "fix at the source" list. Each memory file in the
monitors store corresponds to one alarm and records the cause categories that
have produced incidents for it, with per-investigation evidence.

## Memory stores this skill reads

Read-only. Managed stores maintained by the platform's learning agent.

- `monitors`: per-monitor recurring root-cause history - for each alarm, the
  cause categories that produced incidents and the supporting evidence. Note that
  entries are pruned when they have no updates for two weeks, so recall reflects
  roughly the trailing two weeks of activity.
- `reflections` (if present): lessons from investigation feedback about what past
  investigations missed, which can correct a misattributed cause.

## Method

1. Enumerate the monitors store: list each alarm with a history entry and read
   its cause categories and incident counts.
2. Cross-check with live alarm state using `list_cloudwatch_alarms` so the
   summary reflects alarms that still exist and their current state; drop history
   for alarms that no longer exist and note them.
3. Classify each alarm:
   - Single-cause repeat offender: most incidents share one cause category - a
     candidate to fix at the source (the cause), not by tuning the alarm.
   - Multi-cause chronic: incidents span many causes - investigate why it fires
     so broadly, or whether the threshold is wrong.
   - Stable: few or no recent incidents.
4. Apply reflections. If a reflection indicates a past root cause was
   misattributed for an alarm, prefer the corrected cause and note the
   correction.
5. Prioritize: rank single-cause repeat offenders by incident count and by the
   severity of the underlying cause, because those give the largest reduction in
   incident volume per fix.

## Output

Produce a table of alarms with: incident count in the recall window, dominant
cause category and its share, classification (single-cause repeat offender,
multi-cause chronic, stable), any reflection correction, and a recommended action
(fix the source cause, retune the alarm, or no action). Note the two-week recall
window as a freshness caveat. Do not modify alarms or memory; recommend actions
for a human.
