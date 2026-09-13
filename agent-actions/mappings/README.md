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

Core AWS domains:

- [security.md](security.md) - security group scoping, IMDSv2, S3 protection,
  flow logs, GuardDuty, KMS rotation, TLS policy.
- [cost.md](cost.md) - idle resource tagging, lifecycle tiering, log retention,
  right-sizing capacity.
- [reliability.md](reliability.md) - autoscaling, Lambda concurrency, DynamoDB
  capacity and PITR, backup settings.
- [observability.md](observability.md) - alarm configuration, anomaly detectors,
  log retention, metric hygiene.

Service-category domains:

- [contact-center.md](contact-center.md) - Amazon Connect flows, routing
  profiles, phone number association, Lambda association, recording encryption.
- [iot.md](iot.md) - IoT Core policy scoping and quotas, certificate lifecycle,
  Greengrass deployments, FleetWise campaigns (with the rules-engine PassRole
  refusal).
- [media.md](media.md) - Elemental MediaLive channel restart, MediaConvert queue,
  MediaPackage and MediaTailor config (with live-broadcast blast radius).
- [messaging-deliverability.md](messaging-deliverability.md) - SES suppression,
  DKIM, sending options and quota, Pinpoint channels and campaigns, Chime SDK
  quota (with the reputation-is-a-process caveat).
- [purpose-built-databases.md](purpose-built-databases.md) - DocumentDB, Neptune,
  Timestream, MemoryDB, Keyspaces sizing, capacity, and failover.

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
