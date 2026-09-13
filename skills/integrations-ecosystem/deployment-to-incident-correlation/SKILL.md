---
name: deployment-to-incident-correlation
agent_type: "Generic"
description: >
  Correlates pipeline deploy events tracked across GitHub Actions, GitLab CI/CD,
  and Azure DevOps with resource health and incident timelines to attribute
  regressions to specific releases. Use this skill during or after an incident to
  answer whether a recent deploy caused the degradation and which one.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Deployment to Incident Correlation

The fastest question in an incident is often the most useful: did something ship
right before this started? When teams deploy through different CI systems, the
answer is scattered across GitHub Actions, GitLab CI/CD, and Azure DevOps. This
skill unifies the deploy timeline, lines it up against resource health and the
incident window, and attributes the regression to a specific release when the
evidence supports it.

## Sources

Read-only reasoning over platform-surfaced data:

- Deployment events tracked from connected code and pipeline integrations (GitHub
  Actions, GitLab CI/CD, Azure DevOps) surfaced on the Agent Space.
- CloudWatch metrics, alarms, and logs through use_aws to establish the resource
  health timeline.
- Investigation history (list_investigations) and any webhook-triggered incident
  context for the incident window.

This skill correlates and recommends only. It does not trigger rollbacks or modify
pipelines.

## Method

1. Fix the incident window. Establish first-signal and resolution timestamps from
   alarms, logs, and metric deviations, expanding earlier to catch the trigger.
2. Assemble the deploy timeline. Collect deploy events from all connected pipeline
   sources across the window, normalized to one timezone, with service, version,
   and pipeline identifiers.
3. Overlay health on deploys. Plot the resource health timeline against deploy
   markers. Look for a deploy immediately preceding the first signal on the
   affected service.
4. Score each candidate. For each nearby deploy, weigh proximity in time, whether
   it touched the affected service, and whether the failure mode matches the change
   (config, dependency, code path).
5. Rule out coincidence. A deploy near the incident is not proof. Check that the
   deployed service is on the failing path and that no unrelated trigger (traffic
   spike, dependency outage) better explains the timeline.
6. Attribute or exonerate. Name the release most likely responsible with its
   evidence, or state that no deploy correlates and the cause lies elsewhere.

## Output

Produce a correlation report:

1. Incident Window: first signal, resolution, and the metrics that define it.
2. Deploy Timeline: all deploys across GitHub Actions, GitLab CI/CD, and Azure
   DevOps in the window, with service and version.
3. Correlation Analysis: candidate deploys scored by proximity, service match, and
   failure-mode fit.
4. Attribution: the most likely release with supporting evidence, or a clear
   statement that no deploy correlates.
5. Recommendations: verification steps and, if applicable, a rollback or
   forward-fix consideration. Recommend-only.
