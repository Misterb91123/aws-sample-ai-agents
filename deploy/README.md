# Deployment options

This folder collects the ways to deploy the custom agents and skills in this
repository to AWS DevOps Agent. Pick the option that matches how you work.

**New here? Start with [QUICKSTART.md](QUICKSTART.md)** for a clean, ordered,
step-by-step walkthrough from clone to a running agent.

| Option | Folder | Best for | Automatable |
|--------|--------|----------|-------------|
| AWS Console (web app) | [console/](console/) | First-time setup, a few assets, guided tool assignment | No |
| AWS CLI | [aws-cli/](aws-cli/) | Scripted one-off creates, trying the Asset API | Yes |
| Bash | [bash/](bash/) | End-to-end bulk deploy from the terminal | Yes |
| AWS CloudFormation | [cloudformation/](cloudformation/) | Declarative IaC, pipelines, repeatable environments | Yes |
| AWS CDK | [cdk/](cdk/) | IaC in TypeScript alongside application infrastructure | Yes |
| Terraform | [terraform/](terraform/) | IaC for Terraform-standardized teams | Yes |
| AI assistants | [ai-assistants/](ai-assistants/) | Having Kiro, Cursor, Amazon Q, Claude, or Codex drive the deploy, or reusing the skills inside those tools | Yes |

Every option produces the same result: `skill` and `custom_agent` assets (and
optionally `Trigger` resources) in your Agent Space. The main repository
[DEPLOYMENT.md](../DEPLOYMENT.md) covers the Console flow in the most detail;
the IaC and CLI options here use the Asset API.

---

## The asset model

AWS DevOps Agent stores skills and custom agents as **assets** in an Agent
Space. You manage them three ways, all of which create the same underlying
resource:

- **Operator Web App (Console)** - interactive, one asset at a time.
- **Asset API** - `aws devops-agent create-asset` (CLI), the `devops-agent`
  Boto3 client (Python), used by the Bash and AWS CLI options here.
- **CloudFormation** - the `AWS::DevOpsAgent::Asset` and
  `AWS::DevOpsAgent::Trigger` resource types, used by the CloudFormation, CDK,
  and Terraform options here.

A **skill** asset is a `SKILL.md` (plus optional `references/` and `assets/`).
A **custom_agent** asset is a system prompt plus a curated list of `tools`,
`skills`, and `memory_stores`. A **Trigger** runs a custom agent on a schedule.

---

## Two things that trip people up

**1. Agent import reads only the system prompt.** When you import an agent from
GitHub through the Console, the service ingests a single `.md` file as the
system prompt and does not read `agent-config.json`. Tools, skills, and the
trigger are applied separately. The Asset API and IaC options in this folder
apply all of them together, which is why they are better for repeatable deploys.

**2. Agent-type values differ between the skill files and the API.** The
`SKILL.md` files in this repo use human-readable `agent_type` values that match
the Console labels (for example `Incident RCA`). The Asset API and
CloudFormation expect an uppercase `agent_types` **array** enum. Map them as
follows when you set agent types programmatically:

| SKILL.md `agent_type` (Console label) | API / CloudFormation `agent_types` value |
|----------------------------------------|------------------------------------------|
| Generic | `GENERIC` |
| On-demand | `CHAT` |
| Incident Triage | `INCIDENT_TRIAGE` |
| Incident RCA | `INCIDENT_RCA` |
| Incident Mitigation | `INCIDENT_MITIGATION` |
| Incident UI | `INCIDENT_UI` |
| Evaluation | `PREVENTION` |
| Release testing | `RELEASE_TESTING` |

`GENERIC` makes a skill available to all agent types and cannot be combined with
other values. When you import a skill from GitHub, the service reads `name` and
`description` from the `SKILL.md` frontmatter automatically; you only supply
`agent_types` in the request metadata.

---

## Prerequisites (all options)

- An AWS DevOps Agent **Agent Space**. Note its **Agent Space ID** (a UUID); the
  CLI and IaC options take it as input.
- The AWS accounts you want the agents to analyze **connected** to the Agent
  Space, with read-only IAM permissions on the analyzed services. A scoped
  starting policy is at [../policies/agent-readonly-policy.json](../policies/agent-readonly-policy.json).
- For the API and IaC options: IAM permissions in the `aidevops:` namespace
  (`CreateAsset`, `UpdateAsset`, `ListAssets`, and so on) on your Agent Space.
  See the example policies in
  [aws-cli/README.md](aws-cli/README.md#iam-permissions).
- For GitHub import (Console, and the `sourceUrl` path in Bash/CLI): a GitHub
  account connected to the Agent Space, and this repository pushed to GitHub.
- The MCP tools the agents use available in your Agent Space: `use_aws`,
  `query_cloudwatch_metrics`, `query_cloudwatch_logs`, `list_cloudwatch_alarms`,
  `list_investigations`, and `use_kubectl` (EKS agents only).

Regions: `AWS::DevOpsAgent::Asset` and `AWS::DevOpsAgent::Trigger` are available
only in the Regions where AWS DevOps Agent is offered. Deploy into one of those
Regions.

---

## Which skill source to use

The skill assets can be created two ways, and the options here support both:

- **Import from GitHub (`sourceUrl`)** - the service fetches the skill directory
  from this repo on GitHub and keeps a sync link. Recommended when the repo is
  on GitHub. Used by the Console option and available in Bash/CLI.
- **Inline content** - the `SKILL.md` text is embedded directly in the request
  or template. Works without GitHub. Used by the CloudFormation, CDK, and
  Terraform examples so the templates are self-contained.

---

## Safety

Every agent here is read-only and never modifies resources. The IaC templates
create only DevOps Agent assets and triggers; they do not grant the agents any
write permissions. Review [../SECURITY.md](../SECURITY.md) before deploying.
