---
name: greengrass-deployment-and-core-health
agent_type: "Incident RCA"
description: Provides investigation procedures for AWS IoT Greengrass v2 edge
  health, including UNHEALTHY core devices, failed effective deployments,
  components stuck in BROKEN or ERRORED state, and core device connectivity loss.
  Use this skill when Greengrass core devices report UNHEALTHY, when a deployment
  revision fails to converge, when components will not start or crash-loop, or
  when edge nodes drop connectivity to the cloud.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Greengrass Deployment and Core Health

Use this skill to diagnose and resolve AWS IoT Greengrass v2 edge fleet issues
across core devices, deployments, and components. Posture is read-only
investigation; recommend specific, least-change fixes only.

## When to Activate

- One or more Greengrass core devices report status UNHEALTHY.
- An effective deployment shows status FAILED or stays IN_PROGRESS and never
  completes.
- Components are stuck in BROKEN or ERRORED lifecycle state.
- Core devices lose connectivity to AWS IoT (no telemetry, missed deployments).
- A new deployment revision correlates with a spike in edge failures.

## Step 1: List Core Devices and Status

1. Call greengrassv2 ListCoreDevices via `use_aws` to enumerate every core device
   with its status (HEALTHY or UNHEALTHY) and lastStatusUpdateTimestamp.
2. For UNHEALTHY devices, call greengrassv2 GetCoreDevice to read the core device
   metadata, platform, and the Greengrass nucleus version reported.
3. Quantify blast radius: count UNHEALTHY vs HEALTHY and note whether failures
   cluster by platform, nucleus version, or thing group (which points at a common
   deployment target).
4. A stale lastStatusUpdateTimestamp (no update within the expected reporting
   interval) indicates connectivity loss rather than a component fault; branch to
   Step 5 in that case.

## Step 2: List Effective Deployments and Failures

1. For each affected core device call greengrassv2 ListEffectiveDeployments to see
   the deployments applied to it, each with deploymentId, targetArn (thing or
   thing group), coreDeviceExecutionStatus, and the reason field.
2. Interpret coreDeviceExecutionStatus:

| Status | Meaning | Action |
|--------|---------|--------|
| COMPLETED | Converged successfully | Not the cause |
| IN_PROGRESS | Still applying | If long-running, check component install/download stalls |
| FAILED | Deployment did not converge | Read reason; inspect components in Step 3 |
| REJECTED | Core rejected the deployment | Check nucleus version compatibility and device requirements |
| CANCELED / TIMED_OUT | Did not finish | Check connectivity and deployment policies |

3. Identify the deployment revision (targetArn plus revision) common to the
   failing devices. A shared failing revision is the prime suspect.

## Step 3: Inspect Installed Components State

1. Call greengrassv2 ListInstalledComponents for an affected core device to read
   each componentName, version, lifecycleState, and lifecycleStatusCodes.
2. Interpret lifecycle states:

| State | Meaning | Likely Cause |
|-------|---------|--------------|
| RUNNING | Healthy | Not the fault |
| ERRORED | Component errored during a lifecycle step | Run/install script failure, bad configuration |
| BROKEN | Component cannot recover | Repeated startup failure, missing dependency, exhausted restart budget |
| INSTALLED / STARTING | Transitional | If stuck, check install script or dependency ordering |
| FINISHED | Ran to completion (expected for one-shot) | Not a fault for one-shot components |

3. On the device (where logs are accessible) the greengrass.log and the
   per-component logs under the Greengrass logs directory record the install and
   run script exit codes and stderr. Note the failing lifecycle step (install vs
   run vs startup) and the exit code.
4. Check for dependency and version conflicts: a BROKEN component often follows a
   failed dependency component or an incompatible component version pinned by the
   deployment.

## Step 4: Correlate the Failed Deployment Revision

1. Line up the deployment revision timestamp from Step 2 against the onset of
   UNHEALTHY status and component BROKEN/ERRORED transitions from Steps 1 and 3.
2. If failures begin at the revision rollout, the new revision is the root cause:
   a changed component version, a new configuration value, or a new component with
   a failing install.
3. If a subset of devices on the same revision are healthy, compare platform,
   nucleus version, disk space, and network egress to isolate the differentiator.
4. Confirm the deployment policies (component update policy, failure handling
   policy such as ROLLBACK vs DO_NOTHING) to understand whether devices attempted
   an automatic rollback.

## Step 5: Check Core Device Connectivity

1. If lastStatusUpdateTimestamp is stale, the core cannot reach AWS IoT. Verify
   the device certificate is ACTIVE and attached, the IoT policy permits the
   Greengrass operations, and the token exchange role alias resolves.
2. Confirm the core can reach the ATS data endpoint (iot DescribeEndpoint
   iot:Data-ATS) and the Greengrass service endpoints over the required ports.
3. Rule out local resource exhaustion (disk full prevents component artifact
   download and deployment convergence) and expired credentials on the token
   exchange service.

## Step 6: Remediate

| Root Cause | Recommended Fix |
|------------|-----------------|
| Bad deployment revision | Deploy a corrected revision or roll back to the last COMPLETED revision via a new deployment |
| Component BROKEN from install/run failure | Fix the component recipe/script or configuration and redeploy that component version |
| Version/dependency conflict | Pin compatible component versions in the deployment and redeploy |
| Connectivity loss (auth) | Reactivate/attach the correct ACTIVE cert and scoped IoT policy; fix token exchange role alias |
| Disk full on core | Reclaim space so artifact download and convergence can complete |
| Nucleus incompatibility (REJECTED) | Align nucleus version with component requirements before redeploying |

Prohibited: do not disable Greengrass or device logging, do not grant wildcard IAM
to the token exchange role, and do not remove authentication to restore
connectivity.

## Output

Provide:
1. Core device health summary (HEALTHY vs UNHEALTHY counts, clustering by platform
   or thing group).
2. Deployment analysis (failing deploymentId/revision, coreDeviceExecutionStatus,
   reason) and component states (ERRORED/BROKEN with lifecycle step and exit code).
3. Root cause with evidence correlating the revision to failure onset, or the
   connectivity/auth finding.
4. Specific least-change fix (redeploy or roll back to last COMPLETED revision) and
   prevention steps (canary deployments, failure-handling ROLLBACK policy, alarms
   on UNHEALTHY core devices).
