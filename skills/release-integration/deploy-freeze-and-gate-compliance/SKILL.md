---
name: deploy-freeze-and-gate-compliance
agent_type: "Generic"
description: Scores deployments fleet-wide for compliance with change-management
  rules across CI/CD providers - deploys that violated a freeze window and deploys
  that skipped a required gate such as a readiness review, approval, or release
  test. Produces a compliance scorecard by team and repository. Use this to see
  where the release process is being followed and where it is being bypassed.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Deploy Freeze and Gate Compliance

Use this skill to check whether deploys followed the rules. Freeze windows and
required gates exist to reduce risk; a deploy that shipped during a freeze or
skipped a required review undermines that. This skill scores compliance across the
fleet. It is read-only and recommend-only: it reports violations and scores, it
does not block or reverse any deploy.

## Sources

- Pipeline associations (GitHub Actions, GitLab CI-CD, Azure DevOps) for deploy
  events with timestamps and the gates each deploy passed or skipped.
- Release Readiness Review and Release Testing history to confirm which required
  gates actually ran for each deploy.
- The team's freeze-window and change-policy definitions where the platform can
  read them (calendar, config, or change-management association).
- AWS-native reads (use_aws) to confirm deploys actually landed in the account.
- Comms/ticketing associations for approvals and change records tied to a deploy.

## Method

1. Enumerate all deploy events across providers over the window with timestamps
   and target environments.
2. Overlay freeze windows and flag any deploy that landed inside a freeze without
   a documented exception.
3. For each deploy, determine the required gates (readiness review, approval,
   release test) and check which actually ran.
4. Flag gate skips: deploys that reached prod without a required review, approval,
   or test.
5. Correlate approvals and change records from comms/ticketing to verify a claimed
   exception is real.
6. Score compliance per deploy, then roll up by repository and by team.
7. Highlight repeat offenders and the most frequently skipped gate.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill a
custom CI or change-management MCP server that wraps the provider API or the
team's change/freeze calendar is the most relevant addition: it lets the agent
read exact deploy timestamps, gate configuration, and freeze definitions rather
than inferring them. No AWS-owned MCP server is strictly required here. To enable,
connect the MCP server to the Agent Space through the DevOps Agent MCP-server
integration, after which this custom agent can call the MCP's tools during its
run. Use it in addition to the regular sources - AWS reads via use_aws, review and
testing history, and the connected pipeline and comms integrations - never
instead of them. AWS MCP server names and availability evolve, so verify the
current server before relying on it.

## Output

Provide a compliance scorecard:
1. Deploys that landed inside a freeze window without a documented exception.
2. Deploys that skipped a required gate, with which gate was skipped.
3. Compliance score per repository and per team.
4. Repeat offenders and the most frequently skipped gate.
5. Recommendations to tighten enforcement of freezes and required gates.
