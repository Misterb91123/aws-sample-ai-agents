---
name: connect-contact-flow-troubleshooting
agent_type: "Incident RCA"
description: Provides investigation procedures for Amazon Connect contact flows that
  fail, loop, drop callers, or misroute contacts, including ContactFlowErrors metric
  spikes, Lambda data-dip timeouts and failures, Lex bot errors, Get customer input
  timeouts, module and flow reference errors, and prompts that do not play. Use this
  skill when callers report dropped or looping calls, when ContactFlowErrors rises,
  when a flow branches to its error path, or when a flow-invoked integration is
  suspected of breaking the caller experience.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Amazon Connect Contact Flow Troubleshooting

Use this skill to diagnose and resolve Amazon Connect contact flows that fail,
loop, drop callers, or misroute contacts. Investigation is read-only; any fix is
specific and reversible.

## When to Activate

- Callers are dropped, disconnected, or stuck in a loop inside a flow.
- ContactFlowErrors (AWS/Connect) spikes above baseline.
- A flow follows its error branch instead of the intended path.
- Get customer input or Get customer input (Lex) times out or returns no input.
- Prompts do not play or the wrong prompt plays.
- A Lambda data dip inside a flow times out or returns an error.
- Contacts land in the wrong queue or hit the default routing fallback.

## Step 1: Classify the Failure Symptom

| Symptom | Likely Origin | First Signal to Check |
|---------|---------------|----------------------|
| Caller dropped early | Disconnect/hang-up block, unhandled error branch | Flow logs ResultType, ContactFlowErrors |
| Flow loops | Loop/loop-prompts block, missing exit condition | Flow logs repeated block IDs |
| Misrouting | Set working queue, routing profile, branch logic | Flow logs Transfer to queue results |
| No input captured | Get customer input timeout, DTMF/Lex mismatch | Flow logs GetParticipantInput |
| Silence / no prompt | Play prompt block, missing prompt ARN | Flow logs PlayPrompt errors |
| Integration failure | Invoke Lambda / Lex fails or times out | Flow logs InvokeExternalResource |

Confirm scope: single contact, one flow, one phone number, or instance-wide.

## Step 2: Enable and Inspect Contact Flow Logs

Contact flow logging must be enabled on the instance (Data storage settings ->
Flow logs). Logs land in CloudWatch Logs group `/aws/connect/<instance-alias>`.

1. Retrieve the ContactId from the CTR or the reporter.
2. Query the log group filtering on `ContactId = "<contact-id>"` to reconstruct
   the exact block-by-block path.
3. For each entry inspect: `ContactFlowModuleType`, `ContactFlowName`,
   `Identifier` (block ID), `Parameters`, and `Results`.
4. Look for the first entry where `Results` is an error, an unexpected branch, or
   a timeout. That block is the failure origin; everything after it is downstream
   noise.

## Step 3: Correlate ContactFlowErrors

Pull the AWS/Connect metric `ContactFlowErrors` with GetMetricDataV2 (or
GetMetricData for the raw CloudWatch metric), grouped by InstanceId and, where
available, by contact flow.

- Baseline vs incident window: a jump from near-zero to sustained errors marks a
  regression, commonly a recent flow publish or a broken integration.
- Cross-check the flow publish time (DescribeContactFlow, ListContactFlows) with
  the error onset. A flow republished minutes before the spike is the prime
  suspect.
- If errors are spread across many flows that share one Lambda or Lex bot, the
  shared integration is the more likely root cause (see Step 4).

## Step 4: Check Invoked Lambda and Lex Integrations

Contact flow data dips call Lambda with a hard 8-second timeout for the flow to
receive a response (default 3 seconds configurable up to 8).

1. Identify integrations from the flow definition (DescribeContactFlow) and from
   `InvokeExternalResource` entries in the flow logs.
2. Lambda: check the function CloudWatch metrics Errors, Throttles, and Duration.
   Duration approaching or exceeding the flow data-dip timeout (3-8 s) causes the
   flow to take its error branch even when the function eventually succeeds.
3. Lex: check the bot for `FailedIntent`/missed utterances and confirm the bot
   alias is published and associated with the instance.
4. Confirm the returned attributes match what later blocks reference. A missing
   or misnamed attribute breaks Check contact attributes branching.

## Step 5: Validate Flow Logic and Error Branches

1. In DescribeContactFlow output, verify every block that can fail has an error
   branch wired to a safe fallback (queue callback, apology prompt, transfer to a
   staffed queue), not a dead end that disconnects the caller.
2. Verify Set working queue precedes Transfer to queue, and that the queue is
   valid (ListQueues, DescribeQueue) and inside hours of operation.
3. For Get customer input, confirm timeout, max digits, and terminator match the
   prompt instructions; a mismatch produces empty input and an error branch.
4. Confirm all referenced prompt ARNs, module ARNs, and flow ARNs exist and are
   published; a stale reference produces a module/flow reference error.

## Step 6: Remediate

Recommend specific, reversible fixes:

- Add or repair error branches so no failure path disconnects the caller.
- Raise the Lambda data-dip timeout toward the 8-second maximum only if function
  Duration justifies it; otherwise optimize the function.
- Republish or roll back the offending flow version and re-test with a known
  ContactId path in the logs.
- Correct attribute names, prompt/module/flow references, and queue assignments.
- Re-run the affected contact path and confirm ContactFlowErrors returns to
  baseline.

## Output

Provide:
1. Failure classification (dropped, loop, misroute, no input, silent, integration).
2. The exact failing block and flow, cited from the contact flow logs by
   ContactId and block Identifier.
3. Root cause with evidence (flow log Results, ContactFlowErrors trend, Lambda/Lex
   metrics, flow publish timeline).
4. Specific fix (branch repair, timeout change, rollback, reference correction)
   and the verification path.
