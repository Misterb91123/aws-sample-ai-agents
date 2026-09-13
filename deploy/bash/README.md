# Deploy with Bash

[`deploy.sh`](deploy.sh) deploys the skills and custom agents end-to-end from
the terminal using the Asset API. Skills are imported from GitHub (keeping a
sync link); custom agents are created with their system prompt inline and their
tools and skills attached from each `agent-config.json`.

Use this for a full or partial bulk deploy from a shell. For declarative,
pipeline-driven deploys, use the [CloudFormation](../cloudformation/README.md),
[CDK](../cdk/README.md), or [Terraform](../terraform/README.md) options instead.

---

## Requirements

- `bash`, AWS CLI v2 with the `devops-agent` service, `jq`, and `python3`.
- IAM permissions in the `aidevops:` namespace on your Agent Space (see
  [../aws-cli/README.md](../aws-cli/README.md#iam-permissions)).
- This repository pushed to GitHub, and a GitHub account connected to the Agent
  Space (required for the skill `sourceUrl` import).

---

## Usage

```bash
export AGENT_SPACE_ID=8f6187a7-0388-4926-8217-3a0fe32f757c
export AWS_REGION=us-east-1
export REPO_BASE=https://github.com/YOUR-ORG/YOUR-REPO/tree/main

# see exactly what it would do without calling AWS
./deploy.sh --dry-run

# deploy everything
./deploy.sh

# skills only, or agents only
./deploy.sh --skills-only
./deploy.sh --agents-only

# a subset of agents by directory prefix or name fragment
./deploy.sh --agents 01 02 cost
```

Run `chmod +x deploy.sh` first if needed.

---

## What it does

1. **Skills** - walks `skills/**/SKILL.md`, reads the `agent_type` from each
   file's frontmatter, maps it to the API enum (for example `Incident RCA` ->
   `INCIDENT_RCA`), and calls `create-asset` with a `sourceUrl` pointing at the
   skill directory on GitHub.
2. **Agents** - for each `agents/*/agent-config.json`, builds the `custom_agent`
   metadata (`name`, `tools`, `skills`) and passes the matching
   `system-prompt.md` as inline content via `scripts/_asset_content.py`.

## Notes and limits

- **Order matters.** Deploy skills before agents so the `skills` an agent
  references already exist. `./deploy.sh` (no flags) does skills first.
- **Idempotency.** The script creates assets; it does not reconcile existing
  ones. Re-running creates duplicates. For repeatable, idempotent deploys use an
  IaC option. To update an existing asset, use `aws devops-agent update-asset`
  (see [../aws-cli/README.md](../aws-cli/README.md)).
- **Triggers** are not part of the Asset API. Set schedules in the Console or
  use the CloudFormation `AWS::DevOpsAgent::Trigger` resource. Each agent's
  recommended expression is in its `agent-config.json`.
- Always run `--dry-run` first to review the calls.
