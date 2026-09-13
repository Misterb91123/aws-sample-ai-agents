# Media finding to directed action mappings

This file maps the read-only AWS Elemental media findings produced by the skills in this repository's skills/media/ directory to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Media is high-visibility and live: several of these actions touch a channel that is actively serving a broadcast, so blast radius is large and safety ratings run YELLOW to RED (never GREEN), with the delete-class and pass-a-role cases refused outright and left manual.

## MediaLive channel stuck or idle needs a restart to recover the input pipeline

| Field | Value |
| --- | --- |
| Read-only finding | A MediaLive channel is in an unexpected state (stuck STARTING, stuck RECOVERING, or IDLE when it should be RUNNING) and the input pipeline needs a channel restart to recover. |
| Source | medialive-channel-and-input-health |
| Directed action | medialive:StopChannel followed by medialive:StartChannel (restart the existing channel) |
| Parameters | Stop then start the specific existing ChannelId. This restarts an already-created channel; it does not create a channel and passes no RoleArn, so it does not trip the passrole guardrail. |
| Guardrail status | allowed (no PassRole on start/stop of an existing channel) |
| Safety | RED when the channel is a live viewer-facing broadcast (the restart interrupts the stream); YELLOW only for a channel that is not currently serving viewers |
| Approval scope | single-use, with senior/escalated approval required for a live broadcast channel and ideally a maintenance window |
| Rollback | None needed and none applicable - the restart is itself the recovery action, not a change to revert. The relevant caveat is the interruption: viewers see loss or slate during the stop/start, so the "revert" is simply that the channel comes back RUNNING. |
| Notes | Blast radius is the entire channel: on a STANDARD two-pipeline channel a full restart drops the healthy pipeline too, so do not restart to clear a single-pipeline alert - repair that input path instead. Only restart when the whole channel is stuck. Confirm the channel returns to RUNNING with ActiveAlerts 0 and InputLossSeconds back at 0 after start. Escalate before touching a live broadcast. |

## MediaConvert reserved queue saturated causing job backlog

| Field | Value |
| --- | --- |
| Read-only finding | A RESERVED MediaConvert queue has all committed RTS (Reserved Transcode Slots) busy; jobs pile up in SUBMITTED and StandbyTime climbs while submissions stay steady. |
| Source | mediaconvert-job-failure-and-backlog |
| Directed action | mediaconvert:UpdateQueue (adjust the reservation plan RTS, or move overflow off the queue) |
| Parameters | Update the specific queue's ReservationPlan to raise committed RTS toward peak concurrency, or route overflow to an on-demand queue. This updates an existing queue and passes no service RoleArn, so it does not trip the passrole guardrail. |
| Guardrail status | allowed (UpdateQueue passes no role) |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run mediaconvert:UpdateQueue with the prior ReservationPlan captured before the change. Raising RTS is additive capacity and reversible; note that reservation commitment changes can carry billing commitment terms, so confirm the plan change is what the operator intends. |
| Notes | Raising committed RTS increases cost; verify peak concurrency from StandbyTime and ProgressingJobsCount before committing more slots. Verify by re-reading the queue and watching StandbyTime fall as the backlog drains. |

## MediaConvert on-demand backlog or a paused queue needs resuming

| Field | Value |
| --- | --- |
| Read-only finding | Jobs are not progressing because a queue is PAUSED, or an on-demand queue needs to be brought back to active service to clear a backlog. |
| Source | mediaconvert-job-failure-and-backlog |
| Directed action | mediaconvert:UpdateQueue with Status=ACTIVE (resume the queue) |
| Parameters | Set the specific queue's Status to ACTIVE. This updates an existing queue and passes no service RoleArn, so it does not trip the passrole guardrail. |
| Guardrail status | allowed (UpdateQueue passes no role) |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run mediaconvert:UpdateQueue with Status=PAUSED to restore the prior state. Fully reversible - the status is a single captured value. |
| Notes | Resuming a queue releases queued jobs into processing; confirm the backlog was paused intentionally and that downstream delivery can absorb the burst. Verify by re-reading queue Status and watching SubmittedJobsCount drain. |

## Creating a new MediaLive channel or MediaConvert job that needs a service role

| Field | Value |
| --- | --- |
| Read-only finding | The remediation would require creating a new MediaLive channel or a new MediaConvert queue/job that references a service RoleArn (for example medialive:CreateChannel with a RoleArn, or mediaconvert:CreateJob/CreateQueue referencing an IAM role). |
| Source | medialive-channel-and-input-health, mediaconvert-job-failure-and-backlog |
| Directed action | Would be medialive:CreateChannel / mediaconvert:CreateJob (with a service RoleArn) - NOT executed |
| Parameters | Not applicable. Creating the resource requires handing a service role to the media service, which is an iam:PassRole operation the agent refuses regardless of approval. |
| Guardrail status | refused-passrole |
| Safety | RED (a new live channel is a broadcast-affecting resource, and the create path passes a role) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | Not applicable - the action is never taken. |
| Notes | Passing a role to a service is refused across the board, and channel/job creation on the media services requires exactly that. Remediation stays manual: a human creates the channel or job with their own credentials and the correct execution role. The agent's role is limited to diagnosing and recommending the change. |

## MediaPackage origin endpoint misconfigured (window or packaging error)

| Field | Value |
| --- | --- |
| Read-only finding | A MediaPackage origin endpoint is misconfigured - for example a PlaylistWindowSeconds/ManifestWindowSeconds or StartoverWindowSeconds shorter than the CDN cache and player buffer (causing 404s on aged-out segments), or a packaging setting producing 400s. |
| Source | mediapackage-origin-and-packaging-health |
| Directed action | mediapackage:UpdateOriginEndpoint (correct the window or packaging configuration) |
| Parameters | Update the specific origin endpoint's HLS or DASH settings - for example increase PlaylistWindowSeconds/ManifestWindowSeconds and StartoverWindowSeconds to cover the CDN and buffer needs, or fix the identified packaging parameter. This updates an existing endpoint and passes no service RoleArn. |
| Guardrail status | allowed (UpdateOriginEndpoint passes no role) |
| Safety | YELLOW (recoverable config change on a live origin; test with a player before and after) |
| Approval scope | single-use |
| Rollback | Re-run mediapackage:UpdateOriginEndpoint with the prior packaging/window values captured before the change. The settings are fully described, so revert is exact. |
| Notes | Do not clear a 403 by removing CDN authorization or opening the endpoint publicly; realign the shared CDN secret instead. Confirm the fix against a test player and watch the egress 4xx/5xx ratio fall. Because the endpoint is serving a live audience, treat propagation and cache behavior as part of the change. |

## MediaTailor ad decision server URL or playback config wrong causing ad errors

| Field | Value |
| --- | --- |
| Read-only finding | A MediaTailor playback configuration has a wrong AdDecisionServerUrl or malformed targeting macros (empty ADS responses, ADS errors), or another playback-config setting is causing ad insertion failures. |
| Source | mediatailor-ad-insertion-health |
| Directed action | mediatailor:PutPlaybackConfiguration (correct the ADS URL, macros, or config) |
| Parameters | Update the specific ConfigurationName's AdDecisionServerUrl / targeting macros / related settings to the corrected values. In the common case this passes no service role and is allowed. |
| Guardrail status | allowed (note: if the configuration variant references an IAM role, that path needs review and may be refused-passrole) |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run mediatailor:PutPlaybackConfiguration with the prior configuration captured before the change. PutPlaybackConfiguration replaces the config with a fully specified body, so the prior body restores the exact previous state. |
| Notes | If the playback configuration references a role (for example a logging/personalization role), confirm that variant does not require passing a role before proceeding; where it does, it becomes refused-passrole and stays manual. Verify by re-reading the configuration and watching AdDecisionServer.Errors/Timeouts fall and fill rate recover. |

## Deleting a stale channel or origin endpoint

| Field | Value |
| --- | --- |
| Read-only finding | A channel or origin endpoint appears stale or unused and is a candidate for removal (for example an idle MediaLive channel or an unused MediaPackage origin endpoint). |
| Source | medialive-channel-and-input-health, mediapackage-origin-and-packaging-health, mediaconvert-job-failure-and-backlog |
| Directed action | Would be medialive:DeleteChannel / mediapackage:DeleteOriginEndpoint - NOT executed |
| Parameters | Not applicable. The removal is a delete-class operation, which the agent refuses. |
| Guardrail status | refused-delete-class |
| Safety | RED (deletion is hard to reverse, and a deleted channel/endpoint takes its configuration with it) |
| Approval scope | Not applicable - the agent will not propose or execute this even with approval |
| Rollback | None available from the agent: a deleted channel or origin endpoint cannot be restored, only recreated from scratch. This is exactly why delete-class is refused. |
| Notes | Remediation stays manual: a human confirms the channel or endpoint is truly stale (no live event, no CDN pulling from it) and performs the deletion with their own credentials. The agent detects and reports the candidate only. |

## Refused and manual remediations

The following findings above do not resolve to an executable directed action and stay a manual step:

- Creating a MediaLive channel or a MediaConvert queue/job that references a service role (medialive-channel-and-input-health, mediaconvert-job-failure-and-backlog) - refused-passrole. Handing a service RoleArn to the media service is an iam:PassRole operation the agent refuses regardless of approval, and channel/job creation requires it. A human creates the resource with the correct execution role using their own credentials.
- Deleting a stale channel or origin endpoint (any media skill) - refused-delete-class. Deleting a MediaLive channel or a MediaPackage origin endpoint is a delete-class operation the agent always refuses, and it is not reversible. A human confirms the resource is truly unused and performs the deletion manually.

For the executable findings, per-action operator approval applies and the rollback is documented in each section, but the live-broadcast blast radius dominates the risk picture:

- A MediaLive channel restart (medialive:StopChannel then StartChannel) interrupts every viewer while the channel comes back up, so on a live viewer-facing feed it is RED, requires senior/escalated approval, and should run in a maintenance window rather than mid-broadcast. On a STANDARD channel, prefer repairing the affected input path over restarting the whole channel.
- MediaConvert queue changes (mediaconvert:UpdateQueue) and MediaPackage/MediaTailor config corrections (mediapackage:UpdateOriginEndpoint, mediatailor:PutPlaybackConfiguration) are allowed and YELLOW, but they still act on live-serving resources: verify with a test player or by watching the relevant CloudWatch metrics recover, and capture the prior configuration first so the revert is exact. The MediaTailor path is allowed only in the no-role variant; a role-referencing configuration becomes refused-passrole and stays manual.
