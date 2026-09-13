---
name: memory-store-hygiene-and-limits
agent_type: "Generic"
description: Audits the memory footprint of an Agent Space against the service
  limits (memory stores per Agent Space, memories per store, and per-memory
  content size) and against retrieval-quality best practices - vague store or
  memory descriptions the agent silently skips, inactive stores, oversized
  memories, and churn. Use this skill to keep memory both within limits and
  actually usable by agents, and to recommend consolidation, description
  rewrites, and cleanups. It reports and recommends; it does not modify memory.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Memory-Store Hygiene and Limits

Use this skill to keep an Agent Space's memory healthy: inside the service
limits, and structured so agents actually retrieve the right memory at the right
moment. Memory that is over a limit blocks new writes; memory with vague
descriptions is present but never read, which is just as useless.

## Limits this skill checks against

- Memory stores per Agent Space: 50.
- Memories per memory store: 200.
- Individual memory content size: 100 KB.

Report usage as a percentage of each limit and flag any store or Agent Space
approaching a limit before it blocks new memories.

## Memory stores this skill reads

- All memory stores visible in the Agent Space (managed and custom): their
  names, descriptions, memory counts, per-memory sizes, active or inactive state,
  and version history where available. Read-only.

## Audit checks

1. Limit pressure: Agent Space near the 50-store limit; any store near the
   200-memory limit; any memory near the 100 KB size limit.
2. Retrieval quality: store or memory descriptions that are vague (for example
   "notes" or "misc") or phrased as an instruction to a person rather than a
   plain statement of subject and when-to-use, because the agent matches on the
   description and skips a store it cannot recognize.
3. Inactive or dead weight: stores or memories toggled inactive, or custom stores
   with no recent updates that may be safe to consolidate or remove.
4. Structure: flat stores that would retrieve better as folder-nested memories
   (path-style names such as `services/checkout/overview`), and oversized memories
   that pack many facts into one file instead of one fact per memory.
5. Duplication: multiple memories or stores covering the same fact.

## Method

1. Enumerate stores and memories, recording counts, sizes, descriptions, and
   active state.
2. Compute usage against each limit and flag pressure.
3. Evaluate every description against the specific-and-concrete standard and flag
   the ones that will not match.
4. Identify inactive, duplicated, oversized, and poorly structured items.
5. Recommend consolidations, description rewrites (with a proposed replacement
   description), splits of oversized memories, and removals - each as an explicit
   recommendation an operator can apply.

## Output

Produce a hygiene report: usage against the 50 / 200 / 100 KB limits with
percentages and any pressure warnings; a list of vague descriptions with proposed
rewrites; inactive, duplicated, and oversized items; and a prioritized cleanup
plan. Managed stores (monitors, directives, reflections, the understanding
stores) cannot be deleted - recommend action only on custom stores for removals,
and description or structure improvements where the store type allows. State that
the agent does not modify memory; an operator applies changes.
