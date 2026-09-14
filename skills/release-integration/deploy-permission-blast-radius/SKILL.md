---
name: deploy-permission-blast-radius
agent_type: "Generic"
description: Reports what each pipeline deploy role can actually do in AWS - the
  effective privilege scope granted to the identities that CI/CD pipelines assume
  to release. Translates attached and inline policies into concrete capabilities
  (which services, which actions, which resources, whether it can delete data or
  broaden access) so the blast radius of a compromised or buggy pipeline is
  visible. Use this to right-size deploy permissions toward least privilege.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Deploy Permission Blast Radius

Use this skill to make the real power of deploy roles legible. A pipeline that can
assume a role with broad permissions is a large blast radius if that pipeline is
compromised or misbehaves. This skill translates policy into plain capabilities.
It is read-only and recommend-only: it reports scope and suggests reductions, it
does not modify any role or policy.

## Sources

- AWS-native IAM reads (use_aws): the deploy role's attached managed policies,
  inline policies, permission boundaries, and any session policies.
- AWS resource reads to understand which concrete resources the allowed actions
  can reach (buckets, tables, clusters, functions).
- Pipeline associations to map each deploy role to the pipeline and repository
  that assumes it.
- Access history the platform surfaces to compare granted permissions against
  what the role actually uses.
- Comms/ticketing associations only for reporting.

## Method

1. For each deploy role, collect all policy sources and compute the effective
   permission set after boundaries and denies.
2. Group the effective permissions into capability categories: compute control,
   data read, data delete/destroy, IAM/access broadening, network changes, secret
   access.
3. Highlight the high-impact capabilities first: ability to delete data stores,
   modify IAM, open security groups, or change infrastructure.
4. Compare granted permissions against actually used actions from access history
   to find unused, over-granted permissions.
5. Map each role back to the pipeline and repo that assumes it so the blast radius
   has an owner.
6. Score each role's blast radius by the severity and reach of what it can do.
7. Recommend least-privilege reductions targeting unused and high-impact grants.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the
general "Agent Toolkit for AWS" is the most relevant addition: it helps the agent
enumerate IAM roles and policies and resolve which resources the allowed actions
touch while computing the effective permission set. If the team has its own
policy-simulation or access-analysis service, a custom MCP server wrapping that
API can add stronger effective-permission reasoning. To enable, connect the MCP
server to the Agent Space through the DevOps Agent MCP-server integration, after
which this custom agent can call the MCP's tools during its run. Use any MCP in
addition to the regular sources - IAM and resource reads via use_aws, access
history, and the connected pipeline integrations - never instead of them. AWS MCP
server names and availability evolve, so verify the current server before relying
on it.

## Output

Provide a blast-radius report:
1. Per-role effective capability summary grouped by category.
2. High-impact capabilities called out first (delete, IAM change, network open).
3. Granted-but-unused permissions from access-history comparison.
4. Blast-radius score per role with the mapped pipeline and repo owner.
5. Least-privilege reduction recommendations prioritized by impact.
