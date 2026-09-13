# Read-only finding to directed action mappings

These files connect the read-only findings the agents and skills in this
repository produce to the specific directed action that remediates each one. For
every finding, the mapping names:

- **Read-only finding** - what an existing agent or skill detects.
- **Source** - the agent(s) or skill(s) that produce the finding.
- **Directed action** - the exact mutating API operation (`service:Action`) that
  fixes it.
- **Guardrail status** - whether the agent can execute it (`allowed`) or refuses
  it (`refused-delete-class`, `refused-passrole`, `refused-prohibited-action`),
  in which case remediation stays a manual step.
- **Safety** - YELLOW (recoverable) or RED (hard to reverse); directed actions are
  never GREEN.
- **Rollback** - how to revert.

Every mapped directed action still requires per-action operator approval in chat
and executes under the elevated role (see [../iam/](../iam/)). A directed action
is one approvable operation on one resource, described by
[../directed-action.schema.json](../directed-action.schema.json).

## Files

- [security.md](security.md) - security group scoping, IMDSv2, S3 protection,
  flow logs, GuardDuty, KMS rotation, TLS policy.
- [cost.md](cost.md) - idle resource tagging, lifecycle tiering, log retention,
  right-sizing capacity.
- [reliability.md](reliability.md) - autoscaling, Lambda concurrency, DynamoDB
  capacity and PITR, backup settings.
- [observability.md](observability.md) - alarm configuration, anomaly detectors,
  log retention, metric hygiene.

## Reading the guardrail column

- **allowed** - passes the agent's service-side guardrails and this repository's
  prohibited actions. Can be proposed, approved, and executed.
- **refused-delete-class** - the fix would delete a resource. The agent refuses;
  a human performs the deletion with their own credentials.
- **refused-passrole** - the fix would pass an IAM role to a service. Refused by
  default; remains manual.
- **refused-prohibited-action** - the fix would be a prohibited action (wildcard
  IAM, disabling a control, opening 0.0.0.0/0). Never proposed. The correct
  directed action is always the scoped alternative, which is what these mappings
  list.

When the safe remediation is a delete (for example an orphaned snapshot), the
mapping shows the finding as `refused-delete-class` and the recommendation stays
a human action - consistent with the read-only, propose-not-delete posture of the
whole collection.
