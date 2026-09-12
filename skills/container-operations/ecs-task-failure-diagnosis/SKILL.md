---
name: ecs-task-failure-diagnosis
agent_type: "Incident RCA"
description: Provides systematic diagnosis procedures for ECS task failures
  including OOM kills, image pull errors, health check failures, and resource
  constraints. Use this skill when ECS tasks are stopping unexpectedly, services
  have fewer running tasks than desired, or deployments are stuck due to task
  failures.
version: "1.0.0"
last_updated: "2026-08-14"
---

# ECS Task Failure Diagnosis

Use this skill to diagnose why ECS tasks are failing to start or being
stopped unexpectedly.

## When to Activate

- ECS service has runningCount < desiredCount.
- Tasks repeatedly starting and stopping (crash loop).
- New deployment stuck with new tasks failing health checks.
- Tasks stopped with error exit codes.

## Step 1: Identify the Stop Reason

Check the task stopped reason from ECS describe-tasks:

| Stop Code | Meaning | Investigation Path |
|-----------|---------|-------------------|
| EssentialContainerExited | Main container crashed | Check exit code and logs |
| TaskFailedToStart | Task couldn't start at all | Check image pull, IAM, resources |
| ServiceSchedulerInitiated | Health check failed | Check health check config and app startup |
| UserInitiated | Manual stop or deployment | Normal - unless unexpected |
| SpotInterruption | Spot capacity reclaimed | Check Spot fleet diversification |

## Step 2: Diagnose by Exit Code

| Exit Code | Meaning | Common Cause |
|-----------|---------|-------------|
| 0 | Normal exit | Application completed (expected for batch tasks) |
| 1 | Application error | Unhandled exception, bad config, missing env var |
| 2 | Shell misuse | Incorrect CMD/ENTRYPOINT in Dockerfile |
| 127 | Command not found | Binary not in image, wrong ENTRYPOINT path |
| 137 | OOM killed (SIGKILL) | Container exceeded memory hard limit |
| 139 | Segfault (SIGSEGV) | Application memory corruption, native library bug |
| 143 | SIGTERM received | Graceful shutdown triggered (normal during deploys) |

## Step 3: Common Failure Patterns

### OOM Kills (Exit 137)
1. Check container memory limit vs actual usage.
2. Check if the application has a memory leak (growing over time).
3. Check if JVM heap is set larger than container memory limit.
4. Fix: Increase memory limit OR fix the memory leak OR tune JVM heap.

### Image Pull Failures
1. Check ECR repository exists and image tag is correct.
2. Check task execution role has ecr:GetAuthorizationToken and ecr:BatchGetImage.
3. Check VPC has NAT Gateway or VPC endpoint to reach ECR.
4. Check Docker Hub rate limiting (for public images).

### Health Check Failures
1. Confirm the health check path returns HTTP 200.
2. Confirm the application starts within the grace period.
3. Confirm the health check port matches the container port.
4. Check if the app needs time to initialize (increase grace period).

### Resource Constraints
1. "No container instances with enough resources" - cluster is full.
2. Check for placement constraint that can't be satisfied.
3. Check subnet IP address availability (awsvpc mode).
4. For Fargate: check account vCPU limits.

## Step 4: Verify After Fix

After applying a fix:
1. Force a new deployment: `aws ecs update-service --force-new-deployment`
2. Watch running count return to desired count.
3. Verify health checks pass for new tasks.
4. Monitor for 15 minutes for stability.

## Output

Provide:
1. Failure classification (OOM, image pull, health check, resource, application error).
2. Root cause with evidence (logs, metrics, exit code).
3. Specific fix recommendation.
4. Verification steps to confirm the fix worked.