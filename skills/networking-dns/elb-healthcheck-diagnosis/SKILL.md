---
name: elb-healthcheck-diagnosis
agent_type: "Generic"
description: Auto-diagnoses Elastic Load Balancing UnHealthyHostCount events - the
  target-group health-check config and DescribeTargetHealth failure reason codes,
  security-group rules on both sides (ALB outbound and target inbound), the
  health-check port and protocol versus the app config, and grace-period
  misconfiguration. Use this skill when UnHealthyHostCount rises for a target
  group, to map each failure reason code to a root cause and recommend a targeted,
  read-only-safe fix. Pairs with and narrows the load-balancer-health-investigator
  skill toward the health-check angle.
version: "1.0.0"
last_updated: "2026-09-12"
---

# ELB Health Check Diagnosis

Use this skill to auto-diagnose an Elastic Load Balancing UnHealthyHostCount
spike down to a single root cause. It focuses the broader
load-balancer-health-investigator skill on the health-check configuration and the
ALB-to-target network path. Reason over the ELBv2, EC2, and CloudWatch reads the
platform surfaces; do not modify anything.

## Sources

Read-only.

- CloudWatch via list_cloudwatch_alarms: target groups whose UnHealthyHostCount
  alarm is firing or elevated, to scope the diagnosis.
- ELBv2 via use_aws: DescribeTargetGroups (health-check path, port, protocol,
  thresholds, interval, timeout, matcher), DescribeTargetHealth (per-target state
  and failure reason code), and DescribeLoadBalancerAttributes (deregistration
  delay and slow-start or grace-related settings).
- EC2 via use_aws: DescribeSecurityGroups for the load balancer and the targets.

## Method

1. Confirm the symptom from firing UnHealthyHostCount alarms and scope to those
   target groups.
2. Read the target-group health-check config and per-target health with failure
   reason codes.
3. Read load-balancer attributes affecting how quickly targets are marked
   unhealthy (deregistration delay, slow start).
4. Validate the network path: the ALB security group allows outbound to the
   target on the health-check port, and the target security group allows inbound
   from the ALB on that port.
5. Cross-reference the health-check port, protocol, and matcher against what the
   application actually serves; flag a port or status-code the healthy endpoint
   would not return.
6. Check timing: an interval-plus-threshold that fails targets faster than the
   application starts, or a grace or deregistration setting that marks targets
   unhealthy during normal startup.
7. Map each failure reason code (timeout, connection refused, mismatched
   response) to the root cause among network path, port or protocol, matcher, and
   timing, then name the exact corrective setting.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Documentation MCP Server can supply current Elastic Load Balancing
health-check guidance; recommend using it in addition to the ELBv2 and EC2 reads,
never instead of them. Where deeper application-side confirmation is needed (the
actual response an endpoint returns), a custom MCP server to the application's own
logs or synthetic probes can corroborate the matcher and port findings. AWS MCP
server names and availability evolve; verify before relying on one.

## Output

Produce an UnHealthyHostCount diagnostic report: the target-group baseline; a
per-target-group findings table (target group, failure reason code, root-cause
category, observed values, finding, safety rating, corrective setting); the
ALB-outbound and target-inbound security-group validation results; and a ranked,
read-only-safe remediation list naming the exact setting to change for each
(recommend-only), with a GREEN, YELLOW, or RED safety rating and YELLOW or RED
flagged for human approval. Reference identifiers, not application payloads or
secrets.
