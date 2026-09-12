---
name: config-conformance-drift-remediation
agent_type: "Evaluation"
description: Use this skill to remediate AWS Config conformance pack noncompliance and rule drift. It reads conformance pack compliance scores and rule-level detail to find failing controls, prioritizes critical and long-standing drift, and recommends remediation actions to restore compliance.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Config Conformance Drift Remediation

This skill evaluates AWS Config conformance packs and rules to surface noncompliant controls and configuration drift, then drives the highest-risk findings back into compliance.

## When to Activate

- A conformance pack compliance score falls below 90%.
- Any control mapped as critical is NON_COMPLIANT.
- Drift on a resource has persisted more than 7 days without remediation.
- A new conformance pack was deployed and needs a baseline compliance pass.
- DescribeComplianceByConfigRule reports rules flipping between compliant and noncompliant.

## Step 1: Score the Conformance Packs

- Call Config DescribeConformancePackCompliance and DescribeConformancePackStatus to read each pack and its compliance summary.
- Compute the compliance score as compliant rules divided by total rules per pack.
- Flag packs scoring below 90% for detailed review.

## Step 2: Drill Into Failing Rules

- Call GetConformancePackComplianceDetails to list the specific NON_COMPLIANT rules within each low-scoring pack.
- Call DescribeComplianceByConfigRule and GetComplianceDetailsByConfigRule to enumerate the noncompliant resource IDs per rule.
- Tag rules mapped to critical controls (encryption, public access, IAM) as highest priority.

## Step 3: Measure Drift Duration

- For each noncompliant resource, read the ConfigRuleInvokedTime and the resource's ResultRecordedTime to estimate how long the resource has been out of compliance.
- Flag DRIFT_PERSISTENT when noncompliance has lasted more than 7 days.
- Distinguish newly noncompliant resources from chronic offenders.

## Step 4: Plan Remediation

- For rules with an SSM Automation remediation, review the RemediationConfiguration and confirm the document and target parameters.
- For manual controls, define the specific fix per resource (enable encryption, remove public access, attach the required policy).
- Group remediations by control type so a single automation can fix many resources.

## Step 5: Execute and Verify

- Trigger remediation via StartRemediationExecution or apply the manual fix per resource.
- Re-evaluate the rule with StartConfigRulesEvaluation and confirm the resource returns to COMPLIANT.
- Re-read DescribeConformancePackCompliance to confirm the pack score returns to 90% or above.

## Output

The skill produces a titled "Config Conformance Drift Remediation Report" listing each conformance pack with its compliance score, the noncompliant rules and affected resource counts, which controls are critical, and how long each drift has persisted. It concludes with a prioritized remediation list ordered by control criticality and drift age, such as auto-remediating critical controls via SSM Automation, fixing persistent drift older than 7 days, resolving flapping rules, and re-evaluating to confirm each pack clears the 90% threshold.