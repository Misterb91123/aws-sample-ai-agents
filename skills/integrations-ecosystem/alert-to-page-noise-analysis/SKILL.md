---
name: alert-to-page-noise-analysis
agent_type: "Generic"
description: >
  Measures how many alerts became human pages versus auto-resolved, broken down by
  routing target, to give alarm-fatigue work the paging half of the story. Use this
  skill alongside alarm-noise reduction when the team needs to know which routes
  wake people up for nothing.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Alert to Page Noise Analysis

Alarm-noise work usually counts alarms. It rarely counts pages. Yet the pain that
drives burnout is being paged, especially for something that resolved itself before
anyone opened a laptop. This skill measures the conversion from alert to page per
routing target and isolates the routes that generate pages with no action taken,
so fatigue work targets the right destinations.

## Sources

Read-only reasoning over platform-surfaced data:

- CloudWatch alarms and their state-change history through use_aws, to count alerts
  and see which auto-resolved.
- Connected PagerDuty and Slack associations surfaced on the Agent Space, used to
  see which alerts escalated to a page or channel notification and to which target.
- Connected ServiceNow association where alerts create incident records, to
  corroborate whether a human acted.

This skill measures and recommends only. It does not change alarms or routing.

## Method

1. Set the window and targets. Choose the analysis period and enumerate the routing
   targets (escalation policies, channels, assignment groups) in scope.
2. Count alerts per target. For each target, count the alerts that routed to it over
   the window.
3. Split paged versus auto-resolved. Classify each alert as escalated to a human
   page, delivered as a notification only, or auto-resolved before escalation.
4. Measure actionability. For paged alerts, determine whether a human acted (an
   acknowledgement, a ticket update, a corresponding investigation) or whether it
   closed with no action.
5. Compute noise ratios per target. For each target, report page rate, auto-resolve
   rate, and no-action page rate. High no-action page rate marks the noisiest routes.
6. Find flapping and repeat offenders. Identify alarms that page repeatedly and
   auto-resolve, and off-hours pages that never needed a human.
7. Correlate with alarm-noise findings. Tie the paging view back to the specific
   alarms so remediation targets both the alarm and its route.

## Output

Produce a paging-noise report:

1. Conversion Table: per target, alerts, pages, auto-resolves, and no-action pages.
2. Noisiest Routes: targets ranked by no-action page rate.
3. Repeat Offenders: alarms that page and self-resolve, with off-hours emphasis.
4. Alarm Linkage: the specific alarms behind each noisy route.
5. Recommendations: routes to re-tune, alarms to adjust, and pages to downgrade to
   notifications. All recommend-only.
