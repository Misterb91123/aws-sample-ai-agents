---
name: mediaconvert-job-failure-and-backlog
agent_type: "Incident RCA"
description: Diagnoses AWS Elemental MediaConvert transcode job failures and
  queue backlog by analyzing job error rates and error codes, failing job input
  and output settings, queue depth, standby time, and reserved versus on-demand
  queue saturation. Use this skill when JobsErroredCount spikes, transcode jobs
  fail with recurring error codes, jobs sit in SUBMITTED for long periods, or a
  queue backlog delays delivery of encoded assets.
version: "1.0.0"
last_updated: "2026-08-14"
---

# MediaConvert Job Failure and Backlog

Use this skill to systematically diagnose why AWS Elemental MediaConvert jobs
are failing or backing up, separate per-job failures from queue capacity
problems, and recommend targeted remediation. Posture is read-only: inspect job
and queue state and metrics first, then propose specific fixes.

## When to Activate

- CloudWatch AWS/MediaConvert JobsErroredCount spikes above baseline.
- Jobs complete with ERROR status and repeat the same error code.
- Assets are delivered late because jobs sit in SUBMITTED (queued) too long.
- StandbyTime rises, indicating jobs wait before processing begins.
- A reserved queue is saturated (all reserved slots busy) or an on-demand queue
  is throttled.
- JobsCompletedCount falls while submissions stay constant, signaling a stall.

## Step 1: Measure Error Rate and Classify Error Codes

Establish the scale and shape of the failures first.

1. In CloudWatch AWS/MediaConvert, evaluate over the incident window (SUM at
   5-minute period), per Queue where possible:
   - JobsErroredCount: number of jobs ending in ERROR.
   - JobsCompletedCount: successful completions in the same window.
   - Compute the error ratio JobsErroredCount / (JobsErroredCount +
     JobsCompletedCount). A ratio climbing above a few percent is abnormal.
2. Enumerate failing jobs with use_aws (mediaconvert ListJobs with
   Status=ERROR), then GetJob on representative failures. Capture the ErrorCode
   and ErrorMessage on each.
3. Group failures by ErrorCode. A single dominant code points at a systemic
   input or settings problem; scattered codes suggest content-specific issues.

Common MediaConvert error categories:

| Error Category | Typical Signal | Likely Cause |
|----------------|----------------|--------------|
| Input fetch / access | Cannot open or read input, S3 access denied | Missing input object, wrong path, IAM role lacks s3:GetObject |
| Unsupported / corrupt input | Demux or decode failure | Corrupt source, unsupported codec or container |
| Output / write | Cannot write output, access denied | Output bucket path wrong, role lacks s3:PutObject |
| Settings validation | Invalid job settings | Bad output group config, incompatible codec settings |
| Encryption / KMS | Decrypt or GenerateDataKey denied | Role lacks kms:Decrypt or kms:GenerateDataKey on the key |
| Capacity / internal | Transient service error | Retryable; correlate with a specific time window |

## Step 2: Inspect Failing Job Settings and Inputs

For the dominant error code, open the actual job definition.

1. From GetJob, review the Settings block:
   - Inputs: FileInput S3 URI, audio and caption selectors, input clipping.
     Confirm the object exists and the path and Region are correct.
   - OutputGroups: type (File, Apple HLS, DASH ISO, CMAF, Microsoft Smooth),
     destination S3 path, and per-output codec settings.
2. Validate that the source characteristics match the settings:
   - Codec, resolution, and frame rate of the input versus the output
     transcode targets.
   - Caption source format versus configured caption selectors.
   - Audio track count and language versus audio selectors.
3. Confirm the MediaConvert job role permissions when the code is access or KMS
   related:
   - s3:GetObject and s3:ListBucket on the input prefix.
   - s3:PutObject on the output prefix.
   - kms:Decrypt and kms:GenerateDataKey when input or output is
     KMS-encrypted.
   Check S3 bucket policies and KMS key policies too; they can deny access even
   when the role policy allows it. Do not resolve access errors with wildcard
   IAM permissions or by making buckets public; grant the specific actions on
   the specific resources.

## Step 3: Measure Queue Backlog and Standby Time

If jobs are not failing but are slow to start, the problem is queue capacity.

1. List and describe queues with use_aws (mediaconvert ListQueues then GetQueue
   per queue). Capture:
   - PricingPlan: ON_DEMAND or RESERVED.
   - For RESERVED queues, the ReservationPlan committed slots (RTS, Reserved
     Transcode Slots) and Commitment.
   - SubmittedJobsCount and ProgressingJobsCount from the queue status.
2. In CloudWatch AWS/MediaConvert, per Queue:
   - StandbyTime: time jobs wait before transcoding begins. Rising StandbyTime
     with steady submissions means the queue cannot keep up.
   - TranscodingTime: active processing time; use it to size throughput.
   - The backlog is effectively SubmittedJobsCount that is not yet
     PROGRESSING.
3. Distinguish the two saturation modes:
   - RESERVED queue saturation: all committed RTS are busy; additional jobs
     wait in SUBMITTED and StandbyTime grows. Throughput is capped by the
     reservation.
   - ON_DEMAND queue: scales with service capacity but is subject to account
     concurrency limits; sustained backlog suggests hitting those limits or a
     burst larger than the account can absorb.

| Symptom | Queue Type | Interpretation |
|---------|-----------|----------------|
| High StandbyTime, RTS all busy | Reserved | Committed slots exhausted; under-provisioned |
| High StandbyTime, on-demand | On-demand | Account concurrency limit or large burst |
| Low StandbyTime, high error rate | Either | Not a capacity problem; go to Step 1 and 2 |
| Backlog only at peak hours | Either | Predictable burst; schedule or split workloads |

## Step 4: Right-Size and Route the Queue

Match capacity to the workload once the mode is identified.

1. For a saturated reserved queue: increase committed RTS to match peak
   concurrent demand, or route overflow to an on-demand queue during peaks.
2. For on-demand backlog from bursts: spread submissions over time, use
   multiple queues to isolate priority tiers, or request an account
   concurrency limit increase through Service Quotas.
3. Separate priority classes: place urgent, short jobs on a dedicated queue so
   long-running jobs do not block them (head-of-line blocking).
4. Reserve capacity for steady baseline load and use on-demand for spiky
   overflow, rather than over-committing reserved slots that sit idle.

## Step 5: Remediate

Match the fix to the confirmed root cause. Keep changes specific.

- Input fetch or access errors: correct the input S3 path or Region, restore
  the missing object, and grant the job role s3:GetObject on the exact prefix.
- Output write errors: correct the destination path and grant s3:PutObject on
  the exact output prefix.
- KMS errors: grant kms:Decrypt and kms:GenerateDataKey on the specific key and
  confirm the key policy trusts the job role.
- Unsupported or corrupt input: re-request the source asset or adjust input
  selectors and codec settings to match the real source.
- Settings validation failures: fix the specific invalid output group or codec
  parameter reported in the ErrorMessage; retest with one representative asset.
- Reserved queue saturation: raise committed RTS to peak concurrency or add an
  on-demand overflow queue.
- On-demand backlog: smooth submission rate, split into priority queues, or
  raise the account concurrency quota.

## Output

Provide a diagnosis summary:
1. Root cause category: input or output access, unsupported input, settings
   validation, KMS permission, reserved queue saturation, or on-demand backlog.
2. Supporting evidence: error ratio from JobsErroredCount and
   JobsCompletedCount, the dominant ErrorCode with a sample ErrorMessage, and
   StandbyTime and TranscodingTime per queue.
3. The affected queue, its PricingPlan, and committed RTS if reserved.
4. Specific remediation steps tied to the confirmed cause.
5. Preventive measures: CloudWatch alarms on JobsErroredCount and StandbyTime,
   queue separation by priority, and reserved-plus-on-demand capacity planning.
