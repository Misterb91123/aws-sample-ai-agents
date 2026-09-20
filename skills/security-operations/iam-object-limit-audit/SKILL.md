---
name: iam-object-limit-audit
agent_type: "Generic"
description: Enumerates IAM roles and policies and flags every object approaching
  an IAM size or count limit - managed policies per role near the limit, trust
  policy near 2048 characters, managed policy near 6144, inline policy near 10240,
  and entity counts near account quotas. Use this skill to catch IAM objects that
  will soon reject the next attachment or statement, to classify each as
  consolidate versus request-increase, and to pre-draft the Service Quotas
  requests, all read-only. This is about object size and count limits, not
  least-privilege or unused-access.
version: "1.0.0"
last_updated: "2026-09-12"
---

# IAM Object Limit Audit

Use this skill to find IAM objects that are close to a hard IAM limit before a
deployment fails on a rejected attachment or an oversized policy. This differs
from least-privilege, trust, and unused-access audits: the concern here is object
SIZE and COUNT against IAM limits and account quotas. Reason over the IAM and
Service Quotas reads the platform surfaces; do not modify anything.

## Sources

Read-only.

- IAM via use_aws: GetAccountSummary (current entity counts), ListRoles and
  GetRole (trust policy AssumeRolePolicyDocument and its length),
  ListAttachedRolePolicies (managed policies per role), GetRolePolicy (inline
  policy lengths), and ListPolicies plus the default policy version (managed
  policy document lengths).
- Service Quotas via use_aws: the applicable IAM quotas so comparisons use the
  account's actual limits, not just documented defaults.

## Method

1. Read account limits: GetAccountSummary for entity counts and the IAM Service
   Quotas so every comparison uses the account's real limits where available.
2. Enumerate roles and capture each trust policy's character length against the
   2048 limit.
3. Count managed policies attached per role against 10 (default) or the raised
   limit, and read inline policies for their length against 10240.
4. Enumerate managed policies and capture each document's length against 6144.
5. Compute proximity to each limit and flag any object within a configurable
   warning band; also flag entity counts near account quotas.
6. Classify each flagged object as consolidate (merge inline into managed, split
   or combine statements, remove redundant attachments) or request-increase (the
   object is legitimately large), based on whether it can be reduced without
   losing needed permissions.
7. For each request-increase case, pre-draft a Service Quotas request naming the
   quota, current value, observed usage, and justification, ranked by how close
   each object is to breaking.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Documentation MCP Server can supply current IAM quota values and Service
Quotas guidance, which change over time; recommend using it in addition to the
IAM and Service Quotas reads to confirm the exact limit before flagging, never
instead of them. No AWS-managed IAM object-limit MCP server exists today. AWS MCP
server names and availability evolve; verify before relying on one.

## Output

Produce an object-limit report: the account position (entity counts and nearest
quotas); a per-object findings table (object, limit type, observed value, percent
of limit, consolidate-or-increase classification, safety rating, corrective
action); and pre-drafted Service Quotas requests for each request-increase case,
ranked by proximity to limit (recommend-only), with a GREEN, YELLOW, or RED
safety rating and YELLOW or RED flagged for human approval. Reference identifiers
and character counts, not full policy documents.
