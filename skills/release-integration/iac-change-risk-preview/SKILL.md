---
name: iac-change-risk-preview
agent_type: "Generic"
description: For open infrastructure-as-code pull requests, previews the AWS-side
  risk of the proposed change by reading the plan or template - resource deletions
  and replacements, security-group openings, IAM broadening, and other high-impact
  edits. Use this alongside a Release Readiness Review to give reviewers a clear,
  plain-language picture of what the IaC change will do to live AWS resources
  before it merges.
version: "1.0.0"
last_updated: "2026-09-12"
---

# IaC Change Risk Preview

Use this skill to make infrastructure-as-code changes reviewable in terms of their
real AWS impact. A diff that looks small can delete a data store, replace a
resource, or open a security group to the internet. This skill reads the plan or
template and explains the risk in plain language. It is read-only and
recommend-only: it previews risk, it does not apply, approve, or block the change.

## Sources

- The IaC PR contents from the source-control association: CloudFormation
  templates, CDK synth output, or Terraform plan artifacts attached to the PR.
- AWS-native reads (use_aws) for the current state of the resources the change
  targets, so the delta is grounded in what exists today.
- Release Readiness Review context where the same PR is under review.
- Pipeline associations to see whether a plan step already runs in CI and where
  its output lives.
- Comms/ticketing associations only for reporting.

## Method

1. Locate the IaC artifact for the open PR (template, synthesized stack, or plan)
   from the source-control association or the CI plan step.
2. Parse the change set into actions per resource: create, update in place,
   replace, or delete.
3. Flag high-impact actions first: deletions or replacements of stateful resources
   (databases, buckets, volumes), IAM policy or role broadening, and
   security-group or network-ACL openings.
4. Ground each flagged change against current AWS state so reviewers see what is
   actually at risk (for example, is the bucket being deleted non-empty).
5. Identify data-loss and availability risks (replacement causing downtime,
   dropped retention).
6. Note security regressions: wider ingress, public access, weaker encryption, or
   expanded principals.
7. Produce a ranked, plain-language risk summary a reviewer can act on quickly.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the
"AWS IaC MCP Server" is the most relevant and is recommended by AWS for
CloudFormation and infrastructure-as-code agents: it helps the agent interpret
templates and change sets and reason about their AWS impact. The "AWS
Documentation MCP Server" can supply current resource-behavior and best-practice
guidance while assessing risk. To enable, connect the MCP server to the Agent
Space through the DevOps Agent MCP-server integration, after which this custom
agent can call the MCP's tools during its run. Use any MCP in addition to the
regular sources - the PR contents from source control, AWS reads via use_aws, and
the connected pipeline integrations - never instead of them. AWS MCP server names
and availability evolve, so verify the current server before relying on it.

## Output

Provide an IaC risk preview:
1. Change set summarized as create/update/replace/delete per resource.
2. High-impact actions flagged first with the concrete resource at risk.
3. Data-loss and availability risks called out explicitly.
4. Security regressions (network opening, IAM broadening, weaker encryption).
5. Ranked, plain-language reviewer summary with mitigation suggestions.
