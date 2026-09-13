# Quickstart - deploy step by step

This is the shortest path from a fresh clone to a running custom agent in AWS
DevOps Agent. Follow the steps in order. Each step says what to do and how to
confirm it worked before moving on.

If you would rather have an AI assistant (Kiro, Cursor, Amazon Q, Claude, Codex)
run these steps for you, or reuse the skills inside those tools, see
[ai-assistants/README.md](ai-assistants/README.md).

---

## Before you start

You need:

- An AWS DevOps Agent **Agent Space**, and its **Agent Space ID** (a UUID).
- The AWS accounts you want analyzed **connected** to the Agent Space.
- A **GitHub account connected** to the Agent Space (needed to import skills and
  agents from a repository).
- `python3` on your machine (to run the validation and helper scripts).
- For the CLI, Bash, and IaC methods: AWS credentials with `aidevops:`
  permissions on the Agent Space (see
  [aws-cli/README.md](aws-cli/README.md#iam-permissions)).

Pick a **Region where AWS DevOps Agent is offered** and use it throughout.

---

## Step 1 - Get the repository onto GitHub

The DevOps Agent import flow only accepts GitHub URLs.

```bash
git clone <this-repo>
cd aws-sample-ai-agents

# create an empty GitHub repo first (no README/license), then:
git remote add github https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u github main
```

Confirm: open the repo on GitHub and check that `agents/`, `skills/`, and
`deploy/` are all present.

---

## Step 2 - Validate the collection

```bash
python scripts/validate.py
```

Confirm: the output ends with `VALIDATION PASSED` (227 agents, 145 skills). If
it fails, fix the reported file before continuing.

---

## Step 3 - Confirm the tools exist in your Agent Space

The agents use these MCP tools: `use_aws`, `query_cloudwatch_metrics`,
`query_cloudwatch_logs`, `list_cloudwatch_alarms`, `list_investigations`, and
`use_kubectl` (EKS agents only).

Confirm: in the DevOps Agent web app, check that these tools are available in
your Agent Space. If one is missing, the agent that needs it will not function.

---

## Step 4 - Attach read-only IAM permissions

The role backing your Agent Space needs read access to the services the agents
analyze. A scoped starting policy is provided.

1. Open [../policies/agent-readonly-policy.json](../policies/agent-readonly-policy.json).
2. Trim it to the services you actually use.
3. Attach it to the Agent Space execution role.

Confirm: the policy grants only `Describe`, `Get`, and `List` style actions and
no write permissions.

---

## Step 5 - Choose a deployment method

| If you want to... | Use | Guide |
|-------------------|-----|-------|
| Click through a UI, deploy a few assets | Console | [console/README.md](console/README.md) |
| Run one-off API calls or learn the API | AWS CLI | [aws-cli/README.md](aws-cli/README.md) |
| Bulk-deploy everything from a terminal | Bash | [bash/README.md](bash/README.md) |
| Manage assets as declarative IaC in a pipeline | CloudFormation | [cloudformation/README.md](cloudformation/README.md) |
| Do IaC in TypeScript, generated from the repo | CDK | [cdk/README.md](cdk/README.md) |
| Do IaC with Terraform | Terraform | [terraform/README.md](terraform/README.md) |
| Have an AI assistant do it | AI assistants | [ai-assistants/README.md](ai-assistants/README.md) |

The two most common starting points are below.

### Option A - Console (simplest, no local tooling)

1. **Import skills.** In the web app: **Knowledge > Skills > Add skill > Import
   from repository**. Paste a skill directory URL, for example
   `https://github.com/YOUR-ORG/YOUR-REPO/tree/main/skills/incident-management/blast-radius-assessment`.
   Select the agent type from the skill's `SKILL.md` `agent_type`, set status
   **Active**, and choose **Import skill**. Repeat for the skills you want.
2. **Create an agent in Chat.** Generate the exact command to paste:

   ```bash
   python scripts/generate_deploy_commands.py 01
   ```

   Send that message in Chat, pasting the contents of the referenced
   `system-prompt.md` where indicated. Chat creates the agent and assigns tools
   and skills.
3. **Set the trigger.** Open the agent, go to **Triggers**, and add a schedule
   using the `expression` from the agent's `agent-config.json`.

### Option B - Bash (bulk, from the terminal)

```bash
export AGENT_SPACE_ID=8f6187a7-0388-4926-8217-3a0fe32f757c
export AWS_REGION=us-east-1
export REPO_BASE=https://github.com/YOUR-ORG/YOUR-REPO/tree/main

# preview first - calls nothing
./deploy/bash/deploy.sh --dry-run

# then deploy everything (skills first, then agents)
./deploy/bash/deploy.sh
```

Then set triggers in the Console (Step 5, Option A, item 3), or use the
CloudFormation option to create them as code.

---

## Step 6 - Verify the deployment

1. Open the agent in the web app and choose **Run** to start an on-demand
   invocation.
2. Open the **invocation trajectory**. Confirm the agent called the expected
   tools and loaded the expected skills.
3. Confirm the **report artifact** was produced.
4. Read the **Issues Encountered** section of the report. If it lists
   `Access denied`, grant the missing read-only IAM permission and re-run.

Confirm: the agent produced a report and the trajectory shows the expected tool
calls. You are done.

---

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Skill import fails | `SKILL.md` missing or bad frontmatter | Confirm the directory URL points at a folder with a valid `SKILL.md` |
| Agent runs but skips a skill | Skill not assigned, or not `Generic` | Assign the skill to the agent, or set its agent type to match the task |
| Agent produces no artifact | Tool not assigned | Assign the tools from `agent-config.json` via Chat |
| `Access denied` in the report | Execution role missing a read permission | Grant the read-only permission and re-run |
| CLI/IaC call rejected | Missing `aidevops:` permission, or wrong Region | Add the permission; deploy in a supported Region |

For the full reference, see [../DEPLOYMENT.md](../DEPLOYMENT.md).
