---
name: infrastructure-drift-detector
agent_type: "Generic"
description: Detects configuration drift between infrastructure-as-code definitions
  and actual deployed state in AWS. Use this skill when auditing for manual changes
  (clickops), validating IaC accuracy, or when investigating unexpected behavior
  that may be caused by untracked configuration changes.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Infrastructure Drift Detector

Use this skill to identify resources whose actual configuration has drifted
from their infrastructure-as-code definitions.

## When to Activate

- Regular compliance audit (weekly/monthly).
- Post-incident: checking if manual changes contributed to the issue.
- Before IaC apply/deploy: ensuring no untracked state will be overwritten.
- Team reports "something changed but we didn't deploy anything."
- Onboarding a new service to IaC that was previously managed manually.

## Step 1: Identify IaC-Managed Resources

Determine what is supposed to be managed by IaC:
1. CloudFormation stacks - list all stacks and their resources.
2. Terraform state - list all resources in state files.
3. CDK deployments - synthesized CloudFormation stacks.
4. Resources with `ManagedBy` tag indicating IaC tool.

## Step 2: Detect CloudFormation Drift

For each CloudFormation stack:
1. Initiate drift detection: `aws cloudformation detect-stack-drift`.
2. Retrieve drift results: `aws cloudformation describe-stack-resource-drifts`.
3. For each drifted resource, capture:
   - Resource type and logical ID
   - Drift status (MODIFIED, DELETED, NOT_CHECKED)
   - Properties that differ (expected vs actual)
   - Timestamp of last known good state

**Drift categories:**
- **MODIFIED**: Resource exists but configuration differs from template.
- **DELETED**: Resource defined in template but doesn't exist.
- **NOT_CHECKED**: Resource type doesn't support drift detection.

## Step 3: Identify Manual Changes via CloudTrail

For drifted resources, investigate who made the change:
1. Query CloudTrail for API calls that modified the resource.
2. Identify the actor (IAM user, role, service).
3. Determine the timestamp of the modification.
4. Check if the change was made through the IaC pipeline (expected) or directly (drift).

**Signals of manual change (clickops):**
- API call source is `console.amazonaws.com` (AWS Console).
- API call made by a human IAM user (not a service role or pipeline role).
- No corresponding git commit or deployment around the same timestamp.
- `userAgent` indicates console or direct CLI usage.

## Step 4: Classify Drift Severity

| Severity | Criteria | Examples |
|----------|----------|---------|
| Critical | Security-impacting drift | Security group rules opened, IAM policy changed, encryption disabled |
| High | Availability-impacting drift | Auto Scaling min capacity reduced, health check modified, AZ removed |
| Medium | Operational drift | Instance type changed, tags modified, logging disabled |
| Low | Cosmetic drift | Description changed, non-functional tags added |

## Step 5: Assess Drift Risk

For each drifted resource:
1. **Revert risk**: If IaC is applied now, will the revert cause disruption?
   - Security group change may drop active connections.
   - Instance type change requires stop/start.
   - Scaling changes may terminate instances.
2. **Leaving as-is risk**: If drift is left unmanaged, what could go wrong?
   - IaC state is inaccurate - future deploys may overwrite the manual fix.
   - Other environments won't have the same change (inconsistency).
   - Change is undocumented (knowledge loss).
3. **Was the manual change intentional?**: Check if it was an emergency hotfix during an incident.

## Step 6: Find Unmanaged Resources

Identify resources that exist in AWS but are NOT tracked by any IaC:

1. Compare deployed resources (from AWS resource inventory) against IaC state.
2. Resources without IaC references or `ManagedBy` tags are likely unmanaged.
3. Prioritize by cost and criticality:
   - Expensive unmanaged resources (production RDS, large EC2).
   - Security-sensitive unmanaged resources (IAM roles, security groups).
   - Orphaned resources that may be waste.

## Step 7: Generate Remediation Plan

For each drift finding:

| Remediation Option | When to Use |
|-------------------|-------------|
| Update IaC to match reality | Manual change was correct and intentional |
| Revert to IaC state | Manual change was unauthorized or incorrect |
| Import into IaC | Unmanaged resource that should be managed |
| Delete resource | Unmanaged resource that is no longer needed |
| Accept with exception | Temporary drift with documented reason and expiry |

## Prevention Recommendations

1. **Detect**: Enable AWS Config rules for change detection.
2. **Prevent**: Use SCPs to restrict direct console modifications in production.
3. **Alert**: CloudTrail + EventBridge rule for manual changes -> notification.
4. **Enforce**: Restrict production IAM to pipeline roles only (no human write access).
5. **Audit**: Schedule drift detection runs weekly.

## Output

Produce a drift detection report:
1. **Summary**: Total resources checked, drift count, unmanaged count, critical findings.
2. **Drifted Resources Table**: Resource, stack/module, drift type, properties changed, severity, who changed it, when.
3. **Unmanaged Resources Table**: Resource, type, account, region, estimated cost, recommended action.
4. **Critical Drift Findings**: Security and availability impacting drift requiring immediate attention.
5. **Drift by Stack/Module Chart**: Bar chart showing drift count per IaC unit.
6. **Remediation Recommendations**: Per-finding action plan (revert, adopt, delete, accept).
7. **Prevention Controls**: Recommended guardrails to reduce future drift.