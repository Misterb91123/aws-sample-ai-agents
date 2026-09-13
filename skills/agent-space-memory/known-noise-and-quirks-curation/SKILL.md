---
name: known-noise-and-quirks-curation
agent_type: "Generic"
description: Identifies confirmed noisy alarms and environmental quirks and
  recommends recording them in a custom memory store so future runs and
  investigations stop rediscovering and re-flagging them. Use this skill to
  distinguish a genuine issue from known, expected behavior (a batch job that
  spikes latency nightly, an alarm that flaps during deploys, a NAT gateway that
  drops idle connections) and to propose the exact memory entries that capture
  each quirk. It proposes memory edits; it does not write to memory automatically.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Known-Noise and Quirks Curation

Use this skill to build and maintain a custom store of confirmed environmental
truths - the expected-but-surprising behaviors that otherwise get re-investigated
every time they appear. Capturing a quirk once, with its evidence and its
expected signature, lets every future run treat it as known instead of raising it
as new.

## Memory stores this skill reads

- Custom quirks store (for example `network-quirks` or `known-noise`): read
  existing entries so recommendations do not duplicate what is already recorded.
  Writable by an operator; this skill only recommends edits.
- `monitors` (read-only): recurring root-cause history that helps confirm an
  alarm is chronically noisy for a benign reason.

## What qualifies as a quirk worth storing

- A noisy alarm with a confirmed benign cause and a repeatable signature (fires
  during nightly batch, flaps during deploys, known false positive under a
  specific condition).
- An environmental behavior that is easy to misread as a fault (idle-connection
  timeouts, expected cold-start latency, a metric namespace that is
  environment-specific).
- A naming or ownership fact that repeatedly causes confusion.

Only store a quirk after it is confirmed - corroborated by metrics, the monitors
history, or an explicit operator statement. Do not store a one-off, and do not
store raw data; store the synthesized fact and its expected signature so a future
run can match against it.

## Method

1. Read the existing quirks store to avoid duplicates.
2. Gather candidates: alarms the monitors store shows as chronically firing for a
   benign cause, and metric patterns corroborated with `query_cloudwatch_metrics`
   or `query_cloudwatch_logs` that match a known-benign signature.
3. Confirm each candidate against evidence; discard anything not corroborated.
4. Recommend memory entries as explicit adds or updates, each with a focused
   single-fact memory name (for example `alarms/checkout-latency-nightly-batch`),
   a precise description, and content stating the quirk, its expected signature,
   the evidence, and how a future run should treat it.

## Output

Produce a curation report: existing quirks, newly confirmed candidates with
evidence, and a proposed change set (adds and updates) with names, descriptions,
and content. State that the agent does not write to memory itself and that an
operator approves and applies the changes. Reference alarms and resources by
identifier; do not include sensitive content.
