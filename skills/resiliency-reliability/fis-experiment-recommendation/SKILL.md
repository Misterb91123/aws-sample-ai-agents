---
name: fis-experiment-recommendation
agent_type: "Generic"
description: Maps AWS DevOps Agent resilience findings to appropriate AWS Fault
  Injection Service (FIS) experiments. Use this skill to turn a finding (network
  latency, database failover, CPU or memory pressure, ECS or EKS task failure,
  Lambda error handling, cache or stream disruption, API throttling, AZ
  availability) into a prioritized backlog of FIS actions to validate the
  hypothesis behind the finding, each with a duration, target type, and stop
  condition. It recommends experiments to design and review; it does not run
  them.
version: "1.0.0"
last_updated: "2026-09-12"
---

# FIS Experiment Recommendation

Use this skill to convert a resilience finding into the specific AWS FIS
experiments that would validate whether the system actually withstands the
failure the finding describes. FIS injects real faults, so this skill only
recommends and designs; a human reviews, and a human runs the experiment in a
controlled way. Pair it with the chaos-experiment-planner skill for the
hypothesis and safety framing.

## Sources

Read-only.

- The finding to validate (from a report artifact, an investigation, or the
  operator), including its summary and type.
- use_aws for the affected resource's control-plane configuration (resource type,
  tags, AZ span, deployment mode) so the recommended target selection is concrete.
- list_investigations for related incidents that motivate the experiment.
- The existing chaos-experiment-planner skill for the steady-state definition,
  hypothesis, and blast-radius framing.

## Method

1. Classify the finding into a failure category: network and connectivity,
   database and storage, compute and instances, ECS and containers, EKS and
   Kubernetes, Lambda and serverless, caching and streaming, API and throttling,
   or availability and recovery.
2. Select the matching FIS action(s) for the category. Representative mappings:
   - Network: aws:network:disrupt-connectivity (partition, latency);
     aws:ecs:task-network-packet-loss (packet loss); vpc-endpoint and
     cross-region disruption actions for endpoint and multi-region tests.
   - Database and storage: aws:rds:reboot-db-instances and
     aws:rds:failover-db-cluster (failover); aws:dynamodb:global-table-pause-
     replication; aws:ebs:pause-volume-io and aws:ebs:volume-io-latency.
   - Compute: aws:ec2:stop-instances and aws:ec2:reboot-instances;
     aws:ssm:send-command for memory stress; aws:ec2:send-spot-instance-
     interruptions for spot handling.
   - ECS/EKS: aws:ecs:stop-task, aws:ecs:task-cpu-stress; aws:eks:pod-delete,
     aws:eks:pod-cpu-stress, aws:eks:terminate-nodegroup-instances.
   - Lambda: aws:lambda:invocation-error, aws:lambda:invocation-add-delay,
     aws:lambda:invocation-http-integration-response.
   - Caching/streaming: ElastiCache AZ-power interruption, MemoryDB replication
     pause, Kinesis throughput and iterator exceptions.
   - API and availability: FIS API throttle/internal-error/unavailable injection;
     aws:arc:start-zonal-autoshift; aws:cloudwatch:assert-alarm-state.
   Confirm the current action name against the FIS documentation, since the
   action catalog evolves.
3. Set a conservative duration (start short, for example 2 to 10 minutes) and a
   target selection scoped by tags or COUNT, non-production first.
4. Define the stop condition: a CloudWatch alarm on the metric the finding cares
   about (error rate, latency, availability) so the experiment aborts if blast
   radius exceeds the threshold.
5. Prioritize the recommendations by the severity of the finding and the
   likelihood the experiment reveals a real gap; note which validate the exact
   finding hypothesis versus adjacent risks.

## MCP augmentation

The awslabs Resilience guidance ships an MCP server that recommends FIS
experiments from DevOps Agent findings and generates templates
(guidance-for-enhancing-resilience-devops-agent-fis). Where available, connect
that FIS-recommender MCP server to the Agent Space and call it in addition to the
control-plane reads for a maintained finding-to-action mapping and template
generation. The AWS Documentation MCP Server can supply the current FIS action
catalog. Use any MCP in addition to the use_aws reads, never instead of them. AWS
MCP server names and availability evolve; verify before relying on one.

## Output

Produce a recommendation set: the finding and its failure category; a prioritized
list of FIS actions with duration, target selection (tags or COUNT, environment),
and the CloudWatch stop condition for each; which actions validate the finding's
core hypothesis; and a clear statement that these are experiments to review and
run under human control, not actions this skill executes.
