---
name: tag-policy-enforcement-strategy
agent_type: "Generic"
description: Use this skill when designing and enforcing a tagging strategy for cost allocation and governance across an AWS Organization. It triggers on requests to define required tag keys and value constraints, enforce tags via tag policies, SCPs, and AWS Config rules, remediate untagged resources, or activate cost allocation tags in the billing console.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Tag Policy Enforcement Strategy

This skill designs a tagging standard and enforces it across an AWS Organization for cost allocation and governance. It combines Organizations tag policies, preventive SCPs, detective Config rules, and cost allocation tag activation into a coherent enforcement model.

## When to Activate

- An Organization needs a consistent tagging standard for cost allocation and ownership.
- Untagged or inconsistently tagged resources are blocking accurate cost reporting.
- A team wants to prevent creation of untagged resources or flag existing ones.
- Cost allocation tags need to be activated so they appear in Cost Explorer and the Cost and Usage Report.
- Tag values are inconsistent (for example "prod", "Prod", "production") and need normalization.

## Step 1: Define the tag standard

- Define the required tag keys and their purpose, for example: CostCenter, Owner, Environment, Application, and DataClassification. Fix the exact key casing, since tag keys are case sensitive.
- Define allowed values where a closed set applies. For example Environment allowed values are production, staging, development, and sandbox. Free-form keys such as Owner should still specify a format (for example a team alias or an email).
- Decide which resource types must be tagged, prioritizing cost-driving and taggable resources (EC2, EBS, RDS, S3, Lambda, EKS, and similar).

## Step 2: Publish an Organizations tag policy

- Create a tag policy in AWS Organizations that declares each required key, its allowed values, and the resource types it enforces capitalization and value compliance on.
- Attach the tag policy at the root or a top-level OU so it inherits. A tag policy reports non-compliance and can prevent non-compliant tagging operations on supported resource types; it does not by itself require that a tag be present at creation.
- Review the compliance report the tag policy produces to see which resources violate the key casing or value constraints.

## Step 3: Prevent untagged creation with SCPs

- Add an SCP that denies resource-creating actions when a required tag key is absent, using a condition with Null on aws:RequestTag for the required key (for example deny ec2:RunInstances when aws:RequestTag/CostCenter is null).
- Add an SCP that denies creation when a tag value is outside the allowed set, using StringNotEquals on aws:RequestTag for a closed-value key such as Environment.
- Scope these SCPs carefully and test on a non-production OU first, since a too-broad tag-required deny can block legitimate automation that does not yet set tags.

## Step 4: Detect and remediate with Config rules

- Enable the AWS Config managed rule required-tags to detect existing resources missing the required keys. Config evaluates supported resource types and marks non-compliant ones.
- Attach an automated remediation (for example an SSM Automation document that applies a default or placeholder tag, or opens a ticket to the resource owner) so drift is corrected or escalated.
- Use Resource Groups Tagging API (get-resources with a tag filter) or Tag Editor to bulk-identify and bulk-apply tags to existing untagged resources during a cleanup pass.

## Step 5: Activate cost allocation tags

- In the management account billing console, activate the required tag keys as user-defined cost allocation tags. Only activated keys appear as cost dimensions.
- Allow up to 24 hours for activated tags to begin populating in Cost Explorer and the Cost and Usage Report. Historical costs before activation are not retroactively tagged.
- Confirm the activated keys match the tag standard exactly, since a casing mismatch produces a separate cost dimension.

## Step 6: Monitor and iterate

- Track tagging compliance over time using the tag policy compliance report and the Config required-tags rule compliance percentage, targeting a defined threshold (for example 95 percent of taggable resources compliant).
- Review new services and resource types periodically and extend the standard, SCPs, and Config rules as coverage gaps appear.

## Output

Produce a Tag Enforcement Strategy document containing: the defined tag standard (keys, allowed values, and required resource types), the Organizations tag policy definition and attachment point, the preventive SCP statements for tag-required and value-constrained creation with a testing plan, the detective Config rule and remediation approach, the list of cost allocation tag keys to activate with the expected propagation delay, and a compliance target with the metrics used to track it. Include a bulk-remediation plan for existing untagged resources.