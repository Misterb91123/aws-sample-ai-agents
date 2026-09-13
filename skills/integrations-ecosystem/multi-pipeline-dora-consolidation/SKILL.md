---
name: multi-pipeline-dora-consolidation
agent_type: "Generic"
description: >
  Computes the DORA four keys (deployment frequency, lead time for changes,
  change-failure rate, and mean time to restore) unified across GitHub Actions,
  GitLab CI/CD, and Azure DevOps. Use this skill for organizations whose teams use
  different CI systems and need one comparable delivery-performance view.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Multi-Pipeline DORA Consolidation

DORA metrics only mean something when they are measured the same way everywhere.
In an organization where one team ships through GitHub Actions, another through
GitLab CI/CD, and a third through Azure DevOps, each tool reports delivery data in
its own shape. This skill normalizes deploy and incident data across all three
into the four keys so teams can be compared fairly and trends read across the
whole org.

## Sources

Read-only reasoning over platform-surfaced data:

- Deployment events tracked from connected pipeline integrations (GitHub Actions,
  GitLab CI/CD, Azure DevOps) on the Agent Space, for frequency and lead-time
  inputs.
- Incident and resource-health timelines from CloudWatch and use_aws, plus
  investigation history (list_investigations), for change-failure and restore-time
  inputs.
- Any connected ticketing association (ServiceNow) surfaced by the platform, used
  to corroborate incident start and restore times.

This skill computes and reports only. It does not modify pipelines or records.

## Method

1. Set scope and window. Choose the services, teams, and reporting period. Confirm
   which pipeline source each service deploys through.
2. Normalize a deploy event. Define one canonical deploy record across all three
   tools: service, environment, timestamp, version, and success or failure. Map
   each tool's native event onto it.
3. Compute deployment frequency. Count successful production deploys per service
   and per team over the window, then aggregate to the org level.
4. Compute lead time for changes. Measure from code committed to running in
   production using the pipeline timestamps, reporting the median and tail.
5. Compute change-failure rate. Divide deploys that led to a degradation or
   rollback (from health timelines and incident correlation) by total deploys.
6. Compute mean time to restore. Measure from incident start to restore using the
   resource-health timeline corroborated by ticketing, per service and org-wide.
7. Reconcile cross-tool bias. Note where a tool's definitions differ (what counts
   as a deploy, how environments are labelled) so comparisons stay fair.

## Output

Produce a consolidated DORA report:

1. Four Keys Table: deployment frequency, lead time, change-failure rate, and MTTR
   per team and rolled up org-wide.
2. Source Normalization Notes: how each tool's events mapped to the canonical
   deploy record and any definitional caveats.
3. Trend View: how each key moved over recent periods.
4. Outliers: teams or services dragging a key up or down.
5. Recommendations: where to focus delivery-performance improvement, and
   measurement gaps to close. Recommend-only.
