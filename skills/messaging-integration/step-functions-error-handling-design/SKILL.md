---
name: step-functions-error-handling-design
agent_type: "Generic"
description: Use when designing AWS Step Functions retry, catch, and error handling. It finds high execution failure rates, states missing Retry or Catch blocks, and uncaught error types, then recommends resilient state machine definitions. Apply during workflow reliability reviews.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Step Functions Error Handling Design

Design Step Functions retry and catch behavior so transient failures recover and terminal failures route to defined handlers.

## When to Activate
- CloudWatch ExecutionsFailed relative to ExecutionsStarted exceeds 5 percent.
- GetExecutionHistory shows repeated TaskFailed events with no matching Retry.
- Task states lack a Catch block for States.ALL or specific error names.
- ExecutionsTimedOut is greater than 0 due to missing TimeoutSeconds.
- A workflow has no failure notification path on the terminal Fail state.

## Step 1: Measure Failure Rates
- Query CloudWatch ExecutionsStarted, ExecutionsFailed, ExecutionsTimedOut, and ExecutionsAborted per state machine.
- Compute the failure rate and flag anything above 5 percent.
- Identify the state machines with the highest absolute failure counts.

## Step 2: Analyze Failure History
- Call GetExecutionHistory for recent failed executions and read TaskFailed and ExecutionFailed events.
- Group failures by error name (for example Lambda.ServiceException or States.Timeout).
- Distinguish transient errors from terminal business errors.

## Step 3: Audit Retry Coverage
- Read the state machine definition and inspect each Task state Retry array.
- Recommend Retry with IntervalSeconds 2, MaxAttempts 3, and BackoffRate 2 for transient errors.
- Flag Task states with no Retry on retriable errors.

## Step 4: Audit Catch Coverage
- Inspect each state Catch array for States.ALL and specific error names.
- Recommend a Catch that routes to a failure-handling state and preserves error output.
- Flag states with no Catch block.

## Step 5: Add Timeouts and Notifications
- Recommend TimeoutSeconds on every Task state to prevent stuck executions.
- Route terminal failures to an SNS notification or DLQ.
- Add a CloudWatch alarm on ExecutionsFailed for critical workflows.

## Output
Produce a titled "Step Functions Error Handling Report" listing state machines with failure rate above 5 percent, states missing Retry or Catch, uncaught error types, and states without timeouts. Include a prioritized remediation list: add Retry to transient-error task states first, add Catch blocks routing to failure handlers second, then set timeouts and add failure notifications and alarms.