---
name: telemetry-coverage-and-webhook-health
agent_type: "Generic"
description: >
  Audits whether connected telemetry sources cover the critical request paths and
  whether the webhooks that trigger investigations are configured and firing. Use
  this skill to catch silent gaps: an uninstrumented path, or a broken webhook
  that means incidents never auto-investigate.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Telemetry Coverage and Webhook Health

Two silent failures undermine an otherwise healthy observability setup. First, a
critical request path that no connected telemetry source watches, so a real
problem produces no signal. Second, a webhook that once triggered investigations
but has quietly stopped delivering, so incidents fire in the monitoring tool yet
never reach the agent. Both are invisible until an incident exposes them. This
skill audits for both before that happens.

## Sources

Read-only reasoning over platform-surfaced data:

- Connected telemetry integrations (CloudWatch, Datadog, Dynatrace, Splunk,
  Grafana, New Relic) surfaced on the Agent Space, used to see what each source
  instruments.
- AWS-native topology via use_aws and CloudWatch to enumerate the actual request
  paths and components that should be covered.
- Webhook configuration and recent investigation history (list_investigations) to
  confirm which triggers exist and which have recently fired.

This skill recommends only. It does not create or repair webhooks or integrations.

## Method

1. Map the critical paths. From AWS reads, enumerate the customer-facing request
   paths and their components: edge, load balancer, compute, data store, and key
   dependencies.
2. Overlay telemetry coverage. For each component, record which connected sources
   emit signals for it. Mark components watched by zero sources.
3. Rank coverage gaps by exposure. Weight uncovered components by how close they
   sit to customer traffic and how central they are to the path.
4. Inventory the trigger webhooks. List the webhooks that are supposed to start
   investigations from telemetry sources. Note the source, target, and
   authentication posture of each.
5. Check firing health. Compare configured webhooks against recent investigation
   history. A webhook with alarms firing in its source but no corresponding
   triggered investigations is a suspected silent break.
6. Distinguish quiet from broken. A webhook with no recent activity may simply
   have had no incidents. Separate healthy-but-quiet from configured-but-not-firing
   using the source's own alarm activity.
7. Assess authentication. Flag trigger webhooks that lack authentication or use
   shared secrets that appear stale.

## Output

Produce a coverage and webhook report:

1. Path Coverage Map: critical components against the sources watching them, with
   uncovered components highlighted.
2. Coverage Gap List: uncovered paths ranked by customer exposure.
3. Webhook Inventory: each trigger webhook with source, target, and auth posture.
4. Firing Health: webhooks suspected broken (source alarming, no triggered
   investigations) versus healthy-but-quiet.
5. Recommendations: instrumentation to add and webhooks to verify or re-secure.
   All recommend-only.
