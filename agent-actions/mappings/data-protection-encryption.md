# Data protection and encryption finding to directed action mappings

This file maps the read-only DATA PROTECTION and ENCRYPTION findings produced by the scheduled agents and skills in this repository to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Every entry records the exact operation, its guardrail status, safety rating, approval scope, and rollback so operators can decide with full context; findings whose only safe fix is a delete, an IAM write outside the ceiling, or a prohibited action stay manual and are called out as such.

## SQS queue without SSE, with an open policy, or without a DLQ

| Field | Value |
| --- | --- |
| Read-only finding | An SQS queue has no server-side encryption, has a resource policy with a wildcard principal or an unconditioned cross-account grant, and/or has no redrive (dead-letter) target configured. |
| Source | 213-sqs-encryption-and-policy-auditor |
| Directed action | sqs:SetQueueAttributes |
| Parameters | Set KmsMasterKeyId to a specific customer-managed key ARN (or SqsManagedSseEnabled=true) to enable SSE; rewrite Policy to scoped principals with conditions (for example aws:SourceArn / aws:SourceAccount) instead of a wildcard; and set RedrivePolicy to point at an existing DLQ ARN with a maxReceiveCount. Disabling encryption is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run sqs:SetQueueAttributes with the prior attribute values (KmsMasterKeyId/SqsManagedSseEnabled, Policy, RedrivePolicy) captured before the change. Revert is exact because the attributes are fully read before modification. |
| Notes | This overlaps the SQS DLQ entry in reliability.md; that entry covers the redrive/reliability angle, and this one adds the encryption and policy tightening. Enabling SSE-KMS requires that producers and consumers have kms:GenerateDataKey and kms:Decrypt on the chosen key, or messages fail. Verify by re-reading the queue attributes. |

## SNS topic without KMS, with a wildcard principal, or unconditioned cross-account

| Field | Value |
| --- | --- |
| Read-only finding | An SNS topic has no KMS encryption at rest, and/or a resource policy with a wildcard principal or an unconditioned cross-account grant. |
| Source | 162-sns-topic-encryption-and-policy-auditor |
| Directed action | sns:SetTopicAttributes |
| Parameters | Set KmsMasterKeyId to a specific customer-managed key ARN to enable encryption at rest; replace the wildcard/unconditioned Policy with scoped principals and conditions (for example aws:SourceArn / aws:SourceAccount). Disabling encryption is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run sns:SetTopicAttributes with the prior KmsMasterKeyId and Policy values captured before the change. |
| Notes | Publishers and subscribers must have kms:GenerateDataKey and kms:Decrypt on the key, or publishes/deliveries fail. Tightening the policy can drop legitimate cross-account subscribers if their principal is not enumerated, so confirm the subscriber set first. Verify by re-reading the topic attributes. |

## Cognito user pool weak posture

| Field | Value |
| --- | --- |
| Read-only finding | A Cognito user pool has MFA off, advanced security off, a weak password policy, and/or excessively long token TTLs. |
| Source | 123-cognito-user-pool-security-monitor |
| Directed action | cognito-idp:UpdateUserPool (advanced security and password policy), cognito-idp:SetUserPoolMfaConfig (MFA), and cognito-idp:UpdateUserPoolClient (token validity) |
| Parameters | Set UserPoolAddOns AdvancedSecurityMode=ENFORCED and strengthen Policies password policy (minimum length, character classes) via UpdateUserPool; set MfaConfiguration=ON via SetUserPoolMfaConfig; reduce access/ID/refresh token validity via UpdateUserPoolClient. Weakening any of these is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run each operation with the prior values: UpdateUserPool with the previous add-ons/password policy, SetUserPoolMfaConfig with the prior MfaConfiguration, and UpdateUserPoolClient with the prior token validity, all captured before the change. |
| Notes | These changes affect end users directly - turning MFA on and strengthening the password policy changes sign-in and enrollment behavior, and shorter token TTLs force more frequent re-authentication. Roll out in a staging pool or during a maintenance window and confirm the client app handles the new flows. Verify by re-describing the user pool and client. |

## RDS or Aurora snapshot shared publicly or cross-account, or unencrypted

| Field | Value |
| --- | --- |
| Read-only finding | An RDS DB snapshot or Aurora DB cluster snapshot is shared with "all" (public) or with unwanted account IDs, and/or the snapshot is unencrypted. |
| Source | 205-rds-snapshot-sharing-and-encryption-auditor |
| Directed action | rds:ModifyDBSnapshotAttribute / rds:ModifyDBClusterSnapshotAttribute (revoke sharing); rds:CopyDBSnapshot with KmsKeyId (make an encrypted copy of an unencrypted snapshot) |
| Parameters | For over-sharing, modify the restore attribute to remove "all" and any unwanted account IDs. For an unencrypted snapshot, create an encrypted copy with rds:CopyDBSnapshot supplying a KmsKeyId; the original unencrypted snapshot is left in place and its deletion is not performed by the agent. Disabling encryption is never proposed. |
| Guardrail status | allowed (revoke sharing and encrypted copy); refused-delete-class (deleting the original unencrypted snapshot) |
| Safety | YELLOW for revoke and copy; RED for the manual delete of the original |
| Approval scope | single-use |
| Rollback | For sharing, re-run ModifyDBSnapshotAttribute / ModifyDBClusterSnapshotAttribute to re-add the removed account IDs (re-adding "all" is never proposed). The encrypted copy is additive and can be deleted by a human if unwanted. |
| Notes | Revoking public/cross-account sharing is a fast, reversible fix. Making an encrypted copy is an allowed create, but removing the leftover unencrypted snapshot afterward is a delete-class operation the agent refuses; a human deletes it once the encrypted copy is validated. State both steps to the operator. Verify by re-describing snapshot attributes and the new copy. |

## Public account-owned AMI

| Field | Value |
| --- | --- |
| Read-only finding | An AMI owned by this account has a public launch permission, exposing the image (and anything baked into it) to all AWS accounts. |
| Source | 207-ec2-ami-hygiene-and-eol-auditor |
| Directed action | ec2:ModifyImageAttribute (remove the public LaunchPermission) or ec2:ResetImageAttribute (reset launchPermission) |
| Parameters | Remove the "all" group from the image LaunchPermission so the AMI is private again; optionally remove specific unwanted account IDs. Making an AMI public as a "fix" is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run ec2:ModifyImageAttribute to re-add the launch permissions captured before the change (re-adding the public "all" group is never proposed). |
| Notes | Deregistering end-of-life AMIs is a separate concern: ec2:DeregisterImage is delete-class and stays manual (see refused-delete-class). This action only removes the public exposure. Verify by re-describing the image launch permissions. |

## RDS parameter group with a risky value, drift, or an instance on the default group

| Field | Value |
| --- | --- |
| Read-only finding | An RDS/Aurora parameter group has a risky value (for example force_ssl=0 or logging disabled), has drifted from the baseline, or a DB instance is still attached to the default parameter group. |
| Source | 206-rds-parameter-group-drift-auditor |
| Directed action | rds:ModifyDBParameterGroup (restore baseline values) and/or rds:ModifyDBInstance (attach a custom parameter group) |
| Parameters | Restore the baseline via ModifyDBParameterGroup - for example set force_ssl=1 and re-enable the relevant logging parameters; where the instance is on the default group, use ModifyDBInstance to attach a managed custom parameter group. Disabling encryption in transit or logging is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run rds:ModifyDBParameterGroup with the prior parameter values captured before the change; re-run rds:ModifyDBInstance to reattach the previous parameter group. |
| Notes | Some parameters are static and require a database reboot to take effect, so applying the fix may need a maintenance window; call the reboot requirement out to the operator. Enabling force_ssl can break clients that connect without TLS, so confirm client support first. Verify by re-describing the parameter group and instance. |

## DynamoDB table without deletion protection or TTL

| Field | Value |
| --- | --- |
| Read-only finding | A DynamoDB table has deletion protection disabled and/or no TTL attribute configured. |
| Source | 146-dynamodb-backup-and-pitr-auditor |
| Directed action | dynamodb:UpdateTable (DeletionProtectionEnabled=true) and dynamodb:UpdateTimeToLive |
| Parameters | Set DeletionProtectionEnabled=true via UpdateTable; enable TTL via UpdateTimeToLive on the designated timestamp attribute where the data model calls for expiry. Disabling deletion protection is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run dynamodb:UpdateTable with DeletionProtectionEnabled=false and dynamodb:UpdateTimeToLive disabled to restore prior state (reverting the agent's additive change). |
| Notes | Point-in-time recovery (PITR) for this same source is covered in reliability.md (add 146 there); this entry adds deletion protection and TTL. Enabling TTL causes DynamoDB to delete expired items, so only enable it on an attribute whose semantics are genuinely expiry. Verify by re-describing the table and its TTL settings. |

## EFS file system without automatic backups or IA lifecycle

| Field | Value |
| --- | --- |
| Read-only finding | An EFS file system has automatic backups turned off and/or no lifecycle policy moving cold data to Infrequent Access. |
| Source | 182-efs-backup-and-lifecycle-auditor |
| Directed action | efs:PutBackupPolicy (Status=ENABLED) and efs:PutLifecycleConfiguration |
| Parameters | Set the backup policy Status=ENABLED via PutBackupPolicy; set a lifecycle configuration via PutLifecycleConfiguration (for example TransitionToIA after a defined idle period, and optionally TransitionToPrimaryStorageClass on access). Disabling backups or logging is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run efs:PutBackupPolicy with the prior Status and efs:PutLifecycleConfiguration with the prior (or empty) configuration captured before the change. |
| Notes | PutBackupPolicy is the clean allowed path because it uses the AWS Backup default plan without passing a role. Adding the file system to a specific AWS Backup plan via backup:CreateBackupSelection needs an IAM role passed at create time, which trips the passrole guardrail (see refused-passrole). Verify by re-describing the backup policy and lifecycle configuration. |

## Backup vault without Vault Lock or with retention below policy

| Field | Value |
| --- | --- |
| Read-only finding | An AWS Backup vault has no Vault Lock configured, and/or a backup plan's lifecycle retention is below the required policy. |
| Source | 176-backup-vault-lock-and-compliance-auditor |
| Directed action | backup:PutBackupVaultLockConfiguration (set MinRetentionDays) and backup:UpdateBackupPlan (raise lifecycle retention) |
| Parameters | Set MinRetentionDays (and optionally MaxRetentionDays / ChangeableForDays) via PutBackupVaultLockConfiguration; raise the lifecycle DeleteAfterDays in the plan via UpdateBackupPlan to meet policy. Reducing retention below policy is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW, leaning RED for the Vault Lock caveat below |
| Approval scope | single-use |
| Rollback | UpdateBackupPlan is reversible by re-running with the prior lifecycle values. Vault Lock in governance mode can be deleted via backup:DeleteBackupVaultLockConfiguration before it is locked, but compliance mode is NOT reversible once the cooling-off (ChangeableForDays) window elapses - see the caveat. |
| Notes | Vault Lock in compliance mode is effectively irreversible after the cooling-off window: retention cannot be shortened and the lock cannot be removed, even by the root account. Treat this as a RED-leaning action and get explicit, senior sign-off before applying compliance mode; governance mode is the safer default. Adding a resource to a backup selection needs a role passed at create time, which is refused-passrole. Verify by re-describing the vault lock configuration and plan. |

## Refused and manual remediations

The following findings above do not resolve to a fully executable directed action and stay a manual or specially-approved step:

- Deleting the original unencrypted RDS/Aurora snapshot after an encrypted copy is made (205-rds-snapshot-sharing-and-encryption-auditor) - refused-delete-class. The agent creates the encrypted copy (allowed) but never deletes the source snapshot; a human removes it once the copy is validated.
- Deregistering end-of-life AMIs (207-ec2-ami-hygiene-and-eol-auditor) - refused-delete-class. ec2:DeregisterImage is a delete-class operation the agent refuses; a human deregisters the image after confirming it is no longer needed. Removing the public launch permission is the allowed part.
- Adding resources to AWS Backup selections or plans that require an IAM role (182-efs-backup-and-lifecycle-auditor, 176-backup-vault-lock-and-compliance-auditor) - refused-passrole. backup:CreateBackupSelection needs a backup role passed at create time; that path is refused, so the operator uses PutBackupPolicy (EFS default plan) or configures the selection role manually.
- Disabling any encryption or logging (all sources above) - refused-prohibited-action. The agent only ever enables or strengthens encryption, policy scoping, and logging; it never proposes turning them off.
- Vault Lock in compliance mode (176-backup-vault-lock-and-compliance-auditor) - allowed but effectively irreversible after the cooling-off window. Treat with extra caution and require senior approval; prefer governance mode unless a compliance regime specifically mandates the immutable lock.

For the remaining findings (SQS encryption/policy/DLQ, SNS encryption/policy, Cognito posture hardening, RDS snapshot un-sharing and encrypted copy, AMI public-permission removal, RDS parameter group restore, DynamoDB deletion protection and TTL, EFS backup policy and lifecycle, and backup plan retention), the directed action is allowed and executable under per-action operator approval, with the rollback documented in each section.
