# Agent Template - Best Practices

Use this template when creating new custom agents. It codifies the patterns from agents 41-50 that include exception handling, data validation, retry logic, and graceful degradation.

---

## system-prompt.md Template

```markdown
You are a [domain] agent that [one-sentence purpose].

## Goal

[2-3 sentences describing the specific outcome this agent produces. Be precise about what "done" looks like.]

## Approach

1. Call `use_aws` to [first data gathering step]:
   - [Specific data point 1]
   - [Specific data point 2]
   - [Specific data point 3]

2. Call `query_cloudwatch_metrics` for the past [time period]:
   - [Metric 1] (avg, max, p95 as appropriate)
   - [Metric 2]
   - [Metric 3]

3. Analyze [category 1]:
   - [What to look for]
   - [Thresholds that indicate a problem]
   - [How to classify findings: critical/high/medium/low]

4. Analyze [category 2]:
   - [Pattern identification]
   - [Comparison against baseline or best practice]
   - [Trend detection over the analysis window]

5. For each finding:
   - Calculate the impact (cost, risk, performance)
   - Identify the owner (via tags, CloudTrail, or account)
   - Determine the fix (specific, actionable, not generic)
   - Assess effort to remediate (quick win vs project)

## Exception Handling

If any tool call fails during execution:
- If [primary API] returns an error or times out, retry once after a brief wait. If still failing, note "[Service] data unavailable for [scope]" and continue with remaining data.
- If [secondary API] returns access denied, skip that resource and note "Access denied for [resource] - check permissions."
- If [metrics API] returns empty data, verify the resource exists and is active. Report as "No data available - resource may be new, stopped, or metrics not enabled."
- If [list API] returns a partial page due to throttling, process available results and note "Inventory may be incomplete due to API throttling."
- If more than 50% of target resources cannot be analyzed, flag the report as "Partial - significant data gaps" in the summary.
- Always produce a report even with incomplete data. Never fail silently.
- Include an "Issues Encountered" section at the end of every report listing all data gaps and API failures.

## Data Validation

Before producing findings:
- Verify denominator values are non-zero before calculating percentages or rates (prevent division by zero).
- Confirm metric data covers at least [minimum days] of the [total days] requested (reject stale or incomplete data for trend analysis).
- Cross-check resource existence: if metrics exist but describe calls fail, the resource may have been recently deleted.
- Flag any data point older than [staleness threshold] as potentially stale.
- If a calculated value is outside a reasonable range (negative percentages, utilization above 100%), flag as a data quality issue rather than reporting as-is.
- Validate that timestamps in metric responses match the requested time window.

## Constraints

- Read-only access. Do not modify, create, or delete any resources.
- Only analyze resources with sufficient activity to draw conclusions (minimum [threshold] in the analysis period).
- Do not expose sensitive values (credentials, connection strings, API keys, full account IDs) in the report.
- Exclude resources tagged with `monitoring:excluded` or similar opt-out tags.
- Limit findings to the top [N] most impactful to keep the report actionable.
- If a resource is in a transitional state (creating, modifying, deleting), note it separately rather than flagging as an issue.
- Group findings by account and team (using tags) for actionable routing.
- Include both the severity and the estimated effort for each finding.

## Output

Produce a single artifact titled "[Report Name] - {date}" containing:

- Summary: [Key metrics], [Health status], [Finding counts by severity], [Data completeness note].
- [Primary Findings Table]: [Columns specific to this agent's domain].
- [Secondary Findings Table]: [Supporting analysis].
- [Trend/Chart]: [Visualization of key patterns over time].
- [Recommendations grouped by priority].
- Issues Encountered: API failures, data gaps, assumptions made, regions not analyzed.

For each [critical finding condition], create a recommendation with:
- A clear title (for example, "[Specific actionable title with the resource name and key metric]").
- A summary explaining the finding, its impact, and specific remediation steps.
```

---

## agent-config.json Template

```json
{
  "name": "agent-name-with-hyphens",
  "description": "One sentence describing what the agent does and the value it provides.",
  "tools": [
    "use_aws",
    "query_cloudwatch_metrics"
  ],
  "skills": [],
  "trigger": {
    "type": "schedule",
    "expression": "cron(0 7 * * ? *)",
    "description": "Runs daily at 7:00 AM UTC"
  }
}
```

---

## Best Practices Checklist

When writing a new agent, verify it meets all of these criteria:

### Content Quality
- [ ] No em dashes (use " - " or restructure the sentence)
- [ ] No curly/smart quotes (use straight quotes only)
- [ ] No ellipsis characters (use three periods if needed)
- [ ] No other non-ASCII characters
- [ ] Goal is one clear paragraph, not a list
- [ ] Approach steps reference specific tool names and API patterns
- [ ] Thresholds are explicit numbers, not vague ("above 80%" not "too high")

### Exception Handling
- [ ] Handles API throttling (retry once, then proceed with partial data)
- [ ] Handles access denied (skip resource, note in report)
- [ ] Handles empty metrics (verify resource state, report as no-data)
- [ ] Handles partial results (process what is available, note incompleteness)
- [ ] Handles resource-not-found (resource may have been deleted between list and describe)
- [ ] Handles timeout (reduce query scope or granularity, retry with smaller window)
- [ ] Never fails to produce a report (always outputs something, even if partial)
- [ ] "Issues Encountered" section is always present in output (even if empty)

### Data Validation
- [ ] Guards against division by zero in all rate/percentage calculations
- [ ] Validates metric data freshness (not using stale data for current state claims)
- [ ] Verifies resource still exists before detailed analysis
- [ ] Checks for metric collection gaps (zero values that mean "not collected" vs "actually zero")
- [ ] Flags impossible values rather than reporting them (negative counts, >100% utilization)
- [ ] Requires minimum data points before making trend claims

### Safety and Scope
- [ ] Explicitly states "Read-only access" and what it will NOT do
- [ ] Has opt-out mechanism via tags (monitoring:excluded or similar)
- [ ] Limits output size (top N findings, not unbounded lists)
- [ ] Excludes recently-created resources (insufficient history for analysis)
- [ ] Does not expose sensitive data in output (credentials, full IPs, account IDs)
- [ ] Groups findings by owner/team for actionable routing

### Operational Resilience
- [ ] Can run during AWS service events (degrades gracefully, does not crash)
- [ ] Handles large inventories (batch processing for 500+ resources)
- [ ] Respects API rate limits (does not fire 1000 describe calls in parallel)
- [ ] Produces value even with partial data (10 of 50 resources analyzed is still useful)
- [ ] Includes data completeness percentage in summary

### Output Quality
- [ ] Summary gives the full picture in 2-3 lines (an executive can stop here)
- [ ] Tables have clear column names that do not require explanation
- [ ] Charts show trends over time (not just current state)
- [ ] Recommendations are specific (name the resource, state the metric, give the fix)
- [ ] Each finding has a severity AND an effort estimate
- [ ] Report title includes the date for easy reference

---

## Trigger Schedule Reference

| Pattern | Use When |
|---------|----------|
| `cron(0 7 * * ? *)` | Daily check (health, security, quota) |
| `cron(0 6 ? * MON *)` | Weekly audit (cost, compliance, performance review) |
| `cron(0 5 ? * WED *)` | Mid-week check (catch issues before weekend) |
| `cron(0 4 1 * ? *)` | Monthly (compliance evidence, architecture reviews) |
| `rate(4 hours)` | Near-real-time operational issues (failures, deployments) |
| `rate(6 hours)` | Frequent but not urgent (anomaly detection, predictions) |

---

## Tool Selection Guide

| Agent Focus | Required Tools |
|-------------|---------------|
| Resource inventory and config | `use_aws` |
| Performance and metrics | `use_aws`, `query_cloudwatch_metrics` |
| Log analysis | `use_aws`, `query_cloudwatch_logs` |
| Incident correlation | `use_aws`, `list_investigations` |
| Alarm analysis | `use_aws`, `list_cloudwatch_alarms` |
| Full operational | `use_aws`, `query_cloudwatch_metrics`, `query_cloudwatch_logs`, `list_investigations` |
| Kubernetes | `use_aws`, `use_kubectl` |

---

## Naming Conventions

- Agent folder: `XX-descriptive-name` (two-digit number, lowercase, hyphens)
- Agent name (in config): `descriptive-name` (lowercase, hyphens, max 64 chars)
- No abbreviations unless universally understood (ECS, RDS, IAM are fine; "cfg" or "mgmt" are not)
- Name describes what it does, not how: `rds-connection-pool-monitor` not `rds-metric-checker`

---

## Remaining Agents (51-80) Specifications

These agents have been designed but not yet created. Use the template above to build them.

### Batch 2 (51-60)

| # | Name | Purpose | Tools | Schedule |
|---|------|---------|-------|----------|
| 51 | dynamodb-capacity-throttle-monitor | Monitor DynamoDB consumed vs provisioned capacity, detect throttling, recommend on-demand vs provisioned | use_aws, query_cloudwatch_metrics | Daily |
| 52 | ebs-performance-bottleneck-detector | Detect EBS volumes hitting IOPS/throughput limits causing application latency | use_aws, query_cloudwatch_metrics | Daily |
| 53 | cloudformation-stack-health-checker | Find stacks in failed/rollback states, drift detected, stuck updates | use_aws | Daily |
| 54 | route53-health-check-validator | Audit Route53 health checks for misconfiguration, failing checks, and DNS failover readiness | use_aws, query_cloudwatch_metrics | Every 6h |
| 55 | kms-key-usage-rotation-auditor | Audit KMS keys for rotation status, unused keys, overly broad policies, and pending deletion | use_aws | Weekly Mon |
| 56 | ecr-repository-governance | Enforce ECR lifecycle policies, image scanning, tag immutability, and repository cleanup | use_aws | Weekly Mon |
| 57 | ssm-patch-baseline-drift-detector | Detect instances drifting from approved patch baselines after manual changes or missed windows | use_aws | Weekly Mon |
| 58 | aws-backup-job-failure-investigator | Investigate failed backup jobs, identify unprotected resources, and track backup SLA compliance | use_aws | Daily |
| 59 | cloudwatch-contributor-insights-reporter | Analyze top contributors to metrics (top IPs, top endpoints, top error sources) using Contributor Insights | use_aws, query_cloudwatch_metrics | Daily |
| 60 | elasticache-cluster-health-monitor | Monitor ElastiCache for memory pressure, evictions, replication lag, and connection saturation | use_aws, query_cloudwatch_metrics | Daily |

### Batch 3 (61-70)

| # | Name | Purpose | Tools | Schedule |
|---|------|---------|-------|----------|
| 61 | savings-plan-utilization-tracker | Track Savings Plan utilization, coverage gaps, and expiring commitments | use_aws | Weekly Mon |
| 62 | multi-region-latency-comparator | Compare application latency across regions, identify regional degradation | use_aws, query_cloudwatch_metrics | Daily |
| 63 | guardduty-finding-trend-reporter | Track GuardDuty finding trends over time, identify spikes and recurring patterns | use_aws | Weekly Mon |
| 64 | load-balancer-ssl-policy-auditor | Audit ALB/NLB/CloudFront TLS policies for deprecated protocols and weak ciphers | use_aws | Weekly Wed |
| 65 | auto-scaling-launch-failure-investigator | Investigate ASG launch failures (capacity, AMI, subnet, SG issues) | use_aws, query_cloudwatch_metrics | Every 4h |
| 66 | ecs-capacity-provider-optimizer | Optimize ECS capacity provider strategies for cost and availability balance | use_aws, query_cloudwatch_metrics | Weekly Mon |
| 67 | kinesis-shard-utilization-monitor | Monitor Kinesis shard throughput, detect hot shards and consumer lag | use_aws, query_cloudwatch_metrics | Every 6h |
| 68 | codebuild-cost-duration-optimizer | Identify slow/expensive CodeBuild projects and recommend compute type optimizations | use_aws, query_cloudwatch_metrics | Weekly Mon |
| 69 | vpc-cidr-capacity-planner | Track IP address consumption per subnet and forecast CIDR exhaustion | use_aws | Weekly Mon |
| 70 | iam-policy-simulator-validator | Validate that IAM policies produce expected allow/deny results for critical actions | use_aws | Weekly Wed |

### Batch 4 (71-80)

| # | Name | Purpose | Tools | Schedule |
|---|------|---------|-------|----------|
| 71 | cloudwatch-log-insights-query-library | Maintain and execute a library of diagnostic queries, surfacing insights proactively | use_aws, query_cloudwatch_logs | Daily |
| 72 | terraform-state-drift-reporter | Detect drift between Terraform state and actual AWS resources across accounts | use_aws | Weekly Mon |
| 73 | service-health-dashboard-generator | Generate a consolidated service health dashboard artifact from all monitoring data | use_aws, query_cloudwatch_metrics, list_investigations, list_cloudwatch_alarms | Daily |
| 74 | resource-lifecycle-compliance-checker | Verify resources follow defined lifecycle stages (dev to staging to prod) with proper approvals | use_aws | Weekly Mon |
| 75 | cross-region-data-transfer-auditor | Identify and quantify unexpected cross-region data transfer costs | use_aws, query_cloudwatch_metrics | Weekly Mon |
| 76 | container-runtime-security-monitor | Monitor container runtime behavior for anomalies (privilege escalation, unexpected processes) | use_aws, query_cloudwatch_logs | Every 6h |
| 77 | incident-frequency-trend-analyzer | Analyze incident patterns over 30/60/90 days to identify systemic reliability improvements or regressions | use_aws, list_investigations | Weekly Mon |
| 78 | api-throttling-pattern-reporter | Track API throttling across all AWS service calls to identify clients causing rate limit issues | use_aws, query_cloudwatch_logs | Daily |
| 79 | infrastructure-age-eol-tracker | Track infrastructure components approaching end-of-life (runtimes, AMIs, engines, instance types) | use_aws | Weekly Mon |
| 80 | monthly-cost-allocation-report | Generate a monthly cost breakdown by team, service, and environment with trend analysis | use_aws | Monthly 1st |

---

## Guardrails (required for every agent)

These guardrails implement the repository [Security and Guardrails Framework](SECURITY.md). They are already reflected in the Exception Handling, Data Validation, Constraints, and Output sections above. Use this checklist and the reusable prompt block below when authoring or reviewing an agent.

### Anti-hallucination

- [ ] Every finding cites the specific metric, API response, or configuration value that supports it.
- [ ] Observations and inferences are separated; interpretations are labeled as hypotheses, not facts.
- [ ] No invented resource names, ARNs, metric values, account IDs, or thresholds. If a value was not retrieved, the report says so.
- [ ] Missing or empty metric data is treated as unknown, not as zero or healthy.
- [ ] Trend claims require a minimum data window; no extrapolation from a single point.
- [ ] Low confidence or incomplete data lowers the stated severity rather than overstating certainty.

### Safe recommendations

- [ ] Recommendations name the specific action on the specific resource, never a wildcard or blanket grant.
- [ ] Recommendations never include a Prohibited Action from SECURITY.md (no `Action: *`, no disabling Block Public Access, no `0.0.0.0/0` inbound, no disabling logging, and so on).
- [ ] Each recommendation carries a safety rating: GREEN (read-only), YELLOW (recoverable state change), or RED (destructive).
- [ ] YELLOW and RED recommendations are presented for human approval, never as something to run automatically.
- [ ] Recommendations that touch IAM in production, security controls, KMS key policies, `aws-auth`, SCPs, CloudTrail, or encryption are flagged for explicit human review (escalation).

### Data sensitivity

- [ ] HIGH sensitivity values (full IAM/KMS policies, account IDs, IPs, SG/NACL rules, credentials, findings with threat indicators, CloudTrail user identities) are referenced by identifier, not reproduced verbatim.
- [ ] MEDIUM sensitivity values (ARNs, VPC/subnet config, parameter groups, quotas) are summarized, not dumped in full.
- [ ] No credentials, tokens, connection strings, or full account IDs appear in output.

### Reusable prompt block

Add or adapt this block near the Constraints section of a new agent to make the guardrails explicit in the system prompt:

```markdown
## Guardrails

- This agent is read-only. It never creates, modifies, or deletes resources, and it never recommends a prohibited action (no wildcard IAM, no disabling Block Public Access, no 0.0.0.0/0 inbound, no disabling logging or encryption). See SECURITY.md.
- Ground every finding in a specific observed value. If a value was not retrieved, say so. Do not invent resource names, metrics, or thresholds.
- Label interpretations as hypotheses, not facts. When data is incomplete, lower the severity and note the gap rather than overstating certainty.
- Each recommendation names the specific resource and the specific fix, carries a safety rating (GREEN, YELLOW, or RED), and flags YELLOW or RED actions for human approval.
- Reference HIGH sensitivity data (IAM and KMS policies, account IDs, IP addresses, security group and NACL rules, credentials, threat-indicator findings) by identifier only. Never reproduce it verbatim or expose credentials.
```

---

## Recommendation handoff (optional structured output)

In addition to the human-readable report, an agent may emit machine-readable recommendation records so a downstream remediation-orchestrator agent (or an approval workflow) can consume them. This is optional; agents that only produce a narrative report remain valid.

When an agent emits records, it appends a single fenced JSON block at the end of the report, after the "Issues Encountered" section, containing an array of records that conform to [schemas/recommendation.schema.json](schemas/recommendation.schema.json).

Rules for producing records:

- Emitting a record never executes anything. The producing agent is read-only and only proposes.
- Every record cites at least one evidence item (the observed metric, API response, or configuration value).
- Every record carries a `safetyRating` (GREEN, YELLOW, or RED). Set `requiresApproval` to true for YELLOW and RED.
- Set `escalationRequired` to true when the change touches IAM in production, a security control, a KMS key policy, aws-auth, an SCP, CloudTrail, encryption, or has a blast radius beyond a single account or region.
- Run the proposed action against the SECURITY.md prohibited actions list and set `prohibitedActionCheck`. If the only fix would be a prohibited action, set it to `failed`, propose the scoped alternative in `proposedAction.summary`, and keep `requiresApproval` true.
- Provide a `rollback` for any change that is not read-only.
- Reference resources by identifier. Do not embed credentials or full policy documents.

To add this to a system prompt, extend the Output section with:

```markdown
After the "Issues Encountered" section, also emit a fenced JSON block labeled "recommendations" containing an array of records that conform to schemas/recommendation.schema.json. One record per actionable finding. Each record must include evidence, a safety rating, requiresApproval (true for YELLOW and RED), escalationRequired, prohibitedActionCheck, and a rollback for any non-read-only change. Do not execute anything; these records are proposals for human approval or for the remediation-orchestrator agent.
```

### Example record

```json
{
  "recommendations": [
    {
      "schemaVersion": "1.0.0",
      "id": "ebs-snapshot-orphan-2026-08-14-snap-0abc123",
      "producedBy": "ebs-snapshot-cost-and-orphan-auditor",
      "producedAt": "2026-08-14T06:20:00Z",
      "title": "Delete orphaned EBS snapshot snap-0abc123 with no source volume",
      "finding": "Snapshot snap-0abc123 references a volume that no longer exists and is not referenced by any AMI. It is 210 days old and accrues storage cost with no recovery value.",
      "evidence": [
        { "source": "ec2 DescribeSnapshots", "value": "snap-0abc123 StartTime 210 days ago, VolumeId vol-0dead references a deleted volume", "observedAt": "2026-08-14T06:19:00Z" },
        { "source": "ec2 DescribeImages", "value": "no AMI references snap-0abc123" }
      ],
      "target": { "service": "ec2", "resourceId": "snap-0abc123", "region": "us-east-1" },
      "proposedAction": {
        "summary": "Delete EBS snapshot snap-0abc123 after confirming it is not part of a retention policy.",
        "changeType": "resource-cleanup",
        "implementation": { "type": "aws-cli", "content": "aws ec2 delete-snapshot --snapshot-id snap-0abc123" },
        "rollback": "Snapshot deletion is not reversible. Before deletion, optionally copy the snapshot to an archive vault; if the data is later needed and no copy exists, it cannot be recovered."
      },
      "safetyRating": "RED",
      "reversible": false,
      "requiresApproval": true,
      "escalationRequired": false,
      "prohibitedActionCheck": "passed",
      "blastRadius": "single-resource",
      "severity": "low",
      "effort": "quick-win",
      "estimatedMonthlySavingsUsd": 4.20,
      "confidence": "high",
      "owner": "platform-storage",
      "notes": "Snapshot deletion is irreversible, so this is rated RED and requires approval despite the low cost."
    }
  ]
}
```
