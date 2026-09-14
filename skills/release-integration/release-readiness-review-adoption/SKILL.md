---
name: release-readiness-review-adoption
agent_type: "Generic"
description: Measures adoption of AWS DevOps Agent Release Readiness Reviews across
  the codebase. Reports how many merges and pull requests went through a readiness
  review versus bypassed one, surfaces the recurring categories of findings the
  reviews raise, and lists repositories that are not enrolled at all. Use this to
  see whether the review gate is actually being used and where cross-repo
  dependency, standards, and access-control risks are slipping through.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Release Readiness Review Adoption

Use this skill to understand how consistently Release Readiness Reviews are being
used. A readiness review is a code review for cross-repo dependency risk,
standards, and access-control correctness, plus automated verification testing
that builds, runs, and tests the change in an agent-managed verification
environment. This skill is read-only and recommend-only: it reports adoption and
finding trends, it does not enforce or change any gate.

## Sources

- Release Readiness Review history the platform surfaces: which PRs and merges
  were reviewed, the verdicts, and the findings raised per review.
- Source-control association data (GitHub, GitLab, Azure DevOps) for the full set
  of merges and PRs, so reviewed can be compared against total.
- Repository enrollment state from the pipeline and source-control associations
  to identify repositories with no reviews configured.
- Pipeline/deploy correlation to see whether bypassed changes still reached AWS.
- Comms/ticketing associations only to see where review outcomes were posted.

## Method

1. Pull the total set of merges and PRs over the window from the source-control
   association, then the subset that had a Release Readiness Review.
2. Compute adoption rate overall and per repository and per team. Flag repos with
   low or zero adoption.
3. Identify bypassed changes: merges or deploys that reached AWS with no
   associated review, and rank by the risk of what they touched.
4. Categorize review findings (cross-repo dependency risk, standards violations,
   access-control correctness, verification-test failures) and rank by frequency.
5. Track recurring finding categories over time to show whether the same issues
   keep reappearing.
6. List unenrolled repositories and estimate their exposure from recent deploy
   activity.
7. Summarize adoption, bypass, and finding trends into one view.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill,
connecting a custom source-control MCP server that wraps the team's GitHub,
GitLab, or Azure DevOps API lets the agent read merge history, PR metadata,
required-check configuration, and branch protection directly, which sharpens the
reviewed-versus-bypassed comparison and the unenrolled-repo list. No AWS-owned
MCP server is strictly required for adoption analysis; the value here is the
source-control MCP. To enable, connect the MCP server to the Agent Space through
the DevOps Agent MCP-server integration, after which this custom agent can call
the MCP's tools during its run. Use it in addition to the regular sources -
review history, AWS reads via use_aws/CloudWatch, and connected pipeline and
comms integrations - never instead of them. AWS MCP server names and availability
evolve, so verify the current server before relying on it.

## Output

Provide an adoption report:
1. Overall and per-repo/per-team adoption rate for readiness reviews.
2. Bypass list: unreviewed merges and deploys ranked by risk of what they touched.
3. Recurring finding categories with frequency and trend over time.
4. Unenrolled repository list with estimated exposure.
5. Recommendations to raise adoption and reduce recurring findings.
