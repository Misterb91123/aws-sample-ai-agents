---
name: step-functions-workflow-optimizer
agent_type: "Generic"
description: Optimizes AWS Step Functions state machines for cost and performance
  by analyzing state transition counts, per-state execution duration, Standard
  versus Express suitability, and parallelism tuning. Use this skill when
  workflows run slowly, cost more than expected, or approach execution history
  and duration limits.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Step Functions Workflow Optimizer

Use this skill to find where a Step Functions workflow spends time and money,
decide between Standard and Express workflow types, and recommend transition,
concurrency, and integration changes.

## When to Activate

- Executions take longer than the workflow logic requires.
- Step Functions cost is high relative to the value of the workflow.
- Executions approach the history event limit or the duration limit.
- Parallel or Map states run less efficiently than expected.

## Step 1: Count State Transitions

Standard workflows are billed per state transition:
1. Standard workflows cost $0.025 per 1000 state transitions. Count the
   transitions per execution from the execution history or the
   StateTransition metric.
2. Multiply transitions per execution by execution volume to project cost. High
   transition counts on high-volume workflows are the primary Standard cost
   driver.
3. Identify unnecessary transitions: redundant Pass states, over-decomposed
   Choice chains, and loops that could be collapsed or moved into a single
   Lambda.

## Step 2: Measure Per-State Duration

Locate the states that dominate wall-clock time:
1. Read ExecutionTime for the whole workflow and inspect the execution history
   timestamps to compute the duration of each state.
2. Rank states by contribution to total duration. A single slow Task state
   (a long Lambda or a slow service call) usually dominates.
3. Distinguish compute time from waiting: a state waiting on an external
   callback or a Wait state is not consuming compute but still extends duration.

## Step 3: Decide Standard Versus Express

Choose the workflow type that fits the pattern:
1. Standard: exactly-once, durable, up to 1 year duration, full execution
   history, billed per transition. Best for long-running, low-to-moderate
   volume, auditable workflows.
2. Express: at-least-once, billed by number of executions plus duration and
   memory, maximum duration 5 minutes. Best for high-volume, short-lived
   workflows such as event processing and streaming ingestion.
3. For high-volume workflows that finish under 5 minutes, Express is typically
   far cheaper than Standard because it is not billed per transition.
4. Confirm the workflow tolerates at-least-once semantics before moving to
   Express; add idempotency where needed.

## Step 4: Tune Parallel and Map Concurrency

Parallelism reduces wall-clock time when configured correctly:
1. Parallel state: branches run concurrently, so total time is the slowest
   branch, not the sum. Confirm independent work is actually split into
   branches.
2. Map state: set MaxConcurrency to process items in parallel. A value of 0
   means unbounded, which can overwhelm downstream services; a value of 1
   serializes and negates the benefit.
3. For large datasets, use Distributed Map to process items in parallel batches
   from S3, well beyond the inline Map limits.
4. Right-size concurrency to the downstream throughput so the workflow does not
   throttle its own dependencies.

## Step 5: Optimize Wait States

Wait states extend duration and, in some designs, cost:
1. Replace fixed Wait states with the wait-for-callback pattern (waitForTaskToken)
   where an external system signals completion, removing guesswork about how
   long to wait.
2. For polling loops (Wait then Choice), lengthen the interval or switch to a
   callback to cut transition count and duration.

## Step 6: Review Retry and Catch Configuration

Retry and error handling affect both reliability and cost:
1. Configure Retry with IntervalSeconds, MaxAttempts, and BackoffRate on Task
   states so transient errors do not fail the whole execution or trigger a full
   restart.
2. Excessive retries inflate transition count and duration; bound MaxAttempts
   and use targeted error names rather than catching all errors blindly.
3. Use Catch to route failures to a cleanup or notification path instead of
   failing hard.

## Step 7: Prefer Direct Service Integrations

Cut Lambda hops where a direct integration exists:
1. Step Functions supports optimized and AWS SDK service integrations that call
   DynamoDB, SQS, SNS, ECS, and many other services directly from a Task state.
2. Replacing a pass-through Lambda (a function whose only job is to call another
   AWS API) with a direct SDK integration removes Lambda cost, cold starts, and
   one layer of failure.
3. Keep Lambda for genuine business logic, not for plumbing calls.

## Step 8: Stay Within Execution Limits

Avoid hitting hard limits that fail executions:
1. Standard workflows have a history event limit of 25000 events per execution;
   long loops and large Maps can exhaust it. Use Distributed Map or split the
   workflow to stay under the limit.
2. Standard workflows allow up to 1 year duration; Express is capped at 5
   minutes. Confirm the chosen type fits the expected runtime.
3. Watch payload size between states (256 KB limit); pass references to S3 or
   DynamoDB instead of large payloads.

## Output

Provide an optimization summary:
1. Cost breakdown: transitions per execution, projected monthly transition cost
   for Standard, and the Express alternative estimate where applicable.
2. Duration breakdown by state, identifying the states that dominate wall-clock
   time.
3. Workflow type recommendation (Standard or Express) with the reason.
4. Specific changes: reduced transitions, Map concurrency value, wait-for-callback
   conversions, retry bounds, and direct service integrations to replace
   pass-through Lambdas.
5. Recommended CloudWatch alarms (ExecutionsFailed, ExecutionThrottled,
   ExecutionTime threshold) and a note on the 25000 history event limit to
   catch recurrence early.