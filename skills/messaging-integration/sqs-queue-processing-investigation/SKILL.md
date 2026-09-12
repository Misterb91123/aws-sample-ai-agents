---
name: sqs-queue-processing-investigation
agent_type: "Incident RCA"
description: Investigates Amazon SQS queue processing problems including consumer
  lag, rising message age, visibility timeout misconfiguration, and poison
  messages by analyzing queue depth, throughput, and in-flight limits. Use this
  skill when ApproximateNumberOfMessagesVisible grows, ApproximateAgeOfOldestMessage
  rises, or consumers cannot keep pace with the message arrival rate.
version: "1.0.0"
last_updated: "2026-08-14"
---

# SQS Queue Processing Investigation

Use this skill to determine why an SQS queue is backing up, quantify the gap
between message arrival and consumption, and recommend visibility timeout,
batching, redrive, and consumer scaling changes.

## When to Activate

- ApproximateNumberOfMessagesVisible grows steadily and does not drain.
- ApproximateAgeOfOldestMessage rises toward the retention period (default 4
  days, maximum 14 days).
- Consumers report duplicate processing or messages that never complete.
- The dead-letter queue (DLQ) accumulates messages, indicating repeated
  failures.

## Step 1: Measure Queue Depth and Message Age

Establish the size and age of the backlog:
1. Read ApproximateNumberOfMessagesVisible (Sum) for the backlog size and
   ApproximateNumberOfMessagesNotVisible for in-flight messages currently being
   processed.
2. Read ApproximateAgeOfOldestMessage (Maximum). A value near 0 is healthy;
   sustained growth means consumers cannot keep up.
3. Compare age against the message retention period. Messages older than the
   retention window are silently deleted, so a rising age near the limit
   signals imminent data loss.

## Step 2: Compare Arrival Rate to Consumption Rate

Determine whether the queue is arrival-bound or consumer-bound:
1. Read NumberOfMessagesSent (arrival rate) and NumberOfMessagesDeleted
   (successful consumption rate). If sent exceeds deleted over a sustained
   window, the backlog grows.
2. Read NumberOfMessagesReceived to see how many messages consumers pull;
   received minus deleted approximates failed or abandoned processing.
3. Compute the drain time: backlog divided by (deleted rate minus sent rate).
   If the denominator is zero or negative, the queue never drains at current
   capacity.

## Step 3: Diagnose Visibility Timeout Misconfiguration

The visibility timeout must match actual processing time:
1. Retrieve the queue VisibilityTimeout (default 30 seconds, range 0 to 43200
   seconds, that is 12 hours).
2. Too short: a consumer that takes longer than the timeout to process a
   message causes the message to become visible again and be delivered to
   another consumer, producing duplicate processing.
3. Too long: after a consumer crashes, the message stays hidden for the full
   timeout before retry, delaying recovery.
4. Set VisibilityTimeout to at least the maximum expected processing time plus
   a safety margin, or extend it per message with ChangeMessageVisibility for
   variable workloads.

## Step 4: Check In-Flight Message Limits

SQS caps concurrently in-flight (received but not deleted) messages:
1. Standard queues allow up to 120000 in-flight messages.
2. FIFO queues allow up to 20000 in-flight messages.
3. If ApproximateNumberOfMessagesNotVisible approaches these limits, ReceiveMessage
   calls return OverLimit and no new messages are delivered even though the
   backlog is large.
4. Reaching the in-flight cap usually means consumers hold messages too long
   (slow processing or an oversized visibility timeout).

## Step 5: Detect Poison Messages via Redrive

Messages that repeatedly fail block progress:
1. Confirm a redrive policy exists with a DLQ and a maxReceiveCount (commonly 3
   to 5). Without it, a poison message is retried indefinitely.
2. Inspect the DLQ. A steady flow into the DLQ identifies messages that fail
   deterministically (bad payload, schema mismatch, missing dependency).
3. Sample DLQ message bodies and attributes to find the failure pattern, then
   fix the handler or filter the offending source.
4. Use DLQ redrive to replay messages back to the source queue after the fix.

## Step 6: Tune Batching and Long Polling

Reduce empty receives and per-call overhead:
1. Set ReceiveMessage MaxNumberOfMessages to 10 to pull a full batch per call
   and lower request cost.
2. Enable long polling by setting ReceiveMessageWaitTimeSeconds to 20 seconds
   (the maximum). Short polling wastes calls returning empty responses and can
   miss messages on some hosts.
3. Use SendMessageBatch and DeleteMessageBatch (up to 10 messages each) to cut
   API round trips.

## Step 7: Resolve FIFO Throughput Bottlenecks

FIFO ordering constraints can throttle throughput:
1. Messages within one MessageGroupId are processed strictly in order, so a
   single hot group serializes all its traffic. Distribute load across many
   group IDs to increase parallelism.
2. Content-based or explicit MessageDeduplicationId dedupes within a 5 minute
   window; unintended duplicate IDs cause messages to be silently dropped.
3. Standard FIFO throughput is 300 messages/s (or 3000 with batching) per API
   action; enable high throughput mode for higher rates when ordering is only
   required per group.

## Step 8: Scale Consumers

Match consumer capacity to the arrival rate:
1. For Lambda event source mapping, raise the batch size (up to 10000 for
   standard) and maximum concurrency; watch for throttling on the function.
2. For EC2 or ECS worker fleets, scale the number of pollers so total
   consumption exceeds peak NumberOfMessagesSent with headroom.
3. Ensure processing is idempotent so at-least-once delivery and occasional
   duplicates do not corrupt state.

## Output

Provide an investigation summary:
1. Bottleneck location: arrival spike, slow consumer, visibility timeout,
   in-flight cap, poison messages, or FIFO group serialization.
2. Quantified backlog (visible messages), oldest message age, and arrival
   versus consumption rates.
3. Specific configuration changes: visibility timeout value, redrive policy and
   maxReceiveCount, batch size, long polling interval, and group ID strategy.
4. Consumer scaling recommendation with a target consumption rate.
5. Recommended CloudWatch alarms (ApproximateAgeOfOldestMessage threshold,
   ApproximateNumberOfMessagesVisible threshold, DLQ message count) to catch
   recurrence early.