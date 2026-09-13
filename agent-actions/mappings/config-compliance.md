# Config and compliance finding to directed action mappings

This file maps the read-only CONFIG and COMPLIANCE findings produced by the scheduled agents and skills in this repository to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Every entry records the exact operation, its guardrail status, safety rating, approval scope, and rollback so operators can decide with full context; findings whose only safe fix is a delete, an IAM write outside the ceiling, a passrole, or a prohibited action stay manual and are called out as such.

## AWS Config recorder missing, stopped, or incomplete

| Field | Value |
| --- | --- |
| Read-only finding | The AWS Config configuration recorder is absent, stopped, or does not record all supported resource types and global resources, leaving configuration and compliance history incomplete. |
| Source | 201-config-recorder-coverage-auditor |
| Directed action | config:PutConfigurationRecorder (allSupported=true, includeGlobalResourceTypes=true) followed by config:StartConfigurationRecorder, plus config:PutDeliveryChannel where the delivery channel is missing |
| Parameters | Set the recording group to allSupported=true and includeGlobalResourceTypes=true, start the recorder, and configure the delivery channel to an existing S3 bucket. Disabling or narrowing recording is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run config:StopConfigurationRecorder to stop recording, or config:PutConfigurationRecorder with the prior recording group and config:PutDeliveryChannel with the prior channel, all captured before the change. |
| Notes | PutConfigurationRecorder references a recorder role. When that role is the pre-existing Config service-linked role (or an existing role already trusted by Config), this is allowed. If a NEW role must be passed at call time, the operation trips the passrole guardrail and becomes refused-passrole; the operator either reuses the existing service-linked role or has a human configure the new role. Verify by describing the recorder status and delivery channel. |

## Config rule non-compliance (aggregated)

| Field | Value |
| --- | --- |
| Read-only finding | One or more managed or custom AWS Config rules report NON_COMPLIANT resources across the account, surfaced as an aggregate drift report rather than a single resource fix. |
| Source | 31-config-rule-drift-remediator |
| Directed action | Routes to existing mappings; add 31-config-rule-drift-remediator as an additional Source on the underlying entries. restricted-ssh -> ec2:RevokeSecurityGroupIngress (security.md); s3-public -> s3:PutBucketPublicAccessBlock (security.md); rds-multi-az -> rds:ModifyDBInstance (reliability.md); cloudtrail-enabled -> cloudtrail:StartLogging; vpc-flow-logs -> ec2:CreateFlowLogs (security.md) |
| Parameters | Per rule, the remediation is the directed action already documented for that finding in its home file, with that file's parameters. This entry is an aggregator that fans out to those covered actions; it introduces no new mutating operation of its own. |
| Guardrail status | allowed (per underlying action) |
| Safety | YELLOW |
| Approval scope | single-use (each underlying action is individually approved) |
| Rollback | The rollback of each fix is the one documented on its underlying entry (for example re-authorize the prior ingress rule, restore the prior public access block, restore the prior DB instance setting). |
| Notes | The iam-user-mfa and encrypted-volumes rule fixes do not route to an executable directed action and stay manual: MFA enablement is an identity change a human performs, and volume encryption cannot be toggled in place on an existing volume. Verify each fix through the source file's own verification step and re-evaluate the Config rule. |

## CloudTrail coverage gap (events not fully logged, validation off, trail stopped)

| Field | Value |
| --- | --- |
| Read-only finding | A CloudTrail trail does not log all management and data events, has log-file validation disabled, or is stopped, leaving an audit gap. |
| Source | 151-cloudtrail-management-event-coverage-auditor |
| Directed action | cloudtrail:PutEventSelectors (ReadWriteType=All, add management and required data event selectors) plus cloudtrail:UpdateTrail (EnableLogFileValidation=true, set KmsKeyId) plus cloudtrail:StartLogging where the trail is stopped |
| Parameters | Set ReadWriteType=All and add the missing management/data event selectors, enable log-file validation, set a KMS key for encryption, and start logging. Disabling logging, narrowing selectors, or turning off validation is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run cloudtrail:PutEventSelectors and cloudtrail:UpdateTrail with the prior selectors and settings captured before the change. Rollback never disables logging; stopping a running trail is not a proposed revert. |
| Notes | This enables logging and integrity validation only. Adding data-event selectors can increase CloudTrail volume and cost; confirm scope before approving. Verify by re-reading the trail status, event selectors, and validation setting. |

## Route 53 DNSSEC not signing / key-signing key needs action

| Field | Value |
| --- | --- |
| Read-only finding | A Route 53 hosted zone has DNSSEC signing disabled, or an existing key-signing key (KSK) is inactive and needs activation, leaving responses unsigned. |
| Source | 180-route53-dnssec-validation-monitor |
| Directed action | route53:ActivateKeySigningKey and/or route53:EnableHostedZoneDNSSEC |
| Parameters | Activate the existing KSK and enable DNSSEC signing on the specified hosted zone. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run route53:DisableHostedZoneDNSSEC to return to the prior unsigned state (and deactivate the KSK if it was inactive before). |
| Notes | DNSSEC changes require careful DS-record coordination with the parent zone: enabling signing without a matching DS record at the parent, or disabling before removing the DS record, can break resolution for the domain. Sequence the DS-record update at the registrar/parent with the signing change. Verify by reading the zone DNSSEC status and confirming the KSK is ACTIVE. |

## Network Firewall logging disabled

| Field | Value |
| --- | --- |
| Read-only finding | An AWS Network Firewall firewall has flow and/or alert logging disabled, so traffic and rule matches are not captured. |
| Source | 130-network-firewall-rule-effectiveness-monitor |
| Directed action | network-firewall:UpdateLoggingConfiguration (enable FLOW and ALERT logs) |
| Parameters | Add logging destinations for FLOW and ALERT log types delivering to an existing CloudWatch Logs group, S3 bucket, or Kinesis stream. This enables logging; disabling logging is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run network-firewall:UpdateLoggingConfiguration with the prior logging configuration captured before the change. |
| Notes | Automatic rule REMOVAL is out of scope; the agent forbids removing or rewriting firewall rules, so rule tuning based on effectiveness data stays manual and review-driven. Only logging enablement is executed. Verify by reading the firewall logging configuration. |

## Lake Formation overly broad grants / IAMAllowedPrincipals

| Field | Value |
| --- | --- |
| Read-only finding | Lake Formation permissions are overly broad - for example IAMAllowedPrincipals still holds grants, or a principal has permissions well beyond need - on an existing database or table. |
| Source | 190-lakeformation-permission-auditor |
| Directed action | lakeformation:RevokePermissions (remove the over-broad grant) followed by lakeformation:GrantPermissions (re-grant the scoped, least-privilege set) |
| Parameters | Revoke the over-broad grant (including IAMAllowedPrincipals) and grant only the specific permissions the principal needs on the specific resource. Widening scope, or granting Super, is refused-prohibited-action and is never proposed. |
| Guardrail status | allowed (only for the tighten direction) |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run lakeformation:GrantPermissions to restore the prior grant and lakeformation:RevokePermissions to remove the scoped grant, using the state captured before the change. |
| Notes | These are lakeformation operations, not iam:* writes, so they are not ceiling-gated. Only tightening is allowed; widening or granting Super is prohibited. Over-tightening can break analytics jobs, so confirm the principal's real access pattern before revoking. Verify by re-listing permissions on the resource. |

## ECR scan-on-push disabled / no lifecycle policy

| Field | Value |
| --- | --- |
| Read-only finding | An ECR repository has scan-on-push disabled and/or no lifecycle policy, so images are not scanned for vulnerabilities and untagged/old images accumulate. |
| Source | 202-ecr-image-scan-and-lifecycle-auditor |
| Directed action | ecr:PutImageScanningConfiguration (scanOnPush=true) plus ecr:PutLifecyclePolicy |
| Parameters | Set scanOnPush=true on the repository and apply a lifecycle policy that expires untagged or aged images per the defined retention. Disabling scanning is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run ecr:PutImageScanningConfiguration with scanOnPush=false and ecr:PutLifecyclePolicy with the prior policy (or delete the policy if none existed), using the state captured before the change. |
| Notes | A lifecycle policy expires images; confirm the retention rules do not remove images still referenced by running deployments before approving. Verify by reading the repository scanning configuration and lifecycle policy. |

## Refused and manual remediations

The following findings above do not resolve cleanly to an executable directed action, or resolve only in the tightening direction, and stay a manual or guarded step:

- Config recorder that requires passing a NEW role (201-config-recorder-coverage-auditor) - refused-passrole. When PutConfigurationRecorder can reference the pre-existing Config service-linked role it is allowed; when a new role must be passed at call time the passrole guardrail blocks it and a human configures the role. See the recorder entry.
- Network Firewall rule removal (130-network-firewall-rule-effectiveness-monitor) - manual. The agent forbids removing or rewriting firewall rules; only logging enablement is executed, and rule tuning stays a human review step.
- Config iam-user-mfa and encrypted-volumes fixes (31-config-rule-drift-remediator) - manual. MFA enablement is an identity change a human performs, and encryption cannot be toggled in place on an existing volume; neither routes to a directed action.
- Lake Formation widening (190-lakeformation-permission-auditor) - refused-prohibited-action. Only tightening is executed; widening a grant or granting Super is prohibited and never proposed.
- Never disable logging or encryption. Across CloudTrail, Network Firewall, VPC flow logs, S3, and KMS, the agent only enables logging and encryption; the disable direction is a prohibited action and is not proposed, even on approval.

For the remaining findings (Config recorder enablement when reusing the existing role, Config rule fixes that route to already-covered directed actions, CloudTrail coverage enablement, Route 53 DNSSEC activation, Network Firewall logging enablement, Lake Formation scope-down, ECR scan-on-push and lifecycle policy), the directed action is allowed and executable under per-action operator approval, with the rollback documented in each section.
