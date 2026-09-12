# Changelog

All notable changes to this collection are documented here. The format is based on Keep a Changelog, and this project uses date-based releases.

## [Unreleased]

### Changed
- Relicensed from MIT to MIT-0 (MIT No Attribution); no attribution required for use, modification, or distribution.

### Added
- Prominent sample and use-at-your-own-risk notice at the top of `README.md` and a full `Disclaimer` section covering due diligence, testing in non-production, permissions ownership, and no warranty.
- Security and guardrails framework in `SECURITY.md`, adapted from the AWS sample-ai-agent-skills SECURITY.md and tailored to these read-only agents (threat model, prohibited recommendations, GREEN/YELLOW/RED safety classification, escalation conditions, anti-hallucination rules, data sensitivity classifications, production deployment recommendations).
- Reusable `## Guardrails` block embedded in all 226 agent system prompts.
- Guardrails checklist and reusable prompt block in `AGENT_TEMPLATE.md`.
- Validation scripts `scripts/validate.py` and `scripts/validate.ps1` enforcing ASCII, JSON validity, required section order, skill frontmatter, and skill reference resolution.
- GitHub Actions workflow `.github/workflows/validate.yml` running validation on push and pull request.
- Issue templates and a pull request template under `.github/`.
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
- Least-privilege read-only IAM policy at `policies/agent-readonly-policy.json`.
- Index by AWS service in `CATALOG.md`.
- `version` and `last_updated` fields in every skill frontmatter.
- `INTEGRATIONS.md` showing how to install and configure these agents and skills with AWS DevOps Agent, Claude Code, Kiro, Cursor, AGENTS.md-compatible tools, and any MCP-capable tool, with the read-only posture preserved.
- Structured recommendation handoff: `schemas/recommendation.schema.json` (machine-readable recommendation records with evidence, safety rating, approval and escalation flags, prohibited-action check, and rollback), a Recommendation handoff output contract in `AGENT_TEMPLATE.md`, the read-only remediation-orchestrator agent (227) that safety-gates records into a human-approval-ready change plan without executing, and a Recommendation handoff and remediation section in `SECURITY.md` including the Option 2 execution opt-in and its required controls.

### Changed
- Linked skills to agents: every agent-config.json now references 2 to 4 relevant skills (previously all empty).
- Staggered agent trigger schedules to avoid a thundering herd (clustered cron slots spread across weekdays, hours, and minutes; the largest single cron slot dropped from 73 agents to 4).

## [2026-08-14] - 226 agents, 145 skills

### Added
- Grew the collection to 226 custom agents across the operational lifecycle and 145 skills across 19 domains.
- Root documentation: `README.md`, `DEPLOYMENT.md`, `CATALOG.md`, `AGENT_TEMPLATE.md`, `agents/README.md`, `skills/README.md`.
