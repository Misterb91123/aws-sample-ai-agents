---
name: release-changelog-generator
agent_type: "Generic"
description: Generates structured release changelogs by analyzing deployments,
  commits, and configuration changes between two release versions. Use this skill
  when preparing release notes, auditing what changed between versions, or when
  investigating issues by understanding what was included in a specific release.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Release Changelog Generator

Use this skill to generate comprehensive changelogs documenting what changed
between two releases, including code changes, configuration updates, and
infrastructure modifications.

## When to Activate

- A new release is being prepared and needs documentation.
- Post-incident: need to understand exactly what was in a specific deployment.
- Audit request: what changes went to production in a given time period.
- Sprint/iteration review: summarize shipped changes.

## Step 1: Identify Release Boundaries

Determine the scope of the changelog:
1. Previous release identifier (commit SHA, image tag, version, deployment ID).
2. Current release identifier.
3. Time range if versions not available (e.g., "changes deployed between Monday and Friday").
4. Services in scope (single service or multi-service release).

## Step 2: Gather Code Changes

For each service in the release:
1. Retrieve commits between the two release boundaries.
2. Extract pull requests / merge requests merged in this range.
3. For each PR, capture:
   - Title and description
   - Author
   - Labels/tags (feature, bugfix, hotfix, chore, refactor)
   - Linked tickets (Jira, GitHub Issues)
   - Files changed (for categorization)

## Step 3: Gather Infrastructure Changes

Check for infrastructure modifications in the release window:
1. CloudFormation stack updates - what resources were added/modified/deleted.
2. Terraform state changes (if tracked via deployment tooling).
3. ECS task definition changes - environment variables, resource limits, image tags.
4. Lambda configuration changes - memory, timeout, environment variables.
5. Parameter Store or Secrets Manager changes.

## Step 4: Gather Configuration Changes

Identify non-code changes that accompanied the release:
1. Feature flag changes (LaunchDarkly, AWS AppConfig, custom).
2. Environment variable additions or modifications.
3. IAM policy changes associated with the service.
4. Security group or networking changes.
5. Scaling configuration changes (min/max capacity, thresholds).

## Step 5: Categorize Changes

Group changes into categories:

### New Features
Changes introducing new customer-facing functionality.

### Bug Fixes
Changes resolving reported issues or defects.

### Performance Improvements
Optimizations, caching improvements, query tuning.

### Security
Dependency updates, vulnerability patches, access control changes.

### Infrastructure
Resource configuration changes, scaling, networking.

### Configuration
Feature flags, environment variables, parameters.

### Maintenance
Refactoring, dependency updates, test improvements, documentation.

### [WARN] Breaking Changes
Changes that require action from consumers or operators.

## Step 6: Assess Release Risk

For each change, assess risk level:
- **High Risk**: Database migrations, breaking API changes, new infrastructure, auth changes.
- **Medium Risk**: New features behind feature flags, dependency updates, performance changes.
- **Low Risk**: Bug fixes for edge cases, documentation, test improvements, refactoring.

Produce an overall release risk score:
- Low: All changes are low risk
- Medium: Contains medium risk changes but no high risk
- High: Contains one or more high-risk changes

## Step 7: Generate Changelog

Structure the changelog as:

```markdown
# Release [version/tag] - [date]

## Summary
[2-3 sentence overview: X features, Y bug fixes, Z infrastructure changes]

## Risk Level: [Low/Medium/High]

## Highlights
- [Most notable change 1]
- [Most notable change 2]

## Changes

### New Features
- [TICKET-123] Feature description (@author)
- [TICKET-456] Feature description (@author)

### Bug Fixes
- [TICKET-789] Fix description (@author)

### Security
- Upgraded dependency X from v1.2 to v1.3 (CVE-XXXX-YYYY)

### Infrastructure
- Increased ECS task memory from 512MB to 1024MB
- Added new DynamoDB table for feature X

### [WARN] Breaking Changes
- API endpoint /v1/foo deprecated, use /v2/foo

## Deployment Notes
- [Any special steps, feature flags to enable, migrations to run]

## Rollback Instructions
- [How to rollback if issues detected]
```

## Output

Produce a formatted changelog document suitable for:
1. Team communication (Slack/email)
2. Release documentation (wiki/Confluence)
3. Stakeholder review
4. Audit trail

Include a machine-readable summary with counts per category and risk assessment.