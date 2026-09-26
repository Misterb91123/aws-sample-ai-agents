# Deployment Guide

This guide provides step-by-step instructions for deploying the custom agents and skills in this repository to AWS DevOps Agent.

> **Disclaimer.** These agents and skills are samples provided for illustrative and educational purposes and are not intended for production use as-is. Before deploying any agent or acting on its output in production, perform your own due diligence: review the system prompt, tools, and IAM permissions each agent needs; validate it in a non-production account first; and confirm it meets your security, compliance, operational, and cost requirements. See the Disclaimer section in [README.md](README.md).

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Understanding the deployment model](#understanding-the-deployment-model)
3. [Deploying skills](#deploying-skills)
4. [Deploying agents](#deploying-agents)
5. [Deploying with an AI assistant (Claude, Kiro, Cursor, Amazon Q)](#deploying-with-an-ai-assistant-claude-kiro-cursor-amazon-q)
6. [Configuring triggers](#configuring-triggers)
7. [Assigning skills to agents](#assigning-skills-to-agents)
8. [Verifying deployment](#verifying-deployment)
9. [Bulk deployment](#bulk-deployment)
10. [Updating and maintenance](#updating-and-maintenance)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, confirm the following:

1. **Agent Space configured.** You have an AWS DevOps Agent Agent Space with at least one connected integration. See [Creating an Agent Space](https://docs.aws.amazon.com/devopsagent/latest/userguide/).

2. **Connected AWS accounts.** The AWS accounts you want the agents to analyze are connected to your Agent Space.

3. **Required MCP tools available.** Your Agent Space provides the tools the agents use. Confirm these are available:
   - `use_aws` (required by all agents)
   - `query_cloudwatch_metrics`
   - `query_cloudwatch_logs`
   - `list_cloudwatch_alarms`
   - `list_investigations`
   - `use_kubectl` (only for the EKS agents, agents 10 and 203)

4. **IAM permissions.** The role backing your Agent Space has read access to the services each agent analyzes. All agents are read-only, so read permissions are sufficient. A scoped least-privilege starting policy is provided at [policies/agent-readonly-policy.json](policies/agent-readonly-policy.json). Review it, trim it to the services you actually use, and attach it to the execution role. It grants only describe, get, and list style actions and no write permissions. Review each agent's system prompt for the specific APIs it calls.

5. **GitHub account connected (for skill import).** To import skills directly from this repository, connect a GitHub account to your Agent Space. See [Connecting GitHub](https://docs.aws.amazon.com/devopsagent/latest/userguide/). Any connected account works for public repositories. For private repositories, the account needs read access.

---

## Understanding the deployment model

AWS DevOps Agent is a managed service. There is no infrastructure to provision (no Lambda functions, no EC2 instances, no CloudFormation stacks). Agents and skills are configuration assets stored in your Agent Space.

- **Agents** are created through the DevOps Agent web app or the Asset API. Each agent consists of a system prompt, a set of assigned tools, and an optional trigger schedule.
- **Skills** are imported from a GitHub repository, uploaded as a ZIP file, or created directly in the UI. Skills are loaded by agents at invocation time when relevant to the task.

The recommended approach is to import skills from GitHub (for automatic synchronization) and create agents through Chat (for guided tool assignment).

### Skill dependency: import skills before or with the agent

Each agent declares the skills it uses in the `skills` array of its `agent-config.json`. For example, agent 326 lists `fis-experiment-recommendation` and `chaos-experiment-planner`. Those skills are the paired procedure the agent follows.

Import an agent's referenced skills into your Agent Space before, or at the same time as, creating the agent. An agent whose referenced skills are absent still creates and runs (skills enhance an agent, they are not a hard requirement to create it), but it runs without its paired procedure and produces shallow or degraded output. This looks like a silent bug rather than a clear failure, so treat the `skills` array as a deployment prerequisite.

To find what an agent needs, open its `agent-config.json` and read the `skills` array. The same pairing is also listed in [skills/README.md](skills/README.md) and [CATALOG.md](CATALOG.md).

---

## Deploying skills

Choose one of the three methods below. Import from GitHub is recommended because it enables automatic synchronization when you push updates.

### Method 1: Import from GitHub (recommended)

1. Push this repository to GitHub (public, or private with a connected GitHub account that has read access).

2. In the DevOps Agent web app, navigate to **Knowledge > Skills > Add skill > Import from repository**.

3. Enter the GitHub directory URL for the skill you want to import. The URL points to the directory containing `SKILL.md`. For example:

   ```
   https://github.com/YOUR-ORG/YOUR-REPO/tree/main/skills/incident-management/blast-radius-assessment
   ```

4. Select one or more agent types that can use this skill:
   - **Generic** (default, available to all agent types)
   - On-demand, Incident Triage, Incident RCA, Incident Mitigation, or Evaluation

5. Set the lifecycle status to **Active**.

6. Choose **Import skill**.

7. Repeat for each skill. There are 229 skills across 27 category directories under `skills/`.

The DevOps Agent reads the `SKILL.md` frontmatter to extract the skill name and description, then imports all files in the directory.

### Method 2: Upload as ZIP

Use this method when GitHub connectivity is not available.

1. Compress a skill directory into a ZIP file. The ZIP must contain `SKILL.md` at its root. For example, on Windows PowerShell:

   ```powershell
   Compress-Archive -Path "skills/incident-management/blast-radius-assessment/*" -DestinationPath "blast-radius-assessment.zip"
   ```

   On macOS or Linux:

   ```bash
   cd skills/incident-management/blast-radius-assessment && zip -r ../../../blast-radius-assessment.zip . && cd -
   ```

2. In the web app, navigate to **Knowledge > Skills > Add skill > Upload skill**.

3. Drag and drop the ZIP file or browse to select it. ZIP files only, maximum 6 MB.

4. Select the agent types that can use the skill.

5. Review the validation results and choose **Upload**.

### Method 3: Create in the UI

Use this method for a single skill when you prefer manual entry.

1. Navigate to **Knowledge > Skills > Add skill > Create skill**.

2. Open the skill's `SKILL.md` file. The frontmatter (between the `---` delimiters at the top) contains the name and description.

3. Enter the **Name** (from the frontmatter `name` field).

4. Enter the **Description** (from the frontmatter `description` field).

5. Copy the instructions (everything below the frontmatter) into the **Instructions** field.

6. Select the **Status** (Active) and **Agent Type**.

7. Choose **Create**.

---

## Deploying agents

Choose one of the methods below. Chat is recommended because it handles MCP tool assignment, which the form-based method cannot do.

### Method 1: Chat (recommended)

1. In the DevOps Agent web app, open Chat.

2. Open the agent's files:
   - `agents/XX-agent-name/agent-config.json` contains the name, tools, and trigger.
   - `agents/XX-agent-name/system-prompt.md` contains the full system prompt.

3. Send a message to Chat using this pattern:

   ```
   Create a custom agent named "cost-anomaly-detector" with these tools:
   use_aws, list_investigations.
   Set a schedule trigger: cron(0 8 * * ? *).

   Here is the system prompt:

   [paste the entire contents of system-prompt.md]
   ```

4. Chat confirms the configuration and creates the agent. Review the tool assignments and trigger before confirming.

5. Repeat for each agent.

### Method 2: Web app form

The form method does not support tool assignment. You assign tools through Chat after creation.

1. Navigate to **Agents > Custom Agents > Create agent**.

2. In the dialog, choose **Form**.

3. Enter the **Name** from `agent-config.json` (for example, `cost-anomaly-detector`).

4. Copy the entire contents of `system-prompt.md` into the **System prompt** field.

5. Optionally select skills to assign.

6. Choose **Create agent**.

7. After creation, open Chat and assign the tools listed in `agent-config.json`. For example:

   ```
   Add the use_aws and list_investigations tools to my cost-anomaly-detector agent.
   ```

### Method 3: Asset API (programmatic)

For automated or bulk deployment, use the AWS CLI or SDK to manage assets. See [Managing Assets](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-managing-assets.html) for the API reference.

This approach is suited to teams that want to manage agent definitions through their own CI/CD pipeline.

---

## Deploying with an AI assistant (Claude, Kiro, Cursor, Amazon Q)

If you work in an AI coding assistant, you can drive the whole deployment from there instead of the web app. AWS DevOps Agent exposes a remote MCP endpoint, so any MCP-capable assistant can create agents, import skills, and run them in your Agent Space. You can also use the assistant purely as an authoring aid (to read this repository's files and hand you ready-to-paste Chat commands) without connecting to the endpoint at all.

There are two patterns:

- **Pattern A - Connect the assistant to your Agent Space over MCP.** The assistant calls the DevOps Agent remote MCP endpoint directly to create and run agents and import skills. Requires the endpoint URL for your Agent Space and either an access token or AWS SigV4 credentials. See [Accessing DevOps Agent](https://docs.aws.amazon.com/devopsagent/latest/userguide/working-with-devops-agent-accessing-devops-agent-index.html).
- **Pattern B - Author locally, apply through Chat.** Point the assistant at this repository so it reads each `agent-config.json` and `system-prompt.md`, then have it generate the Chat commands (or the Asset API calls) you paste into the DevOps Agent web app. This needs no endpoint credentials and keeps a human in the loop for the create step.

Use whichever fits your security posture. Pattern B is the safer default for a first rollout; Pattern A is faster for bulk or repeatable deployment.

### Kiro

Add the DevOps Agent remote MCP server to your MCP config (workspace `.kiro/settings/mcp.json` or user `~/.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "devops-agent": {
      "command": "npx",
      "args": ["-y", "@aws/devops-agent-mcp-server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "DEVOPS_AGENT_ENDPOINT": "https://<your-agent-space-endpoint>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Then prompt Kiro, for example: "Using the devops-agent MCP server, create a custom agent from `agents/307-fsx-ontap-diagnostic/agent-config.json` and `system-prompt.md`, then import the paired skill from `skills/performance-engineering/fsx-ontap-diagnostics/`." Keep `autoApprove` empty so each create/import step is confirmed. For Pattern B, drop the MCP server and just ask Kiro to "read the agent files and generate the Chat commands to create them."

### Claude (Claude Code or Claude Desktop)

For Claude Code, add the server with the CLI:

```bash
claude mcp add devops-agent -e AWS_REGION=us-east-1 -e DEVOPS_AGENT_ENDPOINT=https://<your-agent-space-endpoint> -- npx -y @aws/devops-agent-mcp-server
```

For Claude Desktop, add the same block to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`; Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "devops-agent": {
      "command": "npx",
      "args": ["-y", "@aws/devops-agent-mcp-server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "DEVOPS_AGENT_ENDPOINT": "https://<your-agent-space-endpoint>"
      }
    }
  }
}
```

Then ask Claude to create the agents and import the skills from this repository. Review each proposed action before approving.

### Cursor

Add the server to `.cursor/mcp.json` in the project (or the global Cursor MCP settings):

```json
{
  "mcpServers": {
    "devops-agent": {
      "command": "npx",
      "args": ["-y", "@aws/devops-agent-mcp-server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "DEVOPS_AGENT_ENDPOINT": "https://<your-agent-space-endpoint>"
      }
    }
  }
}
```

Enable the server in Cursor Settings > MCP, then use the assistant to create agents and import skills from the repository files.

### Amazon Q Developer

Amazon Q Developer (CLI or IDE) is MCP-capable; add the same `devops-agent` server block to its MCP configuration (`~/.aws/amazonq/mcp.json` for the Q CLI, or the IDE MCP settings), then prompt Q to create the agents and import the skills.

### Notes and caveats

- Replace `<your-agent-space-endpoint>` with your Agent Space's remote MCP endpoint, and the exact MCP server package/command with the current one from [Accessing DevOps Agent](https://docs.aws.amazon.com/devopsagent/latest/userguide/working-with-devops-agent-accessing-devops-agent-index.html) - the package name and connection details evolve, so verify against the docs before relying on them.
- Prefer per-action approval (do not blanket auto-approve) so a human confirms each agent creation and skill import.
- Authentication is an access token or AWS SigV4; store credentials in the assistant's environment or your standard credential provider, never hard-coded in a committed config file.
- The agents in this repository stay read-only regardless of how they are deployed. Deploying through an assistant does not grant any write capability the agent config does not already declare.

---

## Configuring triggers

Each agent's `agent-config.json` includes a recommended trigger schedule. To configure it after creating the agent:

1. Open the agent in the DevOps Agent web app.

2. Navigate to the **Triggers** section.

3. Add a schedule trigger using the `expression` value from `agent-config.json`.

The schedule expressions used in this repository:

| Expression | Meaning |
|-----------|---------|
| `cron(0 5 * * ? *)` | Every day at 5:00 AM UTC |
| `cron(0 6 * * ? *)` | Every day at 6:00 AM UTC |
| `cron(0 7 * * ? *)` | Every day at 7:00 AM UTC |
| `cron(0 8 * * ? *)` | Every day at 8:00 AM UTC |
| `cron(0 9 * * ? *)` | Every day at 9:00 AM UTC |
| `cron(0 5 ? * MON *)` | Every Monday at 5:00 AM UTC |
| `cron(0 6 ? * MON *)` | Every Monday at 6:00 AM UTC |
| `cron(0 7 ? * MON *)` | Every Monday at 7:00 AM UTC |
| `cron(0 8 ? * MON *)` | Every Monday at 8:00 AM UTC |
| `cron(0 9 ? * MON *)` | Every Monday at 9:00 AM UTC |
| `cron(0 5 ? * WED *)` | Every Wednesday at 5:00 AM UTC |
| `cron(0 6 ? * WED *)` | Every Wednesday at 6:00 AM UTC |
| `cron(0 5 ? * SUN *)` | Every Sunday at 5:00 AM UTC |
| `cron(0 4 1 * ? *)` | Monthly on the 1st at 4:00 AM UTC |
| `rate(4 hours)` | Every 4 hours |
| `rate(6 hours)` | Every 6 hours |

Adjust the schedules to match your timezone and operational cadence. Stagger schedules so that agents sharing tools do not all run at the same minute, which reduces API throttling risk.

---

## Assigning skills to agents

Skills enhance agents with domain-specific investigation procedures. Assign relevant skills to agents through Chat:

```
Add the blast-radius-assessment and metric-correlation-investigator skills
to my incident-postmortem-generator agent.
```

Recommended agent and skill pairings:

| Agent | Recommended skills |
|-------|-------------------|
| daily-infra-health-report | dashboard-gap-analyzer, az-failure-readiness-assessment |
| cost-anomaly-detector | rightsizing-recommendation-engine, idle-resource-hunter, data-transfer-cost-analyzer |
| security-group-auditor | guardduty-finding-investigation, network-anomaly-investigation |
| deployment-rollback-analyzer | rollback-decision-framework, canary-deployment-analysis |
| incident-postmortem-generator | blast-radius-assessment, metric-correlation-investigator, incident-communication-drafter |
| eks-cluster-health-auditor | capacity-planning-forecaster, service-onboarding-checklist |
| well-architected-review-automator | operational-excellence-reviewer, security-reviewer, reliability-reviewer, performance-efficiency-reviewer, cost-optimization-reviewer |
| ecs-task-failure-investigator | ecs-task-failure-diagnosis |
| event-driven-architecture-health | event-driven-troubleshooting |
| api-gateway-health-monitor | api-gateway-troubleshooting |

You can assign up to 200 skills per custom agent. Assign only relevant skills to reduce context consumption and improve focus. The agent-config.json files in this repository already list suggested skills per agent.

---

## Recommendation handoff (optional)

The monitoring and audit agents can emit machine-readable recommendation records that conform to `schemas/recommendation.schema.json`. The remediation-orchestrator agent (227) consumes those records, applies the safety gates in SECURITY.md, and produces a human-approval-ready change plan. No agent in this repository executes changes; the orchestrator prepares them and a human approves.

To use the handoff:

1. Deploy the monitoring agents as usual. To have an agent emit records, extend its Output instruction using the contract in AGENT_TEMPLATE.md (the "Recommendation handoff" section).
2. Deploy the remediation-orchestrator agent (227). Keep it read-only; do not grant it write tools.
3. Run the orchestrator on demand or on its schedule, feeding it the recommendation records from a report. Review the resulting change plan and approve items manually.

If you want an agent to actually apply approved changes, see the Option 2 opt-in in [SECURITY.md](SECURITY.md#recommendation-handoff-and-remediation). This repository does not ship an executor with write access; you configure that separately with its own scoped role and approval gates.

---

## Verifying deployment

After deploying an agent:

1. **Run it on demand.** Open the agent and choose **Run** to trigger an invocation without waiting for the schedule.

2. **Review the trajectory.** Examine the invocation trajectory to confirm the agent called the expected tools and produced output. The trajectory shows reasoning steps, tool calls, and results.

3. **Check the artifact.** Confirm the agent produced its report artifact. Artifacts appear as links at the end of the trajectory and on the Artifacts page.

4. **Check recommendations.** If the agent creates recommendations, confirm they appear on the Improvements page.

5. **Confirm the Issues Encountered section.** Every agent report includes an Issues Encountered section. If it lists permission errors, grant the missing IAM permissions and re-run.

---

## Bulk deployment

To deploy all 329 agents efficiently, generate the Chat commands programmatically, then paste them into Chat in batches.

### Generate Chat commands (PowerShell)

```powershell
Get-ChildItem -Path "agents" -Directory | Sort-Object Name | ForEach-Object {
    $config = Get-Content "$($_.FullName)\agent-config.json" | ConvertFrom-Json
    $tools = $config.tools -join ", "
    Write-Output "=== $($config.name) ==="
    Write-Output "Create a custom agent named `"$($config.name)`" with tools: $tools."
    Write-Output "Set a schedule trigger: $($config.trigger.expression)."
    Write-Output "System prompt is in agents/$($_.Name)/system-prompt.md"
    Write-Output ""
}
```

### Generate Chat commands (bash)

```bash
for dir in agents/*/; do
  name=$(jq -r '.name' "$dir/agent-config.json")
  tools=$(jq -r '.tools | join(", ")' "$dir/agent-config.json")
  schedule=$(jq -r '.trigger.expression' "$dir/agent-config.json")
  echo "=== $name ==="
  echo "Create a custom agent named \"$name\" with tools: $tools."
  echo "Set a schedule trigger: $schedule."
  echo "System prompt is in $dir/system-prompt.md"
  echo ""
done
```

### Import all skills (bash)

```bash
REPO_BASE="https://github.com/YOUR-ORG/YOUR-REPO/tree/main"
for dir in skills/*/*/; do
  echo "Import skill from: $REPO_BASE/${dir%/}"
done
```

Paste each generated import URL into the **Import from repository** flow, or script the imports through the Asset API.

### Suggested rollout order

Deploy in phases rather than all at once. This lets you validate each group before expanding.

1. **Phase 1 (daily operations):** Agents 01, 02, 17, 30, 73. These give immediate daily visibility into health, cost, quotas, SLA risk, and a consolidated dashboard.

2. **Phase 2 (security posture):** Agents 03, 07, 15, 22, 82. Security groups, IAM, S3, CloudTrail anomalies, and public exposure.

3. **Phase 3 (cost optimization):** Agents 24, 27, 32, 61, 81. Storage, logs, orphaned resources, Savings Plans, and Graviton opportunities.

4. **Phase 4 (reliability and operations):** Agents 12, 29, 39, 77, 100. DR sync, event-driven health, on-call burden, incident trends, and the reliability scorecard.

5. **Phase 5 (remaining agents):** Deploy the rest based on the services you run.

---

## Updating and maintenance

### Updating skills

Skills imported from GitHub can be synchronized to pull the latest changes:

1. Open the imported skill in the detail view.

2. Choose **Sync**. The DevOps Agent re-fetches the directory contents from the source repository.

Alternatively, sync from the skills list view using the **Sync** action on the imported skill row.

### Updating agents

To update an agent, edit it in the web app or through Chat:

```
Update the cost-anomaly-detector agent system prompt to the latest version.
Here is the updated prompt: [paste system-prompt.md]
```

### Version control

Keep this repository as the source of truth. When you change a system prompt or skill:

1. Commit and push the change to GitHub.
2. For skills: sync the imported skill in the web app.
3. For agents: update the agent through Chat with the new prompt.

---

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---------|--------------|------------|
| Agent reports "Access denied" in Issues Encountered | Agent Space role lacks read permission for a service | Grant the missing read-only IAM permission and re-run |
| Agent reports "API throttling" and partial data | High API call volume or shared throttle limits | Stagger agent schedules; the agents retry once and degrade gracefully |
| Agent produces no artifact | Tool not assigned or system prompt incomplete | Verify tools in agent-config.json are assigned; re-run |
| Skill not activating during invocation | Skill description does not match the task | Review the skill frontmatter description; make it specific to the trigger scenario |
| Agent runs but the analysis is shallow or missing its documented procedure | A skill the agent references was not imported into the Agent Space | Open the agent's agent-config.json, import each skill named in its `skills` array, then re-run |
| Skill import fails | SKILL.md missing or frontmatter invalid | Confirm SKILL.md is at the directory root with valid name and description frontmatter |
| Agent reports "metrics not enabled" | The metric source is not turned on (for example, VPC Flow Logs, TGW metrics) | Enable the relevant metric or logging source, then re-run |
| Agent times out on large inventories | Account has many resources of the analyzed type | Agents batch large inventories automatically; if it persists, scope the agent to specific accounts via the system prompt |

For issues with the DevOps Agent service itself, consult the [AWS DevOps Agent documentation](https://docs.aws.amazon.com/devopsagent/latest/userguide/) or contact AWS Support.

---

## References

- [AWS DevOps Agent User Guide](https://docs.aws.amazon.com/devopsagent/latest/userguide/)
- [Creating a Custom Agent](https://docs.aws.amazon.com/devopsagent/latest/userguide/custom-agents-creating-a-custom-agent.html)
- [DevOps Agent Skills](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-devops-agent-skills.html)
- [Managing Assets (API)](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-managing-assets.html)
- [Custom Agent Outputs](https://docs.aws.amazon.com/devopsagent/latest/userguide/custom-agents-custom-agent-outputs.html)
