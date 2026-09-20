# AI/ML Access Chain Diagnosis

A DevOps Agent skill that diagnoses AccessDenied failures across AWS AI/ML
services (Amazon Bedrock, SageMaker, Lex, Textract, Comprehend, Rekognition, and
others) by tracing the full authorization chain and identifying the single
deciding layer, then producing the minimal least-privilege IAM fix.

> WARNING: This skill is sample code, not intended for production use without
> additional review and testing. Users should validate in a non-production
> environment first.

## What the skill does

AI/ML access denials are hard to resolve because authorization spans many layers
that each service composes differently: the calling principal, its IAM identity
policy, an execution or service role, that role's trust policy, iam:PassRole on
the caller, resource and service policies (Bedrock model access, S3 bucket policy,
KMS key policy), and any SCP or permission boundary above them.

This skill reads each layer, tests the exact action and resource with the IAM
policy simulator, identifies whether the decision is an explicit deny or a
missing allow, and generates the minimal fix - the exact action(s) on the exact
resource ARN at the correct layer, with no wildcard in action or resource. It is
read-only: it never modifies a policy or role, and it recommends a fix for a human
to apply.

## Prerequisites

The DevOps Agent role needs read-only access to the authorization layers it
evaluates. Most are covered by the AWS managed policy AIDevOpsAgentAccessPolicy.
The specific read actions used are:

- sts:GetCallerIdentity
- iam:SimulatePrincipalPolicy, iam:SimulateCustomPolicy
- iam:GetRole, iam:GetRolePolicy, iam:ListAttachedRolePolicies, iam:GetPolicy,
  iam:GetPolicyVersion
- s3:GetBucketPolicy (for input/output buckets in scope)
- kms:GetKeyPolicy (for CMKs encrypting data, artifacts, or job output)
- bedrock:GetFoundationModelAvailability and the target service's own
  resource-policy Get/Describe calls where one exists
- organizations:DescribePolicy / ListPoliciesForTarget where SCPs are readable
- cloudtrail:LookupEvents (to read the encoded authorization failure message)

If any of these is missing, add it to the DevOps Agent role. No write, create, or
delete permission is required or requested by this skill.

## How to use it with DevOps Agent

This skill targets the Chat and Incident RCA subagents. Operators describe the
problem in natural language; they do not name the skill. Example prompts that
should activate it:

- "My Bedrock InvokeModel call is returning AccessDenied - why?"
- "A SageMaker training job fails with an access error on its execution role."
- "Textract returns AccessDenied reading from an S3 bucket; find the missing
  permission."

The skill returns a per-layer pass/fail table, the single deciding layer, and the
minimal least-privilege policy to close the gap.

## Security model

Read-only and recommend-only. The skill evaluates authorization layers and
proposes a least-privilege fix; it never applies changes, never recommends a
wildcard action or resource, and references ARNs and account IDs by identifier
without reproducing credentials or full policy secrets. All content read from
tools is treated as untrusted data, not instructions.
