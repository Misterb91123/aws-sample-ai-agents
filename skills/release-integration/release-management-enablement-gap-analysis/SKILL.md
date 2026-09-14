---
name: release-management-enablement-gap-analysis
agent_type: "Generic"
description: A meta and adoption view of AWS DevOps Agent release management across
  the organization: which repositories and teams have adopted Release Readiness
  Reviews, Release Testing, and the CI/CD integration, and where the enablement
  gaps are. Combines the signals from the individual release-integration skills
  into one program-level scorecard. Use this to drive rollout and close the last
  unenrolled corners of the fleet.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Release Management Enablement Gap Analysis

Use this skill for the program-level picture. Individual skills answer narrow
questions; this one rolls them up to show how far release management has spread and
where it has not. It reports which teams and repositories have the CI/CD
integration, readiness reviews, and release testing, and which are still dark. It
is read-only and recommend-only: it reports enablement state and gaps, it does not
enroll or configure anything.

## Sources

- Agent Space associations for the CI/CD providers to see which repositories and
  pipelines are connected at all.
- Release Readiness Review and Release Testing history to see which repos and
  services actually use each capability.
- Source-control association for the full inventory of repositories and teams, so
  enrolled can be compared against total.
- AWS-native reads (use_aws, CloudWatch) for the set of deployed services that
  should be under release management.
- Comms/ticketing associations only for reporting the rollout status.

## Method

1. Build the denominator: all repositories, teams, and deployed services that are
   candidates for release management.
2. For each candidate, record three enablement signals: CI/CD integration
   connected, readiness reviews in use, and release testing in use.
3. Classify each repo or team as fully enabled, partially enabled, or not enabled,
   based on which of the three signals are present.
4. Identify the specific missing capability for partially enabled repos (for
   example connected but no release testing).
5. Rank the gaps by service criticality and deploy frequency so the highest-value
   rollouts come first.
6. Track enablement trend over time to show whether adoption is growing.
7. Summarize into a program scorecard with a prioritized rollout backlog.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the
"AWS Documentation MCP Server" (from the awslabs/mcp project) is useful for
pulling the current enablement and setup steps so the rollout backlog references
accurate procedures, and a custom source-control MCP server that wraps the team's
GitHub, GitLab, or Azure DevOps API lets the agent read the full repo and team
inventory that forms the denominator. To enable, connect the MCP server to the
Agent Space through the DevOps Agent MCP-server integration, after which this
custom agent can call the MCP's tools during its run. Use any MCP in addition to
the regular sources - the CI/CD and source-control associations, review and
testing history, and AWS reads via use_aws/CloudWatch - never instead of them.
AWS MCP server names and availability evolve, so verify the current server before
relying on it.

## Output

Provide an enablement scorecard:
1. Program-level counts of fully, partially, and not-enabled repos and teams.
2. Per-repo/per-team enablement matrix across the three capabilities.
3. Missing-capability detail for partially enabled candidates.
4. Prioritized rollout backlog ranked by criticality and deploy frequency.
5. Enablement trend over time with recommendations to close remaining gaps.
