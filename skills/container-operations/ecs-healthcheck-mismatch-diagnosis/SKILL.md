---
name: ecs-healthcheck-mismatch-diagnosis
agent_type: "Generic"
description: Diagnoses Amazon ECS service health-check mismatches - the container
  health-check and ALB target-group health-check config, recent stopped-task
  reasons, and target health - to flag the specific fault: grace period too short,
  health-check path or port wrong, security group blocking ALB-to-task, protocol
  mismatch, or container healthCheck disagreeing with the target-group healthCheck.
  Use this skill when ECS tasks cycle or sit unhealthy behind a load balancer, to
  isolate the health-check-mismatch root cause and recommend a targeted,
  read-only-safe fix. This is the mismatch angle, not deployment-stability.
version: "1.0.0"
last_updated: "2026-09-12"
---

# ECS Health Check Mismatch Diagnosis

Use this skill to isolate why an Amazon ECS service cannot keep tasks healthy
behind a load balancer. The usual cause is a mismatch between the container
health check, the ALB target-group health check, and the network path between
them. This differs from deployment-stability monitoring: the concern here is the
health-check configuration mismatch itself. Reason over the ECS, ELBv2, EC2, and
CloudWatch reads the platform surfaces; do not modify anything.

## Sources

Read-only.

- ECS via use_aws: DescribeServices (health-check grace period, load-balancer and
  target-group association, container and port, desired versus running counts),
  DescribeTaskDefinition (container healthCheck command, interval, timeout,
  retries, startPeriod, and container port and protocol), and DescribeTasks with
  stopped-task reasons.
- ELBv2 via use_aws: DescribeTargetGroups (health-check path, port, protocol,
  thresholds, interval, timeout) and DescribeTargetHealth (current states and
  failure reason codes).
- EC2 via use_aws: DescribeSecurityGroups for the task and load balancer.
- CloudWatch via list_cloudwatch_alarms: health-related alarms for the service or
  target group.

## Method

1. Read the service baseline: grace period, target-group association, container
   and port, and desired versus running counts.
2. Read the task definition's container healthCheck and the container port and
   protocol.
3. Read recent stopped-task reasons to see whether tasks fail the container
   health check, are killed before startup, or are deregistered by the load
   balancer.
4. Read the target-group health-check config and current target health with
   failure reason codes.
5. Read the task and load-balancer security groups and flag a rule set that does
   not allow the ALB to reach the task on the health-check port.
6. Correlate firing health-related alarms to confirm the symptom.
7. Diagnose the specific mismatch: grace period shorter than startPeriod plus
   startup; wrong target-group path or port; a blocking security group; a
   protocol mismatch; or a container-versus-target-group disagreement, then name
   the exact corrective setting.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Documentation MCP Server can supply current ECS and Elastic Load Balancing
health-check guidance; recommend using it in addition to the ECS, ELBv2, and EC2
reads, never instead of them. Where deeper in-container probe detail is needed, a
custom MCP server to the application's own health endpoint or logs can corroborate
the container-side result. AWS MCP server names and availability evolve; verify
before relying on one.

## Output

Produce a health-check mismatch report: the service baseline; a per-service
mismatch table (service, mismatch category, observed values from both sides,
finding, safety rating, corrective setting); current target health with failure
reason codes; and a ranked, read-only-safe remediation list naming the exact
setting to change for each (recommend-only), with a GREEN, YELLOW, or RED safety
rating and YELLOW or RED flagged for human approval. Reference identifiers, not
application payloads or secrets.
