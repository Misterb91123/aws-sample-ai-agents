---
name: rollback-decision-framework
agent_type: "Incident Mitigation"
description: Provides a structured decision framework for determining when and how
  to roll back a production deployment. Use this skill when a deployment shows signs
  of degradation and the team needs to decide between rollback, forward-fix, or
  continued monitoring based on impact severity and fix complexity.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Rollback Decision Framework

Use this skill when a production deployment shows signs of degradation and
the team needs to decide between rolling back, pushing a forward-fix, or monitoring.

## When to Activate

- Post-deployment metrics show degradation.
- Health checks are failing for new deployment targets.
- Customer-facing errors increased after deployment.
- On-call engineer is debating "should we roll back?"

## Step 1: Assess the Situation

Gather current state:
1. What changed? Identify the specific deployment (commit, image tag, config change).
2. How long has it been deployed?
3. What's the current impact? (error rate, latency, customer-visible)
4. Is the impact growing, stable, or shrinking?
5. Are there other changes in flight that could contribute?

## Step 2: Apply the Rollback Decision Matrix

| Factor | Roll Back | Forward Fix | Monitor |
|--------|-----------|-------------|---------|
| Customer impact | Active and growing | Minor or static | None yet, metrics borderline |
| Fix complexity | Unknown or > 30 min | Known fix < 15 min | N/A |
| Fix confidence | Low | High (root cause clear) | N/A |
| Data impact | No data corruption | No data corruption | No data corruption |
| Time deployed | < 2 hours | > 2 hours | < 30 min (too early to tell) |

**Always roll back if:**
- Error rate > 10% and growing
- Data corruption or loss detected
- Security vulnerability introduced
- Multiple services cascading failures
- Fix ETA unknown or > 30 minutes

**Consider forward fix if:**
- Root cause is clear and fix is trivial (< 15 minutes)
- Rollback itself carries risk (database migration applied, breaking schema change)
- Impact is minor and stable (not growing)
- The fix is already coded and tested

**Monitor if:**
- Impact is < baseline + 2% error rate
- Metrics are fluctuating (may be transient)
- Deployed < 15 minutes ago (insufficient data)

## Step 3: Evaluate Rollback Risk

Not all rollbacks are risk-free. Assess:

1. **Database migrations**: Was a schema migration applied?
   - Forward-only migration (add column, new table): safe to rollback (old code ignores new schema)
   - Breaking migration (drop column, rename): CANNOT safely rollback without data migration
   
2. **API contract changes**: Did the deployment change API contracts?
   - Additive changes (new fields): safe to rollback
   - Breaking changes (removed fields, changed types): may break existing consumers
   
3. **State changes**: Did the new code modify persistent state?
   - If new code wrote data in a new format, can old code read it?
   
4. **Cache invalidation**: Did the deployment change cache keys or strategies?
   - Rollback may cause cache miss storm

5. **External dependencies**: Did the deployment integrate with a new external service?
   - Other services may now depend on the new behavior

## Step 4: Execute the Decision

### If Rolling Back:

**ECS Service:**
```
1. Identify previous stable task definition revision
2. Update service to use previous task definition
3. Force new deployment
4. Monitor until running count matches desired count
5. Verify ALB health checks pass
```

**CodeDeploy:**
```
1. Stop current deployment (if in-progress)
2. Create a new deployment with the previous revision
3. OR use automatic rollback if configured
4. Verify deployment completes and health checks pass
```

**Lambda:**
```
1. Update alias to point to previous version
2. OR shift traffic weight back to 0% for new version
3. Verify function invocations succeed
```

**CloudFormation:**
```
1. If stack update in progress: cancel update
2. If completed: initiate rollback (update with previous template)
3. Monitor stack events for rollback completion
```

### If Forward-Fixing:

1. Communicate to incident channel: "Proceeding with forward fix, ETA X minutes"
2. Fast-track the fix through CI (skip non-essential stages if appropriate)
3. Deploy the fix using the same deployment mechanism
4. Set a hard timer: if fix not deployed within agreed time, auto-escalate to rollback

### If Monitoring:

1. Set a review timer (15 minutes)
2. Define specific conditions that would trigger escalation to rollback
3. Actively monitor - do not walk away
4. If metrics worsen at any point, immediately escalate to rollback decision

## Step 5: Post-Rollback Verification

After rollback completes:
1. Verify error rate returns to pre-deployment baseline.
2. Verify latency returns to pre-deployment baseline.
3. Check for data inconsistencies introduced during the degraded window.
4. Confirm customer-facing functionality restored.
5. Communicate resolution to stakeholders.

## Output

Provide a clear decision recommendation:
1. Recommended action: ROLLBACK / FORWARD FIX / MONITOR
2. Justification (which criteria in the matrix drove the decision)
3. Specific rollback procedure for the deployment type
4. Risk factors to be aware of during rollback
5. Post-rollback verification steps