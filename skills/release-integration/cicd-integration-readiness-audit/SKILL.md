---
name: cicd-integration-readiness-audit
agent_type: "Generic"
description: Audits whether the AWS DevOps Agent is correctly integrated with the
  team's CI/CD providers (GitHub Actions, GitLab CI-CD, Azure DevOps) for release
  management. Checks Agent Space association health, repository and pipeline
  coverage, permission scopes, webhook wiring, and whether the
  aws-actions/devops-agent-qa trigger is present in deployment pipelines. Produces
  a per-repo readiness scorecard so gaps are fixed before teams rely on release
  readiness reviews and release testing.
version: "1.0.0"
last_updated: "2026-09-12"
---

# CI/CD Integration Readiness Audit

Use this skill to confirm that release management is actually wired up end to end.
Release Readiness Reviews and Release Testing only add value when the pipeline
association is healthy, the right repositories are covered, and the post-deploy
QA trigger is present. This audit is read-only and recommend-only: it reports the
state of the integration and the gaps, it does not change any pipeline or setting.

## Sources

- Agent Space associations for pipelines (GitHub Actions, GitLab CI-CD, Azure
  DevOps): connection status, last-seen event, and repo/pipeline enrollment that
  the platform surfaces.
- Pipeline run and deploy metadata correlated to AWS resource impact through the
  connected pipeline integration.
- Repository contents the platform can read: workflow and pipeline definition
  files that would contain the aws-actions/devops-agent-qa step.
- AWS-native reads (use_aws, CloudWatch) to confirm the deploy targets the
  integration claims to track actually exist.
- Comms/ticketing associations (Slack, ServiceNow, PagerDuty) only to confirm
  where results are expected to land.

## Method

1. Enumerate every connected CI/CD association and record connection health, the
   last event timestamp, and any auth or token warnings the platform surfaces.
2. For each provider, list enrolled repositories and pipelines, then compare
   against the set of repositories the team expects to be under release
   management. Flag unenrolled or stale repositories.
3. Inspect permission scopes granted to each association. Flag scopes that are
   broader than needed and scopes that are too narrow to support reviews or
   testing.
4. Verify webhook wiring: confirm the events that trigger reviews and
   investigations are configured and that recent events were actually received.
5. Scan each deploy pipeline definition for the aws-actions/devops-agent-qa step
   that triggers release testing after deployment. Record present, missing, or
   misconfigured.
6. Cross-check that deploy targets referenced by the pipeline exist in AWS and are
   the ones the integration is correlating against.
7. Assemble a per-repo readiness scorecard rating connection, coverage,
   permissions, webhooks, and QA-trigger presence.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the
highest-value addition is a custom MCP server that wraps the team's own
source-control or CI provider API (GitHub, GitLab, or Azure DevOps), so the agent
can read branch protection, required checks, webhook delivery history, and token
scopes directly rather than inferring them. The "AWS Documentation MCP Server"
(from the awslabs/mcp project) is useful for pulling current setup and
integration guidance during the audit. To enable, connect the MCP server to the
Agent Space through the DevOps Agent MCP-server integration, after which this
custom agent can call the MCP's tools during its run. Use any MCP in addition to
the regular sources - the pipeline associations, AWS infra reads via
use_aws/CloudWatch, and connected comms integrations - never instead of them.
Note that AWS MCP server names and availability evolve, so verify the current
server before relying on it.

## Output

Provide an integration readiness report:
1. Per-repo scorecard covering connection, coverage, permissions, webhooks, and
   the devops-agent-qa trigger, with a pass/warn/fail rating each.
2. List of unenrolled or stale repositories and pipelines.
3. Permission-scope findings (too broad or too narrow) with recommended scope.
4. Webhook and QA-trigger gaps with the exact pipeline files to fix.
5. Prioritized remediation checklist ordered by release risk.
