---
name: environment-promotion-drift-detection
agent_type: "Generic"
description: Verifies that production runs exactly what passed testing earlier in
  the promotion chain by checking image tag and commit SHA parity across
  environments (for example dev, staging, prod). Flags cases where prod diverged
  from the artifact that was validated, whether from an out-of-band push, a
  reused mutable tag, or a skipped promotion step. Use this to guarantee that the
  thing you tested is the thing you shipped.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Environment Promotion Drift Detection

Use this skill to confirm the promotion chain is honest. The whole point of
staged environments is that what passes testing in staging is what reaches prod.
If prod runs a different image digest or commit than what was validated, the
testing gave false confidence. This skill is read-only and recommend-only: it
reports parity and drift, it does not promote, roll back, or change anything.

## Sources

- AWS-native reads (use_aws) for the running image digest and commit in each
  environment: ECS task definitions, EKS workloads, Lambda versions.
- Release Testing history to know which artifact digest actually passed testing
  and in which environment.
- Pipeline associations for promotion events and the artifact each promotion
  carried.
- Registry reads (ECR and others) to resolve mutable tags to immutable digests.
- Comms/ticketing associations only for reporting.

## Method

1. For each service, resolve the running artifact in every environment to an
   immutable identifier (image digest and/or commit SHA), not just a mutable tag.
2. Identify the artifact that passed Release Testing and the environment it was
   validated in.
3. Compare prod against the validated artifact and against each upstream
   environment to check digest and SHA parity.
4. Flag drift: prod digest differs from the validated digest, or an intermediate
   environment was skipped in the promotion chain.
5. Detect mutable-tag reuse where the same tag now points to a different digest
   than when it was tested.
6. Attribute each drift to the pipeline, promotion step, or manual action that
   caused it.
7. Rank drift findings by environment (prod first) and by blast radius.

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the
"Amazon ECS MCP Server" (from the awslabs/mcp project) deepens the container and
task-definition context needed to resolve the exact digest each environment runs,
and a custom CI MCP server wrapping the provider API lets the agent read the
promotion events and the artifact each step carried. To enable, connect the MCP
server to the Agent Space through the DevOps Agent MCP-server integration, after
which this custom agent can call the MCP's tools during its run. Use any MCP in
addition to the regular sources - AWS and registry reads via use_aws, Release
Testing history, and the connected pipeline integrations - never instead of them.
AWS MCP server names and availability evolve, so verify the current server before
relying on it.

## Output

Provide a promotion drift report:
1. Per-service parity table of running digest/SHA across environments.
2. Prod-versus-validated comparison with drift flagged.
3. Mutable-tag reuse findings where a tag changed digest after testing.
4. Skipped-promotion or out-of-band-push attribution.
5. Recommendations to enforce digest-pinned, chain-ordered promotion.
