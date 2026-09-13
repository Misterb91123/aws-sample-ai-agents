---
name: cross-cloud-dependency-and-egress-cost
agent_type: "Generic"
description: >
  Maps dependencies between connected AWS and Azure resources and analyzes the data
  egress cost and latency of cross-cloud calls. Use this skill when a hybrid
  architecture sends traffic back and forth between clouds and the team needs to
  see the cost and performance of that boundary.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Cross-Cloud Dependency and Egress Cost

Every call that crosses a cloud boundary pays twice: once in egress charges and
again in added latency. In hybrid architectures these calls accumulate quietly
until the bill or a latency complaint surfaces them. This skill maps the AWS to
Azure dependencies from the connected accounts and characterizes the egress cost
and round-trip latency of the traffic crossing between them.

## Sources

Read-only reasoning over platform-surfaced data:

- AWS resources, network flow, and data-transfer signals read through use_aws and
  CloudWatch across connected accounts.
- Connected Azure account and resource associations surfaced on the Agent Space,
  used to identify the Azure side of each dependency.
- Cost and usage signals the platform surfaces for AWS-side data transfer and
  egress.

This skill maps and recommends only. It does not reroute traffic or change any
resource.

## Method

1. Enumerate cross-cloud endpoints. From both clouds, identify resources that
   communicate across the boundary: AWS services calling Azure endpoints and the
   reverse.
2. Build the dependency map. Link each caller to callee across clouds, recording
   direction, protocol, and the workload each belongs to.
3. Attribute egress volume. For each cross-cloud edge, use data-transfer signals to
   estimate the volume leaving AWS toward Azure and characterize the reverse where
   Azure surfaces it.
4. Estimate egress cost. Translate the outbound volume into approximate recurring
   egress spend using the transfer usage the sources report.
5. Characterize latency. From CloudWatch and available latency signals, describe the
   round-trip cost of each cross-cloud call and flag chatty patterns that cross the
   boundary many times per request.
6. Find avoidable crossings. Identify dependencies that could be collapsed by
   co-locating the caller and callee, caching at the boundary, or batching chatty
   calls.
7. Rank by cost and impact. Order edges by combined egress spend and latency
   contribution to customer-facing paths.

## Output

Produce a cross-cloud report:

1. Dependency Map: AWS to Azure edges with direction, protocol, and workload.
2. Egress Cost: estimated recurring transfer spend per edge and in total.
3. Latency Profile: round-trip cost per crossing and chatty patterns flagged.
4. Avoidable Crossings: edges that could be co-located, cached, or batched.
5. Recommendations: architecture changes to cut egress and latency, ranked by
   impact. All recommend-only.
