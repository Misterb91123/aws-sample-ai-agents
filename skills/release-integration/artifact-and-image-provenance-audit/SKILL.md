---
name: artifact-and-image-provenance-audit
agent_type: "Generic"
description: Verifies that the artifacts and container images running in AWS trace
  back to a commit that was reviewed and tested, and reports signing and provenance
  coverage across Amazon ECR and other registries. Flags deployed images with no
  linked reviewed PR, no verification test run, or no signature/attestation. Use
  this to close the gap between "what we reviewed" and "what is actually running".
version: "1.0.0"
last_updated: "2026-09-12"
---

# Artifact and Image Provenance Audit

Use this skill to prove that what is running was actually reviewed, tested, and
signed. A deployed image with no traceable, reviewed, signed origin is a supply
chain risk regardless of how good the review gate is. This skill is read-only and
recommend-only: it reports provenance gaps, it does not delete images or change
registry settings.

## Sources

- AWS-native reads (use_aws) for running workloads: ECS task definitions, EKS
  workloads, and Lambda package references that name the image or artifact in use.
- Amazon ECR reads for image tags, digests, and any signatures or attestations
  attached.
- Release Readiness Review and Release Testing history to link an image or
  artifact back to a reviewed and tested commit.
- Pipeline associations to trace the build that produced each artifact.
- Comms/ticketing associations only for reporting.

## Method

1. Enumerate the artifacts and container images actually running across ECS, EKS,
   and Lambda by resolving each workload to its image digest or package version.
2. For each image, resolve the registry entry (ECR or other) and record digest,
   tags, and any attached signature or provenance attestation.
3. Trace each image back to the build pipeline and the source commit that produced
   it using the pipeline association.
4. Check whether that commit went through a Release Readiness Review and a Release
   Testing run. Flag images with no reviewed, tested origin.
5. Compute signing and provenance coverage across registries and flag unsigned or
   unattested images.
6. Highlight mismatches: a running digest that does not match any known reviewed
   build (possible drift or manual push).
7. Rank findings by exposure (internet-facing, privileged, or data-handling
   workloads first).

## MCP augmentation

The AWS DevOps Agent supports connecting custom MCP servers to an Agent Space
(see the AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the
"Amazon ECS MCP Server" (from the awslabs/mcp project) is the most relevant: it
deepens the container and task-definition context used to resolve which image each
workload actually runs. A custom MCP server wrapping a non-ECR registry or the
team's build/attestation service can extend the same tracing to other registries.
To enable, connect the MCP server to the Agent Space through the DevOps Agent
MCP-server integration, after which this custom agent can call the MCP's tools
during its run. Use any MCP in addition to the regular sources - AWS and ECR reads
via use_aws, review and testing history, and the connected pipeline integrations -
never instead of them. AWS MCP server names and availability evolve, so verify
the current server before relying on it.

## Output

Provide a provenance report:
1. Inventory of running artifacts and images with digest and registry.
2. Traceability status per image: reviewed commit, verification test, signature.
3. Untraceable or unsigned images ranked by workload exposure.
4. Signing and provenance coverage summary across registries.
5. Recommendations to close provenance gaps and enforce signing.
