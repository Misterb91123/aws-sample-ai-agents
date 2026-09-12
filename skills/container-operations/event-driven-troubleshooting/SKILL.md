---
name: event-driven-troubleshooting
agent_type: "Incident RCA"
description: Provides investigation procedures for troubleshooting event-driven
  architectures including SQS backlogs, DLQ accumulation, Lambda invocation
  failures, and EventBridge delivery issues. Use this skill when asynchronous
  workflows are failing, messages are accumulating in DLQs, or events are not
  being delivered to their targets.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Event-Driven Architecture Troubleshooting

Use this skill to diagnose failures in asynchronous messaging and
event-driven systems on AWS.

## When to Activate

- SQS queue depth growing unexpectedly (consumer not keeping up).
- Messages appearing in dead-letter queues.
- Lambda invocations failing from event source triggers.
- EventBridge rules not delivering to targets.
- Kinesis consumers falling behind (iterator age growing).
- Step Functions executions failing or timing out.

## Step 1: Identify the Problem Area

| Symptom | Investigate |
|---------|------------|
| Queue depth growing | Consumer health, processing errors, concurrency limits |
| DLQ has messages | Message format issues, consumer bugs, permission errors |
| Lambda errors from SQS | Function errors, timeout, concurrency throttling |
| EventBridge no invocations | Event pattern mismatch, target permissions, target health |
| Kinesis iterator age growing | Consumer throughput, shard count, processing errors |
| Step Functions failing | State errors, task timeout, IAM permissions |

## Step 2: SQS Troubleshooting

**Queue depth growing (producer > consumer):**
1. Is the consumer running? (Lambda active, ECS task alive)
2. Is the consumer processing messages successfully? (check error metrics)
3. Is the consumer throttled? (Lambda concurrency limit)
4. Is batch size optimal? (too small = overhead, too large = timeout risk)
5. Is visibility timeout sufficient? (if processing takes longer -> message reappears -> reprocessed)

**DLQ accumulation:**
1. Sample a DLQ message: what does it contain?
2. Check the redrive policy: after how many attempts does it go to DLQ?
3. Common DLQ causes:
   - Message format changed (producer updated, consumer can't parse)
   - Downstream dependency unavailable (DB down during processing)
   - Poison pill messages (single bad message blocks the consumer)
   - Timeout (message processing exceeds visibility timeout)

**Fix approaches:**
- For transient failures: set up DLQ reprocessing (replay messages after fix)
- For poison pills: add message validation and skip/quarantine invalid messages
- For timeout: increase visibility timeout or reduce batch size

## Step 3: Lambda Event Source Troubleshooting

**Lambda triggered by SQS not processing:**
1. Check Lambda concurrent executions vs limit.
2. Check batch window and batch size configuration.
3. Check for partial batch failures (enable ReportBatchItemFailures).
4. If function errors: fix the bug (messages will retry until maxReceiveCount).
5. Check that function timeout < SQS visibility timeout (else messages reappear).

**Lambda triggered by Kinesis falling behind:**
1. Check iterator age metric (> 1 min = falling behind).
2. Check parallelization factor (increase to process more concurrently per shard).
3. Check for on-failure destination (DLQ for failed records).
4. Consider: bisect batch on error (isolate the failing record).

## Step 4: EventBridge Troubleshooting

**Events not reaching targets:**
1. Is the rule enabled? (Check rule state)
2. Does the event pattern match? Test with EventBridge TestEventPattern API.
3. Does the target have permission? (Resource-based policy on Lambda, SQS, etc.)
4. Is the target healthy? (Lambda not throttled, SQS queue exists)
5. Check failed invocation metrics on the rule.
6. Check the DLQ on the rule (if configured) for failed deliveries.

**Common event pattern issues:**
- JSON key casing mismatch (EventBridge is case-sensitive)
- Missing `detail-type` filter (matching too broadly or too narrowly)
- Source filtering incorrect
- Using `prefix` when exact match needed (or vice versa)

## Step 5: Kinesis Troubleshooting

**High iterator age (consumer lag):**
1. Add more shards (increase write AND read capacity).
2. Increase consumer parallelization (Lambda parallelization factor).
3. Check for hot shards (one partition key getting all traffic).
4. Reduce per-record processing time.
5. Consider enhanced fan-out (dedicated throughput per consumer).

**WriteProvisionedThroughputExceeded:**
1. Need more shards (each shard: 1MB/s or 1000 records/s write).
2. Distribute records across shards better (improve partition key distribution).
3. Use PutRecords API for batching (more efficient).

## Step 6: Step Functions Troubleshooting

**Execution failures:**
1. Check which state failed (in the execution history).
2. Common failures: Lambda timeout, Lambda error, permission denied on service integration.
3. For timeouts: increase HeartbeatSeconds or TimeoutSeconds.
4. For throttling: add retry with backoff in the state definition.

**Stuck executions:**
1. Execution using Task state waiting for callback that never comes.
2. Check if the worker is alive and sending SendTaskSuccess/SendTaskFailure.
3. Set TimeoutSeconds on Task states to prevent indefinite waits.

## Output

Provide:
1. Problem classification (producer/consumer/infrastructure/configuration).
2. Root cause with evidence (metrics, sample messages, error logs).
3. Immediate fix to resolve the current backlog.
4. Architecture improvement to prevent recurrence.