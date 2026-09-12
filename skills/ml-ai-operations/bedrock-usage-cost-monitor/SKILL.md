---
name: bedrock-usage-cost-monitor
agent_type: "Generic"
description: Monitor Amazon Bedrock foundation model costs, token consumption, and throttling across models and applications. I use this skill to attribute spend to specific models, quantify input and output token usage, detect on-demand quota throttling, and evaluate provisioned throughput versus on-demand economics. I activate it when Bedrock costs rise, requests are throttled, or token usage spikes unexpectedly.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Bedrock Usage Cost Monitor

This skill provides a procedure for controlling Amazon Bedrock spend and reliability. It attributes token consumption and cost to individual models and applications, distinguishes on-demand throttling from capacity limits, and evaluates whether provisioned throughput is more economical than on-demand for steady workloads.

## When to Activate

- The Bedrock line item in Cost Explorer increases week over week without an approved usage change.
- Applications receive ThrottlingException or HTTP 429 responses from the InvokeModel or InvokeModelWithResponseStream APIs.
- Input or output token counts spike relative to request volume, indicating prompt bloat or runaway generation.
- A team is choosing between on-demand and provisioned throughput and needs a cost comparison.

## Step 1: Measure Token Consumption by Model

Retrieve CloudWatch metrics in the AWS/Bedrock namespace, dimensioned by ModelId:

- InputTokenCount and OutputTokenCount, summed over the billing window.
- Invocations and InvocationLatency for context.

Break the totals down per ModelId (for example anthropic.claude, amazon.titan, meta.llama variants). Output tokens are typically priced higher than input tokens, so track them separately. A high output-to-input ratio can indicate generations that are longer than necessary.

## Step 2: Attribute Cost per Model

Multiply token counts by the per-model, per-1000-token price for input and output separately, since prices differ substantially across models. Compute:

- Cost per model = (InputTokenCount / 1000 * input price) + (OutputTokenCount / 1000 * output price).
- Cost per invocation to compare model efficiency for the same task.

Rank models by total cost and by cost per invocation to surface expensive models that could be substituted.

## Step 3: Detect and Diagnose Throttling

Correlate ThrottlingException counts with request rate:

- On-demand invocation is subject to account-level requests-per-minute and tokens-per-minute quotas per model.
- If throttling coincides with traffic peaks on on-demand, the workload has outgrown on-demand quotas.
- Review Service Quotas for the specific model and region to confirm the applicable limit.

## Step 4: Compare Provisioned Throughput Versus On-Demand

For steady, high-volume workloads, provisioned throughput (measured in model units) can be cheaper and eliminates throttling:

- Estimate sustained tokens per minute from Step 1.
- Compare the hourly or committed cost of the required model units against the equivalent on-demand token cost for the same volume.
- Provisioned throughput favors predictable, high-utilization traffic; on-demand favors spiky or low-volume traffic. Recommend provisioned only when sustained utilization justifies the committed cost.

## Step 5: Evaluate Model Selection Efficiency

Confirm the right model is used for each task. Routing simple classification or extraction tasks to a large, expensive model wastes spend. Recommend a smaller or cheaper model where output quality is sufficient, and reserve larger models for tasks that require them.

## Step 6: Reduce Prompt Token Waste

Inspect prompt construction for common inefficiencies:

- Redundant context or full documents resent on every turn instead of summaries or retrieval.
- Verbose system prompts repeated across calls.
- Missing max token limits that allow generations to run longer than needed.

Reducing input tokens directly reduces cost on every invocation.

## Step 7: Account for Guardrail Overhead

If Amazon Bedrock Guardrails are enabled, account for the additional processing they add. Confirm guardrail policies are scoped to the content that requires them, since applying guardrails to every call adds latency and can add cost.

## Step 8: Trend Usage by Application

Where applications tag requests or use separate model access patterns, group usage by application or team to attribute spend and identify the largest drivers. Track daily token and cost trends to detect anomalies early.

## Output

The skill produces a Bedrock usage and cost report containing: per-model token consumption (input and output), attributed cost per model and per invocation, a throttling diagnosis against on-demand quotas, a provisioned-throughput versus on-demand cost comparison, model selection recommendations, prompt efficiency findings, guardrail overhead notes, and application-level usage trends with cost anomaly flags.