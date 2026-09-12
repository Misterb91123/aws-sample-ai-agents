---
name: xray-sampling-strategy-design
agent_type: "Generic"
description: Use this skill when designing AWS X-Ray sampling rules to balance trace coverage against cost. It triggers on high X-Ray recording charges, insufficient trace visibility into errors or slow requests, or requests to tune per-service sampling for high-volume endpoints, and it guides reservoir and fixed-rate configuration, error prioritization, and trace retention.
version: "1.0.0"
last_updated: "2026-08-14"
---

# X-Ray Sampling Strategy Design

This skill designs AWS X-Ray sampling rules that capture the traces teams need for debugging while controlling recording cost. It uses the reservoir-plus-fixed-rate model, prioritizes error and slow traces, and scopes rules per service and endpoint.

## When to Activate

- X-Ray recording or retrieval charges are high and need reduction.
- Errors or slow requests are not consistently captured in traces.
- A high-volume, low-value endpoint (health checks, static polling) is consuming the trace budget.
- A team needs different sampling for different services or request paths.
- Trace coverage is uneven and needs a deliberate sampling policy.

## Step 1: Understand the sampling model

- X-Ray sampling combines a reservoir (a fixed number of traces per second recorded regardless of rate) and a fixed rate (a percentage of requests recorded after the reservoir is filled).
- The default rule records the first 1 request per second (reservoir) and 5 percent of additional requests. This is the fallback when no custom rule matches; keep it modest to bound baseline cost.
- Billing is driven by traces recorded (and traces retrieved and scanned), so the sampling rate directly controls cost.

## Step 2: Prioritize error and slow traces

- Because a low fixed rate can miss rare failures, add higher-rate rules targeting the requests most valuable for debugging.
- Increase sampling on error-prone or critical paths (for example checkout, payment, auth) so a larger share of their requests, including failures, are captured.
- Where the SDK or service supports it, ensure fault and error responses are more likely to be sampled so the traces that explain incidents are present.

## Step 3: Write per-service and per-endpoint rules

- Create sampling rules matched by service name, service type, HTTP method, URL path, and host. More specific rules should have lower priority numbers so they evaluate first.
- Assign each rule a reservoir and fixed rate appropriate to its value. For a critical low-volume API, a small reservoir with a high fixed rate gives near-complete coverage cheaply. For a high-volume general path, a small reservoir with a low fixed rate bounds cost.
- Keep the rule set small and ordered; overlapping rules are resolved by priority, so document the intended precedence.

## Step 4: Suppress high-volume low-value traffic

- Add a low-priority-number (high-precedence) rule matching health checks, readiness probes, and static polling paths with a reservoir of 0 and a fixed rate of 0 (or near 0) so they are effectively not traced.
- Confirm these paths are not needed for latency baselining before suppressing them entirely.

## Step 5: Manage trace retention and retrieval cost

- X-Ray retains traces for 30 days by default and this is not configurable; plan retention-dependent analysis within that window and export or summarize longer-term signals elsewhere.
- Recognize that retrieving and scanning traces (GetTraceSummaries, trace queries) also incurs cost; narrow time ranges and filter expressions to reduce scanned volume.

## Step 6: Validate coverage versus cost

- After applying rules, confirm error traces and slow traces from critical paths are consistently present, and confirm suppressed paths no longer consume budget.
- Estimate recorded traces per second across all rules and compare against the target trace budget; adjust reservoirs and rates to hit the budget while keeping critical-path coverage high.

## Output

Produce an X-Ray Sampling Strategy document containing: the ordered rule set (priority, match criteria, reservoir, fixed rate) with the rationale for each, the error and slow-trace prioritization approach, the suppression rules for high-volume low-value paths, the retention constraint and its impact on analysis, and an estimated recorded-traces-per-second figure against the trace budget. Include before-and-after coverage expectations for critical paths.