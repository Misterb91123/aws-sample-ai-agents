---
name: access-review-auditor
agent_type: "Generic"
description: Performs periodic access reviews to validate that user and service
  permissions remain appropriate, identifying stale access, excessive privileges,
  and orphaned accounts. Use this skill for quarterly access reviews, compliance
  audits requiring evidence of access governance, or when investigating whether
  access controls contributed to a security incident.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Access Review Auditor

Use this skill to perform periodic access reviews ensuring all IAM entities
have appropriate, current permissions aligned with job functions.

## When to Activate

- Quarterly access review cycle.
- Employee offboarding - verify access removal is complete.
- Compliance audit requiring access review evidence (SOC2, ISO 27001).
- Post-incident: validating access controls were appropriate.
- Role change: employee moved teams, old access should be revoked.

## Step 1: Inventory All Access Entities

Collect a complete access inventory:

**IAM Users:**
1. List all IAM users across accounts.
2. For each: last console sign-in, last API activity, MFA status.
3. Flag users with no activity in 90+ days.
4. Identify users vs service accounts (naming convention or tag).

**IAM Roles:**
1. List all IAM roles.
2. For each: last assumed date, trust policy (who can assume it).
3. Flag roles not assumed in 90+ days.
4. Classify: human-assumed roles vs service roles vs cross-account roles.

**SSO/Identity Center Users:**
1. List all SSO users and their permission sets.
2. Map permission sets to AWS accounts they grant access to.
3. Identify overly broad permission sets (AdministratorAccess assigned).

**Service Accounts:**
1. List IAM users used for programmatic access (access keys only, no console).
2. For each: what service/application uses it, key age, last used.

## Step 2: Validate Human Access

For each human user/identity:

1. **Role alignment**: Does their access match their current job function?
   - Developer: read/write to development accounts, read-only to production.
   - SRE/DevOps: appropriate production access for operational tasks.
   - Manager: read-only or no direct access (delegates to team).
   - Former employee: should have ZERO access.

2. **Least privilege check**: 
   - Are they using all the permissions granted?
   - Check IAM Access Advisor: which services were actually used?
   - Flag services granted but never accessed in 90 days.

3. **Cross-account access**:
   - Which accounts can this user access?
   - Is access to production accounts justified and approved?
   - Are there unnecessary cross-account role assumptions?

4. **Credential hygiene**:
   - Password age (should be < 90 days or using SSO).
   - MFA enabled (mandatory for all human users).
   - Access key age (should be < 90 days).
   - Multiple active access keys (usually indicates rotation in progress or forgotten key).

## Step 3: Validate Service Account Access

For each service account / application role:

1. **Necessity**: Is this service account still needed? Is the application still running?
2. **Scope**: Does it have only the permissions the application requires?
3. **Key rotation**: When was the access key last rotated?
4. **Monitoring**: Is usage being monitored for anomalies?
5. **Documentation**: Is the purpose of this service account documented?

## Step 4: Identify Stale Access

Flag access that should be revoked:

| Condition | Action |
|-----------|--------|
| IAM user never logged in | Investigate and likely remove |
| No activity for 90+ days | Flag for review with team lead |
| No activity for 180+ days | Disable immediately, schedule deletion |
| Former employee account exists | Critical - remove immediately |
| Access key unused for 90+ days | Deactivate the key |
| Role unused for 90+ days | Review, potentially remove |
| SSO user for departed employee | Remove SSO assignment |

## Step 5: Check Separation of Duties

Validate that no single identity has conflicting permissions:

1. **Admin + user**: Same person shouldn't be both IAM admin and regular user.
2. **Deploy + approve**: Same person shouldn't approve and execute deployments.
3. **Audit + modify**: Auditors shouldn't have modify access to audited resources.
4. **Billing + provisioning**: Financial approver shouldn't also provision resources.

**Detection method:**
- Identify users with multiple role memberships.
- Check for users with both read and write access to sensitive systems.
- Flag users with AdministratorAccess who also have day-to-day user tasks.

## Step 6: Validate Emergency Access (Break-Glass)

Review emergency/break-glass access mechanisms:

1. Do break-glass accounts exist for emergencies?
2. Are they protected with strong authentication?
3. Is usage monitored and alerted on?
4. Is there a log review process after each use?
5. When was the last time break-glass was used?
6. Is the process documented and tested?

## Step 7: Generate Review Actions

For each finding, determine the required action:

| Action | Description | SLA |
|--------|-------------|-----|
| Revoke | Remove access entirely | Immediate (departed) or 7 days |
| Reduce | Scope down to actual needed permissions | 14 days |
| Rotate | Rotate credentials (old keys) | 7 days |
| Confirm | Access is appropriate, document approval | Review cycle end |
| Investigate | Unclear purpose, needs team input | 7 days |
| Accept | Known exception with documented justification | Document and tag |

## Output

Produce an access review report:
1. **Summary**: Total identities reviewed, compliant count, actions needed, critical findings.
2. **Stale Access Table**: Identity, type, last activity, days idle, recommended action, owner.
3. **Over-Privileged Accounts Table**: Identity, permissions granted, permissions used, excess permissions, recommendation.
4. **Credential Hygiene Table**: Identity, MFA status, password age, key age, key last used, issues.
5. **Separation of Duties Findings**: Identity, conflicting permissions, risk, recommendation.
6. **Action Items by Owner**: Grouped by team lead/manager who needs to confirm or revoke.
7. **Compliance Evidence**: Summary suitable for auditor review (review performed, date, scope, findings, actions).