---
name: self-healing-pattern-designer
agent_type: "Generic"
description: Designs self-healing automation patterns that detect and automatically
  remediate common infrastructure failures without human intervention. Use this
  skill when building automated remediation for recurring incidents, designing
  auto-recovery mechanisms for critical services, or when implementing the
  self-healing capabilities that reduce on-call burden.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Self-Healing Pattern Designer

Use this skill to design automated detection and remediation systems that
fix common failures before they become incidents.

## When to Activate

- Same failure mode has occurred 3+ times and requires the same fix each time.
- On-call team wants to reduce after-hours pages for known issues.
- Building resilience into a new critical service.
- Post-incident action item: "make this self-healing."
- Evaluating which failures should auto-remediate vs alert a human.

## Step 1: Identify Self-Healing Candidates

A failure is a good self-healing candidate if:

| Criteria | Required | Reason |
|----------|----------|--------|
| Known root cause | [PASS] | Must know WHAT to fix |
| Known remediation | [PASS] | Must know HOW to fix |
| Deterministic detection | [PASS] | Must reliably detect without false positives |
| Safe remediation | [PASS] | Fix doesn't cause worse problems |
| Recurring pattern | [PASS] | Worth the automation investment |
| Reversible action | Preferred | Can undo if remediation makes things worse |
| Fast remediation | Preferred | Fixes before customers notice |

**Good self-healing candidates:**
- Instance health check failure -> replace instance.
- Disk filling up -> clear old logs or expand volume.
- Memory leak -> restart service (while investigating root cause).
- Connection pool exhausted -> restart application pod.
- Certificate expiring -> trigger renewal.
- DLQ growing -> reprocess messages.
- Task crash looping -> rollback to previous task definition.

**Poor self-healing candidates:**
- Novel failures never seen before.
- Data corruption (remediation unclear without investigation).
- Security incidents (need investigation, not just remediation).
- Cascading failures with unclear root cause.
- Performance degradation with multiple possible causes.

## Step 2: Design Detection Mechanism

For each self-healing pattern, define precise detection:

### CloudWatch Alarm-Based Detection
```
Detect: Service health check failing
Signal: ALB HealthyHostCount < desired count for > 2 minutes
Confidence: High (very specific signal)
False positive rate: Low (health check is reliable)
```

### Metric Anomaly Detection
```
Detect: Memory leak approaching OOM
Signal: MemoryUtilization > 85% AND trending upward (derivative positive for 10 min)
Confidence: Medium (could be legitimate load increase)
Additional check: Compare with request volume (if traffic flat, it's a leak)
```

### Log Pattern Detection
```
Detect: Connection pool exhausted
Signal: CloudWatch Logs filter for "HikariPool-1 - Connection is not available"
Confidence: High (specific error message)
Threshold: > 5 occurrences in 1 minute
```

### Event-Based Detection
```
Detect: ECS task crashed
Signal: ECS task state change event (STOPPED with reason != user-initiated)
Confidence: High (direct event from ECS)
Additional check: stopCode = EssentialContainerExited
```

## Step 3: Design Remediation Action

For each pattern, define the fix:

### Pattern: Instance Health Failure
```
Detection: ALB unhealthy targets > 0 for 3 minutes
Remediation:
  1. Check if instance is in ASG (if yes, ASG handles replacement - just verify)
  2. If standalone instance: reboot instance
  3. Wait 2 minutes for recovery
  4. If still unhealthy: terminate and let ASG replace
  5. If no ASG: alert human (can't safely self-heal)
Guardrails:
  - Don't terminate more than 1 instance per 10 minutes
  - Don't terminate if HealthyHostCount would drop below minimum
```

### Pattern: Disk Space Critical
```
Detection: DiskSpaceUtilization > 90%
Remediation:
  1. Identify largest log files older than 7 days -> delete
  2. Clear package manager cache (apt, yum)
  3. Compress logs older than 3 days
  4. If still > 90%: expand EBS volume by 20%
  5. If expansion fails: alert human
Guardrails:
  - Never delete files less than 24 hours old
  - Never delete files outside /var/log and /tmp
  - Maximum one volume expansion per day
```

### Pattern: Service Memory Leak
```
Detection: Memory > 85% AND stable/growing while traffic is flat
Remediation:
  1. Trigger graceful restart (SIGTERM -> wait -> SIGKILL if needed)
  2. One instance at a time (rolling restart)
  3. Wait for health check to pass before restarting next
  4. Limit to 2 restarts per hour per service
Guardrails:
  - Don't restart if only 1 instance is healthy
  - Don't restart during active deployment
  - If restarted 3 times in 24 hours: alert human (leak needs code fix)
```

### Pattern: Stuck ECS Task
```
Detection: ECS task in RUNNING state but failing health checks for > 5 minutes
Remediation:
  1. Stop the unhealthy task (ECS will replace it automatically)
  2. Verify replacement task starts and passes health check
  3. If new task also fails: rollback to previous task definition
  4. If rollback also fails: alert human
Guardrails:
  - Don't stop tasks during active deployment
  - Keep minimum 1 healthy task at all times
  - Maximum 3 task replacements per 30 minutes
```

## Step 4: Design Feedback Loops

Self-healing must know if it's working:

### Success Verification
After remediation, verify:
1. The original detection signal has cleared (alarm -> OK).
2. Service metrics returned to normal (error rate, latency).
3. No new issues introduced by the remediation.
4. Wait period: verify stability for N minutes after fix.

### Failure Escalation
If remediation doesn't work:
1. First attempt failed -> retry once with longer wait.
2. Second attempt failed -> escalate to human (page on-call).
3. Include full context: what was detected, what was tried, current state.
4. DO NOT keep retrying indefinitely (automation loop protection).

### Learning Loop
Track self-healing effectiveness over time:
1. How often does each pattern trigger?
2. What's the success rate?
3. Are there patterns where it triggers but shouldn't (false positive)?
4. Are there new failure modes that should become self-healing?

## Step 5: Implement with AWS Services

| Component | AWS Service |
|-----------|-------------|
| Detection | CloudWatch Alarms -> EventBridge |
| Orchestration | Step Functions (complex) or Lambda (simple) |
| EC2 actions | Systems Manager Automation |
| ECS actions | Lambda calling ECS APIs |
| Notifications | SNS -> Slack/PagerDuty |
| Rate limiting | DynamoDB (execution counter with TTL) |
| Audit trail | CloudWatch Logs + S3 |
| Circuit breaker | Step Functions with state tracking |

## Step 6: Safety Architecture

Prevent automation from causing outages:

```
[Detection]
    down
[Pre-check: Is it safe to act?]
  - Is blast radius acceptable?
  - Is rate limit not exceeded?
  - Is there an active deployment? (skip if yes)
  - Is there an active incident? (skip if yes, let humans handle)
  - Are enough healthy instances remaining?
    down (safe)
[Execute Remediation]
    down
[Verify Success]
  - Did the fix work?
    +-- Yes -> Log success, notify (low priority)
    +-- No -> Escalate to human, stop self-healing for this pattern
```

## Output

Produce a self-healing design document:
1. **Pattern Catalog**: Each self-healing pattern with detection, remediation, guardrails.
2. **Architecture Diagram**: AWS services, event flow, and feedback loops.
3. **Safety Controls Matrix**: Guardrails per pattern with rate limits and circuit breakers.
4. **Implementation Plan**: Service-by-service rollout with shadow -> active phases.
5. **Success Metrics**: Expected reduction in pages, MTTR improvement, success rate targets.
6. **Monitoring Dashboard Design**: Panels for tracking self-healing activity and effectiveness.
7. **Escalation Paths**: When each pattern gives up and alerts a human.