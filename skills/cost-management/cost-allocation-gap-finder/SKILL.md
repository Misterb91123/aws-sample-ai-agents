---
name: cost-allocation-gap-finder
agent_type: "Generic"
description: Identifies gaps in cost allocation by finding untagged resources,
  miscategorized spend, and shared costs that need proper attribution to teams
  or services. Use this skill when finance or engineering leadership needs
  accurate cost-per-team or cost-per-service breakdowns and existing allocation
  has blind spots.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Cost Allocation Gap Finder

Use this skill to identify and close gaps in cost allocation so every dollar
of AWS spend can be attributed to a team, service, or cost center.

## When to Activate

- Monthly/quarterly cost allocation review.
- Finance team reports gaps in chargeback/showback models.
- New teams or services are added without proper cost allocation setup.
- Cost anomaly cannot be attributed to any team.
- Building or improving a FinOps practice.

## Step 1: Assess Current Allocation Coverage

1. Retrieve total monthly AWS spend from Cost Explorer.
2. Group spend by cost allocation tag (typically `Team`, `Service`, or `CostCenter`):
   - Tagged spend: can be attributed to a team/service
   - Untagged spend: cannot be attributed (the "gap")
3. Calculate allocation coverage: (tagged spend / total spend) x 100.
4. Goal: > 90% of spend should be attributable.

## Step 2: Identify Untagged Spend by Service

Break down the untagged spend:
1. Group untagged costs by AWS service.
2. Group by account (some accounts may lack tag policies entirely).
3. Group by region.
4. Identify the top 10 untaggable cost categories.

**Common untaggable spend:**
- Data transfer charges (not taggable, must be attributed via architecture knowledge)
- Support charges (account-level, must be split proportionally)
- Tax charges (account-level)
- Some shared services (Route53, CloudFront - sometimes tricky to attribute)
- Marketplace subscriptions

## Step 3: Find Untagged Resources

For taggable resources missing allocation tags:
1. Use Resource Groups Tagging API to find resources without the required tag.
2. Prioritize by cost - find the most expensive untagged resources first.
3. For each untagged resource:
   - Determine likely owner (from CloudTrail creator, account ownership, VPC/subnet context)
   - Estimate monthly cost
   - Suggest correct tag values based on context

## Step 4: Analyze Shared Resources

Some resources legitimately serve multiple teams:
1. Identify shared infrastructure:
   - NAT Gateways (shared by all services in the VPC)
   - Transit Gateways (shared networking)
   - Shared databases or caches
   - Platform services (monitoring, logging, CI/CD)
   - Bastion hosts and VPN endpoints
2. Determine allocation strategy for each:
   - **Proportional**: Split by traffic/usage ratio (e.g., NAT by data processed per service)
   - **Equal split**: Divide evenly among consuming teams
   - **Platform tax**: Allocate to a "Platform" cost center
   - **Usage-based**: Meter actual usage per team (ideal but requires instrumentation)

## Step 5: Analyze Cross-Account Attribution

For organizations with multiple accounts:
1. Identify accounts with mixed ownership (multiple teams in one account).
2. Check for resources in unexpected accounts (shadow IT, legacy resources).
3. Verify account-level costs (support, marketplace) are allocated to the right team.
4. Check if consolidated billing discounts (SP, RI) are allocated to the benefiting account.

## Step 6: Check Cost Allocation Tag Health

Validate existing tags:
1. Are tag values consistent? (e.g., `team:platform` vs `team:Platform` vs `team:platform-eng`)
2. Are tag values current? (teams may have been renamed/reorganized)
3. Are new resources getting tagged? (check resources created in last 7 days)
4. Are cost allocation tags activated in the billing console?

**Common issues:**
- Tag key casing inconsistency (`Team` vs `team` vs `TEAM`)
- Stale tag values referencing teams that no longer exist
- Resources tagged with the wrong team (copy-paste errors)
- Auto-created resources not inheriting tags (Lambda creates ENIs without tags)

## Step 7: Quantify the Gap

For each gap category:
1. Monthly dollar amount that cannot be allocated.
2. Percentage of total spend.
3. Root cause (untagged, shared, untaggable).
4. Remediation effort (add tags, build allocation model, accept as platform cost).

## Output

Produce a cost allocation gap report:
1. **Summary**: Total spend, attributed spend, gap percentage, gap in dollars.
2. **Gap by Category Chart**: Pie chart of unattributed spend (untagged, shared, untaggable).
3. **Top Untagged Resources Table**: Resource, type, account, estimated monthly cost, suggested owner, suggested tags.
4. **Shared Resource Allocation Model**: Shared resource, monthly cost, proposed allocation method, team split.
5. **Tag Health Issues Table**: Issue type (missing, inconsistent, stale), affected resources, remediation.
6. **Coverage Trend**: Line chart of allocation coverage percentage over time.
7. **Recommendations**: Prioritized actions to improve allocation coverage toward 90%+ target.