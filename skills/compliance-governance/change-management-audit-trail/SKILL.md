---
name: change-management-audit-trail
agent_type: "Generic"
description: Validates that all infrastructure changes follow the organization's
  change management process by correlating CloudTrail events with approved change
  tickets. Use this skill when auditing change control compliance, investigating
  unauthorized changes, or generating evidence for compliance certifications that
  require formal change management documentation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Change Management Audit Trail

Use this skill to validate that infrastructure changes are authorized,
documented, and follow the change management process.

## When to Activate

- Compliance audit requiring change management evidence (SOC2 CC8.1, ITIL).
- Investigating unauthorized changes detected by drift detection.
- Monthly change management compliance review.
- Post-incident: was the change that caused the incident properly approved?
- Validating that emergency changes were retroactively documented.

## Step 1: Retrieve Infrastructure Changes

Query CloudTrail for infrastructure-modifying API calls in the review period:

**High-impact change events to track:**

| Category | API Calls |
|----------|-----------|
| Compute | RunInstances, TerminateInstances, ModifyInstanceAttribute, UpdateService (ECS) |
| Networking | AuthorizeSecurityGroupIngress, CreateRoute, ModifySubnetAttribute |
| Data | CreateDBInstance, ModifyDBInstance, DeleteTable, PutBucketPolicy |
| IAM | CreateRole, PutRolePolicy, AttachUserPolicy, CreateAccessKey |
| Configuration | PutParameter, UpdateSecret, UpdateFunctionConfiguration |
| Infrastructure | CreateStack, UpdateStack, DeleteStack, ApplyTerraformPlan |
| Deployment | CreateDeployment, UpdateService, PublishVersion |

**For each change event, capture:**
- Timestamp
- API action
- Actor (IAM principal)
- Source IP
- User agent (console, CLI, SDK, IaC tool)
- Affected resource(s)
- Parameters/changes made
- Success/failure

## Step 2: Correlate with Change Tickets

For each detected change:

1. **Match to a change ticket** by:
   - Time window: change occurred within the approved change window.
   - Resource: changed resource matches the ticket scope.
   - Actor: person making the change matches ticket assignee.
   - Tags: resource tagged with change ticket ID.

2. **Classify correlation result:**
   - [PASS] **Correlated**: Change matches an approved ticket with correct window and actor.
   - [WARN] **Partially correlated**: Change has a related ticket but timing or scope differs.
   - [FAIL] **Uncorrelated**: No matching ticket found - potential unauthorized change.
   - [INFO] **Exempt**: Change type is pre-approved (auto-scaling, automated patching, CI/CD pipeline).

## Step 3: Validate Change Approval Status

For correlated changes, verify the ticket was properly approved:

1. Was the change ticket approved BEFORE the change was made?
2. Was the approval from an authorized approver?
3. Was a peer review completed (for code changes)?
4. Was the change window respected (not deployed outside approved time)?
5. Was a rollback plan documented?
6. Was post-change verification documented?

**Non-compliant scenarios:**
- Change deployed before ticket approval.
- Change deployed outside the approved window.
- Change made by someone other than the ticket assignee.
- Ticket missing required fields (rollback plan, testing evidence).
- Retroactive ticket creation (ticket created after the change).

## Step 4: Analyze Unauthorized Changes

For changes without matching tickets:

1. **Determine intent:**
   - Was it an automated action? (Auto Scaling, AWS-managed, pipeline-triggered)
   - Was it an emergency response? (incident mitigation - may be justified)
   - Was it accidental? (clickops in wrong account/environment)
   - Was it malicious? (unauthorized actor, suspicious timing)

2. **Assess risk:**
   - Did the change affect production?
   - Was it security-relevant? (IAM, security groups, encryption)
   - Could it have caused or masked an incident?
   - Was data potentially exposed?

3. **Determine required follow-up:**
   - Retroactive documentation needed (emergency changes).
   - Revert required (unauthorized modification).
   - Investigation required (suspicious activity).
   - Process improvement needed (gap in automation/guardrails).

## Step 5: Validate Emergency Change Process

Emergency changes are expected during incidents but need retroactive governance:

1. Was the emergency change documented within 24 hours?
2. Was retroactive approval obtained?
3. Was a post-incident review conducted?
4. Was the change permanent (needs a proper ticket) or temporary (needs revert)?
5. Is the emergency change process being overused? (>10% of changes are "emergency" suggests process gaming)

## Step 6: Assess Change Management Metrics

Calculate change management KPIs:

| Metric | Target | Calculation |
|--------|--------|-------------|
| Change compliance rate | > 95% | Correlated changes / total changes |
| Failed change rate | < 10% | Changes causing incidents / total changes |
| Emergency change rate | < 5% | Emergency changes / total changes |
| Mean lead time | < 24 hours | Time from ticket creation to deployment |
| Change backout rate | < 5% | Rolled-back changes / total changes |
| Unauthorized change rate | 0% | Uncorrelated non-exempt changes / total changes |

## Step 7: Identify Process Gaps

Based on findings, identify systemic issues:

- **No coverage for certain change types**: Some API actions not tracked.
- **Automation gaps**: Manual changes that should be automated (and thus pre-approved).
- **Ticket quality issues**: Tickets approved without proper review.
- **Emergency process abuse**: Too many "emergency" changes bypassing normal process.
- **Tooling gaps**: No integration between IaC pipeline and ticketing system.

## Output

Produce a change management audit report:
1. **Compliance Summary**: Total changes, correlated %, uncorrelated %, emergency %, compliance rate.
2. **Uncorrelated Changes Table**: Timestamp, actor, action, resource, risk level, follow-up action.
3. **Compliance Trend Chart**: Monthly change compliance rate over time.
4. **Emergency Changes Table**: Change, timestamp, justification, retroactive approval status.
5. **Change Metrics Dashboard**: KPIs vs targets with trend indicators.
6. **Process Gaps Identified**: Systemic issues and recommended improvements.
7. **Audit Evidence Package**: Formatted for auditor consumption with sampling methodology and findings.