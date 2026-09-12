---
name: eventbridge-dlq-and-retry-design
agent_type: "Generic"
description: Use when designing Amazon EventBridge dead-letter queues and retry policies for reliable delivery. It finds rules with failed invocations, targets without a DLQ, and default retry settings, then recommends resilient delivery configuration. Apply during event-driven reliability reviews.
version: "1.0.0"
last_updated: "2026-08-14"
---

# EventBridge DLQ and Retry Design

Design EventBridge target retry and dead-letter handling so failed events are captured and redriven rather than lost.

## When to Activate
- CloudWatch FailedInvocations for a rule is greater than 0 over the last 24 hours.
- ListTargetsByRule shows a target with no DeadLetterConfig ARN set.
- A target uses the default RetryPolicy with no tuned MaximumRetryAttempts or MaximumEventAgeInSeconds.
- ThrottledRules or InvocationsFailedToBeSentToDlq is greater than 0.
- A critical rule delivers to a single target with no failure alerting.

## Step 1: Inventory Rules and Targets
- Call ListRules and ListTargetsByRule for each event bus.
- Record each target's Arn, RetryPolicy, and DeadLetterConfig.
- Flag targets with no DeadLetterConfig.

## Step 2: Measure Delivery Failures
- Query CloudWatch FailedInvocations and ThrottledRules per rule over 24 hours and 7 days.
- Flag rules with FailedInvocations greater than 0.
- Query InvocationsFailedToBeSentToDlq to catch DLQ delivery failures.

## Step 3: Review Retry Policies
- Read MaximumRetryAttempts and MaximumEventAgeInSeconds per target.
- Recommend MaximumRetryAttempts of at least 185 or a tuned value and MaximumEventAgeInSeconds up to 86400 for critical events.
- Flag targets left on defaults for critical rules.

## Step 4: Design Dead-Letter Queues
- Recommend an SQS DLQ per target with SSE enabled.
- Confirm the EventBridge service principal has sqs:SendMessage on the DLQ.
- Recommend a CloudWatch alarm on the DLQ ApproximateNumberOfMessagesVisible above 0.

## Step 5: Recommend Redrive and Alerting
- Recommend a redrive process from the DLQ once the downstream issue is resolved.
- Add alarms on FailedInvocations and DLQ depth for critical rules.
- Document ownership for each rule's failure handling.

## Output
Produce a titled "EventBridge DLQ and Retry Design Report" listing rules with FailedInvocations greater than 0, targets missing a dead-letter queue, and targets on default retry policies. Include a prioritized remediation list: attach dead-letter queues to critical targets first, tune retry attempts and event age second, then add alarms on FailedInvocations and DLQ depth with a redrive runbook.