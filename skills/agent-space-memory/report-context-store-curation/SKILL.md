---
name: report-context-store-curation
agent_type: "Generic"
description: Curates a custom memory store that holds the standing context behind
  a recurring operational report - the sections, data sources, thresholds,
  audience, and format the report should follow - so the report stays consistent
  run to run. Use this skill to review an existing report-context store for
  staleness, gaps, and drift against the report actually being produced, and to
  recommend the specific memory additions, updates, and deletions. It proposes
  memory edits; it does not write to memory automatically.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Report-Context Store Curation

Use this skill to keep a recurring report's context store accurate and useful.
A custom store such as `weekly-report-context` records what a scheduled report
should contain - its sections, the sources each section draws from, the
thresholds that define "notable," the audience, and the output format - so every
run produces a consistent artifact instead of drifting with whoever authored the
last one.

## Memory stores this skill reads

- Custom report-context store (for example `weekly-report-context`): read its
  current memories - the report's sections, sources, thresholds, and format.
  This store is writable by an operator, but this skill only recommends edits.
- `understanding-agent-space` and `understanding-dependencies` (read-only): to
  check that the sources and services the report references still exist.

## What belongs in the store

Store durable, synthesized context, not raw data or a single run's output:

- The report's sections and the question each answers.
- The data source for each section (specific metrics, APIs, or other stores) and
  the threshold that makes an item notable.
- The audience and the format (artifact title, ordering, masking rules).
- Standing exclusions (for example resources tagged `monitoring:excluded`).

Keep each memory focused on one fact, and write a precise store description that
states what it holds and when to read it, because the agent matches on that
description before it opens the store.

## Method

1. Read the report-context store and the most recent report it governs.
2. Detect drift and gaps: sections in the report not described in the store,
   store entries the report no longer produces, sources that no longer exist
   (confirmed against the topology stores), and thresholds that no longer match
   what the report flags.
3. Detect staleness: entries unchanged while the underlying report or environment
   changed, and vague store or memory descriptions that would cause the agent to
   skip the store.
4. Recommend edits as explicit add, update, or delete operations, each with the
   proposed memory name (using folder-style paths such as
   `sections/cost-summary`), the proposed description, and the content, so an
   operator can apply them in chat.

## Output

Produce a curation report: current store contents, detected drift and staleness,
and a proposed change set (adds, updates, deletes) with names, descriptions, and
content ready to apply. State plainly that the agent does not write to memory
itself and that an operator must approve and apply the changes.
