---
name: sandbox-account-cleanup-advisor
agent_type: "Generic"
description: Use this skill when I need to identify resources in sandbox and development accounts that should be cleaned up to reduce cost and clutter. Activate it during periodic sandbox reviews, when dev account costs rise, or when experimental resources accumulate without owners. It flags stale, idle, and untagged resources and prepares owner notifications before any teardown.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Sandbox Account Cleanup Advisor

This skill scans sandbox and development accounts for resources that outlived their purpose. It ranks candidates by age, activity, and cost, identifies untagged and ownerless resources, and prepares owner notifications so cleanup happens safely with a chance to reclaim anything still needed.

## When to Activate

- A scheduled sandbox review is due, for example monthly or quarterly.
- Development or sandbox account cost is trending upward.
- Experimental resources from proofs of concept accumulate after projects end.
- Resources run outside business hours in non-production accounts.
- A governance policy requires owner tags that are not being applied.

## Step 1: Establish the Cleanup Policy Thresholds

Define what qualifies as stale before scanning:

- Set age thresholds, for example flag resources older than 30 days, escalate at 60 days, and mark for teardown at 90 days without activity.
- Confirm the accounts in scope are sandbox or dev only, never production.
- Record the timezone and business hours used to judge off-hours running.

## Step 2: Find Resources Past the Age Threshold

Enumerate old resources across services:

- Use AWS Config or Resource Groups Tagging API to list resources with their creation time.
- Flag EC2 instances, RDS and Aurora clusters, EBS volumes, load balancers, and NAT gateways older than the age threshold.
- Report the age in days for each so escalation tiers (30, 60, 90) are clear.

## Step 3: Detect Idle and Inactive Resources

Separate old-but-used from truly abandoned:

- For EC2, check CloudWatch CPUUtilization; flag instances averaging below 5 percent over 14 days.
- For RDS, check DatabaseConnections; flag databases with zero connections over 7 days.
- For load balancers, check RequestCount or ActiveConnectionCount; flag those with no traffic over 7 days.
- Idle plus old is the strongest teardown signal.

## Step 4: Identify Expensive Non-Production Resources

Focus cost attention where it matters:

- Flag large instance types (for example anything larger than xlarge) running in sandbox accounts.
- Flag provisioned databases, provisioned IOPS volumes, and dedicated hosts that are costly by default.
- Estimate monthly cost per flagged resource so the highest spend is addressed first.

## Step 5: Check Tagging and Ownership

Find resources no one can be held accountable for:

- Use the Resource Groups Tagging API to find resources missing an Owner or CostCenter tag.
- Flag untagged experimental resources separately, since they are the most likely to be forgotten.
- Where CloudTrail is available, attribute the creating principal so a likely owner can still be contacted for untagged resources.

## Step 6: Detect Off-Hours Running

Find resources burning money when no one is working:

- Compare instance and database running windows against defined business hours.
- Flag resources running 24 by 7 that could use a start-stop schedule, and estimate the savings from stopping nights and weekends (roughly a 65 percent runtime reduction for a standard work week).

## Step 7: Prepare Notification and Cleanup Candidates

Make cleanup safe and reversible:

- Group candidates into auto-cleanup (untagged, idle, and past 90 days) and notify-first (owned but stale).
- Draft an owner notification listing each resource, its age, cost, and the proposed action, with a grace period, for example 7 days to claim.
- Recommend a stop-before-terminate step for compute and a snapshot-before-delete step for storage so nothing is lost irreversibly.

## Output

The skill produces a cleanup report containing: resources grouped by age tier (30, 60, 90 days), idle and inactive resources with the metric that flagged them, expensive non-production resources with estimated monthly cost, untagged and ownerless resources, off-hours running resources with projected savings, and two candidate lists (auto-cleanup and notify-first). It also produces a draft owner notification per resource. All destructive actions are proposed with a snapshot or stop step first and a grace period, and are limited to sandbox and dev accounts, so no production resource is ever included.