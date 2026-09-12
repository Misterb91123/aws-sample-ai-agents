# Contributing

Thanks for your interest in improving this collection of AWS DevOps Agent custom agents and skills. This guide explains how to add or change content so it stays consistent and safe.

## Ground rules

- All content must be pure ASCII. No em dashes, en dashes, curly quotes, ellipsis characters, emojis, box-drawing, arrows, or other non-ASCII bytes. Use a plain hyphen and straight quotes.
- Agents are read-only. They call describe, get, and list APIs plus CloudWatch reads and produce reports and recommendations. They never create, modify, or delete resources.
- Follow the guardrails in [SECURITY.md](SECURITY.md): never recommend a prohibited action, ground every finding in observed data, and reference sensitive values by identifier rather than reproducing them.

## Adding an agent

1. Create a folder `agents/NN-kebab-name/` where `NN` is the next number and the name describes what the agent does.
2. Add `system-prompt.md` with sections in this exact order:
   - Opening role sentence (starts with "You are a ...")
   - `## Goal`
   - `## Approach` (numbered; name specific AWS APIs, CloudWatch metrics, and numeric thresholds)
   - `## Exception Handling`
   - `## Data Validation`
   - `## Guardrails`
   - `## Constraints`
   - `## Output`
3. Add `agent-config.json` with `name`, `description`, `tools`, `skills`, and `trigger`. Populate `skills` with 2 to 4 relevant skill names that exist under `skills/`.
4. Choose a trigger that does not collide with a heavily used slot. See the staggering approach in `scripts/stagger-schedules.ps1`.
5. Use [AGENT_TEMPLATE.md](AGENT_TEMPLATE.md) as the starting point.

## Adding a skill

1. Create `skills/<domain>/<kebab-name>/SKILL.md`.
2. Start with YAML frontmatter containing `name`, `description`, `version`, and `last_updated`.
3. Follow the body structure: a title, a short intro, `## When to Activate`, numbered `## Step N` sections with specific AWS APIs and numeric thresholds, and a final `## Output` section.

## Updating documentation

When you add or change agents or skills, update the affected files:

- `README.md` badges, counts, and range tables
- `agents/README.md` agent list
- `skills/README.md` category tables and directory tree
- `CATALOG.md` domain sections and the service index
- `CHANGELOG.md` with a short entry

## Validate before opening a pull request

Run the validation script from the repository root:

```
python scripts/validate.py
```

or, on Windows:

```
pwsh -File scripts/validate.ps1
```

The script checks ASCII, JSON validity, the required section order, skill frontmatter, and that agent skill references resolve. Continuous integration runs the same check on every pull request.

## Pull request

Open a pull request using the template. Keep the change focused, describe what it adds or fixes, and confirm the checklist.
