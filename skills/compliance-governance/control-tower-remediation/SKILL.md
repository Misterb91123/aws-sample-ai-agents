---
name: control-tower-remediation
agent_type: "Evaluation"
description: Use this skill when remediating AWS Control Tower guardrail violations, landing zone drift, or non-compliant enrolled accounts. It triggers on Control Tower dashboard non-compliance findings, drift notifications, requests to enroll existing accounts, or Account Factory provisioning issues, and it guides detective versus preventive remediation and landing zone repair.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Control Tower Remediation

This skill remediates AWS Control Tower guardrail violations and landing zone drift. It distinguishes detective controls (which report non-compliance) from preventive controls (which block actions), then guides safe repair of resources, accounts, and the landing zone itself.

## When to Activate

- The Control Tower dashboard shows accounts or resources non-compliant with an enabled guardrail (control).
- Control Tower reports drift in the landing zone or in an enrolled account.
- An existing account outside Control Tower must be enrolled under governance.
- Account Factory provisioning fails or produces a partially configured account.
- A team needs to move an account between OUs while keeping controls applied.

## Step 1: Classify the control type

- Determine whether the failing control is preventive (implemented as an SCP that blocks the action), detective (implemented as an AWS Config rule that flags existing non-compliant resources), or proactive (implemented via CloudFormation hooks that block non-compliant resource creation).
- Detective control findings require remediating the existing resource. Preventive control denials require correcting the request or the requesting principal. Proactive control failures require fixing the resource template before deployment.
- Read the control's guidance (Mandatory, Strongly Recommended, or Elective) so remediation priority matches the control category.

## Step 2: Remediate non-compliant resources

- For a detective (Config rule) finding, identify the specific resource and property that is non-compliant using the linked AWS Config rule and its resource evaluation.
- Bring the resource into compliance (for example enable encryption, disable public access, add required logging). Where a Config remediation action is defined, trigger it; otherwise correct the resource directly in the owning account.
- Re-evaluate the Config rule and confirm the Control Tower dashboard returns the account to compliant on the next evaluation cycle.

## Step 3: Repair landing zone and account drift

- Landing zone drift occurs when a governed resource (for example an SCP, an OU, or a shared account setting) is changed outside Control Tower. Review the drift details in the Control Tower console.
- Resolve drift by using the Control Tower "Re-register OU" or "Repair" action, or by running a landing zone update, which reapplies the baseline. Do not hand-edit the Control Tower managed SCPs or the audit and log archive accounts.
- If an enrolled account drifted (for example its baseline CloudTrail or Config was altered), re-register the account through Control Tower to reapply the baseline rather than fixing it manually.

## Step 4: Keep the landing zone current

- Check the landing zone version. When AWS releases a new landing zone version, Control Tower reports that an update is available; running the update reapplies guardrails and baseline resources across enrolled accounts.
- Schedule landing zone updates during a maintenance window because the update touches every enrolled account and may briefly reconfigure baseline resources.

## Step 5: Enroll existing accounts

- To enroll an existing account, confirm prerequisites: the account is in the Organization, has the required Control Tower execution role (AWSControlTowerExecution), and has no conflicting CloudTrail or Config configuration that would collide with the baseline.
- Move the account into a registered OU or use the enrollment workflow. Control Tower then applies the OU's guardrails and baseline. Resolve any pre-existing resources (for example an existing organization-conflicting trail) before enrolling.

## Step 6: Handle Account Factory provisioning

- For failed Account Factory provisioning, review the provisioned product status in Service Catalog and the underlying CloudFormation stack events for the failure cause (commonly a service quota, an email already in use, or a networking baseline conflict).
- After fixing the root cause, update or re-provision the product. Do not manually create resources the factory is meant to own, since that produces drift.

## Output

Produce a Control Tower Remediation Report containing: each non-compliant finding classified as preventive, detective, or proactive, the specific resource or account and the exact non-compliant property, the remediation action taken or recommended, any landing zone or account drift with the repair method (repair, re-register, or landing zone update), enrollment prerequisites for any accounts being brought under governance, and the confirmation that the dashboard returns to compliant after re-evaluation. Flag any action that requires a maintenance window.