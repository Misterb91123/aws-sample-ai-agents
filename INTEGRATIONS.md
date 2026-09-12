# Using these agents with other AI tools

These agents and skills were authored for [AWS DevOps Agent](https://docs.aws.amazon.com/devopsagent/latest/userguide/working-with-devops-agent-custom-agents-index.html), but they are portable prompt-and-configuration assets, not code tied to one product. Each agent is a system prompt plus a small config; each skill is a markdown instruction file. Any agent tool that accepts a custom system prompt or instruction file can use them.

This guide shows how to load them into AWS DevOps Agent, Claude Code, Kiro, Cursor, tools that follow the `AGENTS.md` convention, and any tool that speaks MCP.

---

## What maps to what

| This repository | What it is | Equivalent in other tools |
|-----------------|-----------|---------------------------|
| `agents/NN-name/system-prompt.md` | The agent instructions (Goal, Approach, Guardrails, Output) | A subagent system prompt, a rule file, or a steering file |
| `agents/NN-name/agent-config.json` | Name, tools, skills, schedule | Frontmatter and tool allowlist in the target tool; schedule maps to that tool's automation |
| `skills/<domain>/<name>/SKILL.md` | Reusable domain procedure with frontmatter | A skill, a rule, or an included instruction file |
| `schemas/recommendation.schema.json` | The recommendation handoff contract | The output contract any tool can be asked to follow |

---

## Important: read-only by design

Every agent here is read-only. It reads AWS state and produces reports and recommendations; it never changes resources. When you move an agent into another tool, preserve that posture:

- Grant only read tools (an MCP server that exposes describe, get, and list, or a shell restricted to read-only AWS CLI calls).
- Attach the least-privilege read-only policy at [policies/agent-readonly-policy.json](policies/agent-readonly-policy.json) to whatever credentials the tool uses.
- Keep the `## Guardrails` block in the prompt so the safe-recommendation and anti-hallucination rules travel with the agent. See [SECURITY.md](SECURITY.md).

The agent's access to AWS in any of these tools comes from an MCP server or CLI you configure, not from this repository. This repository provides the instructions; you provide the read-only connection.

---

## AWS DevOps Agent (native)

This is the environment the assets were designed for. See [DEPLOYMENT.md](DEPLOYMENT.md) for full steps. In short: create a custom agent, paste `system-prompt.md`, assign the tools from `agent-config.json`, set the trigger, and import skills from this GitHub repository.

---

## Claude Code

Claude Code loads custom subagents from markdown files with YAML frontmatter, in `.claude/agents/` for a project or `~/.claude/agents/` for your user. Each file has a `name`, a `description`, an optional tool allowlist, and the system prompt as the body. Content was rephrased from public Claude Code documentation for compliance.

To convert an agent from this repository:

1. Create `.claude/agents/<agent-name>.md`.
2. Add frontmatter and paste the system prompt body:

```markdown
---
name: cloudwatch-alarm-fatigue-reducer
description: Read-only agent that analyzes CloudWatch alarms to reduce alert fatigue. Use for alarm hygiene reviews.
tools: Bash
---

(paste the contents of agents/06-cloudwatch-alarm-fatigue-reducer/system-prompt.md here)
```

3. Give it read-only AWS access. The cleanest way is an AWS MCP server configured for read-only, added to Claude Code, so the agent calls AWS through MCP instead of the shell. If you use `Bash` with the AWS CLI instead, restrict the credentials to the read-only policy in `policies/`.
4. Skills: paste the relevant `SKILL.md` bodies into the agent prompt, or keep them as separate reference files the agent reads. Claude Code has no scheduler, so run the agent on demand or trigger it from CI or cron.

A skill maps naturally to a Claude Code subagent too, if you prefer one specialist per procedure.

---

## Kiro

Kiro supports custom agents and steering files. Two clean options:

- Steering files: place an agent's guidance in `.kiro/steering/<name>.md`. Use `inclusion: manual` in the frontmatter so it loads only when you reference it with a context key, or `inclusion: fileMatch` to load it for matching files. This suits skills and always-on conventions.
- Custom agents: define a Kiro custom agent whose system prompt is the agent's `system-prompt.md`, and give it a read-only AWS MCP server for access.

For AWS access in Kiro, configure an AWS MCP server in `.kiro/settings/mcp.json` (workspace) or `~/.kiro/settings/mcp.json` (user), scoped to read-only credentials. Kiro can run agents on demand; use a hook or external scheduler if you want recurring runs.

---

## Cursor

Cursor loads project rules from `.cursor/rules/*.mdc`, each a markdown file with YAML frontmatter (`description`, `globs`, `alwaysApply`). Content was rephrased from public Cursor documentation for compliance.

To convert an agent or skill:

1. Create `.cursor/rules/<agent-name>.mdc`.
2. Add frontmatter and the body:

```markdown
---
description: Read-only CloudWatch alarm fatigue review agent
alwaysApply: false
---

(paste the contents of the agent system-prompt.md or a SKILL.md here)
```

3. Set `alwaysApply: false` and invoke the rule manually when you want that agent's behavior, or set `globs` to scope it. Because these agents operate on live AWS rather than files, manual invocation usually fits best.
4. Give Cursor read-only AWS access through an AWS MCP server configured in Cursor's MCP settings, pointed at read-only credentials.

If you prefer plain markdown over `.mdc`, Cursor also reads `AGENTS.md` (see below).

---

## AGENTS.md-compatible tools

`AGENTS.md` is a plain-markdown convention that a growing set of coding agents read for project instructions. To expose a subset of these agents through it:

1. Create or extend `AGENTS.md` at the repository root of the project where you want the guidance.
2. Summarize the agents you want available and link to their `system-prompt.md` files, or paste the prompt bodies inline.
3. Note the read-only posture and point at [SECURITY.md](SECURITY.md) so the consuming tool inherits the guardrails.

This is the lowest-friction, most portable path when a tool does not have a dedicated agent format.

---

## Any tool that speaks MCP

The common thread across all of these is Model Context Protocol. The agent behavior is just a system prompt; the AWS access is an MCP server. For any MCP-capable tool:

1. Add a read-only AWS MCP server to the tool's MCP configuration, using credentials scoped to `policies/agent-readonly-policy.json`.
2. Load the agent's `system-prompt.md` as the system prompt or as an included instruction file, keeping the `## Guardrails` block.
3. Attach relevant `SKILL.md` files as reference context.
4. Run on demand, or wire the tool's automation (CI job, cron, or the tool's own scheduler) to the trigger cadence in the agent's `agent-config.json`.

---

## The recommendation handoff across tools

The recommendation handoff in this repository is tool-agnostic. Ask any tool running one of these agents to emit records that conform to [schemas/recommendation.schema.json](schemas/recommendation.schema.json), using the output contract in [AGENT_TEMPLATE.md](AGENT_TEMPLATE.md). Those JSON records can then be fed to the remediation-orchestrator agent (227) in whichever tool you run it, or into your own approval workflow. No matter the tool, keep the same rule: the read-only agents propose, a human approves, and only a separately configured executor with its own scoped permissions ever applies a change.

---

## Attribution

Details of the Claude Code subagent format (markdown with YAML frontmatter under `.claude/agents/`) and the Cursor rules format (`.cursor/rules/*.mdc` with frontmatter) are summarized from those tools' public documentation. Content was rephrased for compliance with licensing restrictions. Confirm the current format in each tool's official documentation, since these tools evolve quickly.
