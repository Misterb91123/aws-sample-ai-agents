---
name: connect-queue-and-routing-health
agent_type: "Incident RCA"
description: Provides investigation procedures for Amazon Connect queue backlogs and
  routing problems, including rising queue size and oldest-contact-age, service-level
  breaches, high abandonment rate, agents sitting idle while a queue backs up due to
  routing-profile misconfiguration, and quick-connect or hours-of-operation issues.
  Use this skill when customers wait too long, when service level drops below target,
  when abandonment climbs, or when available agents are not receiving contacts from a
  backed-up queue.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Amazon Connect Queue and Routing Health

Use this skill to diagnose queue backlogs and routing failures in Amazon Connect.
Investigation is read-only; any fix is specific and reversible.

## When to Activate

- Queue size and Oldest contact age are rising in real time.
- Service level (percent answered within X seconds) drops below target.
- Abandonment rate climbs above baseline.
- Agents show Available while a queue backs up (contacts not delivered).
- Average queue answer time increases sharply.
- Quick connects fail to transfer, or contacts arrive outside hours of operation.

## Step 1: Read Real-Time Metrics

Use GetCurrentMetricData for the affected queue(s):

- `CONTACTS_IN_QUEUE` (queue size) and `OLDEST_CONTACT_AGE`.
- `AGENTS_AVAILABLE`, `AGENTS_ON_CALL` (on contact), `AGENTS_AFTER_CONTACT_WORK`
  (ACW), `AGENTS_STAFFED`, `AGENTS_ONLINE`.
- `SLOTS_ACTIVE` and `SLOTS_AVAILABLE`.

Snapshot the decision signal: a growing queue size with `AGENTS_AVAILABLE > 0` is
a routing problem, not a staffing problem. A growing queue with zero available and
high occupancy is a capacity/staffing problem.

## Step 2: Compute Service Level and Abandonment

Use GetMetricDataV2 over the incident window:

- Service level: `SERVICE_LEVEL` at the configured threshold (for example 80
  percent answered within 20 seconds). Compare against the target; a drop from 80+
  to the 50-60 range signals a real breach.
- Abandonment: `CONTACTS_ABANDONED` divided by `CONTACTS_QUEUED`. Baseline is
  often 2-5 percent; sustained values above roughly 10 percent indicate customers
  giving up before answer.
- `AVG_QUEUE_ANSWER_TIME` and `CONTACTS_HANDLED` to see whether throughput
  collapsed or demand surged.

## Step 3: Inspect Routing Profiles and Staffing vs Occupancy

1. List routing profiles (ListRoutingProfiles, DescribeRoutingProfile) and confirm
   the backed-up queue is actually in the profile assigned to available agents,
   with a priority and delay that lets it be served.
2. Verify channel concurrency in the routing profile (voice, chat, task) allows
   the contact type currently queued.
3. Compare Occupancy against Availability: high `AGENTS_AVAILABLE` with a full
   queue means the queue is missing from profiles or has a large routing delay.
   Occupancy near 100 percent with high ACW means agents are stuck in After
   contact work.
4. Check agent Not Responding / Missed contacts (`CONTACTS_MISSED`); repeated
   misses pull agents out of routing and starve the queue.

## Step 4: Find the Misroute

1. Confirm the contact flow sets the intended working queue before Transfer to
   queue (DescribeContactFlow), and that priority/routing steps match design.
2. Validate hours of operation for the queue (DescribeQueue -> HoursOfOperationId);
   contacts arriving out of hours follow the closed branch and may pile in an
   unstaffed overflow queue.
3. Check quick connects (ListQuickConnects) used for transfers; a quick connect
   pointing at a disabled or empty queue silently strands contacts.
4. Verify the queue is not disabled and its max contacts setting is not clamping
   delivery (DescribeQueue).

## Step 5: Distinguish Demand Surge from Capacity Loss

| Pattern | Queue Size | Agents Available | Occupancy | Root Cause |
|---------|-----------|------------------|-----------|-----------|
| Routing gap | Rising | > 0 | Low | Queue missing from routing profile |
| Understaffed | Rising | 0 | ~100% | Not enough staffed agents |
| ACW trap | Rising | ~0 | High, high ACW | Agents stuck in After contact work |
| Demand surge | Rising fast | 0 | ~100% | Contact arrivals exceed capacity |
| Closed/overflow | Rising | 0 | Low | Out of hours or wrong overflow queue |

## Step 6: Remediate

Recommend specific, reversible fixes:

- Add the queue to the correct routing profile(s) or reduce its routing delay.
- Adjust routing-profile channel concurrency to admit the queued contact type.
- Reassign or add staffed agents to the routing profile; coach down excessive ACW.
- Correct hours of operation, quick-connect targets, or overflow queue wiring.
- Re-measure service level, abandonment, queue size, and oldest contact age until
  they return to target.

## Output

Provide:
1. Classification (routing gap, understaffed, ACW trap, demand surge, closed/overflow).
2. Real-time and historical evidence (queue size, oldest contact age, service level,
   abandonment, agents available vs occupancy).
3. Root cause tied to a specific routing profile, queue, hours-of-operation, or
   quick-connect configuration.
4. Specific fix and the metrics to confirm recovery.
