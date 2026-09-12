---
name: performance-efficiency-reviewer
agent_type: "Evaluation"
description: Evaluates infrastructure against the AWS Well-Architected Performance
  Efficiency pillar, checking resource selection, scaling approaches, monitoring,
  and trade-off decisions. Use this skill during Well-Architected reviews,
  performance assessments, or when a service has latency or throughput issues.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Performance Efficiency Reviewer

Use this skill to evaluate workloads against the Performance Efficiency pillar
of the AWS Well-Architected Framework.

## When to Activate

- Well-Architected review session for performance pillar.
- Service experiencing latency or throughput issues.
- Architecture decision on compute/database selection.
- Periodic performance assessment.

## Step 1: Selection (PERF 1-4)

1. **Compute selection:**
   - Is the compute type appropriate for the workload? (instances vs containers vs serverless)
   - Are current-generation instance types used?
   - Is Graviton (ARM) evaluated for compatible workloads?
   - Is the right instance family selected (compute-optimized vs memory-optimized)?
   - For containers: are resource requests/limits appropriately set?

2. **Storage selection:**
   - Is the storage type matched to access pattern? (IOPS vs throughput vs cost)
   - Are EBS volumes sized for performance (gp3 with configured IOPS)?
   - Is S3 access pattern matched to storage class?
   - Is caching reducing storage access for hot data?

3. **Database selection:**
   - Is the database engine appropriate for the access pattern?
   - Is read-heavy workload using read replicas?
   - Is DynamoDB used for key-value patterns (vs forcing into relational)?
   - Are connection pools sized correctly?
   - Is the database instance class adequate for the query load?

4. **Network selection:**
   - Is CloudFront used for cacheable content?
   - Are VPC endpoints used for AWS service access (lower latency than internet)?
   - Is enhanced networking enabled for performance-sensitive instances?
   - Are placement groups used for low-latency inter-instance communication?

## Step 2: Review (PERF 5)

1. **Keep up with technology:**
   - Are new AWS features evaluated when released?
   - Is the architecture reviewed when performance changes?
   - Are benchmarks run to validate performance assumptions?
   - Are performance tests part of the deployment pipeline?

## Step 3: Monitor (PERF 6)

1. **Monitor performance:**
   - Are latency percentiles tracked (p50, p95, p99)?
   - Are saturation metrics monitored (CPU, memory, connections, IOPS)?
   - Are there alarms for performance degradation?
   - Is performance correlated with deployments (deploy markers)?
   - Are anomalies auto-detected (CloudWatch Anomaly Detection)?

## Step 4: Trade-offs (PERF 7)

1. **Use trade-offs effectively:**
   - Is caching used to trade freshness for speed?
   - Is read replication used to trade consistency for throughput?
   - Are CDNs used to trade global consistency for latency?
   - Is eventual consistency acceptable (and used) for non-critical paths?
   - Are async patterns used where synchronous isn't required?
   - Is data partitioning used to improve query performance?

## Performance Anti-Patterns to Check

| Anti-Pattern | Check |
|-------------|-------|
| Synchronous calls where async would work | Sequential API calls that could be parallelized |
| Database as a queue | Polling a table for work instead of using SQS |
| Over-normalized schema | Excessive JOINs for read-heavy access patterns |
| No caching layer | Database hit for every request (even identical queries) |
| Monolithic Lambda | Single function doing too much, large package, slow cold start |
| Network bottleneck | All traffic through single NAT GW or proxy |
| Under-provisioned IOPS | EBS queuing causing latency spikes |

## Scoring

Rate each area:
- **Optimized** (3): Performance best practices applied and measured
- **Partial** (2): Some optimization, not measured or validated
- **Gap** (1): Performance risk from poor selection or missing optimization
- **N/A** (0): Not applicable

## Output

Provide:
1. Per-area score with specific bottlenecks identified.
2. Overall Performance Efficiency score.
3. Anti-patterns detected with latency/throughput impact.
4. Top 5 performance improvements with expected gain.