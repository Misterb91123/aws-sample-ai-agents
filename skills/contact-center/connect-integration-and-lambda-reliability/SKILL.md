---
name: connect-integration-and-lambda-reliability
agent_type: "Incident RCA"
description: Provides investigation procedures for the reliability of Amazon Connect
  integrations, including Lambda data-dip errors and timeouts against the 8-second
  data-dip limit, Lex bot failures, Customer Profiles lookups, Contact Lens
  processing, and Kinesis streaming of CTRs and agent events with iterator age,
  throttling, and delivery failures, plus Amazon Q in Connect / Wisdom when used. Use
  this skill when a flow-invoked integration is slow or failing, when CTR or
  agent-event streaming lags or drops records, or when ContactFlowErrors correlate
  with a specific downstream integration.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Amazon Connect Integration and Lambda Reliability

Use this skill to diagnose reliability problems in the integrations an Amazon
Connect flow depends on. Investigation is read-only; any fix is specific and
reversible.

## When to Activate

- A flow data dip (Invoke Lambda) errors or times out.
- A Lex bot returns failures or misses intents inside a flow.
- Customer Profiles lookups fail or return stale data.
- Contact Lens processing does not appear for contacts.
- CTR or agent-event Kinesis streaming lags, throttles, or drops records.
- Amazon Q in Connect / Wisdom responses fail or time out.
- ContactFlowErrors correlate in time with a downstream integration.

## Step 1: Map the Integrations a Flow Uses

1. DescribeContactFlow (and ListContactFlows) to enumerate Invoke Lambda, Get
   customer input (Lex), Customer Profiles, and Wisdom/Amazon Q blocks.
2. Identify Kinesis targets from ListInstanceStorageConfigs for
   `CONTACT_TRACE_RECORDS` and `AGENT_EVENTS`.
3. Build the dependency list so each downstream can be checked in isolation.

## Step 2: Check Lambda Data Dips

The contact flow waits at most 8 seconds for a Lambda data-dip response (default
timeout 3 seconds, configurable up to 8). Even a successful function that answers
after the flow timeout drives the flow to its error branch.

1. Lambda CloudWatch metrics: `Errors`, `Throttles`, `Duration` (use p99/Max),
   `ConcurrentExecutions`.
2. If Duration p99 approaches or exceeds the configured data-dip timeout, the flow
   times out; optimize the function or raise the flow timeout toward 8 seconds if
   justified.
3. Throttles indicate the function hit its concurrency limit; check reserved
   concurrency and account limits.
4. Read the function logs for the failing invocations by request time correlated
   to the incident window.

## Step 3: Check Lex, Customer Profiles, Contact Lens

1. Lex: check the bot for errors and missed utterances, confirm the alias is
   published and associated with the instance, and confirm fulfillment latency is
   within the flow input timeout.
2. Customer Profiles: confirm the domain is associated with the instance and that
   lookup latency and error rate are healthy; a failed lookup should have a flow
   error branch so it does not disconnect the caller.
3. Contact Lens: confirm it is enabled for the flow/contact and that analytics
   output reaches its configured store; missing output points at storage config or
   permissions.

## Step 4: Check Kinesis Streaming of CTRs and Agent Events

For the CTR and agent-event streams:

- `GetRecords.IteratorAgeMilliseconds`: rising iterator age means the consumer is
  falling behind and records are delayed.
- `WriteProvisionedThroughputExceeded` / `ReadProvisionedThroughputExceeded`:
  throttling from insufficient shards.
- `PutRecords.FailedRecords` or delivery failures at the downstream (Firehose/
  Lambda consumer) indicate dropped or stuck records.
- Confirm shard count matches ingest rate; scale shards if throttling is chronic.

## Step 5: Correlate with ContactFlowErrors and Isolate the Failure

1. Pull AWS/Connect `ContactFlowErrors` and overlay the error onset with each
   integration's error/latency/throttle timeline.
2. The integration whose failure window aligns with the ContactFlowErrors onset is
   the prime suspect; a shared Lambda or Lex across many flows explains broad
   errors, while a single-flow error points to that flow's unique dependency.
3. Confirm with the contact flow logs (`InvokeExternalResource` results by
   ContactId) which block actually failed.

## Step 6: Remediate

Recommend specific, reversible fixes:

- Optimize a slow Lambda or raise the data-dip timeout toward 8 seconds only when
  Duration justifies it; add reserved concurrency to stop throttling.
- Ensure flows have error branches on every integration block so a downstream
  failure never disconnects the caller.
- Republish/associate the correct Lex alias or Customer Profiles domain.
- Scale Kinesis shards or fix the downstream consumer to clear iterator age and
  failed records.
- Re-run the affected path and confirm ContactFlowErrors and the integration
  metrics return to baseline.

## Output

Provide:
1. The integration dependency map for the affected flow.
2. Per-integration evidence (Lambda Errors/Throttles/Duration, Lex failures,
   Customer Profiles latency, Kinesis iterator age/throttling/failed records).
3. Root cause isolated to a specific integration, correlated with ContactFlowErrors
   and confirmed in the flow logs by ContactId.
4. Specific fix and the metrics to confirm recovery.
