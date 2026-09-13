---
name: medialive-channel-and-input-health
agent_type: "Incident RCA"
description: Diagnoses AWS Elemental MediaLive live channel and input problems
  by analyzing channel state, active alerts, input loss, pipeline failover on
  redundant channels, primary input activity, frame rate drops, and dropped
  frames. Use this skill when a live channel goes to black or freezes, viewers
  report buffering or loss of stream, MediaLive raises input loss or pipeline
  alerts, or a STANDARD two-pipeline channel fails over unexpectedly.
version: "1.0.0"
last_updated: "2026-08-14"
---

# MediaLive Channel and Input Health

Use this skill to systematically diagnose why a live MediaLive channel is
degraded or off-air, isolate whether the fault is in the channel, the pipeline,
or the upstream input source, and recommend targeted remediation. Posture is
read-only: inspect state and metrics first, then propose specific fixes.

## When to Activate

- A channel is in an unexpected state (not RUNNING when it should be, or stuck
  in STARTING, STOPPING, RECOVERING, or reporting IDLE).
- CloudWatch AWS/MediaLive ActiveAlerts is greater than 0 for the channel.
- InputLossSeconds is climbing, indicating the encoder is not receiving frames.
- InputVideoFrameRate drops below the expected source rate (for example, below
  25, 29.97, 50, or 59.94) or goes to 0.
- A STANDARD (two-pipeline) channel shows pipeline 0 or pipeline 1 unhealthy or
  has failed over.
- PrimaryInputActive is 0 on a channel with input failover configured.
- Dropped frames appear in output, or FillMsec rises relative to OutputMsec.

## Step 1: Establish Channel State and Active Alerts

Collect the current channel context before touching metrics.

1. List and describe the channel with use_aws (medialive ListChannels, then
   DescribeChannel on the ChannelId). Capture:
   - State: CREATING, IDLE, STARTING, RUNNING, RECOVERING, STOPPING, DELETING,
     UPDATING, or CREATE_FAILED. A healthy live channel is RUNNING.
   - PipelinesRunningCount and the ChannelClass: STANDARD (two pipelines, 0 and
     1) or SINGLE_PIPELINE (one pipeline, no redundancy).
   - InputAttachments and the InputSpecification (codec, resolution, maximum
     bitrate).
2. Pull the alert signal from CloudWatch AWS/MediaLive:
   - ActiveAlerts per ChannelId and Pipeline. Any value greater than 0 means
     MediaLive has a standing problem it wants attention on.
3. Map the state to a first hypothesis using the table below.

| Channel State | Meaning | First Action |
|---------------|---------|--------------|
| RUNNING, ActiveAlerts 0 | Healthy | Confirm the reported symptom is real; check output/CDN |
| RUNNING, ActiveAlerts > 0 | Live but degraded | Go to Step 2 (input) and Step 3 (pipeline) |
| RECOVERING | Pipeline restarting after fault | Go to Step 3; identify which pipeline failed and why |
| IDLE | Stopped intentionally or never started | Confirm whether it should be running |
| STARTING stuck | Failing to acquire input or resources | Go to Step 2; check input state and source |
| CREATE_FAILED / UPDATE errors | Config or capacity problem | Review last channel update and error detail |

## Step 2: Quantify Input Loss and Primary Input Activity

Input loss is the most common cause of black or frozen output.

1. In CloudWatch AWS/MediaLive, evaluate per ChannelId and Pipeline over the
   incident window (use SUM at 1-minute period):
   - InputLossSeconds: seconds in the period the pipeline saw no usable input.
     Sustained non-zero values point at the source, network, or input config,
     not the encoder.
   - InputVideoFrameRate: should track the source frame rate. A drop toward 0
     confirms the encoder stopped receiving frames.
   - PrimaryInputActive: 1 means the primary input is the active one; 0 means
     MediaLive is on the failover/secondary input (or has no active input).
2. Determine the configured input loss behavior on the channel
   (InputLossBehavior): whether output shows a fill slate/color, freezes the
   last frame, or repeats a frame. This explains what viewers see during loss.
3. Inspect the input itself with use_aws:
   - medialive ListInputs then DescribeInput for the attached input. Confirm
     Type (RTP_PUSH, RTMP_PUSH, RTMP_PULL, URL_PULL, MP4_FILE, MEDIACONNECT,
     INPUT_DEVICE) and State (DETACHED, ATTACHED, CREATING).
   - For hardware contribution encoders, medialive DescribeInputDevice to check
     ConnectionState (CONNECTED vs DISCONNECTED), DeviceState, and the reported
     input signal.

Interpretation:

| Signal | Reading | Likely Cause |
|--------|---------|--------------|
| InputLossSeconds > 0, both pipelines | Loss on all inputs | Upstream source or contribution network down |
| InputLossSeconds > 0, one pipeline only | Single-path loss | Network path or one push URL for that pipeline |
| InputVideoFrameRate = 0 | No frames arriving | Source stopped, wrong port, firewall, or encoder off |
| PrimaryInputActive = 0 | On secondary input | Primary source failed; failover did its job |
| InputDevice DISCONNECTED | Appliance offline | Field encoder power, network, or link failure |

## Step 3: Verify Pipeline Redundancy and Failover

STANDARD channels run two independent pipelines (0 and 1). Failover between
them should be transparent; a channel is only fully off-air when both fail.

1. Confirm ChannelClass from Step 1. If SINGLE_PIPELINE, there is no pipeline
   redundancy: any pipeline fault takes the channel down, and RECOVERING means
   a full restart. This is a design limitation, not a transient fault.
2. For STANDARD, evaluate per-pipeline metrics for pipeline 0 and pipeline 1
   separately:
   - ActiveAlerts per Pipeline to see which pipeline is unhealthy.
   - FillMsec versus OutputMsec per Pipeline. FillMsec rising while OutputMsec
     is flat means the encoder is inserting fill (slate or repeat) because it
     lacks real input on that pipeline.
   - NetworkIn and NetworkOut per Pipeline to confirm data is flowing.
3. Determine whether a failover occurred and whether it is stable:
   - If pipeline 0 alerts cleared and pipeline 1 is carrying output cleanly,
     failover succeeded and the channel is up on one pipeline. Restore the
     failed pipeline's input path rather than restarting the whole channel.
   - If both pipelines show ActiveAlerts and InputLossSeconds, the fault is
     upstream (shared source), not a pipeline fault.

Do not stop and restart a RUNNING redundant channel to clear a single-pipeline
alert; that removes the working pipeline too. Repair the affected input path.

## Step 4: Assess Output and Dropped Frames

Confirm whether the problem is input-side or output/encoding-side.

1. Compare InputVideoFrameRate (frames in) against evidence of output frames
   out. If input frame rate is healthy but viewers still see problems, the
   fault is downstream of encode.
2. Check for dropped frames: sustained FillMsec with healthy input indicates
   the pipeline is padding output, which viewers perceive as freeze or stutter.
3. Confirm the InputSpecification matches the actual source. A source that
   exceeds the configured maximum bitrate, resolution, or codec can cause
   dropped frames or decode errors that surface as ActiveAlerts.
4. If output is fine at MediaLive but the symptom persists downstream, the
   issue is in the packaging or CDN layer (see the MediaPackage skill), not
   MediaLive.

## Step 5: Correlate With the Upstream Source

Anchor the root cause to a specific source event.

1. Align the start of InputLossSeconds and any InputVideoFrameRate drop to the
   contribution encoder or MediaConnect flow timeline.
2. For MEDIACONNECT inputs, check the associated MediaConnect flow for source
   disconnects or bitrate drops in the same window.
3. For PUSH inputs (RTP_PUSH, RTMP_PUSH), confirm the source is still pushing to
   the correct MediaLive input endpoint and that the input security group still
   allows the source CIDR. Do not widen the input security group to 0.0.0.0/0;
   scope it to the known contribution source ranges.
4. For PULL inputs, confirm the origin URL is reachable and returning the
   stream.

## Step 6: Remediate

Match the fix to the confirmed root cause. Keep changes specific and reversible.

- Upstream source loss (both pipelines): restore the contribution encoder or
  MediaConnect flow; MediaLive recovers automatically once frames return.
- Single input path loss on a STANDARD channel: repair that pipeline's network
  path or push URL; leave the healthy pipeline running.
- Primary input failed, on secondary: confirm automatic input failover behaved
  correctly, then repair the primary and let it resync before failing back.
- SINGLE_PIPELINE fragility causing repeated RECOVERING: recommend migrating to
  a STANDARD (two-pipeline) channel for redundancy on business-critical feeds.
- Source exceeding InputSpecification: adjust the contribution encoder to match
  the configured codec, resolution, and maximum bitrate, or update the input
  specification to accommodate the real source.
- Input device DISCONNECTED: dispatch to restore power and network to the field
  appliance; confirm ConnectionState returns to CONNECTED.
- Input security group scoped too narrowly and blocking a legitimate new source
  IP: add the specific source CIDR (never 0.0.0.0/0).

## Output

Provide a diagnosis summary:
1. Root cause category: upstream source loss, single-pipeline fault, input
   failover event, source specification mismatch, input device offline, or
   downstream (non-MediaLive) issue.
2. Supporting evidence: channel State, ActiveAlerts count, InputLossSeconds,
   InputVideoFrameRate, PrimaryInputActive, and per-pipeline FillMsec vs
   OutputMsec values over the incident window.
3. Which pipeline(s) were affected and whether failover succeeded.
4. Specific remediation steps tied to the confirmed cause.
5. Preventive measures: input failover configuration, migration to STANDARD
   class for critical channels, and CloudWatch alarms on ActiveAlerts > 0 and
   InputLossSeconds > 0.
