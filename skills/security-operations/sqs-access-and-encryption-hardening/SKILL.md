---
name: sqs-access-and-encryption-hardening
agent_type: "Evaluation"
description: Use when hardening Amazon SQS encryption and access policies. It finds queues without server-side encryption, wildcard principal policies, and missing dead-letter queues, then recommends fixes. Apply during messaging security reviews or before onboarding new producers and consumers.
version: "1.0.0"
last_updated: "2026-08-14"
---

# SQS Access and Encryption Hardening

Harden SQS queues by enforcing encryption, scoping access policies, and ensuring reliable failure handling.

## When to Activate
- GetQueueAttributes shows neither KmsMasterKeyId nor SqsManagedSseEnabled set (no SSE).
- A queue Policy grants Principal * without a Condition restricting source.
- RedrivePolicy is absent, so failed messages have no dead-letter queue.
- A queue policy allows sqs:* to a broad principal.
- MessageRetentionPeriod is too short to allow reprocessing after an incident.

## Step 1: Inventory Queues and Attributes
- Call ListQueues and GetQueueAttributes with AttributeNames All.
- Record KmsMasterKeyId, SqsManagedSseEnabled, Policy, and RedrivePolicy.
- Separate standard from FIFO queues.

## Step 2: Check Encryption at Rest
- Flag queues where both KmsMasterKeyId and SqsManagedSseEnabled are absent.
- Prefer a customer managed KMS key where policy requires key control.
- Recommend SetQueueAttributes to enable SSE.

## Step 3: Review Access Policies
- Parse the Policy attribute and flag statements with Principal * and no Condition.
- Flag Action sqs:* or overly broad action sets.
- Recommend scoping principals to specific role ARNs and adding aws:SourceArn conditions.

## Step 4: Validate Failure Handling
- Flag queues with no RedrivePolicy pointing to a dead-letter queue.
- Recommend a maxReceiveCount of 5 before redrive to the DLQ.
- Confirm MessageRetentionPeriod allows at least 4 days (345600 seconds) for reprocessing.

## Step 5: Recommend Hardening Actions
- Enable SSE on all unencrypted queues.
- Replace wildcard principals with scoped ARNs and source conditions.
- Add dead-letter queues and CloudWatch alarms on ApproximateNumberOfMessagesVisible.

## Output
Produce a titled "SQS Access and Encryption Hardening Report" listing queues without SSE, policies with wildcard principals, queues missing a dead-letter queue, and short retention periods. Include a prioritized remediation list: scope wildcard access policies first, enable SSE on unencrypted queues second, then add dead-letter queues and adjust retention for safe reprocessing.