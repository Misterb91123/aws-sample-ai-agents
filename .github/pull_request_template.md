# Pull Request

## Summary

Describe what this change adds or fixes.

## Type of change

- [ ] New agent
- [ ] New skill
- [ ] Update to an existing agent or skill
- [ ] Documentation
- [ ] Tooling or CI

## Checklist

- [ ] Files are pure ASCII (no em dashes, curly quotes, emojis, or other non-ASCII characters).
- [ ] New agents follow the section order in AGENT_TEMPLATE.md: Goal, Approach, Exception Handling, Data Validation, Constraints, Output.
- [ ] New skills have YAML frontmatter with name and description.
- [ ] The change respects the guardrails in SECURITY.md (read-only, no prohibited recommendations, findings grounded in data, sensitive values referenced by identifier).
- [ ] CATALOG.md, README.md, agents/README.md, and skills/README.md are updated where relevant.
- [ ] `python scripts/validate.py` (or `pwsh -File scripts/validate.ps1`) passes locally.
