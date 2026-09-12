---
name: lambda-execution-role-hardening
agent_type: "Evaluation"
description: Use when hardening AWS Lambda execution role permissions toward least privilege. It finds wildcard actions, AdministratorAccess attachments, and unused permissions, then recommends scoped policies. Apply during security reviews or before granting new Lambda access.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Lambda Execution Role Hardening

Harden Lambda execution roles by removing wildcard and unused permissions and scoping access to what each function calls.

## When to Activate
- GetPolicyVersion returns a policy statement with Action set to * or a service wildcard like s3:*.
- A Lambda execution role has AdministratorAccess attached.
- IAM Access Analyzer or last-accessed data shows granted services unused for more than 90 days.
- A role's Resource element is * where specific ARNs could be used.
- Multiple functions share one broad role instead of scoped per-function roles.

## Step 1: Enumerate Execution Roles
- Call ListFunctions and read the Role ARN for each Lambda function.
- Group functions that share the same execution role.
- Call ListAttachedRolePolicies and ListRolePolicies for each role.

## Step 2: Inspect Policy Content
- Call GetPolicyVersion for managed policies and GetRolePolicy for inline policies.
- Flag statements where Action contains * or a service-level wildcard.
- Flag statements where Resource is * for services that support resource-level permissions.

## Step 3: Detect Excessive Attachments
- Flag any role with AdministratorAccess or PowerUserAccess attached.
- Flag roles granting IAM write actions not needed by the function.
- Record the count of distinct services granted per role.

## Step 4: Correlate With Actual Usage
- Use IAM service last-accessed data to find granted services with no access in 90 days.
- Cross-check CloudTrail for the actual API calls each function makes.
- Flag permissions granted but never exercised.

## Step 5: Recommend Scoped Policies
- Draft least-privilege policies limited to the observed API calls and specific resource ARNs.
- Recommend one dedicated role per function to avoid permission bleed.
- Recommend removing AdministratorAccess and replacing with scoped policies.

## Output
Produce a titled "Lambda Execution Role Hardening Report" listing roles with wildcard actions, AdministratorAccess attachments, unused permissions older than 90 days, and shared broad roles. Include a prioritized remediation list: remove AdministratorAccess and wildcard actions first, strip unused permissions second, then split shared roles into scoped per-function roles with specific resource ARNs.