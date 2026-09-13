---
name: incident-notification-routing-audit
agent_type: "Generic"
description: >
  Audits that alarm and finding severities map to the right PagerDuty escalation
  policy, Slack channel, and ServiceNow assignment group, and finds severities that
  route nowhere. Use this skill to verify that when something fires, the right
  humans are actually reached.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Incident Notification Routing Audit

An alarm is only useful if it reaches someone who can act. Routing tends to rot:
teams reorganize, channels are archived, escalation policies change, and a
severity level quietly ends up pointing at nobody. This skill traces each severity
from the signal source through to its destination in PagerDuty, Slack, and
ServiceNow, and flags every path that dead-ends.

## Sources

Read-only reasoning over platform-surfaced data:

- CloudWatch alarms and their configured actions, plus security and other findings,
  read through use_aws, to establish the severities that exist and where they send.
- Connected communication and ticketing associations (PagerDuty, Slack,
  ServiceNow) surfaced on the Agent Space, used to see the escalation policies,
  channels, and assignment groups that exist as targets.

This skill audits and recommends only. It does not change alarm actions, escalation
policies, or routing rules.

## Method

1. Enumerate severities and sources. List the alarm and finding severities in use
   and where each is emitted from.
2. Trace each route. For every severity, follow the configured action to its
   destination: which PagerDuty escalation policy, which Slack channel, which
   ServiceNow assignment group.
3. Find routes to nowhere. Flag severities with no destination configured, and
   destinations that no longer exist (archived channel, deleted policy, retired
   group).
4. Check severity-to-urgency fit. Confirm high severities reach an escalation
   policy that actually pages a human, not just a low-urgency channel, and that
   low severities are not paging people at night.
5. Find duplicate routing. Identify a single event that fans out to multiple pages
   for the same responder, a common source of alert fatigue.
6. Check ownership alignment. Confirm the destination group or policy owns the
   service that emitted the signal, so pages do not land on a team that cannot act.
7. Rank findings. Order by how severe the mis-route is: a critical severity that
   routes nowhere ranks above a cosmetic mismatch.

## Output

Produce a routing-audit report:

1. Routing Matrix: severity by source mapped to its PagerDuty, Slack, and
   ServiceNow destination.
2. Dead Ends: severities that route nowhere or point at destinations that no longer
   exist.
3. Urgency Mismatches: high severities that do not page, and low severities that do.
4. Duplicate and Misowned Routes: fan-out duplicates and destinations owned by the
   wrong team.
5. Recommendations: routing corrections per severity, ranked by risk. All
   recommend-only.
