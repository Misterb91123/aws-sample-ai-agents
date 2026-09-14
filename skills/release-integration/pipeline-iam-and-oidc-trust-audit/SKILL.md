---
name: pipeline-iam-and-oidc-trust-audit
agent_type: "Generic"
description: Audits the IAM roles and OIDC trust relationships that CI/CD providers
  assume into AWS to deploy - GitHub Actions OIDC, GitLab, and Azure DevOps service
  connections. Flags over-broad trust policies, wildcard or missing subject
  conditions, and stale deploy roles that are no longer used. Use this to make
  sure the pipeline-to-AWS trust boundary is tight so a compromised pipeline
  cannot assume more access than it needs.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Pipeline IAM and OIDC Trust Audit

Use this skill to review how CI/CD providers gain access to AWS. Deploy pipelines
assume IAM roles, usually through OIDC federation (GitHub) or provider service
connections (GitLab, Azure DevOps). Loose trust policies let the wrong workflow,
branch, or repo assume a role. This skill is read-only and recommend-only: it
reports trust and staleness problems, it does not modify any role or policy.

## Sources

- AWS-native IAM reads (use_aws): role trust policies, attached and inline
  permission policies, and the OIDC identity providers configured in the account.
- CloudTrail-style access data the platform surfaces to see which roles were
  actually assumed and when (for staleness).
- Pipeline associations (GitHub Actions, GitLab CI-CD, Azure DevOps) to map each
  deploy role back to the repository and pipeline that assumes it.
- Repository workflow definitions to confirm which role each pipeline references.
- Comms/ticketing associations only for reporting.

## Method

1. Enumerate IAM roles used for deployment and the OIDC providers and service
   connections that federate into the account.
2. For each role trust policy, parse the conditions and flag wildcard or missing
   subject claims (for example a GitHub OIDC sub that allows any repo, branch, or
   environment).
3. Map each role to the specific pipeline and repository that should assume it,
   using the pipeline association and workflow definitions. Flag roles no pipeline
   references.
4. Review each role's permission policies at a high level to note whether trust
   breadth is paired with broad permissions (compounded risk).
5. Use assume-role history to flag stale deploy roles not assumed within the
   window.
6. Check for provider-specific weaknesses: unrestricted audience, shared roles
   across many repos, long-lived static keys used instead of OIDC.
7. Rank findings by exploitability (breadth of trust times breadth of permission).

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the
general "Agent Toolkit for AWS" helps the agent enumerate and describe IAM roles,
policies, and OIDC providers programmatically during the audit. A custom
IAM-analysis MCP server (wrapping the team's own policy-evaluation tooling) can
add deeper trust-condition reasoning than a manual read. To enable, connect the
MCP server to the Agent Space through the DevOps Agent MCP-server integration,
after which this custom agent can call the MCP's tools during its run. Use any MCP
in addition to the regular sources - IAM reads via use_aws, access history, and
the connected pipeline integrations - never instead of them. AWS MCP server names
and availability evolve, so verify the current server before relying on it.

## Output

Provide a trust audit report:
1. Inventory of deploy roles with their federating provider and mapped pipeline.
2. Over-broad trust findings: wildcard or missing subject/audience conditions.
3. Stale deploy roles not assumed within the window.
4. Compounded-risk roles where broad trust meets broad permission.
5. Prioritized remediation with tighter trust-condition recommendations.
