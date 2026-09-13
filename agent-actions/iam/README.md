# Elevated role IAM for directed actions

For each AWS account where you want DevOps Agent to apply changes, register an
elevated role. The agent assumes this role to perform directed actions. Its
permission policy is the **ceiling** of what the agent can ever do in the
account; every directed action is additionally gated by operator approval and
scoped down to the approved operation at execution time.

This folder provides two files:

- [elevated-role-trust-policy.json](elevated-role-trust-policy.json) - who may
  assume the role (the DevOps Agent service principal, with confused-deputy
  protection).
- [elevated-role-permission-policy.json](elevated-role-permission-policy.json) -
  a scoped, least-privilege ceiling that matches the directed actions this
  repository maps in [../mappings/](../mappings/).

---

## Trust policy

Attach [elevated-role-trust-policy.json](elevated-role-trust-policy.json) as the
role's trust relationship. Replace `111122223333` with your account ID and
`us-east-1` with your agent space's Region (or use a Region wildcard
`arn:aws:aidevops:*:111122223333:agentspace/*` for multi-Region).

It must allow all three STS actions - `sts:AssumeRole`, `sts:SetSourceIdentity`,
and `sts:TagSession`. Omitting the latter two makes directed actions fail at
credential time even when the role validates. The `aws:SourceAccount` and
`aws:SourceArn` conditions prevent the confused-deputy problem by limiting the
role to your own agent spaces.

A recognizable name such as `DevOpsAgent-ElevatedAction-<scope>` makes elevated
roles easy to audit. The service does not require a specific name.

---

## Permission policy: two options

### Option 1 - AWS managed policy (broadest ceiling)

Attach `arn:aws:iam::aws:policy/AIDevOpsAgentActionsPolicy`. It grants all actions
on all resources **except** identity, credential, and organization management
services (`account:*`, `cognito-identity:*`, `iam:*`, `identitystore:*`,
`organizations:*`, `ram:*`, `rolesanywhere:*`, `sso:*`, `sts:*`), allowing back
only a few read-only actions from those. The ceiling includes delete-class
actions, but the agent refuses delete-class operations regardless. Effective
permission for any single action is narrowed at approval time.

Use this when you want the agent to be broadly capable and you rely on approval,
SCPs, and permissions boundaries to constrain it.

### Option 2 - scoped customer-managed policy (recommended for this repository)

Attach [elevated-role-permission-policy.json](elevated-role-permission-policy.json)
for a tighter ceiling aligned to the specific remediations this repository maps.
It permits only the mutating operations used by the mappings, grouped by intent:

| Statement | Enables remediation of |
|-----------|------------------------|
| NetworkRuleScoping | Overly broad security group rules (scope 0.0.0.0/0), IMDSv2 enforcement |
| TaggingAndCompliance | Tagging-compliance findings across services |
| StorageLifecycleAndProtection | S3 lifecycle, Block Public Access, default encryption, versioning |
| ObservabilityTuning | Alarm config, anomaly detectors, log retention |
| ScalingAndCapacity | Autoscaling, Lambda concurrency, DynamoDB capacity/PITR |
| SecurityControlEnablement | Enable VPC Flow Logs, GuardDuty, KMS key rotation |
| ReadContextForProposals | Read-only calls the agent needs to build a safe proposal |

Deliberately excluded from this ceiling, because the agent refuses them or this
repository prohibits them:

- No delete-class actions (agent refuses them anyway).
- No `iam:*` write, no permissions-boundary actions, no `sts:*` beyond assume.
- No operations requiring `iam:PassRole`.
- No disabling of logging, encryption, or Block Public Access.

Start from this and expand only as you add mapped remediations. Directed actions
the role does not permit fail at execution time even when an operator approves.

---

## Layer on additional controls

The elevated role is an ordinary IAM role in your account. You can further
constrain it with service control policies (SCPs) and a permissions boundary. A
permissions boundary on the elevated role is a strong control because the agent
refuses to modify permissions boundaries, so it cannot loosen its own limit.

---

## Validate and audit

- After registering the role (`agentElevatedRoleArn` on the association), confirm
  `agentElevatedRoleArnStatus` is `valid` (synchronous for the monitor account,
  asynchronous for source accounts - poll `GetAssociation`).
- Every directed action appears in CloudTrail with a source identity attributing
  it to the approving operator. Review these regularly.
