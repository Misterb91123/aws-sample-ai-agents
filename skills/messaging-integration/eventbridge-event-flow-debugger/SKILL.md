---
name: eventbridge-event-flow-debugger
agent_type: "Incident RCA"
description: Debugs Amazon EventBridge event delivery failures by tracing events
  from source through rules to targets, checking event pattern matching, target
  permissions, dead-letter queues, and cross-account or cross-region delivery.
  Use this skill when events do not reach their targets, rules fail to match, or
  target invocations fail with FailedInvocations.
version: "1.0.0"
last_updated: "2026-08-14"
---

# EventBridge Event Flow Debugger

Use this skill to follow an event through EventBridge, find the stage where it
is dropped, and recommend fixes to event patterns, permissions, retry policy,
and delivery configuration.

## When to Activate

- A target (Lambda, SQS, Step Functions, API destination) is not invoked when
  an event is expected.
- The FailedInvocations metric on a rule is greater than 0.
- Rules do not match events that appear correct at the source.
- Cross-account or cross-region event delivery silently stops.

## Step 1: Confirm the Event Reaches the Bus

Verify the event is published before debugging rules:
1. Identify which event bus the source publishes to: default (AWS service
   events), a custom bus (application events via PutEvents), or a partner bus
   (SaaS integrations).
2. Check the MatchedEvents metric on the bus. If it is 0, the event is not
   arriving or matches no rule.
3. For PutEvents callers, confirm the API returns FailedEntryCount of 0. A
   nonzero count means entries were rejected (bad detail-type, oversized event
   above the 256 KB limit).

## Step 2: Test the Rule Event Pattern

Pattern mismatches are the most common cause of missed events:
1. Capture the actual event JSON as delivered (from CloudTrail, an archive, or
   a catch-all rule to CloudWatch Logs).
2. Compare the rule event pattern field by field. Matching is case sensitive
   and exact; "Source" is not "source" and "OrderPlaced" is not "orderplaced".
3. Remember that a pattern matches only the fields it names; every named field
   must be present and match. Nested objects must mirror the event structure.
4. Use the TestEventPattern API to validate the pattern against the captured
   event JSON before deploying changes.

## Step 3: Verify Target Permissions

A matched rule still fails if EventBridge cannot invoke the target:
1. For Lambda targets, confirm a resource-based policy grants
   events.amazonaws.com permission to invoke the function with the rule ARN as
   source.
2. For SQS, SNS, and other resource targets, confirm the resource policy allows
   EventBridge to send.
3. For targets that require a role (Step Functions, ECS, Kinesis, API
   destinations), confirm the rule role has the needed action and that
   EventBridge can assume it.
4. Read FailedInvocations. Permission errors surface here even when the pattern
   matches correctly.

## Step 4: Configure and Inspect the Dead-Letter Queue

Capture events that fail after retries:
1. Attach a DLQ (an SQS queue) to the target so events that exhaust retries are
   preserved rather than lost.
2. EventBridge retries with exponential backoff for up to 24 hours (or the
   configured maximum event age, 60 to 86400 seconds) and up to the configured
   maximum retry attempts (0 to 185).
3. Inspect DLQ messages; the message attributes include the error code and
   error message explaining why delivery failed.

## Step 5: Check Input Transformer Errors

Input transformers can produce invalid target input:
1. Confirm the InputPathsMap JSONPath expressions resolve against the actual
   event; an unresolved path yields an empty or malformed value.
2. Confirm the InputTemplate produces valid JSON for the target; a broken
   template causes the target invocation to fail after the rule matches.
3. Test the transformer with a sample event and inspect the rendered output.

## Step 6: Debug Cross-Account and Cross-Region Delivery

Multi-account and multi-region routing adds delivery hops:
1. Cross-account: the destination bus resource policy must allow PutEvents from
   the source account, and the source rule must target the destination bus ARN
   via a role.
2. Cross-region: confirm the target region bus permits the source and that the
   rule targets the correct region endpoint.
3. Each hop is a separate rule-and-target evaluation; check MatchedEvents and
   FailedInvocations on both the source and destination buses to locate the
   drop.

## Step 7: Assess Target Throttling

Targets have their own limits that reject bursts:
1. Lambda targets throttle when concurrency is exhausted (429), returning
   errors that show as FailedInvocations and trigger retries.
2. SQS, Kinesis, and API destinations have their own throughput and rate
   limits; API destinations honor the configured invocation rate limit per
   second.
3. When throttling is the cause, either raise the target limit or add a DLQ and
   accept retry-driven delay.

## Step 8: Validate Against the Schema Registry

Optionally confirm event shape matches the expected schema:
1. If the source event is registered in the EventBridge schema registry,
   validate the delivered event against the schema to detect drift in field
   names or types.
2. Schema drift (a renamed or removed field) breaks patterns and input
   transformers that reference the old shape.

## Output

Provide a debugging summary:
1. The stage where the event is dropped: not published, no rule match, target
   permission denied, transformer error, throttling, or cross-account or
   cross-region misconfiguration.
2. The captured event JSON alongside the rule pattern, with the specific field
   that failed to match.
3. Concrete fixes: corrected event pattern, target permission or role change,
   DLQ configuration, retry policy values, or transformer correction.
4. Confirmation of MatchedEvents and FailedInvocations before and after the
   fix.
5. Recommended CloudWatch alarms (FailedInvocations threshold, DLQ message
   count, and a low MatchedEvents alarm) to catch recurrence early.