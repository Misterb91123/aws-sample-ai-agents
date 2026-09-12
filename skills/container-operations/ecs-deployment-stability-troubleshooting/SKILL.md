---
name: ecs-deployment-stability-troubleshooting
agent_type: "Incident RCA"
description: Use this skill to diagnose unstable Amazon ECS service deployments such as rollbacks, stuck rollouts, and task churn. It inspects deployment state, stopped task reasons, and container metrics to find why a deployment is not reaching steady state, then recommends fixes for health checks, resources, and image issues.
version: "1.0.0"
last_updated: "2026-08-14"
---

# ECS Deployment Stability Troubleshooting

This skill investigates an ECS service that is failing to deploy cleanly, correlating deployment rollout state with task stop reasons and metrics to pinpoint the cause of the instability.

## When to Activate

- ECS DescribeServices shows a deployment with rolloutState FAILED.
- A service has more than 2 task restarts within a 10-minute window.
- A deployment has not reached steady state within 15 minutes.
- DescribeTasks shows tasks with a stoppedReason indicating health check or OOM failures.
- CloudWatch CPUUtilization or MemoryUtilization spikes right after a new task set launches.

## Step 1: Read Deployment State

- Call ECS DescribeServices and inspect the deployments array, reading rolloutState, rolloutStateReason, desiredCount, runningCount, and pendingCount.
- Flag FAILED when rolloutState is FAILED and note whether circuit breaker triggered a rollback.
- Flag STUCK when a PRIMARY deployment has not reached steady state within 15 minutes.

## Step 2: Analyze Stopped Tasks

- Call ListTasks with desiredStatus STOPPED and DescribeTasks to read stoppedReason and container exitCode.
- Bucket stop reasons: health check failures, OutOfMemory (exit 137), image pull errors (CannotPullContainerError), and application crashes (non-zero exit).
- Flag CHURN when more than 2 task restarts occur within 10 minutes.

## Step 3: Check Health Checks

- Inspect the task definition container healthCheck and the target group HealthCheckPath, interval, timeout, and healthy threshold.
- Confirm the container startPeriod is long enough for application boot.
- Flag health checks failing before the app is ready as a likely false failure.

## Step 4: Correlate Resources and Image

- Query CloudWatch GetMetricStatistics on namespace AWS/ECS, metrics CPUUtilization and MemoryUtilization, around the deployment time.
- Flag MemoryUtilization sustained above 90% or exit code 137 as an OOM cause; recommend raising the memory reservation.
- Verify the new image tag exists and the task execution role can pull it, to rule out image pull errors.

## Step 5: Recommend Fixes

- For health-check failures, extend startPeriod or correct the HealthCheckPath and thresholds.
- For OOM, increase the container memory or task memory and re-test.
- For image pull errors, fix the image reference or task execution role ECR permissions.
- Recommend enabling the ECS deployment circuit breaker with rollback to contain future bad deployments.

## Output

The skill produces a titled "ECS Deployment Stability Report" summarizing the service, the failing deployment rolloutState and reason, desired versus running counts, the dominant task stoppedReason with counts, and correlated CPU and memory metrics at deployment time. It ends with a prioritized remediation list ordered by likelihood and impact, such as tuning health check timing, raising memory to stop OOM churn, fixing image or IAM pull errors, and enabling the deployment circuit breaker with rollback.