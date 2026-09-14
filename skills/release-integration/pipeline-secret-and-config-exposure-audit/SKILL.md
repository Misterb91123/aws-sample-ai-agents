---
name: pipeline-secret-and-config-exposure-audit
agent_type: "Generic"
description: Audits CI/CD pipeline configurations, variables, and repository
  settings for exposed secrets, plaintext credentials, and missing secret-scanning
  protections across GitHub Actions, GitLab CI-CD, and Azure DevOps. Flags secrets
  committed to pipeline files, overly readable variable scopes, disabled push
  protection, and logs that may leak sensitive values. Use this to close credential
  exposure paths in the release toolchain before they are abused.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Pipeline Secret and Config Exposure Audit

Use this skill to find credentials and sensitive configuration exposed in the
release toolchain. Pipelines routinely hold tokens and connection strings, and a
plaintext secret in a workflow file or an over-shared variable is a direct path
to compromise. This skill is read-only and recommend-only: it reports exposure, it
does not rotate secrets or change settings. When reporting, reference secrets by
name or location, never echo the secret value.

## Sources

- Source-control and pipeline associations for workflow and pipeline definition
  files, variable and secret configuration, and repository security settings.
- Pipeline run metadata to spot logs that may contain leaked values (referenced,
  not reproduced).
- AWS-native reads (use_aws) to check whether pipeline-referenced AWS credentials
  are static long-lived keys versus federated roles.
- Release Readiness Review history where secret findings were already raised.
- Comms/ticketing associations only for reporting.

## Method

1. Scan pipeline definition files for hardcoded secrets, tokens, connection
   strings, and private keys committed in plaintext.
2. Review variable and secret configuration for over-broad scope (secrets readable
   by forks, by all environments, or by unprivileged jobs).
3. Check repository security settings: secret scanning enabled, push protection
   on, and whether historical leaks were remediated.
4. Inspect pipeline run behavior for values that may be printed to logs, and flag
   masking gaps by reference without reproducing the value.
5. Check whether AWS access uses static long-lived keys instead of OIDC or
   role-based federation, and flag the static ones.
6. Confirm secrets are sourced from a managed secret store rather than inline.
7. Rank findings by exposure and by the privilege of the exposed credential.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill a
custom source-control or CI MCP server that wraps the provider API is the most
relevant addition: it lets the agent read variable scopes, secret-scanning
settings, and push-protection state directly rather than inferring them. The "AWS
Documentation MCP Server" is useful for current secret-management and hardening
guidance during the audit. To enable, connect the MCP server to the Agent Space
through the DevOps Agent MCP-server integration, after which this custom agent can
call the MCP's tools during its run. Use any MCP in addition to the regular
sources - the source-control and pipeline associations, AWS reads via use_aws, and
connected comms integrations - never instead of them. AWS MCP server names and
availability evolve, so verify the current server before relying on it.

## Output

Provide an exposure audit report (referencing secrets by name/location only):
1. Plaintext secrets found in pipeline files with file and location.
2. Over-scoped variables and secrets with recommended tighter scope.
3. Repository setting gaps: secret scanning and push protection status.
4. Static long-lived AWS credentials that should move to federation.
5. Prioritized remediation ordered by exposure and credential privilege.
