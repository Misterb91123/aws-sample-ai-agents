# Deploy with the AWS Console (Operator Web App)

The Operator Web App is the fastest way to deploy a handful of assets
interactively and the only option that guides you through MCP tool assignment.
For bulk or repeatable deploys, prefer the CLI or an IaC option.

This guide is a condensed walkthrough. The full reference, including bulk
deployment and a suggested rollout order, is in the main
[DEPLOYMENT.md](../../DEPLOYMENT.md).

---

## 1. Import skills

Skills import as a directory that contains a `SKILL.md`. Import from GitHub to
keep a sync link back to this repository.

1. Push this repository to GitHub.
2. In the web app, go to **Knowledge > Skills > Add skill > Import from repository**.
3. Enter the GitHub directory URL for the skill, for example:

   ```
   https://github.com/YOUR-ORG/YOUR-REPO/tree/main/skills/incident-management/blast-radius-assessment
   ```

4. Select the **agent type(s)** for the skill. Use the `agent_type` recorded in
   each skill's `SKILL.md` frontmatter (and listed in
   [../../skills/README.md](../../skills/README.md)). `Generic` makes it
   available to all agent types.
5. Set the status to **Active** and choose **Import skill**.
6. Repeat per skill. There are 145 skills under `skills/`.

Alternatives when GitHub is not available: **Upload skill** (a ZIP of the skill
directory, max 6 MB) or **Create skill** (paste the frontmatter fields and the
instructions). Both are described in [DEPLOYMENT.md](../../DEPLOYMENT.md#deploying-skills).

---

## 2. Create agents and assign tools

The Console imports only the system prompt from GitHub. Tools are assigned
through Chat, so the recommended path is to create the agent in Chat where both
happen together.

**Recommended - create in Chat.** Generate a ready-to-paste command for the
agent with the helper script, then send it in Chat:

```bash
python scripts/generate_deploy_commands.py 01
```

That prints something like:

```
Create a custom agent named "daily-infra-health-report" with these tools:
use_aws, query_cloudwatch_metrics, list_cloudwatch_alarms, list_investigations.
Assign these skills: operational-excellence-reviewer, reliability-reviewer.
Set a schedule trigger: cron(0 6 * * ? *).
Use the system prompt in agents/01-infrastructure-health-report/system-prompt.md.
```

Open the referenced `system-prompt.md`, paste its full contents into the Chat
message where indicated, and send. Chat confirms the tools, skills, and trigger
before creating the agent.

**Alternative - Form plus GitHub import.** Under **Agents > Custom Agents >
Create agent**, choose **Import** and point at the agent's
`system-prompt.md` on GitHub (a single `.md` file). Set the name and select
skills. After creation, open Chat and assign the tools from `agent-config.json`,
for example:

```
Add the use_aws and query_cloudwatch_metrics tools to my
daily-infra-health-report agent.
```

---

## 3. Configure the trigger

Each agent's `agent-config.json` includes a recommended schedule.

1. Open the agent in the web app.
2. Go to the **Triggers** section and add a schedule trigger using the
   `expression` value from `agent-config.json` (for example `cron(0 6 * * ? *)`).

Stagger schedules so agents that share tools do not all run at the same minute.

---

## 4. Verify

1. Open the agent and choose **Run** to trigger an on-demand invocation.
2. Review the **invocation trajectory** to confirm the agent called the expected
   tools and loaded the expected skills.
3. Confirm the report artifact appears, and check the **Issues Encountered**
   section for permission errors. Grant any missing read-only permission and
   re-run.

See [DEPLOYMENT.md](../../DEPLOYMENT.md#verifying-deployment) for the full
verification checklist and the recommended agent-to-skill pairings.
