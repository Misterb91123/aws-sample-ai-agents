---
name: webhook-trigger-coverage
agent_type: "Generic"
description: >
  Ensures the incident-triggering webhooks from connected telemetry and ticketing
  tools are present, authenticated, and actually invoking investigations. Use this
  skill to confirm the automatic-investigation path is wired end to end, so events
  that should start an investigation really do.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Webhook Trigger Coverage

The value of automatic investigation depends entirely on the webhooks that start
it. If a telemetry or ticketing tool can fire an event but no webhook carries it to
the agent, that whole class of incident is investigated late or not at all. This
skill audits the trigger webhooks for presence, authentication, and proof of
firing, so the automatic-investigation path is verified rather than assumed.

## Sources

Read-only reasoning over platform-surfaced data:

- Webhook registrations surfaced on the Agent Space for connected telemetry
  sources (CloudWatch, Datadog, Dynatrace, Splunk, Grafana, New Relic) and ticketing
  tools (ServiceNow, PagerDuty).
- Investigation history (list_investigations) to confirm which webhooks have
  actually invoked investigations recently.
- Alarm and finding activity in the source tools, read through use_aws where AWS
  native, to know when a trigger should have fired.

This skill audits and recommends only. It does not create, repair, or reconfigure
webhooks.

## Method

1. Enumerate the expected triggers. For each connected telemetry and ticketing
   source, list the event types that should start an investigation.
2. Inventory the registered webhooks. Match each expected trigger to a configured
   webhook. Flag expected triggers with no webhook as coverage gaps.
3. Check authentication. For each present webhook, confirm it authenticates the
   sender (signed payloads or a secret) and uses encrypted transport. Flag
   unauthenticated or plaintext webhooks.
4. Confirm firing. Cross-reference recent source activity against triggered
   investigations. A source that alarmed with no matching triggered investigation
   indicates a webhook that is present but not delivering.
5. Distinguish quiet from broken. Separate webhooks that simply had no qualifying
   events from those that had events and still did not fire.
6. Check payload adequacy. Flag webhooks that fire but deliver too little context to
   start a useful investigation.
7. Rank by exposure. Prioritize missing or broken triggers on the most critical
   services and highest severities.

## Output

Produce a trigger-coverage report:

1. Trigger Matrix: expected triggers per source mapped to their webhook, present or
   missing.
2. Coverage Gaps: expected triggers with no webhook.
3. Firing Health: webhooks present but not delivering (source active, no triggered
   investigation) versus healthy-but-quiet.
4. Security and Payload: unauthenticated, plaintext, or context-poor webhooks.
5. Recommendations: triggers to add, webhooks to verify or re-secure, ranked by
   exposure. All recommend-only.
