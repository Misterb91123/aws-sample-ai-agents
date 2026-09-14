---
name: merge-to-deploy-gap-analysis
agent_type: "Generic"
description: Analyzes the gap between what was merged and what was deployed across
  CI/CD providers. Finds commits that merged to a release branch but never reached
  a deployed environment, and deploys that landed in AWS with no reviewed pull
  request behind them. Use this to catch undelivered work, drifted environments,
  and out-of-band deploys that skipped the normal review path.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Merge-to-Deploy Gap Analysis

Use this skill to reconcile the two ends of the release path. Merges that never
deploy mean work is stranded; deploys with no reviewed PR mean changes bypassed
governance. Both are risks. This skill is read-only and recommend-only: it reports
the gaps in both directions, it does not deploy, revert, or change anything.

## Sources

- Source-control associations (GitHub, GitLab, Azure DevOps) for merge and PR
  history on release branches.
- Pipeline associations for deploy events and the commit each deploy carried.
- Release Readiness Review history to know which commits had a reviewed PR.
- AWS-native reads (use_aws, CloudWatch) to confirm the running commit or image in
  each environment.
- Comms/ticketing associations only for reporting.

## Method

1. Build the merged set: commits merged to release branches over the window from
   the source-control association.
2. Build the deployed set: commits or image digests that reached each environment
   from the pipeline association and AWS reads.
3. Compute merged-but-not-deployed: merges with no corresponding deploy within the
   expected window, and rank by age and by criticality of the change.
4. Compute deployed-but-not-reviewed: deploys whose commit has no reviewed PR or
   readiness review behind it, and rank by what the deploy touched.
5. Reconcile against the actual running commit in AWS to catch environments that
   drifted from the expected deployed set.
6. Attribute each gap to a repository, pipeline, and owning team.
7. Summarize both gap directions with likely causes (stuck pipeline, manual
   deploy, abandoned branch).

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill a
custom source-control MCP server that wraps the team's GitHub, GitLab, or Azure
DevOps API is the highest-value addition: it lets the agent read exact merge
timestamps, branch relationships, and PR-to-commit mappings needed to reconcile
merged against deployed with precision. No AWS-owned MCP server is strictly
required here. To enable, connect the MCP server to the Agent Space through the
DevOps Agent MCP-server integration, after which this custom agent can call the
MCP's tools during its run. Use it in addition to the regular sources - AWS reads
via use_aws/CloudWatch, review history, and the connected pipeline integrations -
never instead of them. AWS MCP server names and availability evolve, so verify
the current server before relying on it.

## Output

Provide a gap report:
1. Merged-but-not-deployed list ranked by age and change criticality.
2. Deployed-but-not-reviewed list ranked by what each deploy touched.
3. Environments that drifted from the expected deployed set.
4. Per-repo and per-team attribution of the gaps.
5. Recommendations to close each gap and prevent out-of-band deploys.
