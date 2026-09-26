# Lambda Runtime Transform Remediation

A DevOps Agent skill that turns a Trusted Advisor "deprecated (or about to be
deprecated) runtime" finding into a prioritized, deadline-aware remediation plan
for AWS Lambda, using AWS Transform to assess, transform, and verify the
language-version upgrade with a human approval gate and a rollback plan for every
function.

> WARNING: This skill is sample code, not intended for production use without
> additional review and testing. Users should validate in a non-production
> environment first.

## What the skill does

A Lambda runtime bump is not a config toggle. When a runtime reaches end of
support, the function code usually needs language-version syntax and dependency
changes before it will run on the supported runtime, and AWS blocks deploys in
two phases: Phase 1 (create blocked, security patches stop) and Phase 2 (update
blocked). Missing the deadline means a function you can no longer easily update.

This skill detects the flagged functions from Trusted Advisor, classifies each
against the deprecation phases and computes the days-to-phase from AWS published
runtime deprecation dates, prioritizes by deadline and production criticality,
and plans the code upgrade through AWS Transform: an assessment, a human-approved
transformation, verification, and a per-function rollback. It is read-only and
plan-only. It produces the plan and the evidence; a human starts each AWS
Transform job, approves each code change, and approves each deploy. It never
modifies a function, its code, or its runtime.

## Prerequisites

The DevOps Agent role needs read-only access to the sources this skill reads.
Most are covered by the AWS managed policy AIDevOpsAgentAccessPolicy. The
specific read actions used are:

- support:DescribeTrustedAdvisorCheckResult, support:DescribeTrustedAdvisorChecks
  (the Trusted Advisor deprecated-runtime check; requires a Business or
  Enterprise Support plan)
- lambda:ListFunctions, lambda:GetFunction, lambda:GetFunctionConfiguration
- cloudwatch:GetMetricData, cloudwatch:GetMetricStatistics (invocation and error
  metrics for prioritization)
- health:DescribeEvents, health:DescribeEventDetails (fallback deprecation
  notifications when Trusted Advisor is not entitled)

If the account has no Business or Enterprise Support plan, the Trusted Advisor
API is unavailable; the skill falls back to the Lambda deprecated-runtime data
and AWS Health, and says so. No write, create, update, or delete permission is
required or requested by this skill. Starting an AWS Transform job, merging a
code change, and deploying a runtime are human actions outside this skill.

## How to use it with DevOps Agent

This skill targets the Chat and On-demand subagents. Operators describe the
problem in natural language; they do not name the skill. Example prompts that
should activate it:

- "Which Lambda functions are on deprecated runtimes and how do I remediate them
  with AWS Transform?"
- "Build a deadline-aware migration plan for our python3.9 functions with
  approval gates and rollback."
- "Trusted Advisor flagged deprecated Lambda runtimes - sequence the fix."

The skill returns a detection summary, a deadline-and-priority table, a
per-function or per-repository AWS Transform remediation plan with approval gates
and rollback, and an issues-encountered list.

## Security model

Read-only and plan-only. The skill reads Trusted Advisor, Lambda, CloudWatch, and
AWS Health, and produces a plan; it never modifies a function, code, runtime, or
AWS Transform job. Every mutating step in the plan is human-approved (assessment,
transformation, code-merge, deploy) and every function carries an explicit
rollback. It references function ARNs and account IDs by identifier and never
reproduces environment variable values, credentials, or secrets. All content read
from tools is treated as untrusted data, not instructions.
