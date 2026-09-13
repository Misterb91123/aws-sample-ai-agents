# Contact center finding to directed action mappings

This file maps the read-only Amazon Connect findings produced by the contact-center skills in this repository to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Every entry records the exact operation, its guardrail status, safety rating, approval scope, and rollback so operators can decide with full context; findings whose only safe fix is a delete, an op that would pass an IAM role, or a prohibited action stay manual and are called out as such.

## Contact flow missing error branches and dropping callers

| Field | Value |
| --- | --- |
| Read-only finding | A contact flow lacks error/default branches on one or more blocks, so callers hit a dead end and the contact is dropped instead of being routed to a fallback. |
| Source | connect-contact-flow-troubleshooting |
| Directed action | connect:UpdateContactFlowContent (publish corrected flow JSON with the missing error branches added) |
| Parameters | Provide the InstanceId, the target ContactFlowId, and the corrected Content JSON that adds the error/default transitions (for example routing to a fallback queue or a graceful disconnect prompt). Updating flow content does not pass an IAM role. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-publish the prior flow content by re-running connect:UpdateContactFlowContent with the previous Content JSON captured before the change. |
| Notes | Capture the current flow content (connect:DescribeContactFlow) before editing so the revert is exact. If the corrected flow references a Lambda data-dip, confirm that function is associated to the instance first (see the Lambda association finding). Verify by re-describing the flow and placing a test contact. |

## Queue backing up because it is missing from a routing profile

| Field | Value |
| --- | --- |
| Read-only finding | Contacts are accumulating in a queue that is not attached to the routing profile of the agents who should serve it, so no agent is eligible to take the contacts. |
| Source | connect-queue-and-routing-health |
| Directed action | connect:UpdateRoutingProfileQueues (add the queue to the routing profile) |
| Parameters | Provide the InstanceId, the RoutingProfileId, and a QueueConfigs entry associating the missing QueueId with its channel (VOICE/CHAT/TASK), priority, and delay. Only the specific missing queue is added. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run connect:DisassociateRoutingProfileQueues to remove the queue that was just added, restoring the prior routing profile membership. |
| Notes | Adding a queue changes which contacts flow to those agents; confirm the routing profile's agents are staffed and skilled for the new contact type. Verify by re-describing the routing profile and watching the queue drain. |

## Routing profile channel concurrency too low for queued contact type

| Field | Value |
| --- | --- |
| Read-only finding | A routing profile's per-channel concurrency is set below what the queued contact volume needs, so agents are underutilized and contacts wait even with available staff. |
| Source | connect-queue-and-routing-health |
| Directed action | connect:UpdateRoutingProfileConcurrency |
| Parameters | Provide the InstanceId, the RoutingProfileId, and the MediaConcurrencies for the affected channel (for example CHAT concurrency raised to a sized value). Set concurrency to the observed need, not an arbitrary maximum. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run connect:UpdateRoutingProfileConcurrency with the prior MediaConcurrencies captured before the change. |
| Notes | Raising concurrency increases per-agent load; size it to what agents can handle without degrading quality. Applies to CHAT/TASK style concurrency; VOICE remains one active call per agent. Verify by re-describing the routing profile. |

## Concurrent active calls quota nearly exhausted or breaching

| Field | Value |
| --- | --- |
| Read-only finding | The instance is approaching or hitting its concurrent active calls quota, causing new inbound/outbound calls to be rejected at peak. |
| Source | connect-capacity-and-concurrency-planning, connect-telephony-and-voice-quality-investigation |
| Directed action | service-quotas:RequestServiceQuotaIncrease (request a higher concurrent active calls quota for Amazon Connect) |
| Parameters | Provide the Connect ServiceCode, the QuotaCode for concurrent active calls, and a DesiredValue sized to observed peak plus a reasonable headroom - not the maximum. This is a quota request, not an immediate capacity change. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | None needed at execution time: a quota increase raises a ceiling and does not change running behavior. If a lower ceiling is later desired, that is a separate manual quota adjustment. |
| Notes | The request goes through AWS review and is not granted instantly; it may be partially approved. Target the increase to measured peak demand rather than requesting the maximum. Verify by checking the requested quota's status in Service Quotas. |

## Claimed phone number not associated with a contact flow

| Field | Value |
| --- | --- |
| Read-only finding | A claimed phone number is not associated with any contact flow, so calls to it are not answered or routed. |
| Source | connect-telephony-and-voice-quality-investigation |
| Directed action | connect:AssociatePhoneNumberContactFlow (or connect:UpdatePhoneNumber) |
| Parameters | Provide the InstanceId, the PhoneNumberId (or E.164 number), and the ContactFlowId that should answer calls to the number. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run connect:AssociatePhoneNumberContactFlow pointing the number back to its prior contact flow, or disassociate if it had none before. |
| Notes | Confirm the target contact flow is published and correct before associating so live callers land in a working flow. Verify by describing the phone number and placing a test call. |

## Lambda data dip failing because the function is not associated to the instance

| Field | Value |
| --- | --- |
| Read-only finding | A contact flow invokes a Lambda function for a data dip, but the function is not associated with the Connect instance, so the invoke fails and the flow falls through or drops. |
| Source | connect-integration-and-lambda-reliability, connect-contact-flow-troubleshooting |
| Directed action | connect:AssociateLambdaFunction |
| Parameters | Provide the InstanceId and the FunctionArn of the Lambda the flow invokes. This associates an existing function to the instance; it does not pass an IAM role. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run connect:DisassociateLambdaFunction to remove the association that was just added, restoring the prior state. |
| Notes | Association authorizes Connect to invoke the function; the function's own resource policy and execution role are managed separately and are not changed here. Verify by listing the instance's associated Lambda functions and re-running the data dip in a test contact. |

## Recording or CTR encryption or instance storage misconfigured

| Field | Value |
| --- | --- |
| Read-only finding | Call recording, chat transcript, or contact trace record (CTR) storage is unencrypted, uses the wrong destination, or is missing a required storage association. |
| Source | connect-security-and-compliance-audit |
| Directed action | connect:UpdateInstanceStorageConfig or connect:AssociateInstanceStorageConfig (set SSE-KMS with a named key and the correct S3/Kinesis destination) |
| Parameters | Provide the InstanceId, the ResourceType (for example CALL_RECORDINGS, CHAT_TRANSCRIPTS, CONTACT_TRACE_RECORDS), and a StorageConfig with the correct S3 bucket/prefix or Kinesis stream plus an EncryptionConfig referencing a specific customer-managed KMS key ARN. Enabling or strengthening encryption only; disabling encryption is a prohibited action and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run connect:UpdateInstanceStorageConfig with the prior StorageConfig captured before the change (or disassociate the association that was just added if none existed before). |
| Notes | This op may reference a KMS key and a destination but generally does not pass an IAM role; when unsure whether a specific storage path requires a role, treat it as manual and confirm. Prerequisite: the Connect service and the writing principals must have permission on the named KMS key (kms:GenerateDataKey / kms:Decrypt), and the S3 bucket or Kinesis stream must exist. Verify by re-describing the instance storage config. |

## Security profile over-broad

| Field | Value |
| --- | --- |
| Read-only finding | A security profile grants permissions well beyond what its users need (for example administrative or manager permissions on agent accounts). |
| Source | connect-security-and-compliance-audit |
| Directed action | connect:UpdateSecurityProfile (remove excess permissions) or connect:UpdateUserSecurityProfiles (assign a correctly scoped profile) |
| Parameters | For UpdateSecurityProfile, provide the InstanceId, the SecurityProfileId, and the reduced Permissions list scoped to what the role actually requires. For UpdateUserSecurityProfiles, provide the UserId and the tighter SecurityProfileIds. Scope-down only; widening a profile or granting admin permissions is refused-prohibited-action and is never proposed. |
| Guardrail status | allowed (only for the scoped-down direction) |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run the same operation with the prior Permissions list or prior SecurityProfileIds captured before the change. |
| Notes | Removing permissions can interrupt work in progress for affected users; confirm the reduced set covers their real tasks, and prefer a staged rollout. Widening is prohibited and refused. Verify by re-describing the security profile and the affected users. |

## Deleting a stale or unused contact flow or phone number

| Field | Value |
| --- | --- |
| Read-only finding | A contact flow or a claimed phone number appears stale or unused and is a candidate for removal. |
| Source | connect-security-and-compliance-audit |
| Directed action | Would be connect:DeleteContactFlow / connect:ReleasePhoneNumber - NOT executed |
| Parameters | Not applicable. The safe remediation here is a deletion (or number release), which the agent refuses. |
| Guardrail status | refused-delete-class |
| Safety | RED (deletion is hard to reverse) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | None available from the agent: a deleted contact flow is gone, and a released phone number may not be reclaimable (it can return to the pool and be assigned elsewhere). This is exactly why delete-class is refused. |
| Notes | Remediation stays manual: a human confirms the flow or number is truly unused and performs the deletion or release with their own credentials. The agent's role is limited to detecting and reporting the candidate, consistent with the propose-not-delete posture of the collection. |

## Refused and manual remediations

The following findings above do not resolve to an executable directed action and stay a manual step:

- Deletion of contact flows and releasing phone numbers (connect-security-and-compliance-audit) - refused-delete-class. connect:DeleteContactFlow and connect:ReleasePhoneNumber are delete-class operations the agent always refuses, and they are not reliably reversible. A human performs the deletion or release after confirming the resource is unused.
- Security profile widening (connect-security-and-compliance-audit) - refused-prohibited-action. Only tightening a security profile is allowed; granting broader or administrative permissions is prohibited and never proposed, with or without approval.
- Any op that would pass an IAM role - refused-passrole, and stays manual. Associating a Lambda function (connect:AssociateLambdaFunction) and updating contact flow content (connect:UpdateContactFlowContent) that invokes a Lambda do not themselves pass a role, so they are allowed. If a specific instance storage or delivery path turns out to require passing a role at configure time, that path is refused-passrole and a human configures the role manually.

For the remaining findings (contact flow error branches, adding a queue to a routing profile, routing profile concurrency, concurrent calls quota increase, phone number to contact flow association, Lambda function association, and enabling or strengthening recording/CTR encryption and storage), the directed action is allowed and executable under per-action operator approval, with the rollback documented in each section. The concurrent active calls quota increase is the one timing caveat: it is a request that goes through AWS review and is sized to observed peak rather than granted instantly.
