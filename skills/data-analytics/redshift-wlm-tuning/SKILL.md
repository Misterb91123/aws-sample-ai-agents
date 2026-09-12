---
name: redshift-wlm-tuning
agent_type: "Generic"
description: Use when tuning Amazon Redshift workload management queues and concurrency. It finds high queue wait times, long queue depth, and disk pressure, then recommends WLM and concurrency scaling changes. Apply during query performance reviews or when reports run slowly under contention.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Redshift WLM Tuning

Tune Redshift workload management so queries do not queue behind each other and disk-based operations are minimized.

## When to Activate
- CloudWatch WLMQueueWaitTime is high, indicating queries wait for a slot.
- CloudWatch WLMQueueLength shows queries backing up in a queue.
- PercentageDiskSpaceUsed is above 85 percent.
- Queries spill to disk due to insufficient memory per slot.
- A single queue mixes short dashboards with long ETL, starving fast queries.

## Step 1: Measure Queue Contention
- Query CloudWatch WLMQueueWaitTime and WLMQueueLength per queue.
- Flag queues with sustained wait time or growing length.
- Query the STL_WLM_QUERY and SVL_QUERY_QUEUE_INFO views for queue statistics.

## Step 2: Assess Disk and Memory
- Query CloudWatch PercentageDiskSpaceUsed and flag above 85 percent.
- Query SVL_QUERY_SUMMARY for queries that spill to disk (is_diskbased).
- Flag queues where memory per slot is too small for typical queries.

## Step 3: Profile Workload Mix
- Identify short interactive queries versus long ETL and reporting queries.
- Recommend separate WLM queues by workload type and user group.
- Flag a single catch-all queue serving mixed workloads.

## Step 4: Recommend WLM Configuration
- Recommend Automatic WLM with query priorities, or manual WLM with tuned memory and slot counts.
- Set concurrency and memory so common queries fit in memory without spilling.
- Recommend a short query acceleration setting for sub-second queries.

## Step 5: Enable Scaling and Monitoring
- Recommend Concurrency Scaling for read queues to absorb spikes.
- Recommend VACUUM and ANALYZE schedules to control disk usage.
- Add alarms on PercentageDiskSpaceUsed above 85 percent and on rising queue wait time.

## Output
Produce a titled "Redshift WLM Tuning Report" listing queues with high WLMQueueWaitTime and WLMQueueLength, disk usage above 85 percent, disk-spilling queries, and workload mix issues. Include a prioritized remediation list: separate mixed workloads into dedicated queues first, size memory and slots to stop disk spills second, then enable Concurrency Scaling and add disk and wait-time alarms.