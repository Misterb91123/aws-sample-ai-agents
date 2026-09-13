---
name: iot-rules-engine-action-failures
agent_type: "Incident RCA"
description: Provides investigation procedures for AWS IoT Rules Engine action
  failures, including throttled or errored deliveries to Lambda, SQS, DynamoDB,
  Kinesis, and Republish, error-action and DLQ gaps, and SQL topic-filter misses.
  Use this skill when RulesEngine.ActionExecution drops, when
  ActionExecutionThrottled rises, when downstream targets stop receiving IoT data,
  or when a rule appears to never match incoming messages.
version: "1.0.0"
last_updated: "2026-08-14"
---

# IoT Rules Engine Action Failures

Use this skill to diagnose and resolve AWS IoT Rules Engine failures where rule
actions do not execute, are throttled, or fail to deliver to downstream targets.
Posture is read-only investigation; recommend specific, least-change fixes only.

## When to Activate

- Downstream systems (Lambda, SQS, DynamoDB, Kinesis) stop receiving IoT messages.
- CloudWatch AWS/IoT metric RulesEngine.ActionExecution.Failure is non-zero.
- RulesEngine.ActionExecutionThrottled is rising.
- A rule appears to never match (RulesEngine.TopicMatch flat despite traffic).
- Republish action loops or fails to reach the target topic.
- Error action / dead-letter destination is empty when failures are occurring.

## Step 1: Identify Affected Rules

Enumerate rules and isolate which are failing before touching metrics.

1. Call iot ListTopicRules via `use_aws` to list rule names, targeted topic
   patterns, and whether each is disabled (ruleDisabled).
2. For each suspect rule, call iot GetTopicRule to retrieve the SQL statement, the
   actions array, and the errorAction (the fallback invoked when a primary action
   fails).
3. Build a quick map: rule name -> SQL topic filter -> action type(s) -> target
   ARN -> errorAction present (yes/no).

Focus first on rules whose target ARN matches the downstream system reported as
missing data.

## Step 2: Check Action Execution Metrics

In the AWS/IoT namespace, RulesEngine metrics are dimensioned by RuleName and
ActionType. Use Sum over a 1-minute period.

| Metric | Meaning | Interpretation |
|--------|---------|----------------|
| RulesEngine.TopicMatch | Messages matched the rule topic filter | If flat, the SQL/topic filter is not matching (go to Step 4) |
| RulesEngine.ActionExecution | Action attempts | Compare to TopicMatch; large gap means matched messages are not producing actions |
| RulesEngine.ActionExecution.Success | Successful deliveries | Should track ActionExecution |
| RulesEngine.ActionExecution.Failure | Failed deliveries | Non-zero indicates target or permission errors (Step 3) |
| RulesEngine.ActionExecutionThrottled | Throttled by IoT or the target | Rising indicates rate pressure (Step 3 / Step 5) |

If TopicMatch is healthy but ActionExecution.Failure or ActionExecutionThrottled
is high, the SQL is fine and the problem is delivery.

## Step 3: Inspect Error Action and CloudWatch Logs

1. Confirm IoT logging is enabled with iot GetLoggingOptions. In CloudWatch Logs
   group AWSIotLogsV2 filter eventType = RuleExecution with status FAILURE. The
   log records reason and the failed action target.
2. Common failure reasons by target:
   - Lambda: AccessDenied (IoT rule role lacks lambda:InvokeFunction), function
     throttled (concurrency limit), or function error.
   - SQS: AccessDenied on sqs:SendMessage, wrong queue URL/region, or FIFO queue
     missing MessageGroupId.
   - DynamoDB: AccessDenied on dynamodb:PutItem, provisioned throughput exceeded
     (ProvisionedThroughputExceededException), or key attribute missing from SQL.
   - Kinesis: AccessDenied on kinesis:PutRecord, shard limit exceeded, or missing
     partition key.
   - Republish: role lacks iot:Publish on the target topic, or the target topic
     re-triggers the same rule (loop).
3. Check the errorAction destination (for example an SQS DLQ or a separate
   Republish topic). If errorAction is absent, failed messages are dropped
   silently, which explains missing data with no visible target errors.

## Step 4: Validate the SQL and Topic Filter

If RulesEngine.TopicMatch is flat, matched-message logic is the fault.

1. Re-read the SQL FROM clause from GetTopicRule. Confirm the topic filter matches
   the topics devices actually publish to (verify against AWSIotLogsV2 PUBLISH
   records). A common miss is a leading slash, wrong level count, or using `+`
   where `#` is required.
2. Validate WHERE-clause predicates against real payload fields. A WHERE that
   references a field absent from the message evaluates to no match, so no action
   fires even though messages arrive.
3. Confirm the SQL version (for example 2016-03-23) supports the functions used.
4. Check that the rule is not disabled (ruleDisabled = false from Step 1).

## Step 5: Check Downstream Target Health

Delivery failures are frequently caused by the target, not IoT.

1. Lambda: review the function CloudWatch metrics for Throttles and Errors and
   Concurrent Executions vs the reserved/account concurrency limit.
2. SQS: confirm the queue exists in the same region, policy permits the IoT role,
   and the queue is not full or misconfigured (FIFO requirements).
3. DynamoDB: check ThrottledRequests / ConsumedWriteCapacity vs provisioned or
   on-demand limits.
4. Kinesis: check WriteProvisionedThroughputExceeded and shard count.
5. Confirm the IoT rule action IAM role trust and permissions grant only the
   specific action on the specific target resource ARN.

## Step 6: Remediate

| Root Cause | Recommended Fix |
|------------|-----------------|
| Rule role missing permission | Add the specific action (for example lambda:InvokeFunction) scoped to the exact target ARN; do not use wildcard resources |
| Target throttled (Lambda/DynamoDB/Kinesis) | Increase target capacity/concurrency or add batching; smooth ingest rate |
| ActionExecutionThrottled by IoT quota | Request a Service Quotas increase for rules engine actions per second; reduce redundant actions |
| SQL topic filter mismatch | Correct the FROM topic filter to the actual device topic; fix WHERE field references |
| Missing errorAction / DLQ | Add an errorAction (for example an SQS DLQ) so failed messages are captured, not dropped |
| Republish loop | Point Republish at a distinct topic that does not re-match the same rule |

Prohibited: do not disable IoT logging, do not attach wildcard IAM permissions to
the rule role, and do not remove the error action to hide failures.

## Output

Provide:
1. Affected rule(s) with SQL, action types, target ARNs, and errorAction status.
2. Failure classification (no match vs delivery failure vs throttling) with the
   RulesEngine metrics observed.
3. Root cause with evidence (AWSIotLogsV2 RuleExecution reasons, target metrics,
   IAM findings).
4. Specific least-privilege fix and prevention steps (DLQ coverage, alarms on
   ActionExecution.Failure and ActionExecutionThrottled, SQL tests against sample
   payloads).
