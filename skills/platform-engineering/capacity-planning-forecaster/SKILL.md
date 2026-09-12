---
name: capacity-planning-forecaster
agent_type: "Generic"
description: Forecasts resource capacity needs based on historical growth trends,
  upcoming product launches, and seasonal patterns. Use this skill when planning
  infrastructure scaling ahead of known traffic events, performing quarterly capacity
  reviews, or when growth trends suggest resources will hit limits soon.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Capacity Planning Forecaster

Use this skill to forecast resource needs and ensure infrastructure can handle
upcoming demand without over-provisioning or running out of capacity.

## When to Activate

- Quarterly capacity planning review.
- Upcoming product launch or marketing campaign expected to increase traffic.
- Seasonal traffic event approaching (Black Friday, holidays, back-to-school).
- Growth trends indicate resources approaching limits within 30 days.
- Team requests capacity assessment for a specific service.

## Step 1: Gather Historical Usage Data

Collect at least 90 days (ideally 12 months) of usage data:

**Compute:**
- EC2/ECS/EKS CPU and memory utilization (avg, p95)
- Instance/task count over time
- Auto Scaling group size history
- Lambda concurrent executions

**Data:**
- RDS connections (current vs max_connections)
- RDS storage used vs provisioned
- DynamoDB consumed vs provisioned capacity (RCU/WCU)
- ElastiCache memory utilization
- S3 storage growth rate

**Network:**
- ALB request count over time
- NAT Gateway data processing volume
- API Gateway request count
- CloudFront request volume

**Queue/Stream:**
- SQS message volume over time
- Kinesis shard utilization
- EventBridge event volume

## Step 2: Identify Growth Trends

For each metric:
1. Calculate the linear growth rate (slope over the measurement period).
2. Identify if growth is linear, exponential, or stepped.
3. Account for seasonality (weekly patterns, monthly patterns, annual patterns).
4. Factor in known one-time events (customer onboarding, feature launch).

**Forecasting methods:**
- **Linear projection**: Suitable for steady, predictable growth.
- **Exponential projection**: For rapid growth phases (new product traction).
- **Seasonal decomposition**: For services with predictable peaks (e-commerce, gaming).
- **Step function**: For B2B services with customer-driven capacity jumps.

## Step 3: Identify Capacity Limits

For each resource, determine the hard and soft limits:

| Resource | Soft Limit (target max) | Hard Limit (failure point) |
|----------|------------------------|---------------------------|
| EC2 CPU | 70% sustained | 100% (throttling) |
| RDS connections | 80% of max_connections | 100% (connection refused) |
| RDS storage | 80% of provisioned | 100% (writes blocked) |
| DynamoDB | 80% of provisioned RCU/WCU | 100% (throttling) |
| ElastiCache memory | 75% | 100% (evictions, OOM) |
| Lambda concurrency | 80% of account limit | 100% (throttling) |
| ALB | No fixed limit (but LCU-based) | Target group max targets |
| EBS IOPS | 80% of provisioned | 100% (queuing, latency spike) |

## Step 4: Calculate Time-to-Limit

For each resource approaching limits:
1. Current utilization percentage.
2. Growth rate (per day/week/month).
3. Remaining headroom = limit - current.
4. Time to reach soft limit at current growth rate.
5. Time to reach hard limit at current growth rate.

**Priority classification:**
- **Urgent**: Will hit limit within 7 days.
- **Soon**: Will hit limit within 30 days.
- **Plan**: Will hit limit within 90 days.
- **Monitor**: Will hit limit within 6 months.

## Step 5: Account for Known Events

Factor in upcoming events that will affect capacity:

1. **Planned events**: Marketing campaigns, product launches, sales events.
2. **Customer onboarding**: Large new customers with known traffic profiles.
3. **Seasonal patterns**: Holiday traffic, end-of-quarter spikes, school calendar.
4. **Technical events**: Migrations, backfill jobs, data processing runs.

For each event, estimate the traffic multiplier (e.g., "Black Friday typically sees 3x normal traffic").

## Step 6: Generate Capacity Recommendations

For each resource approaching limits:

| Recommendation Type | When to Use |
|--------------------|-------------|
| Scale vertically (bigger instance) | Simple, immediate, limited by instance family max |
| Scale horizontally (more instances) | Preferred for compute, requires app support |
| Provision more capacity | For DynamoDB, IOPS, reserved concurrency |
| Migrate to different service | When approaching service limits (RDS -> Aurora) |
| Optimize usage | When current usage is inefficient (reduce to fit) |
| Request limit increase | For AWS service quotas |

Include for each recommendation:
- Current state and projected need
- Recommended action and new capacity target
- Cost impact of the scaling
- Timeline (when to implement)
- Risk if not addressed

## Step 7: Service Quota Assessment

Check AWS Service Quotas that may constrain growth:
1. VPC limits (IPs available in subnets, ENIs).
2. Lambda concurrent execution limits.
3. EC2 instance limits by type.
4. EBS volume limits.
5. Load balancer limits (targets per group, rules per ALB).
6. API Gateway throttling limits.

Request increases proactively (they can take 1-5 days to approve).

## Output

Produce a capacity planning report:
1. **Executive Summary**: Services at risk, timeline to limit, recommended investment.
2. **Growth Trend Charts**: Per-service utilization trend with projected line to capacity limit.
3. **Time-to-Limit Table**: Resource, current utilization, growth rate, soft limit ETA, hard limit ETA, priority.
4. **Event Impact Assessment**: Upcoming events with expected capacity multiplier.
5. **Scaling Recommendations Table**: Resource, action, new capacity, cost delta, implementation date.
6. **Service Quota Risks**: Quotas approaching that need proactive increase.
7. **Budget Impact**: Total cost of recommended scaling changes.