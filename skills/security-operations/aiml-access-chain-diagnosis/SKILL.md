---
name: aiml-access-chain-diagnosis
agent_type: "Generic"
description: Diagnoses access-denied failures across all AI/ML services (Bedrock,
  SageMaker, Lex, Textract, Comprehend, Rekognition, and others) by tracing the
  full authorization chain - caller identity, IAM identity policy, service or
  execution role, role trust, PassRole, resource policy (model access, S3 bucket
  policy, KMS key policy), and SCP or permission boundary. Use this skill when an
  AI/ML call returns AccessDenied to pinpoint the exact permission gap and
  generate the minimal least-privilege IAM fix with no wildcards.
version: "1.0.0"
last_updated: "2026-09-12"
metadata:
  version: "1.0"
  author: solair
---

# AI/ML Access Chain Diagnosis

Use this skill to isolate why an AI/ML service call is denied. AI/ML access
denials are hard because authorization spans multiple layers that each service
composes differently: the calling principal, its IAM identity policy, an
execution or service role, that role's trust policy, PassRole on the calling
principal, service and resource policies (Bedrock model access, S3 bucket policy,
KMS key policy), and any SCP or permission boundary above them. Reason over
read-only reads; never modify a policy or role.

## Sources

Read-only.

- STS via use_aws: GetCallerIdentity to establish the exact principal, and
  SimulatePrincipalPolicy or SimulateCustomPolicy to test whether an action on a
  resource would be allowed and which statement decides it.
- IAM via use_aws: GetRole, GetRolePolicy, ListAttachedRolePolicies,
  GetPolicyVersion, GetPolicy for identity policies, the execution or service
  role, its trust policy, and any permission boundary.
- Resource and service policies via use_aws: Bedrock model access and any
  resource-based policy, S3 GetBucketPolicy, KMS GetKeyPolicy, and the target
  service Describe/Get calls for its own resource policy where one exists.
- Organizations SCPs where readable, and CloudTrail LookupEvents for the
  AccessDenied event to read the encoded authorization failure message.
- list_investigations for related access or configuration investigations.

## Method

1. Establish the principal with GetCallerIdentity (or the role assumed by the
   service) and the exact action, resource ARN, and region from the failing call.
2. Read the CloudTrail AccessDenied event for that call; the failure message and
   event fields often name the missing action or the deciding policy layer.
3. Evaluate the IAM identity policy: confirm the principal is allowed the AI/ML
   action on the target resource, accounting for conditions and NotAction.
4. Evaluate the execution or service role: confirm it exists, its trust policy
   allows the service principal to assume it, and (if the caller passes it) the
   caller has iam:PassRole scoped to that role.
5. Evaluate resource and service policies: Bedrock model access for the model,
   S3 bucket policy for input/output buckets, and KMS key policy for any CMK used
   to encrypt data, model artifacts, or job output.
6. Evaluate the guardrail layers: permission boundary on the principal or role
   and any SCP that could deny the action regardless of identity policy.
7. Confirm the gap with SimulatePrincipalPolicy against the exact action and
   resource, and identify the single deciding layer (explicit deny vs missing
   allow).
8. Generate the minimal fix: the exact action(s) on the exact resource ARN, at
   the correct layer, least privilege and with no wildcard in action or resource.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
Agent Toolkit for AWS or a custom IAM-analysis MCP server can help reason over
policy evaluation and PassRole chains, and the AWS Documentation MCP Server can
supply each AI/ML service's specific access requirements (for example the
execution-role permissions a SageMaker job needs or the model-access step Bedrock
requires). Use any such server in addition to the STS, IAM, and CloudTrail reads,
never instead of them. AWS MCP server names and availability evolve; verify
before relying on one.

## Output

Produce an access-chain diagnosis: the resolved principal and attempted action
and resource; a per-layer pass/fail table (identity policy, execution/service
role, role trust, PassRole, resource policy, KMS key policy, permission boundary,
SCP); the single deciding layer; and the minimal least-privilege IAM policy that
closes the gap, with no wildcard action or resource. Reference ARNs and account
IDs by identifier; never reproduce credentials or full policy secrets.
