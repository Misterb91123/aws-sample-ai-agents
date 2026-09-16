---
name: devops-agent-usage-cost-estimation
agent_type: "Generic"
description: Measures the downstream API-call cost that running AWS DevOps Agent
  puts on an account's regular AWS bill - the second-order cost beyond agent-second
  usage and support credits. Use this skill to answer "what does running DevOps
  Agent actually cost me in API usage?" It reads the agent's own call log, isolates
  the few operations that are actually billed (CloudWatch Logs Insights StartQuery
  dominates, at roughly 95 percent of downstream cost; almost everything else is a
  free Describe/List/Get), prices them live from the AWS Price List API, and
  reconciles the estimate against Cost Explorer or the CUR. Read-only and
  estimate-only.
version: "1.0.0"
last_updated: "2026-09-12"
---

# DevOps Agent Usage Cost Estimation

Use this skill to make the second-order cost of running AWS DevOps Agent visible
and defensible. There are three cost buckets: direct agent-second usage, support
credits that usually cover it, and the downstream API calls the agent makes during
investigations that land on the regular AWS bill. This skill measures that third
bucket. It is almost always small, one operation dominates it, and it can be
reconciled against the customer's own bill. This skill estimates and reconciles;
it never changes anything.

## Sources

This skill reasons over read-only sources; it never mutates a resource.

- The DevOps Agent call log: the agent logs every call to a CloudWatch log group
  (deployment-specific suffix under /aws/bedrock-agentcore/runtimes/AgentToolbox),
  tagged with service_name, operation_name, and execution_id. Each account must
  find its own log group; never assume another account's suffix.
- CloudWatch Logs Insights over that log group, to count calls per service,
  per execution_id, and per service+operation.
- The AWS Price List API (pricing get-products, endpoint always us-east-1, free to
  call, needs pricing:GetProducts) for live list rates.
- Cost Explorer and, where enabled, the CUR, for top-down reconciliation.
- get-query-results bytesScanned for the bottom-up GB-scanned figure.

## Method

1. Find the agent log group. List log groups with the prefix
   /aws/bedrock-agentcore/runtimes/AgentToolbox and confirm the account's own
   group. Also read direct usage with the DevOps Agent get-account-usage call for
   the full picture.
2. Count the calls. In Logs Insights over the investigation window, filter to
   message = 'Tool call completed' and mcp_tool_name = 'use_aws', then count by
   service_name, by execution_id, and by service_name + operation_name.
3. Keep only the billed operations. Two passes:
   - Triage by verb: Describe*, List*, and most Get* config reads are free - drop
     them. Operations that scan or return data are likely paid - keep them.
   - Filter deterministically: re-run the count filtered to the known paid
     operations rather than eyeballing 40+ services. Known paid operations:
     StartQuery (CloudWatch Logs Insights, GB scanned - the dominant driver),
     GetMetricData and GetMetricStatistics (CloudWatch metrics), GetTraceSummaries
     (X-Ray), StartQueryExecution (Athena, TB scanned), SelectObjectContent (S3
     Select), and on-demand DynamoDB reads. Add cross-region data transfer when
     the workload region differs from the Agent Space region.
4. Price each kept operation live from the Price List API - never hardcode a rate.
   Two rules: (a) the Pricing endpoint is always us-east-1, but the workload region
   is the region of the priced resource - resolve it from the resource, do not
   default it; (b) operation lookups add a regionCode filter, while usagetype
   lookups prepend a region prefix (for example USW2-DataScannedInTB). If a lookup
   returns zero products, HALT and report the gap - that is a lookup failure, not a
   zero-cost result; do not improvise a rate.
5. Estimate bottom-up. Sum bytesScanned across the agent's StartQuery calls in the
   window (from get-query-results), convert to GB, multiply by the live StartQuery
   rate. Add the negligible metric/trace meters and any cross-region transfer.
6. Reconcile top-down. In Cost Explorer for the same account and window, group
   CloudWatch by Usage Type and filter usage type containing DataScanned; or query
   the CUR for AmazonCloudWatch usage types like %DataScanned%. If bottom-up and
   top-down match, the number is proven; a gap is usually other (non-agent)
   Insights activity in the window - narrow the window to shrink it.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space (see the
AWS DevOps Agent "Connecting MCP Servers" capability). For this skill the "AWS
Pricing MCP Server" and the "AWS Billing and Cost Management MCP Server" are the
most relevant: the Pricing MCP can retrieve live list rates as a structured
complement to the pricing get-products calls, and the Billing and Cost Management
MCP can pull the Cost Explorer and usage data for the reconciliation step. Enable
either by connecting it to the Agent Space through the DevOps Agent MCP-server
integration, after which this custom agent can call the MCP's tools during its run.
Use the MCP in addition to the direct AWS reads (Logs Insights, get-query-results,
Cost Explorer via use_aws), never instead of them, and keep the Pricing API HALT
rule: an empty rate result is a lookup failure, not a zero. AWS MCP server names
and availability evolve, so verify the current server before relying on one.

## Output

Produce a usage-cost report:

1. Direct usage snapshot (agent-second usage from get-account-usage) for context,
   with a pointer to the credit-coverage view for buckets 1 and 2.
2. Call composition: calls per service and the service+operation breakdown for the
   window.
3. Costed operations only: the kept billed operations with the live rate fetched
   for each (and any HALT gaps flagged, not guessed).
4. Bottom-up estimate: total GB scanned and the dollar figure, stated as an
   upper-bound list-price estimate (a customer with negotiated pricing pays at or
   below it).
5. Reconciliation: the Cost Explorer or CUR figure for the same window and whether
   it matches, with the exact line to check.
6. Cost-control levers: narrow the time window, prefer free FilterLogEvents for a
   known string over Insights, and co-locate the Agent Space with the workload
   region to avoid cross-region transfer.

State clearly that billing has no per-API-call or per-principal cost line; this
method works because the agent logs its own calls per execution_id and the one
real driver (GB scanned) is a real billing dimension. All figures are read-only
estimates; the reconciled bill is the source of truth.
