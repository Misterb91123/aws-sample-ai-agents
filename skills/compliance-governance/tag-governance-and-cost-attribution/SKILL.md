---
name: tag-governance-and-cost-attribution
agent_type: "Generic"
description: Use when establishing tag governance for accurate cost attribution. It finds resources missing required cost-allocation tags, inconsistent tag values, and unactivated cost tags, then recommends a governance model. Apply during FinOps reviews or before chargeback and showback rollout.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Tag Governance and Cost Attribution

Establish consistent tagging so cost can be attributed to teams, environments, and cost centers with confidence.

## When to Activate
- Resource Groups Tagging API GetResources shows more than 10 percent of resources missing a required cost-allocation tag.
- Cost Explorer groups significant spend under untagged or unassigned.
- Required tag keys such as CostCenter, Environment, or Owner are absent or inconsistent.
- Cost-allocation tags are not activated in the Billing console.
- Tag values vary in case or spelling (for example prod versus Production).

## Step 1: Define the Required Tag Set
- Establish a required tag schema (for example CostCenter, Environment, Owner, Application).
- Define allowed values and casing for each key.
- Document the schema as the governance standard.

## Step 2: Inventory Current Tag Coverage
- Call the Resource Groups Tagging API GetResources across regions and services.
- Compute the percentage of resources missing each required tag.
- Flag services or accounts where missing tags exceed 10 percent.

## Step 3: Detect Value Inconsistency
- Aggregate distinct values per tag key.
- Flag near-duplicate values differing by case or spelling.
- Recommend a canonical value list per key.

## Step 4: Validate Cost Attribution
- Confirm required tags are activated as cost-allocation tags in Billing.
- Use Cost Explorer grouped by the tag keys and measure the untagged share.
- Flag any tag key not activated for cost allocation.

## Step 5: Enforce Governance
- Recommend Tag Policies in AWS Organizations to enforce keys and values.
- Recommend a Config rule (required-tags) to detect noncompliant resources.
- Recommend tagging at provisioning time via infrastructure as code and a remediation backfill.

## Output
Produce a titled "Tag Governance and Cost Attribution Report" listing coverage per required tag with the percentage missing, inconsistent tag values, unactivated cost-allocation tags, and the untagged share of spend. Include a prioritized remediation list: activate cost-allocation tags and backfill high-spend untagged resources first, normalize inconsistent values second, then enforce Tag Policies and a Config rule with provisioning-time tagging.