---
name: cost-anomaly-root-cause-analysis
agent_type: "Incident RCA"
description: Use this skill when an AWS Cost Anomaly Detection alert fires or when unexpected spend appears in Cost Explorer. It investigates the anomaly to isolate the driving service, linked account, usage type, and root cause, then quantifies the dollar impact and recommends remediation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Cost Anomaly Root Cause Analysis

This skill traces an AWS cost anomaly from the alert down to the specific service, account, and usage type driving the spend so the cause can be confirmed and stopped.

## When to Activate

- An AWS Cost Anomaly Detection alert reports a monitor with impact greater than $100 for a single day.
- Daily spend for a service rises more than 20% above its trailing 14-day baseline.
- Cost Explorer shows an unexplained spike in a SERVICE, USAGE_TYPE, or LINKED_ACCOUNT dimension.
- A monthly bill is trending more than 15% over forecast with no known launch.
- Finance or an account owner asks why a specific service cost jumped.

## Step 1: Pull the Anomaly Record

- Call Cost Explorer GetAnomalies for the affected date range to list detected anomalies with TotalImpact and TotalImpactPercentage.
- Call GetAnomalyMonitors to identify which monitor (DIMENSIONAL or CUSTOM) fired and its MonitorDimension.
- Flag any anomaly where TotalImpact is greater than $100 or TotalImpactPercentage is greater than 20%.
- Record the AnomalyStartDate and AnomalyEndDate to bound all follow-up queries.

## Step 2: Isolate the Driving Service

- Call GetCostAndUsage with Granularity DAILY and GroupBy dimension SERVICE across the anomaly window plus 14 prior days for baseline.
- Use metric UnblendedCost and rank services by absolute daily delta.
- Treat any service whose daily cost increased by more than $100 or more than 20% over baseline as a candidate driver.

## Step 3: Drill Into Usage Type and Account

- Re-run GetCostAndUsage filtered to the candidate service, GroupBy USAGE_TYPE, to find the specific usage (for example DataTransfer-Out-Bytes, BoxUsage, Requests-Tier1).
- Re-run GroupBy LINKED_ACCOUNT to attribute the spike to a specific member account.
- Add a GroupBy REGION pass to confirm whether the increase is concentrated in one region.
- Cross-check the top usage type against expected volume; a greater than 3x jump in a single usage type is the likely root cause.

## Step 4: Confirm the Cause

- Correlate the AnomalyStartDate with CloudTrail RunInstances, CreateFunction, or resource-scaling events in the identified account and region.
- Check for new tags, autoscaling activity, or a deployment that maps to the usage-type increase.
- Distinguish one-time cost (backfill, migration) from recurring cost (new steady-state workload).

## Step 5: Quantify and Project

- Compute the anomaly dollar impact as the sum of daily deltas across the window.
- Project the monthly run-rate cost if the increase persists (daily delta multiplied by 30).
- Set severity: HIGH when projected monthly impact is greater than $1000, MEDIUM when greater than $300, LOW otherwise.

## Output

The skill produces a titled "Cost Anomaly Root Cause Report" containing the anomaly identifier, monitor name, total dollar impact and percentage, the driving service, linked account, usage type, and region, the confirmed or suspected cause with correlating CloudTrail evidence, and the projected monthly run-rate if unaddressed. It closes with a prioritized remediation list ordered by dollar impact, such as terminating or right-sizing the offending resource, adding a budget or anomaly monitor threshold, applying lifecycle or data-transfer controls, and assigning an owner for follow-up.