---
name: lambda-concurrency-cost-tuning
agent_type: "Generic"
description: Use this skill to right-size AWS Lambda provisioned concurrency against on-demand based on measured utilization. It reads concurrency metrics to find over-provisioned functions paying for idle capacity and under-provisioned functions spilling to slower on-demand starts, then recommends target concurrency and scheduling.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Lambda Concurrency Cost Tuning

This skill balances Lambda provisioned concurrency cost against cold-start performance by analyzing utilization and spillover, then recommending the right provisioned amount per function and alias.

## When to Activate

- Lambda provisioned concurrency appears as a notable line item in cost reports.
- CloudWatch ProvisionedConcurrencyUtilization for a function is consistently below 60%.
- ProvisionedConcurrencySpilloverInvocations is greater than 0, indicating under-provisioning.
- A latency-sensitive function shows cold starts during traffic peaks.
- Traffic is predictable or cyclical, suggesting scheduled concurrency would fit better.

## Step 1: Identify Functions With Provisioned Concurrency

- Call Lambda ListFunctions and GetProvisionedConcurrencyConfig to list aliases and versions with provisioned concurrency configured.
- Record the allocated provisioned concurrency value per alias.
- Note reserved concurrency limits that may interact with provisioned settings.

## Step 2: Measure Utilization

- Query CloudWatch GetMetricStatistics on namespace AWS/Lambda, metric ProvisionedConcurrencyUtilization, over at least 14 days at 5-minute periods.
- Compute average and peak utilization per alias.
- Flag OVER_PROVISIONED when average utilization is below 60% for the observed window.

## Step 3: Detect Spillover

- Query metric ProvisionedConcurrencySpilloverInvocations and ConcurrentExecutions for the same window.
- Flag UNDER_PROVISIONED when ProvisionedConcurrencySpilloverInvocations is greater than 0 during peak periods.
- Correlate spillover timestamps with peak ConcurrentExecutions to size the shortfall.

## Step 4: Recommend Target Concurrency

- For over-provisioned aliases, recommend a target provisioned concurrency equal to peak ConcurrentExecutions plus a 15% buffer.
- For under-provisioned aliases, recommend raising provisioned concurrency to cover the observed spillover peak.
- Where traffic is cyclical, recommend Application Auto Scaling scheduled scaling instead of a flat value.

## Step 5: Model Cost Impact

- Compute current monthly provisioned concurrency cost per alias.
- Compute projected cost at the recommended target and the net monthly delta.
- For functions with low steady utilization, model switching to pure on-demand.

## Output

The skill produces a titled "Lambda Concurrency Tuning Report" listing each function and alias with its current provisioned concurrency, average and peak utilization, spillover count, an OVER_PROVISIONED or UNDER_PROVISIONED classification, and the recommended target with modeled monthly cost change. It closes with a prioritized remediation list ordered by net dollar savings, such as lowering provisioned concurrency on idle aliases, raising it where spillover occurs, adopting scheduled scaling for cyclical traffic, and reverting rarely used aliases to on-demand.