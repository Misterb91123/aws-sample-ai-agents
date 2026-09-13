# Messaging and deliverability finding to directed action mappings

This file maps the read-only MESSAGING and DELIVERABILITY findings produced by the skills in this repository (ses-deliverability-and-reputation, ses-sending-quota-and-throttle, pinpoint-campaign-delivery-health, chime-sdk-media-session-quality) to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Deliverability carries an important nuance: many fixes are not a single API call - improving sender reputation is a process (list hygiene, authentication, warmup), so each entry is honest that the directed action covers only the concrete config change that can be made, while the reputation or network-quality recovery itself stays a human and process action.

## SES bounce/complaint rate at risk or suppression not enabled

| Field | Value |
| --- | --- |
| Read-only finding | The SES account bounce or complaint rate is trending toward the enforcement threshold, and the account-level or configuration-set suppression list is not enabled, so mail keeps going to addresses that already bounced or complained. |
| Source | ses-deliverability-and-reputation |
| Directed action | sesv2:PutAccountSuppressionAttributes (enable account-level suppression for BOUNCE and COMPLAINT) and/or sesv2:PutConfigurationSetSuppressionOptions (enable suppression on a specific configuration set) |
| Parameters | Set SuppressedReasons to include BOUNCE and COMPLAINT at the account level, or set the equivalent SuppressedReasons on the named configuration set. This turns a protective control on; it does not disable any control. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run sesv2:PutAccountSuppressionAttributes / sesv2:PutConfigurationSetSuppressionOptions with the prior SuppressedReasons captured before the change. Revert is exact because the reason set is fully recorded. |
| Notes | This reduces repeat sends to known-bad addresses, which slows further reputation damage. It is not a fix for the reputation itself: recovering sender reputation is a process (list hygiene, re-permissioning, authentication, warmup), not one mutating call. Verify by reading the account or configuration-set suppression attributes. |

## SES missing or failed DKIM (authentication not aligned)

| Field | Value |
| --- | --- |
| Read-only finding | A sending identity has DKIM disabled or in a failed state, so messages are not DKIM-signed and authentication does not align, hurting deliverability. |
| Source | ses-deliverability-and-reputation |
| Directed action | sesv2:PutEmailIdentityDkimAttributes (enable DKIM signing / configure Easy DKIM on the identity) |
| Parameters | Set SigningEnabled=true on the specified email identity to turn on DKIM signing (Easy DKIM). Turning signing off is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run sesv2:PutEmailIdentityDkimAttributes with SigningEnabled=false to restore the prior state. |
| Notes | DKIM is the part SES controls. SPF and DMARC live in DNS and are changed outside AWS by whoever manages the domain's DNS zone; those remain a manual step. For Easy DKIM the CNAME records must also be published in DNS before signing verifies. Verify by reading the identity's DKIM attributes and status. |

## SES account or configuration set still sending during a reputation event

| Field | Value |
| --- | --- |
| Read-only finding | A complaint or bounce spike is active, yet a specific configuration set keeps sending, or sending needs to be re-enabled on a configuration set after the issue has been fixed. |
| Source | ses-deliverability-and-reputation |
| Directed action | sesv2:PutConfigurationSetSendingOptions (set SendingEnabled on a specific configuration set) |
| Parameters | To stop harm during an active spike, set SendingEnabled=false on the named configuration set (a targeted, protective pause on one config set). After remediation, set SendingEnabled=true on that same configuration set to resume. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run sesv2:PutConfigurationSetSendingOptions flipping SendingEnabled back to the prior value. Both directions are the exact inverse of each other and fully reversible. |
| Notes | Pausing sending on a specific configuration set to stop active harm is a protective action, not an improper disabling of a control, so it is allowed YELLOW; re-enabling after the underlying issue is fixed is likewise allowed YELLOW. This is scoped to one configuration set, not an account-wide sending shutoff. Verify by reading the configuration set's sending options. |

## SES sending quota exhaustion

| Field | Value |
| --- | --- |
| Read-only finding | The account is hitting its SES sending limits (Max24HourSend or the max send rate), throttling legitimate mail. |
| Source | ses-sending-quota-and-throttle |
| Directed action | service-quotas RequestServiceQuotaIncrease for the SES sending quota |
| Parameters | Request a targeted increase to the specific SES quota (24-hour send quota or send rate) sized to the observed and forecast demand, not the maximum possible value. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | The request can be withdrawn while pending; an approved increase can be lowered later via another RequestServiceQuotaIncrease. The action opens a review rather than instantly mutating live capacity. |
| Notes | This opens an AWS review and does not take effect until AWS approves it; it is not instantaneous. Request a targeted value with justification rather than the ceiling. Verify by reading the applied quota value after approval. |

## SES sandbox limiting production sends

| Field | Value |
| --- | --- |
| Read-only finding | The account is still in the SES sandbox, so sends are restricted to verified recipients and low volume, blocking production traffic. |
| Source | ses-sending-quota-and-throttle |
| Directed action | Would be a production-access request - NOT a single mutating API the agent runs |
| Parameters | Not applicable. Moving out of the sandbox is a support/quota request submitted through the console or a support case, not a single mutating API call the agent executes. |
| Guardrail status | manual |
| Safety | YELLOW |
| Approval scope | Not applicable - handled by a human through the console or support |
| Rollback | Not applicable at the agent level; the request itself is a review process. |
| Notes | Framed as manual on purpose: production access is granted after an AWS review of use case and sending practices, so it is a human-submitted request, not an agent directed action. The agent's role is to surface that the account is in the sandbox. |

## Pinpoint channel throttling, disabled, or misconfigured

| Field | Value |
| --- | --- |
| Read-only finding | A Pinpoint channel is throttling, disabled when it should be on, or configured incorrectly, causing delivery problems for that channel. |
| Source | pinpoint-campaign-delivery-health |
| Directed action | pinpoint UpdateEmailChannel / UpdateSmsChannel / UpdateApnsChannel (and the equivalent channel update for the channel in question) |
| Parameters | Apply the corrected channel configuration, for example Enabled=true on a channel that should be active, or the corrected sender/config values for that channel. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run the same channel update with the prior configuration captured before the change (for example set Enabled back to its previous value). |
| Notes | This corrects channel-level configuration only. Downstream carrier or provider throttling (for example SMS carrier limits) is outside AWS and stays a provider-side or manual concern. Verify by reading the channel configuration after the update. |

## Pinpoint campaign misconfigured causing delivery failures

| Field | Value |
| --- | --- |
| Read-only finding | A Pinpoint campaign has a configuration error (segment, schedule, message, or channel settings) that is causing delivery failures. |
| Source | pinpoint-campaign-delivery-health |
| Directed action | pinpoint UpdateCampaign (correct the campaign configuration) |
| Parameters | Apply the corrected campaign settings (for example fix the message template, schedule, or channel binding). Deleting the campaign is never proposed. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run pinpoint UpdateCampaign with the prior campaign configuration captured before the change. |
| Notes | Correcting a campaign is allowed; deleting a campaign is refused-delete-class and stays manual. Verify by reading the campaign configuration and its delivery metrics after the update. |

## Chime SDK meeting capacity or quota limits causing join failures

| Field | Value |
| --- | --- |
| Read-only finding | Chime SDK meetings are hitting a service quota (for example concurrent meetings or attendees), causing join failures; separately, media quality issues such as packet loss or jitter are degrading sessions. |
| Source | chime-sdk-media-session-quality |
| Directed action | service-quotas RequestServiceQuotaIncrease for the affected Chime SDK quota |
| Parameters | Request a targeted increase to the specific Chime SDK limit (for example concurrent meetings or attendees) sized to observed demand, not the maximum. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | The request can be withdrawn while pending; an approved increase can be lowered later via another RequestServiceQuotaIncrease. |
| Notes | A quota increase is the only piece that maps to a mutating AWS op, and it opens an AWS review rather than taking effect instantly. Media quality problems (packet loss, jitter, one-way audio) are client and network-side and are NOT a mutating AWS operation - they stay a manual investigation of the network path, client, and endpoints. Verify the quota by reading the applied value after approval. |

## Refused and manual remediations

The following findings above do not resolve to an executable directed action and stay a manual step, or map only partially to one:

- Pinpoint campaign or application deletion (pinpoint-campaign-delivery-health) - refused-delete-class. Deleting a campaign or app is a delete-class operation the agent always refuses and is not reversible. Correcting a campaign via UpdateCampaign is allowed; a human performs any deletion with their own credentials.
- SES production-access request (ses-sending-quota-and-throttle) - manual. Leaving the SES sandbox is a support/quota request reviewed by AWS through the console or a support case, not a single mutating API the agent runs.
- SPF and DMARC alignment (ses-deliverability-and-reputation) - manual. SPF and DMARC records live in DNS and are changed outside AWS by whoever manages the domain's DNS zone. Only DKIM (Easy DKIM) maps to an SES directed action; the DNS records for DKIM CNAMEs, SPF, and DMARC are published manually.
- Chime SDK media and network quality (chime-sdk-media-session-quality) - manual. Packet loss, jitter, and one-way audio are client and network-side and have no mutating AWS operation; they are investigated and fixed on the network path and endpoints.

Be honest about the deliverability nuance: for the executable actions above (account and configuration-set suppression, DKIM signing, configuration-set sending pause/resume, SES and Chime SDK quota increases, Pinpoint channel and campaign updates), the directed action covers only the concrete configuration change that can be made under per-action operator approval. Sender-reputation recovery and media/network quality are processes, not one API call, and each remains a human and process activity that the agent supports by detecting and reporting, then applying the one config change that is safely reversible.
