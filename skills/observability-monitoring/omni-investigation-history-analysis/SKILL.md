---
name: omni-investigation-history-analysis
agent_type: "Generic"
description: Summarizes Amazon CloudWatch Omni investigation history and DevOps
  Agent investigations into a program-level reliability view - recurring-root-cause
  clusters, time-to-detect and time-to-recover (MTTR) trends, and repeat-offender
  services and dependencies across teams and Spaces. Use this skill to turn the
  investigation history Omni captures automatically (DevOps Agent participates in
  every session) into a cross-team reliability picture that shows what keeps
  breaking and how long it takes to recover. It reasons over CloudWatch-native
  reads plus Omni-surfaced context; it recommends follow-ups, it does not open,
  close, or modify investigations.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Omni Investigation History Analysis

Use this skill to turn CloudWatch Omni investigation history into a program-level
reliability view. Omni captures full investigation history automatically and
DevOps Agent participates in every Omni investigation session, so the history
holds recurring root causes, detection and recovery timing, and the services that
keep breaking. The value this skill delivers is the cross-team pattern: the
root-cause cluster, the MTTR trend, and the repeat-offender service that no single
Space would see on its own.

## Sources

Read-only. CloudWatch Omni does not expose a confirmed dedicated use_aws action
set today, so treat the Omni-specific reads as data the platform surfaces and
lean on the CloudWatch-native signals below; do not assume an Omni API that has
not been verified.

- list_investigations for the DevOps Agent and Omni investigations over the
  reporting window, with start, detect, and resolve timestamps and recorded root
  cause where present.
- use_aws for the CloudWatch-native context around each investigation: affected
  services, alarms, and the resource inventory from tags and AWS Config.
- query_cloudwatch_metrics for the supporting signals behind time-to-detect and
  time-to-recover trends.
- The Omni investigation-session history the platform surfaces, where available.

## Method

1. Pull the investigation set over the window: DevOps Agent and Omni
   investigations with their timestamps and recorded root cause where present.
2. Normalize each investigation: affected service, owning team or Space, severity,
   detected time, recovered time, and recorded or inferred root cause.
3. Cluster recurring root causes: group by root-cause signature and by affected
   service and dependency so repeat patterns across teams surface, not per Space.
4. Compute timing trends: time-to-detect and time-to-recover (MTTR) per service,
   per team, and overall, guarding every average against a zero sample count and
   excluding investigations missing a detect or resolve timestamp.
5. Rank repeat-offender services and dependencies by frequency and cumulative
   recovery time, separating a root-cause origin from a shared-dependency symptom.
6. Recommend the specific follow-up per cluster (a runbook, an instrumentation
   fix, a dependency hardening) for a human to apply; do not open, close, or
   modify investigations.

## MCP augmentation

CloudWatch Omni is reached through its own workspace and the blog points to the
AWS MCP Server for Omni APIs, documentation, and regional availability. Where a
CloudWatch or Omni MCP server is available, connect it to the Agent Space to read
investigation-session history directly, and use the AWS Documentation MCP Server
for current Omni and DevOps Agent guidance. Use any MCP in addition to the
CloudWatch-native use_aws reads, never instead of them, and do not assume an Omni
API that the MCP does not actually expose. AWS MCP server names and availability
evolve; verify before relying on one.

## Output

Produce a reliability report: the investigation set summary; recurring-root-cause
clusters ranked by frequency and cumulative recovery time; time-to-detect and
MTTR trends per service, per team, and overall with the excluded-investigation
count; repeat-offender services and dependencies separating root-cause origins
from symptoms; and a recommended follow-up per cluster. State that the skill
recommends follow-ups and does not open, close, or modify investigations.
Reference services and accounts by identifier.
