---
name: datalake-access-chain-analysis
agent_type: "Generic"
description: Evaluates the full data-lake access chain for a principal and a
  governed AWS Lake Formation resource (or a failed request) - Lake Formation
  permissions and grants, resource links, cross-account RAM shares, IAM identity
  policy, the underlying S3 bucket policy, and the KMS key policy - to pinpoint
  the missing or incorrect grant behind a denial. Use this skill when a principal
  hits AccessDenied on a governed resource, to find the single broken link
  including granted-but-unlinked resources and catalog-versus-table grant-scope
  errors, and to recommend a targeted, read-only-safe fix.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Data Lake Access Chain Analysis

Use this skill to trace one data-lake access denial to its single broken link.
A governed AWS Lake Formation request passes through several layers, and a denial
in any one of them looks the same to the user. This skill differs from a broad
Lake Formation grant audit: it follows one principal-and-resource chain to
ground rather than surveying all grants. Reason over the AWS reads the platform
surfaces; do not modify anything.

## Sources

Read-only.

- Lake Formation via use_aws: ListPermissions and ListResources for the principal
  and target, noting grant scope (catalog, database, table, column) and whether a
  resource link is involved.
- Glue catalog via use_aws: GetResourcePolicy and the relevant Get calls to
  confirm the resource-link target and the catalog resource policy.
- IAM via use_aws: SimulatePrincipalPolicy for the principal against the Lake
  Formation, Glue, S3, and KMS actions the path requires.
- RAM via use_aws: list calls to confirm a cross-account share exists, is
  accepted, and covers the target.
- S3 via use_aws: GetBucketPolicy for the data-location bucket; KMS via use_aws:
  GetKeyPolicy for the encryption key.
- CloudTrail AccessDenied detail and list_investigations to confirm which layer
  emitted the denial.

## Method

1. Establish the request: principal ARN, target database, table, or column set,
   and the owning account, from the failed request or supplied inputs.
2. Read Lake Formation permissions and resources; record the grant scope and any
   resource link on the path.
3. Confirm the Glue resource-link target and catalog resource policy that Lake
   Formation relies on.
4. Simulate the IAM identity policy for the required actions and capture each
   allow or implicit deny.
5. For cross-account resources, confirm the RAM share exists, is accepted, and
   covers the target.
6. Read the S3 bucket policy and KMS key policy and flag a storage guard that
   blocks the principal even when Lake Formation grants access.
7. Correlate with CloudTrail AccessDenied to confirm the emitting layer, then
   pinpoint the break: a granted-but-unlinked resource, or a catalog-versus-table
   grant-scope error, and name the single corrective grant.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. Where
deeper identity or Lake Formation reasoning is needed (policy expansion across
many statements, or grant graphs the list APIs do not flatten), recommend
connecting an Agent Toolkit for AWS or a custom IAM and Lake Formation MCP server
and calling it in addition to the AWS reads, never instead of them. The AWS
Documentation MCP Server can supply current Lake Formation and cross-account
sharing guidance. AWS MCP server names and availability evolve; verify before
relying on one.

## Output

Produce an access-chain report: the request (principal and resource); a
per-link walkthrough (Lake Formation grant, resource link, RAM share, IAM
identity policy, S3 bucket policy, KMS key policy) with each link's allow-or-block
state and its source; the identified root-cause break (granted-but-unlinked or
grant-scope error); and a ranked, read-only-safe remediation list naming the
exact grant or policy statement to add or correct (recommend-only), with a
GREEN, YELLOW, or RED safety rating and YELLOW or RED flagged for human approval.
Reference identifiers, not full policy documents or data contents.
