---
name: emr-cluster-cost-performance-optimizer
agent_type: "Generic"
description: Optimizes Amazon EMR cluster cost and performance by analyzing YARN
  resource utilization, Spot versus On-Demand instance fleet mix, idle clusters,
  node right-sizing, cluster lifecycle patterns, storage choices, step failures,
  and auto-termination. Use this skill when EMR clusters are underutilized, cost
  more than expected, or jobs run inefficiently.
version: "1.0.0"
last_updated: "2026-08-14"
---

# EMR Cluster Cost and Performance Optimizer

Use this skill to find where an Amazon EMR deployment wastes money or runs
slowly, quantify the waste against utilization metrics, and recommend
right-sizing, Spot usage, and lifecycle changes.

## When to Activate

- EMR clusters run with low YARN memory or vCore utilization.
- EMR spend rises without a matching increase in completed work.
- Clusters remain running with no active applications.
- Jobs run longer than expected or steps fail repeatedly.

## Step 1: Measure Cluster Utilization

Establish how much of the cluster is used:
1. Read YARN metrics from CloudWatch: MemoryAllocatedMB versus
   MemoryTotalMB and the corresponding vCore allocation.
2. Compute utilization as allocated divided by total; sustained utilization
   below 50 percent indicates over-provisioning.
3. Check YARNMemoryAvailablePercentage and ContainerPending; high available
   memory with no pending containers confirms excess capacity.
4. Check HDFSUtilization and AppsRunning to correlate load with time of day.

## Step 2: Review Spot Versus On-Demand Mix

Spot capacity reduces cost substantially for interruptible work:
1. Inspect the instance fleet or instance group composition for the primary
   (master), core, and task nodes.
2. The primary node should be On-Demand for stability; task nodes are the best
   Spot candidates since they hold no HDFS data.
3. Spot can cut compute cost by roughly 50 to 90 percent versus On-Demand for
   fault-tolerant task capacity.

Remediation:
- Move task nodes to Spot within instance fleets, defining multiple instance
  types per fleet to improve fulfillment.
- Keep core nodes On-Demand or a conservative Spot ratio to protect HDFS.
- Use allocation strategy (capacity-optimized) to reduce interruptions.

## Step 3: Detect Idle Clusters

Idle running clusters are pure waste:
1. Find clusters in WAITING state with AppsRunning equal to 0 for extended
   periods.
2. Correlate uptime against actual step activity to estimate idle hours and
   cost.

Remediation:
- Enable auto-termination (see Step 8) so transient clusters shut down after
  jobs finish.
- Terminate long-idle clusters or consolidate workloads.

## Step 4: Right-Size Core and Task Nodes

Match capacity to demand:
1. Compare peak versus average container demand to node capacity.
2. If utilization is chronically low, reduce node count or use smaller instance
   families.
3. If ContainerPending is frequently high, add task nodes or enable managed
   scaling with a sensible maximum.
4. Ensure core node count and instance size provide enough HDFS capacity and
   throughput without large idle headroom.

## Step 5: Evaluate Cluster Lifecycle Pattern

Transient clusters usually cost less than always-on:
1. Determine whether the cluster is transient (created per job, then
   terminated) or long-running (persistent, shared).
2. For batch and scheduled jobs, transient clusters avoid paying for idle time.
3. For interactive or steady-state workloads, a long-running cluster with
   managed scaling may be more efficient.

## Step 6: Evaluate EMR on EC2 Versus EMR Serverless

Consider the deployment model:
1. For spiky or intermittent Spark and Hive workloads, EMR Serverless removes
   cluster management and bills for resources consumed by the job.
2. For steady, high-utilization workloads with custom configuration needs,
   EMR on EC2 with Spot and managed scaling is often more cost-effective.
3. Recommend EMR Serverless when clusters show low utilization and frequent
   idle windows.

## Step 7: Review Storage: HDFS Versus S3 (EMRFS)

Storage choice affects cost and cluster lifecycle:
1. Data on HDFS ties the data lifecycle to the cluster and requires core nodes
   to stay running.
2. Using S3 through EMRFS decouples storage from compute, enabling transient
   clusters and smaller core fleets.
3. Recommend S3 (EMRFS) as the durable store and HDFS only for transient
   intermediate data.

## Step 8: Analyze Step Failures and Auto-Termination

Reliability and lifecycle hygiene:
1. Review step states for FAILED steps and root causes (bad input paths,
   memory, permissions) that waste cluster hours on reruns.
2. Confirm an auto-termination policy or KeepJobFlowAliveWhenNoSteps=false so
   transient clusters stop after the last step.
3. Set an idle timeout (for example, 60 minutes) on clusters that must persist
   briefly.

## Output

Provide an optimization report:
1. Utilization summary: YARN memory and vCore allocated versus total.
2. Idle cluster findings with estimated wasted hours and cost.
3. Spot adoption recommendation for task nodes with expected savings range.
4. Node right-sizing and managed scaling recommendations.
5. Lifecycle recommendation (transient versus long-running) and EMR on EC2
   versus EMR Serverless guidance.
6. Storage recommendation (S3/EMRFS versus HDFS).
7. Step failure findings and required auto-termination or idle-timeout
   configuration.