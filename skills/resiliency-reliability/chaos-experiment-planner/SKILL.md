---
name: chaos-experiment-planner
agent_type: "Generic"
description: Designs and plans chaos engineering experiments to validate resilience
  hypotheses for AWS infrastructure. Use this skill when preparing fault injection
  tests, planning GameDay exercises, or when validating that failover mechanisms
  work as expected before relying on them during real incidents.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Chaos Experiment Planner

Use this skill to design safe, controlled chaos experiments that validate
your infrastructure's resilience against specific failure modes.

## When to Activate

- Planning a GameDay or chaos engineering exercise.
- Validating a new failover mechanism before relying on it.
- Post-incident: testing that the fix prevents recurrence.
- New service deployed to production and needs resilience validation.
- Periodic resilience verification (quarterly recommended).

## Step 1: Define the Hypothesis

Every chaos experiment starts with a hypothesis:

**Template:**
"We believe that when [failure condition], [system/service] will [expected behavior],
and [customer impact metric] will remain within [acceptable threshold]."

**Examples:**
- "When we terminate 50% of EC2 instances in us-east-1a, the ALB will route traffic
  to healthy instances in other AZs, and error rate will not exceed 0.5% during recovery."
- "When we inject 500ms latency to the RDS primary, the application circuit breaker
  will open within 10 seconds and serve cached responses, maintaining p99 < 2s."

## Step 2: Select the Failure Mode

Choose what to test:

### Infrastructure Failures
| Failure | How to Inject | Tests |
|---------|---------------|-------|
| EC2 instance termination | Terminate random instances | Auto Scaling recovery |
| AZ impairment | Block traffic to/from one AZ | Multi-AZ failover |
| EBS volume failure | Detach or pause I/O | Storage resilience |
| Network partition | Modify security groups/NACLs | Split-brain handling |
| DNS failure | Return NXDOMAIN for service | DNS failover, caching |

### Application Failures
| Failure | How to Inject | Tests |
|---------|---------------|-------|
| Dependency latency | Inject delay via proxy/FIS | Circuit breakers, timeouts |
| Dependency errors | Return 500s from downstream | Retry logic, fallbacks |
| Memory pressure | Allocate memory via stress tool | OOM handling, auto-scaling |
| CPU saturation | CPU stress on instances | Throttling, auto-scaling |
| Disk exhaustion | Fill disk to capacity | Graceful degradation, alerting |

### Data Failures
| Failure | How to Inject | Tests |
|---------|---------------|-------|
| Database failover | Force RDS failover | Connection handling, retry |
| Cache failure | Flush or terminate cache | Thundering herd protection |
| Corrupt responses | Inject bad data via proxy | Input validation, error handling |

## Step 3: Define Experiment Scope

Establish boundaries for the experiment:

1. **Blast radius control:**
   - Start with the smallest possible scope (single instance, single AZ, canary traffic only)
   - Define maximum acceptable impact before auto-abort
   - Never run first experiments directly on production - start in staging

2. **Duration:**
   - Define how long the failure will be injected
   - Set a maximum experiment duration (e.g., 30 minutes)
   - Include cool-down/observation time after injection

3. **Abort criteria:**
   - Customer error rate > X%
   - Latency p99 > Xms
   - Health check failures on Y% of targets
   - Manual abort trigger (panic button)
   - Any SEV1 incident opens

4. **Scheduling:**
   - Run during business hours (people available to respond)
   - Avoid peak traffic periods for early experiments
   - Avoid deployment freeze periods
   - Ensure relevant team members are present and aware

## Step 4: Pre-Experiment Checklist

Before running the experiment:

- [ ] Hypothesis documented and agreed upon
- [ ] Rollback procedure tested and ready
- [ ] Monitoring dashboards open and baseline captured
- [ ] All relevant teams notified (SRE, service owners, support)
- [ ] Abort criteria defined and monitoring set up
- [ ] No active incidents or deployments in progress
- [ ] On-call engineer aware and available
- [ ] Experiment scope limited (not full production for first run)
- [ ] Customer communication prepared (if customer-visible impact possible)
- [ ] AWS FIS experiment configured (if using FIS)

## Step 5: Design Observation Plan

Define what to observe during the experiment:

**Primary metrics (determines pass/fail):**
- Customer-facing error rate
- Customer-facing latency
- Availability of critical operations

**Secondary metrics (understanding behavior):**
- Auto Scaling activity (launch, terminate events)
- Health check status changes
- Circuit breaker state changes
- Queue depth / backlog growth
- Connection pool utilization
- Recovery time after injection ends

**Logs to watch:**
- Application error logs for new exception types
- Connection timeout errors
- Retry exhaustion events
- Failover events

## Step 6: Document the Experiment

Structure the experiment document:

```markdown
# Experiment: [Name]

## Hypothesis
[What we believe will happen]

## Failure Mode
[What we're injecting and how]

## Scope
- Environment: [staging/production/canary]
- Blast radius: [X instances / Y% traffic / one AZ]
- Duration: [injection time + observation time]

## Abort Criteria
- [Specific metric thresholds that trigger abort]

## Procedure
1. [Step-by-step injection procedure]
2. [Observation steps]
3. [Rollback steps]

## Expected Outcome
- [What metrics should show]
- [What recovery time is acceptable]

## Actual Outcome
- [Filled in after experiment]

## Findings
- [What worked]
- [What didn't work]
- [Action items]
```

## Step 7: Post-Experiment Analysis

After the experiment:
1. Did the system behave as hypothesized? (pass/fail)
2. What was the actual recovery time?
3. Were there unexpected side effects?
4. Did monitoring detect the failure correctly and timely?
5. Would on-call have been alerted appropriately?
6. What action items are needed to improve resilience?

## Output

Produce an experiment plan:
1. **Experiment Summary**: Hypothesis, failure mode, scope, expected outcome.
2. **Pre-Flight Checklist**: All prerequisites validated.
3. **Step-by-Step Procedure**: Detailed injection and observation steps.
4. **Abort Procedure**: How to stop the experiment immediately.
5. **Observation Dashboard**: Metrics and logs to monitor.
6. **Risk Assessment**: What could go wrong and mitigations.
7. **Post-Experiment Report Template**: Structure for documenting findings.