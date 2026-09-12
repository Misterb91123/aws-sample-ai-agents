---
name: service-quota-forecasting
agent_type: "Generic"
description: Use this skill to forecast when an AWS service quota will be exhausted based on utilization trend, before requests start failing. It reads current quotas and usage, projects the crossing date, and alerts when projected utilization passes 80% within 30 days so an increase can be requested early.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Service Quota Forecasting

This skill projects future quota consumption from historical usage so quota-increase requests are filed before limits cause throttling or launch failures.

## When to Activate

- CloudWatch AWS/Usage ResourceCount for a resource type is trending toward its quota.
- A service reports throttling or a LimitExceeded error in CloudTrail or application logs.
- A capacity or scaling plan anticipates growth in EC2, Lambda, VPC, or ENI counts.
- Current utilization of any adjustable quota is already above 70%.
- A large launch or migration is planned within the next 30 days.

## Step 1: Enumerate Quotas

- Call Service Quotas ListServices to identify in-scope service codes.
- Call ListServiceQuotas and GetServiceQuota to read the Value and Adjustable flag for each quota of interest.
- Prioritize adjustable quotas that back critical resources (EC2 vCPUs, Lambda concurrent executions, VPC ENIs, EBS volume storage).

## Step 2: Gather Utilization History

- Query CloudWatch GetMetricStatistics on namespace AWS/Usage, metric ResourceCount, with the Service, Type, Resource, and Class dimensions matching each quota.
- Pull at least 30 days of DAILY datapoints using the Maximum statistic.
- Compute current utilization as ResourceCount divided by quota Value.

## Step 3: Fit the Trend

- Fit a linear trend to the daily utilization series and compute the average daily growth rate.
- Project utilization forward day by day using the fitted slope.
- Identify the projected date when utilization reaches 80% and the date it reaches 100%.

## Step 4: Classify Risk

- Flag CRITICAL when projected utilization crosses 80% within 30 days or is already above 90%.
- Flag WARNING when the 80% crossing falls within 31 to 90 days.
- Flag OK when the 80% crossing is more than 90 days out or growth is flat.

## Step 5: Prepare the Increase Request

- For each CRITICAL or WARNING quota, compute a target new value that keeps utilization below 60% for the next 90 days of projected growth.
- Draft a Service Quotas RequestServiceQuotaIncrease payload with the recommended value.
- Note quotas where Adjustable is false and require an architectural workaround instead.

## Output

The skill produces a titled "Service Quota Exhaustion Forecast" listing each tracked quota with its current value, current utilization percentage, average daily growth, projected 80% crossing date, and projected 100% crossing date, along with a risk classification per quota. It ends with a prioritized remediation list ordered by nearest crossing date, recommending specific quota-increase values to request now, quotas to monitor, and non-adjustable quotas needing an architecture change.