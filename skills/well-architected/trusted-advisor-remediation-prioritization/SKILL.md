---
name: trusted-advisor-remediation-prioritization
agent_type: "Evaluation"
description: Use when turning AWS Trusted Advisor findings into a ranked action plan. It collects red and yellow checks across the five categories, then ranks them by estimated savings and risk. Apply during Well-Architected reviews or quarterly account health assessments.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Trusted Advisor Remediation Prioritization

Convert Trusted Advisor check results into a prioritized action plan ranked by cost savings and risk reduction.

## When to Activate
- DescribeTrustedAdvisorCheckResult returns checks with status red (action recommended) or yellow (investigation recommended).
- Cost optimization checks report idle or underused resources with estimated monthly savings.
- Security checks flag open access, exposed keys, or MFA gaps.
- Fault tolerance checks flag single-AZ resources or missing backups.
- Service limit checks show usage above 80 percent of a quota.

## Step 1: Collect Check Results
- Call DescribeTrustedAdvisorChecks to list available checks and their categories.
- Call DescribeTrustedAdvisorCheckResult for each check and read status and flaggedResources.
- Group results by the five categories: cost optimization, security, fault tolerance, performance, and service limits.

## Step 2: Quantify Cost Findings
- For cost optimization checks read the estimated monthly savings per flagged resource.
- Sum potential savings and rank cost findings from highest to lowest.
- Flag idle load balancers, underused instances, and unattached volumes.

## Step 3: Assess Security and Fault Tolerance Risk
- Flag red security checks such as open security group ports and exposed access keys as high risk.
- Flag fault tolerance checks such as single-AZ deployments and missing snapshots.
- Assign a risk rating (high, medium, low) to each finding.

## Step 4: Check Service Limits
- Read service limit checks and flag usage above 80 percent of any quota.
- Recommend proactive quota increase requests before limits are hit.
- Prioritize limits on services in the critical path.

## Step 5: Build the Ranked Plan
- Score each finding by combining estimated savings and risk severity.
- Rank remediation so high-risk security items and high-savings cost items rise to the top.
- Assign an owner and target date to each item.

## Output
Produce a titled "Trusted Advisor Remediation Plan" summarizing red and yellow checks across all five categories, total estimated monthly savings, and risk ratings. Include a prioritized remediation list ranked by combined savings and risk: fix high-risk security and fault tolerance red checks first, capture high-savings cost items second, then address service limits above 80 percent and remaining yellow checks.