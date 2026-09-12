---
name: scp-guardrail-design
agent_type: "Generic"
description: Use this skill when designing Service Control Policy guardrails for an AWS Organization, including deny-based baselines, region restriction, protection of logging and security services, and root user restriction. It triggers on requests to establish preventive controls across accounts, design an OU structure for policy inheritance, or safely test SCP changes before broad rollout.
version: "1.0.0"
last_updated: "2026-08-14"
---

# SCP Guardrail Design

This skill designs Service Control Policy (SCP) guardrails that set the maximum available permissions for accounts in an AWS Organization. It favors deny-based baselines, protects security tooling, and provides a safe testing path before organization-wide enforcement.

## When to Activate

- An Organization needs preventive guardrails that no account, including administrators, can bypass.
- A team wants to restrict usage to approved regions.
- Logging or security services (CloudTrail, Config, GuardDuty, Security Hub) must be protected from tampering.
- Root user actions must be restricted across member accounts.
- An OU strategy is needed so policies inherit correctly.

## Step 1: Choose deny-list over allow-list

- Prefer deny-based guardrails attached alongside the AWS managed FullAWSAccess policy. Deny statements are simpler to reason about, do not silently break new services, and compose predictably with IAM.
- Reserve allow-list SCPs (removing FullAWSAccess and explicitly allowing services) for highly restricted OUs such as sandbox or regulated workloads, because allow-lists must be updated whenever a new required service appears.
- Remember SCPs never grant permissions; they only set a ceiling. An action is allowed only if permitted by both an SCP and an IAM policy.

## Step 2: Design region restriction

- Add a deny guardrail that blocks all actions outside approved regions using a condition on aws:RequestedRegion with a NotEquals list of allowed regions.
- Exclude global and region-agnostic services from the deny using the NotAction element (for example IAM, Organizations, Route 53, CloudFront, Support, and STS global endpoints) so control-plane operations do not break.
- Validate that no required workload operates in a region the guardrail would block before attaching.

## Step 3: Protect logging and security services

- Add a deny guardrail preventing member accounts from stopping, deleting, or reconfiguring the organization CloudTrail trail (deny cloudtrail:StopLogging, cloudtrail:DeleteTrail, cloudtrail:UpdateTrail on the org trail).
- Protect AWS Config (deny config:DeleteConfigurationRecorder, config:StopConfigurationRecorder, config:DeleteDeliveryChannel), GuardDuty (deny guardduty:DeleteDetector, guardduty:DisassociateFromMasterAccount), and Security Hub (deny securityhub:DisableSecurityHub).
- Where a dedicated automation role must manage these services, scope the deny with a condition that exempts that role's ARN via aws:PrincipalArn so protection does not block legitimate operations.

## Step 4: Restrict the root user

- Add a deny guardrail that blocks the member account root user from taking action using a condition on aws:PrincipalArn matching the account root, or deny sensitive actions when the principal is root.
- Combine with a guardrail that prevents members from leaving the Organization (deny organizations:LeaveOrganization) and from disabling required controls.

## Step 5: Structure the OU hierarchy

- Design OUs so guardrails inherit from the root down. Attach broad baseline guardrails at the root or a top-level OU and add stricter guardrails to child OUs (for example a Sandbox OU with tighter region and service limits, a Production OU protecting change windows).
- Keep the number of SCPs per entity within limits (an entity can have at most 5 SCPs attached, and each policy has a size limit), so consolidate related statements rather than attaching many small policies.
- Avoid attaching restrictive allow-lists at the root, since they affect every account including the management-adjacent accounts.

## Step 6: Test before enforcing

- Test new SCPs on a single non-critical account or a dedicated test OU first, not at the root.
- Use CloudTrail and IAM Access Analyzer to observe whether the guardrail denies any in-use actions. Where available, review access denied events during a soak period.
- Roll out progressively: test OU, then non-production OUs, then production. Keep each SCP statement documented with its intent so future edits do not reintroduce risk.

## Output

Produce an SCP Guardrail Design document containing: the chosen model (deny-list baseline with allow-list exceptions where justified), the specific guardrail statements for region restriction, logging and security protection, and root restriction with their exemption conditions, the OU hierarchy showing where each policy attaches and how it inherits, and a phased testing and rollout plan. Include a note on the SCP-per-entity and size limits and how the design stays within them.