# Deploy with AI coding assistants

AI coding assistants such as Kiro, Cursor, Amazon Q Developer, Claude (Claude
Code / Claude Desktop), and OpenAI Codex are not deployment targets for AWS
DevOps Agent. There is no "deploy to Cursor" step. Instead, they help in two
distinct ways, and this guide covers both:

- **[Part A - Drive the deployment](#part-a---drive-the-deployment)**: point the
  assistant at this repository and have it run the existing deployment steps (the
  AWS CLI, Bash, CloudFormation, CDK, or Terraform options) for you.
- **[Part B - Reuse the skills as portable context](#part-b---reuse-the-skills-as-portable-context)**:
  load the Markdown skills in this repo into the assistant itself as rules,
  steering, or skills, so the assistant follows the same investigation
  procedures. This is independent of AWS DevOps Agent.

A note on accuracy: these tools change quickly. The commands and file locations
below reflect common, documented conventions, but confirm the current specifics
in your tool's own documentation. The prompts in Part A are portable and work in
any assistant that can run shell commands.

---

## Part A - Drive the deployment

The idea: the assistant reads this repo, then executes the same commands from
the [AWS CLI](../aws-cli/README.md), [Bash](../bash/README.md),
[CloudFormation](../cloudformation/README.md), [CDK](../cdk/README.md), or
[Terraform](../terraform/README.md) options. You still need the prerequisites
from [QUICKSTART.md](../QUICKSTART.md) (an Agent Space, connected accounts, AWS
credentials with `aidevops:` permissions).

Two capabilities make an assistant useful here:

1. **Running shell/AWS CLI commands** - most assistants can run terminal
   commands (with your approval). That is all that is required to drive the CLI,
   Bash, CDK, and Terraform options.
2. **AWS MCP servers (optional)** - some assistants can connect to AWS through
   the Model Context Protocol, which lets the assistant call AWS and read docs
   directly instead of shelling out. This is convenient but not required.

### Ready-to-paste prompt (works in any assistant that runs commands)

Open this repository in the assistant, then paste:

```
You are helping me deploy the custom agents and skills in this repository to
AWS DevOps Agent.

Context:
- My Agent Space ID is: <AGENT_SPACE_ID>
- My Region is: <REGION> (a Region where DevOps Agent is offered)
- This repo is on GitHub at: <REPO_BASE e.g. https://github.com/ORG/REPO/tree/main>

Do the following, showing me each command before you run it and stopping if any
command fails:
1. Run `python scripts/validate.py` and confirm it passes.
2. Read deploy/bash/README.md and deploy/bash/deploy.sh.
3. Run the Bash deploy in dry-run mode first:
   AGENT_SPACE_ID=<...> AWS_REGION=<...> REPO_BASE=<...> ./deploy/bash/deploy.sh --dry-run
4. Show me the planned create-asset calls. After I approve, run it for real
   without --dry-run.
5. Remind me that schedule triggers are not created by the Bash option and tell
   me how to add them (Console or the CloudFormation option).

Do not grant any write permissions to the agents. Everything here is read-only.
```

To deploy a subset instead of everything, tell the assistant to pass
`--agents 01 02` (or name fragments) to `deploy.sh`.

### Prompt for the IaC options

For CloudFormation, CDK, or Terraform, swap step 3-4 for:

```
Use the CloudFormation option. Read deploy/cloudformation/README.md, then run:
  aws cloudformation deploy \
    --template-file deploy/cloudformation/agent-stack.yaml \
    --stack-name devops-agent-sample \
    --parameter-overrides AgentSpaceId=<AGENT_SPACE_ID> \
    --region <REGION>
Show me the change set summary before applying.
```

### Tool-by-tool notes

**Kiro**
- Open the repo as your workspace. Ask Kiro in chat to run the prompt above; it
  executes shell commands with your approval.
- Optional: configure an AWS MCP server in `.kiro/settings/mcp.json` (workspace)
  or `~/.kiro/settings/mcp.json` (user) so Kiro can read AWS docs or call AWS
  directly. Example server entry:
  ```json
  {
    "mcpServers": {
      "aws-docs": {
        "command": "uvx",
        "args": ["awslabs.aws-documentation-mcp-server@latest"],
        "disabled": false
      }
    }
  }
  ```
- Optional: turn the deploy steps into a Kiro spec so it tracks them as tasks.

**Cursor**
- Open the repo. Use the Agent/Composer panel and paste the prompt; approve each
  command run.
- Optional: add an AWS MCP server via Cursor's MCP settings so the agent can
  call AWS through MCP instead of the terminal.

**Amazon Q Developer**
- In the IDE extension or the Q CLI, open the repo and paste the prompt. The Q
  CLI (`q chat`) can execute AWS CLI commands directly, which fits the CLI and
  Bash options well.
- Amazon Q has native AWS awareness, so it is comfortable with
  `aws devops-agent create-asset` and CloudFormation deploys.

**Claude (Claude Code / Claude Desktop)**
- Claude Code runs in the terminal in your repo directory; paste the prompt and
  it runs the commands with approval.
- Claude Desktop can use MCP servers (including AWS MCP servers) configured in
  its developer settings, letting it call AWS through MCP.

**OpenAI Codex**
- In the Codex CLI or IDE integration, open the repo and paste the prompt. Codex
  executes shell commands, so it drives the CLI, Bash, CDK, and Terraform
  options.

Whichever tool you use, keep the human-in-the-loop: review each
`create-asset`/`deploy` command before it runs, and start with `--dry-run` or a
change-set preview.

---

## Part B - Reuse the skills as portable context

The 145 skills in `skills/` are plain Markdown with a small frontmatter block.
That format is portable: you can load these procedures into an AI assistant so
it follows the same investigation and review steps when you work in that tool -
without any AWS DevOps Agent involvement. This is useful for local
troubleshooting, code review, and drafting runbooks.

What transfers cleanly is the **body** of each `SKILL.md` (the steps, decision
trees, and output format). The DevOps-Agent-specific frontmatter (`agent_type`)
and any references to DevOps Agent tools are not meaningful outside the service,
so treat them as context, not instructions.

### Kiro - steering files

Kiro reads steering files from `.kiro/steering/*.md` to add standing context.

- Copy a skill body into a steering file, for example
  `.kiro/steering/blast-radius-assessment.md`.
- Use front-matter `inclusion: manual` to load it on demand with `#` in chat, or
  `inclusion: fileMatch` with a `fileMatchPattern` to load it automatically when
  relevant files are open. Default (always included) works for a small number of
  high-value skills.
- You can also point a steering file at a skill with a file reference so you do
  not duplicate content:
  ```markdown
  ---
  inclusion: manual
  ---
  #[[file:../../skills/incident-management/blast-radius-assessment/SKILL.md]]
  ```

### Cursor - project rules

Cursor reads rules from `.cursor/rules/` (modern) or a top-level `.cursorrules`
file (legacy).

- Create `.cursor/rules/blast-radius-assessment.mdc` and paste the skill body.
- Give the rule a clear description and, if your Cursor version supports it, a
  glob so it activates for relevant files. The skill's own "When to Activate"
  section is good source text for the description.

### Claude - skills and projects

- **Claude skills**: Claude supports an Agent Skills format very close to this
  repo's (a `SKILL.md` with `name` and `description` frontmatter plus optional
  bundled files). You can adapt a skill directory into a Claude skill; keep the
  frontmatter `name` and `description`, drop `agent_type`.
- **Claude Projects / Claude Code**: add the skill body as project knowledge or
  a `CLAUDE.md` instruction file so Claude follows the procedure in that project.

### Amazon Q Developer - context and rules

- Amazon Q supports workspace context and rules files (for example a project
  rules/`AmazonQ.md`-style file, depending on your Q version). Paste the skill
  body there so Q applies the procedure. Confirm the exact filename in the Q
  documentation for your version.

### OpenAI Codex - AGENTS.md

- Codex reads an `AGENTS.md` file for repo-level instructions. Add the most
  relevant skill procedures (or links to the skill files) to `AGENTS.md` so
  Codex follows them when working in the repo.

### A simple, tool-agnostic approach

If you do not want per-tool wiring, just attach the specific `SKILL.md` file to
your chat as context when you need it. Every one of these assistants can read a
Markdown file you point it at, and the procedures are written to stand on their
own.

---

## Which part do you want

- Deploying the agents and skills to AWS DevOps Agent? Use **Part A**, or the
  non-AI options in the sibling folders.
- Making an assistant follow these procedures while you code locally? Use
  **Part B**.
- Both are fine to use together.
