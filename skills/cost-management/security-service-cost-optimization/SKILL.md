---
name: security-service-cost-optimization
agent_type: "Generic"
description: Finds over-provisioned AWS security services without reducing
  security posture - CloudTrail duplicate or overlapping multi-region trails and
  redundant management-event delivery, AWS Config recorders capturing unused
  resource types or high-churn resources, and GuardDuty findings suppressed but
  not archived plus usage by data source - and generates cost-optimization
  recommendations that preserve coverage. Use this skill to trim security spend
  while keeping detection intact. Read-only and recommend-only.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Security Service Cost Optimization

Use this skill to reduce the cost of CloudTrail, AWS Config, and GuardDuty
without weakening security posture. The savings come from removing duplication
and waste - not coverage - so every recommendation must preserve detection and
audit capability. Reason over security-service and cost reads; never modify a
trail, recorder, or detector.

## Sources

Read-only.

- CloudTrail via use_aws: DescribeTrails and GetTrailStatus to find multi-region
  trails, overlapping trails, and duplicate management-event delivery to multiple
  destinations.
- AWS Config via use_aws: DescribeConfigurationRecorders,
  DescribeConfigurationRecorderStatus, and DescribeConfigRules to find recorders
  capturing unused resource types or high-churn resources.
- GuardDuty via use_aws: ListDetectors, GetUsageStatistics (usage by data
  source), and ListFindings to find findings suppressed but not archived.
- Cost Explorer via use_aws and CloudWatch usage metrics to attribute spend to
  each service.

## Method

1. CloudTrail: identify multiple multi-region trails delivering the same
   management events; a second full copy is usually redundant. Flag overlapping
   trails and duplicate delivery while ensuring at least one organization or
   account trail retains full management-event coverage.
2. Config: compare recorded resource types against what rules and conformance
   packs actually evaluate; flag unused recorded types and high-churn resources
   (frequent configuration items) that inflate cost without adding assurance.
3. GuardDuty: find findings that are suppressed by a filter but not archived
   (still counted and stored) and review usage by data source to spot a source
   that costs more than its detection value in this environment.
4. For each candidate, state the coverage that must be preserved and confirm the
   recommendation does not remove it.
5. Attribute the estimated monthly saving from cost data and rank by saving.

## MCP augmentation

Where per-service pricing or spend attribution would sharpen a saving estimate,
recommend connecting the AWS Billing and Cost Management MCP Server and the AWS
Pricing MCP Server to the Agent Space and using them in addition to the
security-service reads, never instead of them. Otherwise no MCP server is
required. AWS MCP server names and availability evolve; verify before relying on
one.

## Output

Produce a cost-optimization report: per service the duplicate, unused, or
suppressed-but-not-archived items; the coverage preserved by each
recommendation; the estimated monthly saving; and a ranked, read-only-safe
recommendation list with a safety rating (recommend-only). Reference trails,
recorders, and detectors by identifier and mask account IDs.
