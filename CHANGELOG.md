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

## [2026-09-12] - 269 agents, 170 skills across 24 domains

### Added
- Grew the collection to 269 custom agents and 170 skills across 24 operational domains.
- Application-perspective agents (228-255): application performance monitoring (golden signals, end-to-end latency tracing, Apdex, p99 regression, error-signal correlation, memory-leak/GC, dependency SLO impact), release management (DORA four keys, canary/blue-green analysis, change-failure attribution, feature-flag drift, release-readiness gate, post-deploy verification, rollback frequency/MTTR), disaster recovery (RTO/RPO attainment, DR game-day readiness, failover dependency validation, per-application recoverability, active-active drift), site reliability and SLO (error-budget burn rate, SLI coverage, alert actionability/toil, user-journey availability), and application troubleshooting (log-signature clustering, cascading-failure/retry-storm detection, slow-query/N+1, thundering-herd/cold-start, incident timeline reconstruction).
- CloudWatch observability coverage agents (256-261): Application Signals SLO and service map, Lambda Insights performance, cross-account observability (OAM), native metric anomaly-detector coverage, metric-streams and EMF ingestion health, and dashboard coverage.
- End-of-life and extended-support cost agents (262-266): a cross-service extended-support cost-exposure reporter and per-service detectors for RDS/Aurora, EKS, deprecated Lambda runtimes, and legacy EC2 platforms, each with a 60/90/180-day forecast and migration roadmap and estimate caveats.
- Cost-governance and account-contact agents (267-268): cost-protection controls enablement auditor (detect and drive enablement of Cost Anomaly Detection, AWS Budgets, Cost Explorer, RI/SP utilization alerts) and an account alternate-contacts and notification-consolidation auditor.
- Trusted Advisor remediation-and-migration planner (269) and its playbook skill (trusted-advisor-remediation-and-migration-playbook): for every Trusted Advisor check in red or yellow status, complete the recommendation with the validated quantified impact, concrete step-by-step remediation, a safety rating, and a migration path - the next steps Trusted Advisor itself does not provide. Distinct from the trusted-advisor-check-aggregator (226), which aggregates and prioritizes.
- New skill domains (five): contact-center (Amazon Connect), iot (IoT Core, Greengrass, FleetWise), messaging-deliverability (SES, Pinpoint, Chime SDK), media (AWS Elemental), and purpose-built-databases (DocumentDB, Neptune, Timestream, MemoryDB, Keyspaces).
- Directed actions (`agent-actions/`): documentation of the AWS DevOps Agent directed-actions model, elevated-role trust and scoped permission policies, a `directed-action.schema.json`, and per-domain mappings of each read-only finding to the exact mutating operation with guardrail status (allowed, refused-delete-class, refused-passrole, refused-prohibited-action), safety rating, approval scope, and rollback. Read-only remains the default; directed actions are opt-in and human-approved.
- Adversarial Input Handling guardrail block (prompt injection, exfiltration, LLMjacking, excessive agency) added to `SECURITY.md`, `AGENT_TEMPLATE.md`, and every agent system prompt.
- Deployment options folder (`deploy/`): a step-by-step quickstart plus Console, AWS CLI, Bash, CloudFormation, CDK, and Terraform guides, and an AI-assistant guide (driving the deploy with, and reusing the skills inside, Kiro, Cursor, Amazon Q, Claude, and Codex).
- Deployment workflow diagram in `README.md` and generator/validation tooling (`scripts/generate_deploy_commands.py`; extended `scripts/validate.py` to check agent tool names and skill `agent_type`, and to skip build output).

### Changed
- Extended the ASCII check to `.py`, `.ps1`, `.yml`, `.yaml`, and `.txt` and excluded `.git`, `node_modules`, `cdk.out`, and `.terraform` from validation.
- Updated `README.md` and `CATALOG.md` to the current counts and added catalog sections for all agents through 268 and the new skill domains.

## [2026-08-14] - 226 agents, 145 skills

### Added
- Grew the collection to 226 custom agents across the operational lifecycle and 145 skills across 19 domains.
- Root documentation: `README.md`, `DEPLOYMENT.md`, `CATALOG.md`, `AGENT_TEMPLATE.md`, `agents/README.md`, `skills/README.md`.
