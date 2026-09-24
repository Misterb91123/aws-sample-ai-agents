---
name: omni-space-and-slo-coverage-audit
agent_type: "Generic"
description: Audits Amazon CloudWatch Omni coverage - which applications and
  services have an Omni Space with declared service-health targets (availability,
  latency budget, error-rate threshold) versus which are discovered but
  unmonitored. Use this skill to find services that Omni's automatic topology
  discovery surfaces but that no team Space owns or has set targets for, so
  application-centric observability is not left blind. It reasons over
  CloudWatch-native reads plus Omni-surfaced context; it recommends coverage, it
  does not create Spaces or change targets.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Omni Space and SLO Coverage Audit

Use this skill to check that Amazon CloudWatch Omni actually covers the
applications a team owns. Omni organizes observability by application: it
auto-discovers services, maps dependencies, and lets teams declare what matters
(availability targets, latency budgets, error-rate thresholds) in a per-team
Space. The gap this skill finds is the service that Omni discovered but that sits
in no Space, or a Space with no declared targets - application-centric monitoring
that looks complete but is not.

## Sources

Read-only. CloudWatch Omni does not expose a confirmed dedicated use_aws action
set today, so treat the Omni-specific reads as data the platform surfaces and
lean on the CloudWatch-native signals below; do not assume an Omni API that has
not been verified.

- use_aws for the CloudWatch-native inventory that Omni builds on: Application
  Signals services and SLOs, CloudWatch alarms, and the resource inventory from
  tags and AWS Config that Omni uses for discovery.
- The Omni Space and target context the platform surfaces (which applications are
  grouped into a Space and which targets are declared), where available.
- Tags and ownership metadata to map a discovered service to an owning team.

## Method

1. Build the discovered-service inventory: the services Omni would discover from
   telemetry and AWS Config (Application Signals services, tagged workloads,
   topology nodes).
2. Determine Space membership: for each discovered service, whether it belongs to
   an Omni Space and which team owns that Space; flag services in no Space.
3. Check declared targets: for each covered service, whether availability,
   latency-budget, and error-rate targets are declared; flag Spaces or services
   with no targets (Omni can adapt alarms, but with nothing declared there is no
   objective to adapt to).
4. Cross-check with Application Signals SLOs and CloudWatch alarms so a service
   with real reliability targets elsewhere but none in Omni is surfaced as a
   consolidation gap, not a true blind spot.
5. Rank the gaps by criticality: unowned production services first, then
   production services with no declared targets, then non-production.
6. Recommend the specific coverage action per gap (assign to a Space, declare the
   missing target) for a human to apply; do not create or modify Spaces or
   targets.

## MCP augmentation

CloudWatch Omni is reached through its own workspace and the blog points to the
AWS MCP Server for Omni APIs, documentation, and regional availability. Where a
CloudWatch or Omni MCP server is available, connect it to the Agent Space to read
Space membership and declared targets directly, and use the AWS Documentation MCP
Server for current Omni setup guidance. Use any MCP in addition to the
CloudWatch-native use_aws reads, never instead of them, and do not assume an Omni
API that the MCP does not actually expose. AWS MCP server names and availability
evolve; verify before relying on one.

## Output

Produce a coverage report: the discovered-service inventory; a per-service table
of Space membership, owning team, and declared targets (availability, latency,
error rate); the gaps ranked by criticality (unowned, no-target, non-production);
and a recommended coverage action per gap. State that the skill recommends
coverage and does not create Spaces or change targets. Reference services and
accounts by identifier.
