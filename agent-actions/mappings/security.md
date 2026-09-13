# Security finding to directed action mappings

This file maps the read-only SECURITY findings produced by the scheduled agents and skills in this repository to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Every entry records the exact operation, its guardrail status, safety rating, approval scope, and rollback so operators can decide with full context; findings whose only safe fix is a delete, an IAM write outside the ceiling, or a prohibited action stay manual and are called out as such.

## Security group allows 0.0.0.0/0 on SSH/RDP or sensitive port

| Field | Value |
| --- | --- |
| Read-only finding | An inbound security group rule allows 0.0.0.0/0 (or ::/0) to a sensitive port such as 22 (SSH), 3389 (RDP), 3306, 5432, or 6379. |
| Source | 03-security-group-auditor, 82-public-exposure-surface-scanner, 84-nacl-rule-auditor, 98-vpc-security-group-rule-count-monitor, skill guardduty-finding-investigation |
| Directed action | ec2:RevokeSecurityGroupIngress (remove the open rule) followed by ec2:AuthorizeSecurityGroupIngress (add the scoped rule) |
| Parameters | Revoke the ingress rule for 0.0.0.0/0 on tcp/22 (and tcp/3389 if present); authorize tcp/22 from the corporate/VPN CIDR, for example 10.0.0.0/8, on the same security group. Adding a 0.0.0.0/0 rule as the "fix" is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run ec2:AuthorizeSecurityGroupIngress to restore the prior rule and ec2:RevokeSecurityGroupIngress to remove the scoped rule. The rule set is small and fully described, so revert is exact. |
| Notes | Two operations, each individually approved. Verify by re-describing the group and confirming no 0.0.0.0/0 rule remains on the sensitive port. Existing established connections may drop when the open rule is revoked. |

## EC2 instance without IMDSv2 enforced

| Field | Value |
| --- | --- |
| Read-only finding | An EC2 instance still accepts IMDSv1 (HttpTokens=optional), exposing instance credentials to SSRF-style theft. |
| Source | 48-ec2-metadata-security-checker |
| Directed action | ec2:ModifyInstanceMetadataOptions |
| Parameters | Set HttpTokens=required (enforce IMDSv2); optionally set HttpPutResponseHopLimit to a small value such as 1 or 2. Metadata endpoint stays enabled; it is not disabled. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run ec2:ModifyInstanceMetadataOptions with HttpTokens=optional to restore the prior setting. |
| Notes | Confirm workloads and SDKs on the instance already support IMDSv2 before enforcing; legacy agents pinned to IMDSv1 can lose credential access. Verify by re-describing metadata options. |

## S3 bucket without Block Public Access

| Field | Value |
| --- | --- |
| Read-only finding | An S3 bucket has one or more Block Public Access settings disabled, allowing public ACLs or bucket policies to take effect. |
| Source | 15-s3-bucket-security-scanner, 82-public-exposure-surface-scanner |
| Directed action | s3:PutBucketPublicAccessBlock |
| Parameters | Enable all four: BlockPublicAcls=true, IgnorePublicAcls=true, BlockPublicPolicy=true, RestrictPublicBuckets=true. Disabling Block Public Access is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run s3:PutBucketPublicAccessBlock restoring the prior (looser) flags. Revert is exact because the four booleans are fully captured before the change. |
| Notes | If the bucket legitimately serves public content (for example a static site via CloudFront OAC), confirm that before enabling. Verify by re-reading the public access block configuration. |

## S3 bucket without default encryption

| Field | Value |
| --- | --- |
| Read-only finding | An S3 bucket has no default server-side encryption configured. |
| Source | 15-s3-bucket-security-scanner |
| Directed action | s3:PutBucketEncryption |
| Parameters | Apply a default encryption rule using SSE-KMS with a specific customer-managed key ARN, or SSE-S3 (AES256) where a KMS key is not required. Disabling encryption is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run s3:PutBucketEncryption with the prior configuration, or remove the rule if none existed. Existing objects are unaffected; only new object defaults change. |
| Notes | SSE-KMS requires that principals writing to the bucket have kms:GenerateDataKey on the chosen key. Verify by re-reading the bucket encryption configuration. |

## VPC without flow logs

| Field | Value |
| --- | --- |
| Read-only finding | A VPC (or its subnets/ENIs) has no flow logs, leaving network traffic uncaptured for security and forensic analysis. |
| Source | 160-vpc-flow-log-coverage-auditor |
| Directed action | ec2:CreateFlowLogs |
| Parameters | Create a flow log on the VPC with TrafficType=ALL, delivering to a specified CloudWatch Logs group or S3 bucket. This enables logging; disabling logging is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Delete the created flow log via ec2:DeleteFlowLogs (deleting the log resource the agent just created is the documented revert of its own additive change). |
| Notes | Delivery to CloudWatch Logs needs a delivery role; if that role must be passed at create time this can trip the passrole guardrail (see refused-passrole). Delivering to an existing S3 destination avoids passrole. Verify by re-describing flow logs on the VPC. |

## KMS key rotation disabled

| Field | Value |
| --- | --- |
| Read-only finding | A customer-managed KMS key has automatic annual key rotation disabled. |
| Source | 55-kms-key-usage-rotation-auditor, 178-kms-grant-and-policy-drift-auditor |
| Directed action | kms:EnableKeyRotation |
| Parameters | Enable automatic rotation on the specified customer-managed key ARN. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run kms:DisableKeyRotation to restore the prior state. Rotation adds key material without removing prior material, so decryption of existing ciphertext is unaffected. |
| Notes | Applies only to symmetric customer-managed keys; AWS-managed keys rotate automatically and are out of scope. This changes only rotation, not the key policy. Verify by reading the key rotation status. |

## GuardDuty not enabled in a region

| Field | Value |
| --- | --- |
| Read-only finding | GuardDuty has no active detector in a region that is in use, leaving threat detection off there. |
| Source | 63-guardduty-finding-trend-reporter, 223-guardduty-finding-severity-trend-reporter, 173-guardduty-malware-scan-coverage-auditor |
| Directed action | guardduty:CreateDetector |
| Parameters | Create a detector in the target region with Enable=true and a defined finding publishing frequency. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Delete the created detector via guardduty:DeleteDetector (reverting the additive change the agent just made in that region). |
| Notes | This action is per-region; enabling across many regions is a series of single-resource actions, each approved. If enabling for an organization via a delegated administrator, blast radius is multi-account and requires additional explicit approval. Verify by listing detectors in the region. |

## ELB or CloudFront weak TLS policy

| Field | Value |
| --- | --- |
| Read-only finding | An ALB/NLB HTTPS listener or a CloudFront distribution uses a deprecated TLS policy or minimum protocol version (for example TLS 1.0/1.1 or weak ciphers). |
| Source | 64-load-balancer-ssl-policy-auditor, 221-acm-and-elb-tls-policy-drift-monitor, skill tls-policy-modernization |
| Directed action | elasticloadbalancing:ModifyListener (set a modern SSL policy) or cloudfront:UpdateDistribution (set MinimumProtocolVersion) |
| Parameters | For ELB, set SslPolicy to a current policy such as ELBSecurityPolicy-TLS13-1-2-2021-06. For CloudFront, set MinimumProtocolVersion to TLSv1.2_2021. Downgrading TLS is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run the same operation with the previous SslPolicy / MinimumProtocolVersion captured before the change. |
| Notes | Raising the minimum TLS version can drop very old clients; confirm the client population supports TLS 1.2+ first. CloudFront changes take time to propagate to edge locations. Verify by reading the listener or distribution config. |

## IAM role with wildcard or over-broad policy

| Field | Value |
| --- | --- |
| Read-only finding | An IAM role or its attached policy grants over-broad access (Action:* / Resource:*, or permissions well beyond what usage shows). |
| Source | 07-iam-least-privilege-auditor, 11-unused-permissions-revoker, 212-lambda-iam-permission-scope-auditor, skill lambda-execution-role-hardening |
| Directed action | iam:PutRolePolicy (rewrite an inline policy) or iam:CreatePolicyVersion (new default version of a managed policy), scoped down to the specific actions and resource ARNs the role actually uses |
| Parameters | Replace wildcards with the concrete actions and resource ARNs observed in usage (least privilege). Widening scope, granting AdministratorAccess, or adding Action:* / Resource:* is refused-prohibited-action and is never proposed. |
| Guardrail status | allowed (only for the scoped-down direction) |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | For iam:CreatePolicyVersion, set the prior version back as default (iam:SetDefaultPolicyVersion); for iam:PutRolePolicy, re-put the prior inline document captured before the change. |
| Notes | Widening a policy is prohibited; only tightening is allowed. Many organizations exclude iam:* from the elevated-role ceiling, so even a correct scope-down may not execute and remains a manual change applied by a human. Over-scoping down can break the workload, so verify with a dry run or staged rollout. This action requires senior approval when the role is in production. |

## Unused, exposed, or over-permissioned access key

| Field | Value |
| --- | --- |
| Read-only finding | An IAM access key is old, unused, exposed, or attached to an over-permissioned identity and should be taken out of service. |
| Source | 158-iam-access-key-age-and-usage-auditor |
| Directed action | iam:UpdateAccessKey (Status=Inactive) |
| Parameters | Set the specific access key id to Status=Inactive to disable it without deleting it. Deleting the key (iam:DeleteAccessKey) is refused-delete-class and is not proposed. |
| Guardrail status | allowed-if-ceiling-permits |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run iam:UpdateAccessKey with Status=Active to reactivate the key. Deactivation is fully reversible; deletion would not be, which is why deactivate is the chosen action. |
| Notes | This is an iam write, so it executes only if iam:UpdateAccessKey is inside the elevated-role ceiling; where iam:* is excluded it remains manual. Deactivate first, confirm nothing breaks, then a human deletes the key later. Verify by reading the key status. |

## Orphaned resource cleanup (unused security group, orphaned EBS snapshot)

| Field | Value |
| --- | --- |
| Read-only finding | A resource is orphaned - for example a security group attached to nothing, or an EBS snapshot with no source volume and no dependents - and is a candidate for removal. |
| Source | 32-orphaned-resource-cleaner, 208-ebs-snapshot-cost-and-orphan-auditor |
| Directed action | Would be ec2:DeleteSecurityGroup / ec2:DeleteSnapshot - NOT executed |
| Parameters | Not applicable. The safe remediation here is a deletion, which the agent refuses. |
| Guardrail status | refused-delete-class |
| Safety | RED (deletion is hard to reverse) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | None available from the agent: a deleted security group is gone, and a deleted snapshot cannot be recovered. This is exactly why delete-class is refused. |
| Notes | Remediation stays manual: a human confirms the resource is truly orphaned and performs the deletion with their own credentials. The agent's role is limited to detecting and reporting the orphan, consistent with the propose-not-delete posture of the collection. |

## Refused and manual remediations

The following findings above do not resolve to an executable directed action and stay a manual step:

- Orphaned resource cleanup (32-orphaned-resource-cleaner, 208-ebs-snapshot-cost-and-orphan-auditor) - refused-delete-class. Deleting a security group or EBS snapshot is a delete-class operation the agent always refuses, and it is not reversible. A human performs the deletion after confirming the resource is orphaned.
- IAM role scope-down (07-iam-least-privilege-auditor, 11-unused-permissions-revoker, 212-lambda-iam-permission-scope-auditor) - allowed in principle for tightening only, but iam writes are frequently excluded from the elevated-role ceiling. Where iam:* is excluded, the scope-down cannot execute and a human applies it. Widening is always refused-prohibited-action.
- Access key deactivation (158-iam-access-key-age-and-usage-auditor) - allowed-if-ceiling-permits. iam:UpdateAccessKey executes only when iam is inside the ceiling; otherwise it is manual. Key deletion is always refused-delete-class and stays manual regardless.

For the remaining findings (security group scoping, IMDSv2 enforcement, S3 Block Public Access, S3 default encryption, VPC flow logs, KMS rotation, GuardDuty detector creation, ELB/CloudFront TLS policy), the directed action is allowed and executable under per-action operator approval, with the rollback documented in each section. VPC flow log delivery to CloudWatch Logs is the one caveat: if it requires passing a delivery role at create time, that specific path is refused-passrole and the operator either uses an S3 destination or configures the role manually.
