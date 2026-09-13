---
name: release-freeze-and-change-collision-detection
agent_type: "Generic"
description: >
  Cross-references deploy events from connected pipelines against change-freeze
  windows and ServiceNow change tickets to flag unauthorized releases and colliding
  changes. Use this skill during freeze periods or change audits to find deploys
  that shipped without approval or that overlapped on the same resources.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Release Freeze and Change Collision Detection

Freeze windows and change tickets exist to keep risky work off production at the
wrong time and to keep two teams from changing the same thing at once. Neither
control is worth much if nobody checks it after the fact. This skill compares what
actually deployed against the freeze calendar and the change record, then flags
the releases that broke the rules or collided with each other.

## Sources

Read-only reasoning over platform-surfaced data:

- Deployment events tracked from connected pipeline integrations (GitHub Actions,
  GitLab CI/CD, Azure DevOps) on the Agent Space.
- Connected ServiceNow ticketing association for change requests, their approval
  state, and their scheduled windows.
- CloudWatch and use_aws reads to confirm which resources a deploy actually
  touched.

This skill detects and reports only. It does not block, approve, or roll back
anything.

## Method

1. Load the freeze calendar and change records. Gather the active and recent
   change-freeze windows and the ServiceNow change tickets with their approval
   status and scheduled times.
2. Assemble the actual deploy timeline. Collect deploy events across all connected
   pipeline sources for the same period, normalized to one timezone.
3. Detect freeze violations. Flag any deploy whose timestamp falls inside a freeze
   window without a documented exception.
4. Detect unauthorized deploys. Flag deploys with no matching approved change
   ticket, and tickets in a non-approved state that nonetheless shipped.
5. Detect collisions. Find deploys or changes that targeted the same resource or
   service within an overlapping window, since concurrent changes make failures
   hard to attribute.
6. Detect schedule drift. Flag approved changes that shipped well outside their
   scheduled window, since that undermines the control even when approved.
7. Classify severity. Rank findings by blast radius of the touched resources and
   by whether the deploy coincided with any degradation.

## Output

Produce a change-governance report:

1. Freeze Violations: deploys inside freeze windows lacking an exception.
2. Unauthorized Deploys: deploys with no approved change ticket, and shipped
   non-approved tickets.
3. Collisions: overlapping changes on shared resources, with the teams involved.
4. Schedule Drift: approved changes shipped outside their window.
5. Recommendations: process gaps to tighten and specific releases to review. All
   recommend-only.
