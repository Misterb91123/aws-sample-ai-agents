---
name: ticket-hygiene-and-mttr-reconciliation
agent_type: "Generic"
description: >
  Reconciles ServiceNow incident and change records against the actual resource
  timeline to find missing tickets, stale open tickets, and MTTR discrepancies. Use
  this skill during operational reviews when the ticketing record and reality have
  drifted apart.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Ticket Hygiene and MTTR Reconciliation

The ticketing system is supposed to be the record of what happened, but it is
maintained by humans under pressure and drifts from reality. Real incidents go
unticketed, resolved tickets stay open for weeks, and the recorded restore time
does not match when metrics actually recovered. Any MTTR computed from that record
is wrong. This skill reconciles ServiceNow against the resource timeline and
surfaces the discrepancies.

## Sources

Read-only reasoning over platform-surfaced data:

- Connected ServiceNow ticketing association surfaced on the Agent Space:
  incident and change records with their open, resolved, and closed timestamps.
- CloudWatch metrics, alarms, and logs through use_aws to establish when
  degradation actually began and when it recovered.
- Investigation history (list_investigations) to corroborate incident timelines.

This skill reconciles and reports only. It does not open, update, or close tickets.

## Method

1. Set the review window and scope. Choose the services and period to reconcile.
2. Pull the ticket record. Gather ServiceNow incidents and changes in scope with
   their state transitions and timestamps.
3. Build the reality timeline. From alarms, metrics, and investigations, derive
   the actual degradation-start and recovery times for each event.
4. Find missing tickets. Flag periods of clear degradation in the resource timeline
   with no corresponding incident ticket.
5. Find stale tickets. Flag incidents still open although the resource recovered
   long ago, and changes left open past their implementation.
6. Reconcile MTTR. For each matched incident, compare recorded resolution time
   against metric recovery. Flag material gaps in either direction and note whether
   recorded MTTR is systematically optimistic or pessimistic.
7. Find orphans and duplicates. Flag tickets that reference resources that do not
   exist and multiple tickets covering one event.

## Output

Produce a reconciliation report:

1. Ticket-to-Reality Table: each incident with recorded times beside actual
   degradation and recovery times.
2. Missing Tickets: real incidents with no ticket.
3. Stale Tickets: open records for events already resolved.
4. MTTR Discrepancies: gaps between recorded and actual restore time, with the
   direction of bias.
5. Recommendations: hygiene fixes and a corrected MTTR basis for reporting. All
   recommend-only.
