# IoT finding to directed action mappings

This file maps the read-only IOT findings produced by the skills under skills/iot/ in this repository to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Every entry records the exact operation, its guardrail status, safety rating, approval scope, and rollback; IoT is unusual in that several natural fixes create or replace a topic rule that passes a RoleArn to the rules engine, which is an iam:PassRole path the agent always refuses, so those stay manual and are called out as such.

## IoT policy too narrow: device denied its own topic (PublishIn.AuthError / Subscribe.AuthError)

| Field | Value |
| --- | --- |
| Read-only finding | A device is denied publish or subscribe on a topic it legitimately owns, surfaced as PublishIn.AuthError or Subscribe.AuthError, because the attached IoT policy does not grant the specific topic or topic filter. |
| Source | iot-core-connectivity-and-throttling |
| Directed action | iot:CreatePolicyVersion (add the specific topic and topicfilter ARNs, set as the default version) |
| Parameters | Create a new policy version that adds the concrete iot:Publish/iot:Receive topic ARNs and the iot:Subscribe topicfilter ARNs the device needs, and set it as default. Granting iot:* or Resource:* is refused-prohibited-action and is never proposed. |
| Guardrail status | allowed (only for the scope-correct direction) |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | iot:SetDefaultPolicyVersion back to the prior version captured before the change. The prior version is retained, so revert is exact. |
| Notes | This grants exactly the topics the device owns, never a wildcard. Granting iot:* or Resource:* to "make the error go away" is a prohibited action. Verify by re-reading the default policy version and confirming the device reconnects and publishes. |

## Account IoT connect/publish throttling at legitimate load

| Field | Value |
| --- | --- |
| Read-only finding | Devices hit connect or publish throttling (Throttle metrics, 429-style rejects) at load that is legitimate for the fleet, indicating an account-level IoT Core quota is too low. |
| Source | iot-core-connectivity-and-throttling |
| Directed action | service-quotas RequestServiceQuotaIncrease for the specific IoT Core limit |
| Parameters | Request an increase to the specific throttled IoT Core quota (for example connections per second or inbound publish per second) to a targeted value backed by observed load, not the theoretical maximum. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | None direct: a quota increase is a request that AWS reviews and applies, and it is additive/non-destructive, so there is nothing harmful to revert. A later decrease request would be filed manually if ever needed. |
| Notes | The request goes through AWS review and is not instant. Ask only for the specific limit that is throttling, sized to real load, so the increase is defensible. Verify by reading the applied quota value after approval. |

## Expiring or superseded certificate needs retirement after rotation

| Field | Value |
| --- | --- |
| Read-only finding | A device certificate is near expiry or has been superseded, and an old certificate is still ACTIVE after a replacement has been issued and attached. |
| Source | iot-device-certificate-expiry-fleet |
| Directed action | iot:UpdateCertificate (Status=INACTIVE) to retire the superseded certificate |
| Parameters | Set the specific superseded certificate id to Status=INACTIVE, only after the new certificate is confirmed attached and the device is connecting on it. Deleting the certificate (iot:DeleteCertificate) is refused-delete-class and is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | iot:UpdateCertificate with Status=ACTIVE to reactivate the certificate. Deactivation is fully reversible, which is exactly why it is chosen over deletion. |
| Notes | Deactivate first and confirm nothing breaks; a human deletes the retired certificate later with their own credentials. Deletion is delete-class and stays manual. Verify by reading the certificate status and confirming devices still connect on the new certificate. |

## Revoked certificate still attached to a thing or policy

| Field | Value |
| --- | --- |
| Read-only finding | A certificate that has been revoked or retired is still attached to a thing principal and/or an IoT policy, leaving a stale trust path in place. |
| Source | iot-device-certificate-expiry-fleet |
| Directed action | iot:DetachPolicy and/or iot:DetachThingPrincipal (detach the revoked certificate) |
| Parameters | Detach the revoked certificate from the specific policy (iot:DetachPolicy) and from the specific thing (iot:DetachThingPrincipal). Detaching does not delete the certificate. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-attach via iot:AttachPolicy and iot:AttachThingPrincipal using the identifiers captured before the change. Detach is a reversible relationship change, not a delete. |
| Notes | Detach is allowed because the certificate resource is not deleted, only its attachments are removed. Confirm the thing has a valid current certificate before detaching the old one so the device is not orphaned. Verify by listing the thing principals and policy targets. |

## IoT rule action failing / needs error action, DLQ, or a delivery RoleArn

| Field | Value |
| --- | --- |
| Read-only finding | A topic rule action is failing and needs an error action or DLQ added, or a rule that delivers to Lambda, SQS, or Kinesis needs its RoleArn set or corrected. |
| Source | iot-rules-engine-action-failures |
| Directed action | Would be iot:CreateTopicRule / iot:ReplaceTopicRule specifying a RoleArn - NOT executed |
| Parameters | Not applicable. Creating or replacing a topic rule whose payload specifies a RoleArn passes an IAM role to the rules engine, which is an iam:PassRole operation. |
| Guardrail status | refused-passrole |
| Safety | RED (passes a role; the agent refuses regardless of approval) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | None from the agent, because the agent does not perform the operation. A human applies the rule change with their own credentials. |
| Notes | This is the key refused example for IoT: any CreateTopicRule/ReplaceTopicRule that carries a RoleArn (error action to SQS/SNS, or a Lambda/SQS/Kinesis action) is refused-passrole and stays manual. An operator adds the error action or fixes the RoleArn by hand. Enabling an already-existing, correctly-roled rule is a different case (see below). |

## Disabled rule that should be enabled

| Field | Value |
| --- | --- |
| Read-only finding | A topic rule that should be routing messages is disabled, so matching messages are not being delivered. |
| Source | iot-rules-engine-action-failures |
| Directed action | iot:EnableTopicRule (enable the existing rule) |
| Parameters | Enable the specific existing rule by name. This does not re-pass a role: the rule already exists with its RoleArn intact, so enabling it is not an iam:PassRole operation. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | iot:DisableTopicRule to restore the disabled state. |
| Notes | Enabling an existing rule does not re-pass the role, so it is allowed; still confirm the rule's RoleArn is intact and valid before enabling so messages actually deliver. Creating or replacing the rule is the refused-passrole case above. Verify by reading the rule and confirming deliveries resume. |

## Greengrass bad deployment revision causing UNHEALTHY cores

| Field | Value |
| --- | --- |
| Read-only finding | A Greengrass deployment revision has left one or more core devices UNHEALTHY, and the fix is to deploy a corrected or rollback revision. |
| Source | greengrass-deployment-and-core-health |
| Directed action | greengrassv2:CreateDeployment (deploy a corrected or last-known-good revision) |
| Parameters | Create a deployment targeting the affected thing group or core, pinning a corrected or previously known-good revision. This does not pass a role in the iam:PassRole sense: the core device authenticates with its token exchange role, which already exists. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Create another deployment pinning the last known-good revision. Deployments are versioned, so reverting is another CreateDeployment to a prior revision. |
| Notes | Blast radius caveat: a Greengrass deployment is a fleet-wide change that can affect every targeted core at once, so scope the target group carefully and consider a staged rollout. Because of that blast radius this may warrant escalation and senior approval even though the operation itself is allowed. Verify by watching deployment status and core health return to HEALTHY. |

## FleetWise campaign SUSPENDED that should be running

| Field | Value |
| --- | --- |
| Read-only finding | An IoT FleetWise campaign is SUSPENDED when it should be collecting and ingesting vehicle data, so signals are not flowing. |
| Source | iot-fleetwise-ingestion-health |
| Directed action | iotfleetwise:UpdateCampaign (action RESUME) or approve the campaign |
| Parameters | Resume the specific campaign by name (action RESUME), or approve it if it is pending approval, so ingestion restarts. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | iotfleetwise:UpdateCampaign with action SUSPEND to return the campaign to the suspended state. |
| Notes | Confirm the suspension was not intentional (for example a cost or data-volume pause) before resuming. Verify by reading the campaign status and confirming ingestion metrics recover. |

## Refused and manual remediations

The following IoT remediations do not resolve to an executable directed action and stay a manual step:

- IoT rule creation or replacement that passes a RoleArn (iot-rules-engine-action-failures) - refused-passrole. Any iot:CreateTopicRule or iot:ReplaceTopicRule whose payload carries a RoleArn (adding an error action or DLQ, or wiring a Lambda/SQS/Kinesis action) passes an IAM role to the rules engine, which the agent refuses regardless of approval. A human applies the rule change with their own credentials. Enabling an already-existing, correctly-roled rule via iot:EnableTopicRule is the allowed alternative because it does not re-pass the role.
- Certificate deletion (iot-device-certificate-expiry-fleet) - refused-delete-class. iot:DeleteCertificate is a delete-class operation the agent always refuses and cannot reverse. The agent deactivates the certificate (iot:UpdateCertificate Status=INACTIVE) instead, and a human performs the deletion later after confirming nothing depends on it.
- Widening an IoT policy (iot-core-connectivity-and-throttling) - refused-prohibited-action. Granting iot:* or Resource:* is prohibited by the repository guardrails; only adding the specific topic and topicfilter ARNs the device owns is allowed via iot:CreatePolicyVersion.

For the remaining findings (IoT policy scope-correct grant, IoT Core quota increase, certificate deactivation, revoked-certificate detach, enabling an existing rule, Greengrass corrected deployment, and FleetWise campaign resume), the directed action is allowed and executable under per-action operator approval, with the rollback documented in each section. The Greengrass deployment is the one to watch: it is allowed but fleet-wide, so its blast radius warrants careful target scoping and often escalation to senior approval before it runs.
