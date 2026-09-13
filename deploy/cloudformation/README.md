# Deploy with AWS CloudFormation

Model skills, custom agents, and triggers as `AWS::DevOpsAgent::Asset` and
`AWS::DevOpsAgent::Trigger` resources. This gives you declarative,
version-controlled, repeatable deploys through a pipeline. It is also the only
IaC path that creates schedule triggers (they are not part of the Asset API).

[`agent-stack.yaml`](agent-stack.yaml) is a self-contained example: one skill,
one custom agent that uses it, and a daily trigger for the agent.

---

## Deploy

```bash
aws cloudformation deploy \
  --template-file agent-stack.yaml \
  --stack-name devops-agent-sample \
  --parameter-overrides AgentSpaceId=8f6187a7-0388-4926-8217-3a0fe32f757c \
  --region us-east-1
```

Deploy into a Region where AWS DevOps Agent is offered. The calling principal
needs `aidevops:` permissions on the Agent Space (see
[../aws-cli/README.md](../aws-cli/README.md#iam-permissions)).

---

## How the resources map

| Resource | Purpose | Key properties |
|----------|---------|----------------|
| `AWS::DevOpsAgent::Asset` (`AssetType: skill`) | A skill | `Metadata.agent_types`, `Files` (inline `SKILL.md`) |
| `AWS::DevOpsAgent::Asset` (`AssetType: custom_agent`) | A custom agent | `Metadata.name`, `tools`, `skills`; `Files` (inline `AGENT.md` system prompt) |
| `AWS::DevOpsAgent::Trigger` | A scheduled run | `Type: TIME_BASED`, `Condition.Schedule.Expression`, `Action.task.agent: custom:<assetId>` |

Notes reflected in the template:

- **Agent-type enum.** `Metadata.agent_types` uses the uppercase API enum, not
  the Console label. The example maps the skill's `Evaluation` label to
  `PREVENTION`. See the mapping table in
  [../README.md](../README.md#two-things-that-trip-people-up).
- **Skill references are by name.** A custom agent's `skills` list references
  skills by their `name` metadata, so use `DependsOn` to create the skill first.
- **Trigger wiring.** The trigger's `Action.task.agent` is `custom:<assetId>`,
  built with `Fn::GetAtt` on the agent's `AssetId` so CloudFormation orders the
  two resources and keeps them linked.
- **Create-only fields.** `AgentSpaceId` and `AssetType` are create-only;
  changing either replaces the asset. `Metadata` and `Files` update in place.
  `Status` on the trigger updates in place (set `Inactive` to pause).

---

## Skill content: inline vs GitHub import

This template embeds `SKILL.md` inline so it is self-contained. If you would
rather manage skills from this repo on GitHub with a sync link, import them with
the repository `sourceUrl` content type - that is API-only (CLI or SDK), not a
CloudFormation property. A common pattern is: import the 145 skills once with
the [Bash](../bash/README.md) or [AWS CLI](../aws-cli/README.md) option, then
manage only the custom agents and triggers in CloudFormation, referencing the
imported skills by name.

---

## Scaling to the full repository

The example creates a single agent. To manage more, add another
`AWS::DevOpsAgent::Asset` block per skill and per agent (copy the `SKILL.md` /
`system-prompt.md` text into `ContentText`), and one `AWS::DevOpsAgent::Trigger`
per agent using the `expression` from that agent's `agent-config.json`. For 227
agents, generate the template programmatically from the repo files rather than
by hand, or use the [CDK](../cdk/README.md) option, which builds the same
resources in TypeScript from the repository files directly.
