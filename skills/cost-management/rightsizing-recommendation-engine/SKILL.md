---
name: rightsizing-recommendation-engine
agent_type: "Generic"
description: Analyzes resource utilization patterns to identify over-provisioned
  and under-provisioned AWS resources with specific rightsizing recommendations.
  Use this skill when investigating cost optimization opportunities, responding
  to budget alerts, or performing periodic capacity reviews for EC2, RDS,
  ElastiCache, and container workloads.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Rightsizing Recommendation Engine

Use this skill to identify resources that are over-provisioned (wasting money)
or under-provisioned (risking performance) and recommend optimal sizing.

## When to Activate

- Monthly cost optimization review.
- Budget threshold breach requiring spend reduction.
- New Compute Optimizer or Cost Explorer rightsizing recommendations appear.
- Team requests capacity optimization for specific services.
- Post-incident analysis reveals over/under-provisioned resources contributed to issues.

## Step 1: Gather Utilization Data

Collect metrics for the analysis window (minimum 14 days, recommended 30 days):

**EC2 Instances:**
- CPUUtilization (avg, p95, max)
- Memory utilization (via CloudWatch Agent or Container Insights)
- Network throughput (in/out)
- Disk I/O (read/write IOPS, throughput)
- EBS volume utilization

**RDS Instances:**
- CPUUtilization (avg, p95)
- FreeableMemory / total memory ratio
- DatabaseConnections / max_connections ratio
- ReadIOPS, WriteIOPS vs provisioned IOPS
- FreeStorageSpace trend

**ElastiCache:**
- CPUUtilization and EngineCPUUtilization
- DatabaseMemoryUsagePercentage
- CacheHitRate
- NetworkBytesIn/Out

**ECS/Fargate Tasks:**
- CPU utilization vs reserved CPU
- Memory utilization vs reserved memory
- Task count vs minimum needed

**Lambda Functions:**
- Memory allocated vs memory used (from CloudWatch Logs Insights)
- Duration vs timeout ratio
- Concurrent executions vs reserved concurrency

## Step 2: Identify Over-Provisioned Resources

Flag resources as over-provisioned if sustained patterns show:

| Resource | Over-Provisioned Criteria | Confidence Threshold |
|----------|--------------------------|---------------------|
| EC2 | CPU p95 < 20% AND memory < 30% for 14+ days | High |
| EC2 | CPU p95 < 40% for 14+ days | Medium (may rightsize) |
| RDS | CPU p95 < 15% AND connections < 20% of max for 14+ days | High |
| ElastiCache | Memory < 20% AND CPU < 10% for 14+ days | High |
| Fargate | CPU < 20% AND memory < 30% for 14+ days | High |
| Lambda | Memory used < 40% of allocated consistently | Medium |

**Exclude from over-provisioned analysis:**
- Resources with burst patterns (low avg but high max) - they need headroom.
- Resources in Auto Scaling groups (scaling handles right-sizing dynamically).
- Resources tagged with `rightsizing:skip` or `capacity:reserved`.

## Step 3: Identify Under-Provisioned Resources

Flag resources as under-provisioned if:

| Resource | Under-Provisioned Criteria | Risk |
|----------|---------------------------|------|
| EC2 | CPU p95 > 80% sustained | Performance degradation |
| EC2 | Memory > 85% (swap activity) | OOM risk |
| RDS | CPU p95 > 75% OR connections > 80% max | Query latency, connection failures |
| ElastiCache | Memory > 80% OR evictions > 0 | Cache thrashing |
| Fargate | CPU > 80% OR memory > 85% | Task throttling/OOM kills |
| Lambda | Duration > 80% of timeout | Timeout failures |

## Step 4: Calculate Recommendations

For each over-provisioned resource:

1. **Identify target instance type/size:**
   - Calculate required capacity: max(p95 utilization x current capacity x 1.3 safety factor)
   - Map to the nearest appropriate instance type
   - Prefer current generation instances (graviton where compatible)
   - Consider burstable instances (t3/t4g) for variable workloads with low average

2. **Estimate savings:**
   - Current monthly cost (on-demand or effective rate with RI/SP)
   - Recommended monthly cost
   - Monthly savings = current - recommended
   - Annual savings = monthly x 12

3. **Assess migration effort:**
   - In-place resize (EBS-backed EC2): Low effort, brief downtime
   - New instance required (instance store): Medium effort
   - RDS resize: Low effort, brief failover
   - Architecture change needed: High effort

## Step 5: Identify Quick Wins vs Strategic Changes

**Quick Wins (< 1 hour effort, immediate savings):**
- EBS volume type changes (gp2 -> gp3, io1 -> io2 with lower IOPS)
- Lambda memory reduction
- Fargate task size reduction
- ElastiCache node type downgrade

**Medium Effort (1 day, significant savings):**
- EC2 instance type change (same family, smaller size)
- RDS instance resize
- Moving from on-demand to Savings Plans/Reserved

**Strategic (1+ week, largest savings):**
- Architecture changes (monolith -> microservice with right-sized components)
- Migration to Graviton (ARM) instances
- Serverless migration for variable workloads
- Spot instances for fault-tolerant workloads

## Step 6: Validate Recommendations

Before finalizing:
1. Check for upcoming traffic growth (seasonal patterns, product launches).
2. Verify the workload is not expected to grow significantly.
3. Confirm the recommended instance type supports required features (enhanced networking, EBS optimization).
4. Check if Reserved Instances or Savings Plans cover the current type (changing type may lose RI benefit).

## Output

Produce a rightsizing report:
1. **Summary**: Total resources analyzed, over-provisioned count, potential monthly/annual savings.
2. **Top 10 Savings Opportunities**: Resource, current size, recommended size, monthly savings, effort level.
3. **Over-provisioned Resources Table**: Full list with utilization data and recommendations.
4. **Under-provisioned Resources Table**: Resources at risk of performance issues.
5. **Savings by Category Chart**: Breakdown of potential savings by resource type.
6. **Implementation Priority**: Quick wins first, then medium effort, then strategic.