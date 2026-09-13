# Governance and refused finding to directed action mappings

This file maps the read-only GOVERNANCE and org/identity findings produced by the scheduled agents in this repository to the specific AWS DevOps Agent directed action that would remediate each one, and it documents the large refused-passrole family whose natural fix passes an IAM role to a service. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Governance writes target org and identity-management APIs (organizations:*, sso-admin:*, controltower:*) that are commonly excluded from the elevated-role ceiling the same way iam:* is, so they are marked allowed-if-ceiling-permits and are frequently manual; the passrole family stays manual regardless of approval.

## Account or OU with no restrictive SCP or missing baseline guardrails

| Field | Value |
| --- | --- |
| Read-only finding | An account or organizational unit has no restrictive service control policy attached, or is missing baseline guardrails, so principals in the target are not constrained by an SCP. |
| Source | 134-scp-effectiveness-auditor |
| Directed action | organizations:CreatePolicy followed by organizations:AttachPolicy (or organizations:UpdatePolicy when a policy already exists) |
| Parameters | Create or update an SCP with the specific deny/allow statements the baseline requires, then attach it to the target account or OU by id. Removing existing guardrails or attaching a permissive allow-all policy is never proposed. |
| Guardrail status | allowed-if-ceiling-permits |
| Safety | RED (an SCP affects every principal in the target; high blast radius) |
| Approval scope | single-use, pinned to the specific policy content and target account/OU id |
| Rollback | organizations:DetachPolicy to detach the attached SCP, or organizations:UpdatePolicy to restore the prior policy document captured before the change. |
| Notes | organizations:* is commonly excluded from the elevated-role ceiling like iam:*, so this frequently cannot execute and remains a manual change applied by a human. SCPs affect every principal in the target, so blast radius is high and escalation to senior approval is required. Verify by listing policies attached to the target. |

## SCP drift: a required SCP was detached or altered

| Field | Value |
| --- | --- |
| Read-only finding | A required service control policy was detached from an account or OU, or its document was altered away from the approved baseline. |
| Source | 199-organizations-scp-change-monitor |
| Directed action | organizations:AttachPolicy (re-attach the required SCP) or organizations:UpdatePolicy (restore the approved document) |
| Parameters | Re-attach the required SCP by id to the target, or update the policy document back to the approved baseline captured from source control. Loosening the policy is never proposed. |
| Guardrail status | allowed-if-ceiling-permits |
| Safety | RED (restoring an SCP re-applies constraints to every principal in the target) |
| Approval scope | single-use, pinned to the policy id, target id, and restored document |
| Rollback | organizations:DetachPolicy or organizations:UpdatePolicy with the state captured immediately before the restore. |
| Notes | organizations:* is commonly excluded from the ceiling like iam:*, so this is frequently manual. High blast radius; escalation required. Verify by re-reading the policy attachment and document against the baseline. |

## Member account missing baseline contacts or guardrails

| Field | Value |
| --- | --- |
| Read-only finding | A member account is missing baseline configuration such as alternate contacts or the required org-level guardrails. |
| Source | 136-organizations-account-baseline-auditor |
| Directed action | A mix of organizations:* (attach/update baseline SCP) and account:PutAlternateContact (set the required contact) |
| Parameters | Attach or update the baseline SCP as needed, and set the alternate contact (security, billing, or operations) to the approved value for the account. |
| Guardrail status | allowed-if-ceiling-permits |
| Safety | YELLOW (contact changes) to RED (SCP changes affect every principal in the target) |
| Approval scope | single-use, one approval per operation and target account id |
| Rollback | organizations:DetachPolicy / organizations:UpdatePolicy for the SCP portion; account:PutAlternateContact with the prior contact value (or delete via account:DeleteAlternateContact if none existed) for the contact portion. |
| Notes | organizations:* is commonly excluded from the ceiling like iam:*, so the SCP portion is frequently manual. Account contacts overlap cost-governance.md (Source 268) - cross-reference that file for the billing-contact angle. Verify by reading account contacts and attached policies. |

## Over-broad or stale IAM Identity Center permission-set assignment

| Field | Value |
| --- | --- |
| Read-only finding | An IAM Identity Center (AWS SSO) permission set grants more access than usage shows, or an assignment is stale, so a principal has broader access than needed. |
| Source | 200-iam-identity-center-assignment-auditor |
| Directed action | sso-admin:PutInlinePolicyToPermissionSet or sso-admin:DetachManagedPolicyFromPermissionSet, followed by sso-admin:ProvisionPermissionSet, scope-down direction only |
| Parameters | Tighten the permission set to the specific actions and resource ARNs the assignment actually uses, then re-provision so the change takes effect. Widening the permission set or granting AdministratorAccess is refused-prohibited-action and is never proposed. |
| Guardrail status | allowed-if-ceiling-permits (for the scoped-down direction only); widening is refused-prohibited-action |
| Safety | YELLOW |
| Approval scope | single-use, pinned to the permission-set ARN and the scoped-down document |
| Rollback | Re-put the prior inline policy (sso-admin:PutInlinePolicyToPermissionSet) or re-attach the prior managed policy (sso-admin:AttachManagedPolicyToPermissionSet), then sso-admin:ProvisionPermissionSet to restore. |
| Notes | sso-admin:* is commonly excluded from the elevated-role ceiling like iam:*, so even a correct scope-down is frequently manual. Over-scoping down can break access for assigned principals, so verify with a staged rollout. Only tightening is allowed; widening is always refused. Verify by reading the permission set and re-provisioning status. |

## Control Tower landing-zone or guardrail drift

| Field | Value |
| --- | --- |
| Read-only finding | A Control Tower landing zone or an enabled guardrail has drifted from its expected state, leaving a control not enforced on the target OU. |
| Source | 135-control-tower-drift-detector |
| Directed action | controltower:EnableControl (re-enable the drifted guardrail) or re-attach the underlying policy via organizations |
| Parameters | Enable the specific control by identifier on the target OU, or re-attach the underlying SCP that the control manages. Disabling controls is never proposed. |
| Guardrail status | allowed-if-ceiling-permits |
| Safety | RED (guardrails apply org-wide to the target OU; high blast radius) |
| Approval scope | single-use, pinned to the control identifier and target OU id |
| Rollback | controltower:DisableControl to reverse the enable, or organizations:DetachPolicy for the re-attached policy, using the state captured before the change. |
| Notes | controltower:* is commonly excluded from the elevated-role ceiling like iam:*, so this is frequently manual. High blast radius; escalation to senior approval required. Verify by reading control status and drift on the target OU. |

## SNS delivery-status logging not enabled

| Field | Value |
| --- | --- |
| Read-only finding | An SNS topic has no delivery-status logging configured, so delivery successes and failures are not captured for the topic's protocols. |
| Source | 46-sns-delivery-failure-monitor |
| Directed action | Would be sns:SetTopicAttributes setting an *FeedbackRoleArn - NOT executed |
| Parameters | Not applicable. Setting a delivery-status feedback attribute (for example HTTPSuccessFeedbackRoleArn / SQSFailureFeedbackRoleArn) passes an IAM role to the SNS service, which is an iam:PassRole operation. |
| Guardrail status | refused-passrole |
| Safety | RED (passes a role; the agent refuses regardless of approval) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | Not applicable; no action is executed. |
| Notes | The natural fix binds a feedback role to the topic, which the agent refuses. A human wires the feedback role with their own credentials. Adding a DLQ to a subscription is likewise an operational/manual step and is not a directed action here. Consistent with the observability.md metric-stream and iot.md rules-engine precedents. |

## EventBridge rule target failing, or a rule needs a target or DLQ

| Field | Value |
| --- | --- |
| Read-only finding | An EventBridge rule target is failing to deliver, or a rule needs a target or a dead-letter queue added, so matching events are not reaching their destination. |
| Source | 214-eventbridge-rule-target-failure-monitor, 116-eventbridge-delivery-failure-monitor, 93-eventbridge-rule-health-monitor |
| Directed action | Would be events:PutTargets / events:PutRule specifying a RoleArn - NOT executed |
| Parameters | Not applicable. Adding or fixing a target that carries a RoleArn (or a rule that delivers via a role) passes an IAM role to EventBridge, which is an iam:PassRole operation. |
| Guardrail status | refused-passrole |
| Safety | RED (passes a role; the agent refuses regardless of approval) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | Not applicable; no action is executed. |
| Notes | The failing-target fix needs a role, so it is refused and a human wires the target role with their own credentials. Enabling an already-correct rule that is merely DISABLED via events:EnableRule would be allowed (it re-passes no role), but that is a different case from the failing-target fix here. Consistent with the iot.md rules-engine precedent. |

## Secrets Manager rotation not enabled or rotation Lambda failing

| Field | Value |
| --- | --- |
| Read-only finding | A secret has automatic rotation disabled, or its configured rotation Lambda is failing, so the secret is not rotating on schedule. |
| Source | 152-secrets-manager-rotation-drift-monitor, 126-secrets-rotation-lambda-failure-monitor |
| Directed action | Would be secretsmanager:RotateSecret / configure-rotation binding a RotationLambdaARN - NOT executed |
| Parameters | Not applicable. Configuring rotation binds a RotationLambdaARN to the secret, which passes an IAM role to the service through the rotation function, an iam:PassRole operation. |
| Guardrail status | refused-passrole |
| Safety | RED (passes a role; the agent refuses regardless of approval) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | Not applicable; no action is executed. |
| Notes | Enabling or fixing rotation requires wiring the rotation Lambda, which the agent refuses. A human wires the rotation function and its role with their own credentials. Consistent with the observability.md metric-stream and iot.md rules-engine precedents. |

## S3 replication rule broken or needs re-enabling

| Field | Value |
| --- | --- |
| Read-only finding | An S3 bucket replication rule is broken, disabled, or misconfigured, so objects are not replicating to the destination bucket. |
| Source | 181-s3-replication-lag-and-failure-monitor |
| Directed action | Would be s3:PutBucketReplication including the replication IAM Role - NOT executed |
| Parameters | Not applicable. A replication configuration requires the replication IAM Role ARN in its payload, so applying it passes an IAM role to the S3 service, an iam:PassRole operation. |
| Guardrail status | refused-passrole |
| Safety | RED (passes a role; the agent refuses regardless of approval) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | Not applicable; no action is executed. |
| Notes | The replication config always carries a role, so the fix is refused and a human applies the replication configuration with their own credentials. Consistent with the observability.md metric-stream and iot.md rules-engine precedents. |

## Refused and manual remediations

The governance and identity findings above resolve to directed actions in principle, but they target org and identity-management APIs (organizations:*, sso-admin:*, controltower:*) that are commonly excluded from the elevated-role ceiling the same way iam:* is:

- SCP creation/attachment and SCP drift restore (134-scp-effectiveness-auditor, 199-organizations-scp-change-monitor) - allowed-if-ceiling-permits. organizations:* is usually outside the ceiling, so these are usually manual. SCPs affect every principal in the target, so they are always high blast radius and require escalation.
- Member account baseline (136-organizations-account-baseline-auditor) - allowed-if-ceiling-permits. The organizations:* portion is usually manual; the account:PutAlternateContact portion overlaps cost-governance.md (Source 268), which should be cross-referenced.
- IAM Identity Center scope-down (200-iam-identity-center-assignment-auditor) - allowed-if-ceiling-permits for tightening only; sso-admin:* is usually outside the ceiling, so it is usually manual. Widening is always refused-prohibited-action.
- Control Tower drift (135-control-tower-drift-detector) - allowed-if-ceiling-permits. controltower:* is usually outside the ceiling, so it is usually manual, and guardrails apply org-wide, so it is always high blast radius and requires escalation.

The entire PassRole family stays manual because passing a role to a service is refused regardless of approval:

- SNS delivery-status feedback role (46-sns-delivery-failure-monitor) - refused-passrole. Setting an *FeedbackRoleArn passes a role; a human wires it.
- EventBridge target roles (214-eventbridge-rule-target-failure-monitor, 116-eventbridge-delivery-failure-monitor, 93-eventbridge-rule-health-monitor) - refused-passrole. A failing target that needs a RoleArn is refused; enabling a merely DISABLED, already-correct rule via events:EnableRule is the allowed exception.
- Secrets Manager rotation Lambda (152-secrets-manager-rotation-drift-monitor, 126-secrets-rotation-lambda-failure-monitor) - refused-passrole. Binding a RotationLambdaARN passes a role; a human wires the rotation function.
- S3 replication role (181-s3-replication-lag-and-failure-monitor) - refused-passrole. s3:PutBucketReplication requires the replication IAM Role in its config; a human applies it.

This is consistent with the observability.md metric-stream (cloudwatch:PutMetricStream) and iot.md rules-engine (iot:CreateTopicRule / iot:ReplaceTopicRule) precedents: any operation that passes an IAM role to a service is refused-passrole by default and stays a manual step performed by a human with their own credentials.
