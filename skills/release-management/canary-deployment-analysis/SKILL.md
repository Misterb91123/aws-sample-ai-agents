---
name: canary-deployment-analysis
agent_type: "Generic"
description: Analyzes canary deployment metrics to determine whether a release
  should be promoted to full production or rolled back. Use this skill during
  active canary deployments to compare canary vs baseline metrics and make
  data-driven promotion decisions for CodeDeploy, ECS, or Lambda deployments.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Canary Deployment Analysis

Use this skill during an active canary deployment to analyze whether the
new release is performing acceptably compared to the baseline.

## When to Activate

- A canary deployment is in progress and needs evaluation.
- CodeDeploy canary/linear deployment step is pending promotion.
- ECS deployment with deployment circuit breaker needs assessment.
- Lambda alias traffic shifting is in progress.
- Someone asks "should we promote or roll back this canary?"

## Step 1: Identify the Canary Deployment

Gather deployment context:
1. Identify the deployment mechanism (CodeDeploy, ECS, Lambda alias, custom).
2. Determine the traffic split (% to canary vs baseline).
3. Identify how long the canary has been receiving traffic.
4. Note the minimum bake time required before promotion.

## Step 2: Define Comparison Metrics

Select key metrics to compare canary vs baseline:

**Mandatory Metrics (must pass):**
- Error rate (5xx / total requests)
- Latency p50, p95, p99
- Availability (successful health checks / total checks)

**Service-Specific Metrics (evaluate if available):**
- Business metrics (conversion rate, transaction success rate)
- Resource utilization (CPU, memory - higher may indicate regression)
- Downstream error rates (is the canary causing errors in dependencies?)
- Log error volume (new error patterns in canary logs)

## Step 3: Retrieve Canary Metrics

1. Call `query_cloudwatch_metrics` for the canary target group / task set / alias:
   - ALB target group metrics (if using weighted target groups)
   - ECS service metrics for the new task set
   - Lambda alias invocation metrics
2. Retrieve the same metrics for the baseline (current production) over the same time window.
3. Ensure the comparison window has sufficient sample size (minimum 100 requests for statistical significance).

## Step 4: Statistical Comparison

Compare canary to baseline for each metric:

| Metric | Baseline | Canary | Delta | Verdict |
|--------|----------|--------|-------|---------|
| Error rate | X% | Y% | +/- Z% | Pass/Fail |
| Latency p50 | Xms | Yms | +/- Zms | Pass/Fail |
| Latency p99 | Xms | Yms | +/- Zms | Pass/Fail |

**Pass criteria:**
- Error rate: canary error rate <= baseline + 0.5% (absolute) or <= 1.5x baseline (relative)
- Latency p50: canary <= baseline + 20% 
- Latency p99: canary <= baseline + 30%
- No new error types (errors present in canary that don't exist in baseline)

**Auto-fail criteria:**
- Canary error rate > 5% (absolute)
- Canary latency p99 > 2x baseline
- Health check failures in canary targets
- OOMKilled or CrashLoopBackOff in canary tasks

## Step 5: Log Analysis

Check canary logs for concerning patterns:
1. Query CloudWatch Logs for the canary task/function specifically.
2. Compare error log volume: canary vs baseline.
3. Look for new exception types not present in baseline.
4. Check for panic, fatal, or unhandled error patterns.

## Step 6: Promotion Decision

Based on analysis:

| Decision | Criteria |
|----------|----------|
| [PASS] PROMOTE | All metrics pass, bake time met, no new errors |
| [WAIT] EXTEND | Metrics borderline or insufficient sample size - extend bake time |
| [FAIL] ROLLBACK | Any auto-fail criteria met, or multiple metrics degraded |

## Step 7: Execute Decision

**If PROMOTE:**
1. Advance deployment to next stage (full rollout).
2. Continue monitoring for 15 minutes post-promotion.
3. Keep previous version available for rapid rollback.

**If ROLLBACK:**
1. Trigger immediate rollback (CodeDeploy stop, ECS task definition revert).
2. Verify baseline recovery.
3. Document failure reason for the team.

**If EXTEND:**
1. Maintain current traffic split.
2. Set timer for re-evaluation (typically 15-30 minutes).
3. Alert if metrics worsen during extension.

## Output

Provide a canary analysis report:
1. Comparison table of all metrics (canary vs baseline)
2. Clear PROMOTE / EXTEND / ROLLBACK recommendation
3. Confidence level (high/medium/low) based on sample size
4. If rollback recommended: specific metric(s) that failed and by how much
5. If promote recommended: confirmation of bake time and metric thresholds met