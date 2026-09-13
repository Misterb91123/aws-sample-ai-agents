---
name: hybrid-estate-inventory-and-drift
agent_type: "Generic"
description: >
  Builds a unified inventory and a tag and ownership drift view across connected
  AWS and Azure accounts for hybrid governance. Use this skill when an organization
  runs workloads in both clouds and needs one consistent picture of what exists and
  who owns it.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Hybrid Estate Inventory and Drift

Governance breaks down at the cloud boundary. AWS has one tagging scheme and Azure
another, ownership is tracked differently in each, and no single view shows the
whole estate. This skill assembles a unified inventory across connected AWS and
Azure accounts and reports where tagging and ownership drift from the
organization's standard, so hybrid governance has one source of truth.

## Sources

Read-only reasoning over platform-surfaced data:

- AWS resources and tags read through use_aws across the connected accounts.
- Connected Azure account and resource associations surfaced on the Agent Space,
  used to enumerate Azure resources and their tags.
- The organization's expected tagging and ownership standard, taken from existing
  governance conventions the platform surfaces.

This skill inventories and reports only. It does not tag, move, or modify resources
in either cloud.

## Method

1. Define the standard. Establish the required tags (owner, cost center,
   environment, data classification) and the ownership model both clouds must
   follow.
2. Enumerate the estate. Build one inventory of resources across connected AWS and
   Azure accounts, normalizing resource type and identifier into a common shape.
3. Normalize tags across clouds. Map AWS tag keys and Azure tag keys onto the common
   standard so a missing owner tag reads the same regardless of cloud.
4. Detect tag drift. Flag resources missing required tags, carrying inconsistent
   values for the same concept, or using deprecated tag keys.
5. Detect ownership drift. Flag resources with no resolvable owner, owners who have
   left, and ownership that disagrees between the tag and the account or
   subscription structure.
6. Find cross-cloud inconsistency. Flag the same logical workload tagged one way in
   AWS and another in Azure.
7. Rank by governance risk. Prioritize untagged production and data-bearing
   resources over low-impact ones.

## Output

Produce a hybrid governance report:

1. Unified Inventory: resources across AWS and Azure in one normalized list.
2. Tag Drift: resources missing or misusing required tags, by cloud and account.
3. Ownership Drift: resources with absent, stale, or conflicting ownership.
4. Cross-Cloud Inconsistency: workloads tagged differently across clouds.
5. Recommendations: tags and ownership records to correct, ranked by governance
   risk. All recommend-only.
