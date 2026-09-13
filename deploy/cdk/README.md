# Deploy with AWS CDK

An AWS CDK app (TypeScript) that creates DevOps Agent `skill` and `custom_agent`
assets plus schedule triggers, reading the definitions directly from this
repository's `skills/` and `agents/` folders. Because it reads the repo files,
it scales to all 145 skills and 227 agents without hand-writing a template per
asset.

The resource types (`AWS::DevOpsAgent::Asset`, `AWS::DevOpsAgent::Trigger`) are
created with the CDK `CfnResource` escape hatch, so this works even without
dedicated L2 constructs.

---

## Layout

```
deploy/cdk/
  bin/app.ts                  CDK app entry point (reads agentSpaceId)
  lib/devops-agent-stack.ts   Builds skills, agents, and triggers from the repo
  package.json
  tsconfig.json
  cdk.json
```

---

## Prerequisites

- Node.js 18+ and the AWS CDK (`npm install -g aws-cdk`, or use the local
  devDependency).
- AWS credentials with `aidevops:` permissions on the Agent Space (see
  [../aws-cli/README.md](../aws-cli/README.md#iam-permissions)).
- A bootstrapped environment: `cdk bootstrap` (first time in an account/Region).
- Deploy into a Region where AWS DevOps Agent is offered.

---

## Deploy

```bash
cd deploy/cdk
npm install

# all skills and all agents
cdk deploy -c agentSpaceId=8f6187a7-0388-4926-8217-3a0fe32f757c

# a subset of agents (skills are always created)
cdk deploy -c agentSpaceId=8f6187a7-0388-4926-8217-3a0fe32f757c \
           -c agentDirs=01-infrastructure-health-report,02-cost-anomaly-detector
```

You can also set the Agent Space ID with `export DEVOPS_AGENT_SPACE_ID=...`.
Preview the generated CloudFormation without deploying:

```bash
cdk synth -c agentSpaceId=8f6187a7-0388-4926-8217-3a0fe32f757c
```

---

## What the stack does

- **Skills.** Walks `skills/**/SKILL.md`, reads each file's `agent_type`
  frontmatter, maps it to the API enum (for example `Incident RCA` ->
  `INCIDENT_RCA`), and creates a `skill` asset with the `SKILL.md` inline. The
  service reads `name` and `description` from the frontmatter.
- **Agents.** For each `agents/*/agent-config.json`, creates a `custom_agent`
  asset with `name`, `tools`, and `skills`, and the matching `system-prompt.md`
  inline. It adds a CDK dependency from the agent to each skill it references
  (skills are referenced by name), so ordering is correct.
- **Triggers.** If an agent's `agent-config.json` has a `trigger.expression`, it
  creates an `AWS::DevOpsAgent::Trigger` whose action targets the agent by
  `custom:<assetId>`.

---

## Notes

- **Run `npm install` then `cdk synth` first.** This verifies the app compiles
  and renders the CloudFormation before you deploy. The pinned versions in
  `package.json` are a known-good starting point; adjust to your toolchain.
- **New resource types.** `AWS::DevOpsAgent::Asset` and
  `AWS::DevOpsAgent::Trigger` are created via `CfnResource`, so no specific CDK
  version is required. They are available only in Regions where DevOps Agent is
  offered.
- **One stack, many resources.** Deploying all 227 agents plus 145 skills and
  triggers creates a large stack. Use `-c agentDirs=...` to deploy in batches,
  or split into multiple stacks, to stay within CloudFormation resource limits.
- **Idempotent and updatable.** Re-deploying updates assets in place. Changing
  `AgentSpaceId` or an asset's `AssetType` replaces the asset (create-only
  fields).
- **Skill source.** This app embeds `SKILL.md` inline. To manage skills from
  GitHub with a sync link instead, import them once with the
  [Bash](../bash/README.md) or [AWS CLI](../aws-cli/README.md) option and remove
  the skill creation from the stack, keeping only agents and triggers (which
  reference the imported skills by name).
