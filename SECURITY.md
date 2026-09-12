# Security and Guardrails Framework

This document defines the security, anti-hallucination, and operational guardrails for the custom agents and skills in this repository. It adapts the framework published by AWS in [aws-samples/sample-ai-agent-skills SECURITY.md](https://github.com/aws-samples/sample-ai-agent-skills/blob/main/SECURITY.md) to the design of this collection. Content was rephrased and extended for this repository's read-only monitoring and audit agents.

---

## How this collection differs from the risk baseline

The agents in this repository are designed to be read-only. They call describe, get, and list style APIs and CloudWatch reads, then produce reports and recommendations. They do not create, modify, or delete resources. This removes most direct execution risk, but two categories of risk remain and are the focus of this framework:

1. The agent still tells a human what to do. A hallucinated finding or an over-broad recommendation can lead an operator to take a dangerous action by hand.
2. The agent reads sensitive configuration (IAM policies, key policies, network rules, findings) and can leak it into a stored report.

Skills in this repository contain no executable code. They are markdown instructions that influence how the agent reasons:

```
Skill content (markdown/yaml) -> AI agent (interprets) -> Cloud APIs (reads)
```

There is no checksum verification, signing, or tamper detection on agent or skill files in this repository. Organizations deploying these assets in production should add their own integrity verification (see Production Deployment Recommendations).

---

## Threat model

| Risk | Description | Mitigation in this repository |
|------|-------------|-------------------------------|
| Tampered agent or skill file | A modified file could steer the agent toward recommending destructive actions or exfiltrating data | Store in version control, review pull requests, add file integrity monitoring in production |
| Over-broad recommendation | The agent recommends "grant access" and an operator reads that as a wildcard policy | Prohibited Actions list; recommendations must name the specific action and resource |
| Diagnostic hallucination | The agent reports a finding that the data does not support | Data Validation sections in every agent; anti-hallucination rules below |
| Sensitive data exposure | Reports include IAM policies, account IDs, key policies, network rules, or findings | Data Sensitivity Classifications; Constraints forbid exposing secrets and credentials |
| Scope creep beyond read-only | A future contribution adds a write action | Read-only constraint in every agent; contribution review |
| Privilege over-provisioning | The agent runs with more IAM permission than it needs | Least-privilege execution role guidance below |

---

## Prohibited recommendations (global)

Because these agents produce recommendations rather than execute changes, the rule is that the agent MUST NEVER recommend the following as a fix. Every agent's Constraints section should treat these as forbidden output:

### IAM
- Never recommend `"Action": "*"` or `"Resource": "*"` in an IAM policy fix.
- Never recommend `"Effect": "Allow", "Action": "*", "Resource": "*"`.
- Never recommend granting `AdministratorAccess` to resolve a permission issue.
- Never recommend removing a permission boundary to fix an access denied error.

### S3
- Never recommend disabling S3 Block Public Access.
- Never recommend `"Principal": "*"` in a bucket policy without a restrictive `Condition`.
- Never recommend removing bucket encryption to fix an access issue.

### EKS
- Never recommend adding the `system:masters` group to `aws-auth` for troubleshooting.
- Never recommend disabling RBAC or Pod Security Standards.
- Never recommend running containers as root to fix a permission issue.

### KMS
- Never recommend `"kms:*"` on a key policy as a fix.
- Never recommend disabling key rotation.
- Never recommend making a KMS key policy public.

### Networking
- Never recommend `0.0.0.0/0` inbound on a security group as a fix.
- Never recommend disabling NACLs to troubleshoot connectivity.
- Never recommend removing all firewall rules to test connectivity.

### General
- Never recommend disabling logging, auditing, or monitoring as a troubleshooting step.
- Never recommend using root account credentials.
- Never recommend sharing access keys or credentials in any form.

When a legitimate use case appears to require one of these, the correct recommendation is a scoped alternative (a specific action on a specific resource, a specific exception with a condition) plus escalation to a human owner.

---

## Safety classification for recommended actions

Every recommendation an agent produces should carry a safety rating so the operator understands the blast radius before acting. The agents themselves only perform GREEN reads; the rating applies to the action the agent is recommending a human take.

| Rating | Meaning | Examples |
|--------|---------|----------|
| GREEN | Read-only, no state change | describe, get, list calls; kubectl get; reviewing a report |
| YELLOW | State-changing but recoverable | Modify a security group rule, update a parameter group, restart a service, set a lifecycle policy |
| RED | Destructive or hard to reverse | Delete a resource, terminate an instance, remove encryption, modify a KMS key policy, change CloudTrail |

Recommendations rated YELLOW or RED should be presented for human approval, never framed as something to run automatically.

---

## Escalation conditions

A recommendation should be flagged for explicit human review (stop and ask) when it would involve any of the following:

- Modifying IAM policies in a production account.
- Disabling a security control, even temporarily.
- Modifying KMS key policies.
- Editing the `aws-auth` ConfigMap in a production EKS cluster.
- Modifying Organizations service control policies.
- Changing CloudTrail or audit logging.
- Modifying encryption settings.
- Any action whose blast radius spans more than one account or region.
- Any action involving potential data loss or data exposure.

For diagnostic agents, also escalate rather than assert when the root cause cannot be established from the available data after reasonable analysis (see anti-hallucination rules).

---

## Anti-hallucination rules

These rules apply to every agent in this repository and are enforced through the Data Validation and Output sections of each system prompt.

1. Ground every finding in observed data. State the specific metric, API response, or configuration value that supports it. If there is no supporting data point, do not report the finding.
2. Separate observation from inference. Report what was measured, then label any interpretation as a hypothesis, not a fact.
3. Do not invent resource names, ARNs, metric values, account IDs, or thresholds. If a value was not retrieved, say it was not retrieved.
4. Guard every rate and percentage against a zero denominator before reporting it.
5. Treat missing or empty metric data as unknown, not as zero or as healthy. Verify the resource state (new, stopped, metrics not enabled) before drawing a conclusion.
6. Verify metric freshness. Flag any data point older than the staleness threshold (2 hours for current-state claims) rather than presenting it as current.
7. Flag impossible values (negative counts, utilization above 100 percent) as data quality issues rather than reporting them as findings.
8. Require a minimum data window before making a trend claim. Do not extrapolate a trend from a single data point.
9. When confidence is low or data is incomplete, say so explicitly and lower the severity rather than overstating certainty.
10. Every report includes an "Issues Encountered" section listing data gaps, API failures, and assumptions made, so a reader can judge completeness.

### Remediation hallucination patterns

Recommendation-side patterns to guard against:

- Trigger "access denied" -> dangerous suggestion "add `Action: *` to the policy" -> correct approach: identify the specific denied action from CloudTrail and recommend granting only that action on the specific resource.
- Trigger "blocked by a security control" -> dangerous suggestion "disable the control" -> correct approach: recommend a scoped exception for the legitimate use case while keeping the control active.
- Trigger "resource is throttling" -> dangerous suggestion "raise every limit to maximum" -> correct approach: recommend the specific limit and target value justified by the observed usage.

---

## Recommendation handoff and remediation

The monitoring and audit agents are read-only and cannot execute changes. To turn their findings into action safely, this repository uses a structured handoff rather than giving the monitoring agents write access.

### How the handoff works

1. A monitoring or audit agent emits recommendation records that conform to [schemas/recommendation.schema.json](schemas/recommendation.schema.json). Emitting a record executes nothing; it is a proposal.
2. Each record carries the evidence behind the finding, a safety rating (GREEN, YELLOW, RED), `requiresApproval`, `escalationRequired`, a `prohibitedActionCheck` result, and a `rollback` for any non-read-only change.
3. The [remediation-orchestrator agent](agents/227-remediation-orchestrator/) consumes those records, validates them against the schema, applies the safety gates, de-duplicates and groups them by owner and account, and produces a human-approval-ready change plan. The orchestrator is also read-only; it prepares changes, it does not apply them.
4. A human reviews and approves. Approval is always a human decision, including for GREEN records.

### Default posture (Option 1, human-in-the-loop)

In the default configuration there is no agent in this repository that can execute a change. The dangerous-action boundary is enforced two ways: no agent is granted a write tool, and the least-privilege execution policy grants only read actions. The orchestrator turns recommendations into an approval-ready plan and stops there.

### Handoff gates (always enforced by the orchestrator)

- Refuse any record where `prohibitedActionCheck` is `failed`. It never becomes actionable.
- Refuse any record that fails schema validation or cites no evidence.
- Require human approval for every YELLOW and RED record. Never auto-approve, including GREEN records.
- Require a documented `rollback` for any non-read-only change; without one the record is held as "needs rollback".
- Route escalation-required records (IAM in production, security controls, KMS key policies, aws-auth, SCPs, CloudTrail, encryption, or blast radius beyond one account or region) to senior human approval.
- Flag conflicting records (opposite changes to the same resource) for human decision rather than choosing.

### Optional execution (Option 2, opt-in, not enabled by default)

If you choose to let an agent actually apply approved changes, do not add write permissions to the monitoring agents or to the orchestrator in this repository. Instead, stand up a separate executor in your own environment with the following controls, all of which are your responsibility to configure:

- A dedicated execution role scoped to only the specific actions the approved change types require, never a wildcard, and never the prohibited actions in this document.
- A hard approval gate: the executor only acts on records that carry a recorded human approval, and never on RED records without senior approval.
- Auto-refusal of any record with `prohibitedActionCheck` failed or `requiresApproval` true but not yet approved.
- Mandatory pre-change snapshot, a verification step, and the record's `rollback` on failure.
- Full audit logging of every executed change and the approval that authorized it.
- Blast-radius limits: no cross-account or cross-region change without an additional explicit approval.

Option 2 materially increases risk. It is described here so the boundary is explicit; this repository intentionally does not ship an executor with write access.

---

## Data sensitivity classifications

Agents should classify what they include in stored reports.

### HIGH sensitivity (redact or reference by name, do not reproduce verbatim)
- Full IAM policies and KMS key policies
- Account IDs and organization structure
- IP addresses and network configurations
- Security group rules and NACL rules
- `aws-auth` ConfigMap contents
- API keys, tokens, and credentials
- GuardDuty and other findings that carry threat indicators
- CloudTrail events that include user identities

### MEDIUM sensitivity (summarize, do not reproduce in full)
- Resource ARNs
- VPC and subnet configurations
- Parameter group settings
- Service quotas and limits

### LOW sensitivity (safe to include)
- Resource status and health
- Aggregated CloudWatch metrics
- Error messages and status codes
- Non-security configuration settings

When a HIGH sensitivity value is needed to make a finding actionable, reference it by identifier (for example, the policy name or the security group ID) rather than pasting its full contents into the report.

---

## Integrity and versioning

- Agent and skill files should be changed only through reviewed pull requests.
- Consider adding a `version` and `last_updated` field to skill frontmatter to track which version was active during an investigation, for example:

```yaml
version: "1.0.0"
last_updated: "2026-08-14"
```

- In production, hash the agent and skill files and verify the hash before loading them, so a tampered file is detected before it can influence the agent.

---

## Production deployment recommendations

1. Integrity verification: hash all agent and skill files and verify before loading.
2. Access control: restrict who can create or modify agents and skills in your Agent Space.
3. Audit logging: log which agents run, which skills activate, and what API calls the agent makes.
4. Least privilege: run the agent with the minimum IAM permissions its tools require. For this read-only collection, that means describe, get, and list permissions plus CloudWatch read, and no write permissions. A scoped starting policy is provided at [policies/agent-readonly-policy.json](policies/agent-readonly-policy.json); review and trim it to the services you actually use before attaching it as the execution role. It grants only read actions (describe, get, list, and equivalent) and no create, modify, or delete permissions.
5. Approval gates: require human approval before any YELLOW or RED action a report recommends is carried out.
6. Output sanitization: redact HIGH sensitivity data from stored reports per the classifications above.
7. Version pinning: pin agent and skill versions and review changes before updating.
8. Testing: validate new agents and skills in a non-production account before deploying to production.

---

## Reporting a security issue

If you discover a security issue in these agents or skills (for example, an agent that could recommend a prohibited action, or a prompt that leaks sensitive data), do not open a public issue. Follow your organization's responsible disclosure process, or open a private report to the repository maintainers.

---

## Attribution

The structure of this framework (threat model, prohibited actions, safety classification, escalation conditions, data sensitivity classes, and production recommendations) is adapted from the AWS sample published at [aws-samples/sample-ai-agent-skills](https://github.com/aws-samples/sample-ai-agent-skills/blob/main/SECURITY.md). Content was rephrased and tailored to this repository's read-only monitoring and audit agents for compliance with licensing restrictions.
