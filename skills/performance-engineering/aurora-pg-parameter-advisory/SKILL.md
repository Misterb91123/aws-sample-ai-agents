---
name: aurora-pg-parameter-advisory
agent_type: "Generic"
description: Scans Aurora PostgreSQL cluster parameter groups for known
  misconfiguration - memory-hungry parameters on small instances (shared_buffers,
  work_mem, maintenance_work_mem exceeding capacity), wal_level=logical without
  logical replication use, max_connections too high for instance memory, and
  extension conflicts during upgrades - and compares against best-practice
  baselines using CloudWatch memory and connection signals. Use this skill when an
  Aurora PostgreSQL cluster hits memory pressure, connection exhaustion, or a
  failed upgrade, to recommend safe parameter changes, read-only. This is
  Aurora-PostgreSQL-specific tuning, not generic parameter-group drift.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Aurora PostgreSQL Parameter Advisory

Use this skill to catch Aurora PostgreSQL parameter-group misconfiguration before
it causes memory pressure, connection exhaustion, or a blocked upgrade. This
differs from generic parameter-group drift auditing: the concern here is
Aurora-PostgreSQL-specific tuning against the instance class and observed
runtime. Reason over the RDS and CloudWatch reads the platform surfaces; do not
modify anything.

## Sources

Read-only.

- RDS via use_aws: DescribeDBClusters (Aurora PostgreSQL clusters, engine version,
  instance classes, attached cluster parameter group) and
  DescribeDBClusterParameterGroups (shared_buffers, work_mem,
  maintenance_work_mem, wal_level, max_connections, effective_cache_size, and
  extension-related settings, with default-versus-overridden state).
- CloudWatch AWS/RDS metrics via query_cloudwatch_metrics: FreeableMemory,
  CPUUtilization, and DatabaseConnections per instance over a window long enough
  to show peak pressure.
- Performance Insights where available, referenced by identifier for deeper
  wait-event context.

## Method

1. Inventory Aurora PostgreSQL clusters with engine version, instance classes,
   and the attached parameter group.
2. Read the key parameters and note each value and whether it is default or
   overridden.
3. Pull FreeableMemory, CPUUtilization, and DatabaseConnections peaks per
   instance.
4. Memory-hungry parameters: estimate worst-case demand from shared_buffers plus
   per-connection work_mem times max_connections plus maintenance_work_mem, and
   flag settings whose worst case exceeds instance memory or is contradicted by
   low FreeableMemory at peak.
5. wal_level: flag wal_level=logical when no logical replication slots or
   subscriptions are in use, since logical adds WAL overhead without benefit.
6. max_connections: flag a value too high for instance memory and corroborate
   with DatabaseConnections peaks and FreeableMemory pressure.
7. Extension conflicts: flag extensions and settings known to block or complicate
   a major-version upgrade for the target engine version, and note the safe
   pre-upgrade action; then recommend a specific safe value per finding, ranked
   by outage risk.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. Where
deeper PostgreSQL-internal data is needed (pg_settings effective values,
Performance Insights wait events, or logical replication slot state), recommend
connecting a custom MCP server to the database and calling it in addition to the
RDS and CloudWatch reads, never instead of them. The AWS Documentation MCP Server
can supply current Aurora PostgreSQL parameter guidance. AWS MCP server names and
availability evolve; verify before relying on one.

## Output

Produce a parameter advisory report: the cluster baseline (engine version,
instance classes, parameter group, key parameter values); a per-parameter
findings table (cluster, parameter, current value, observed runtime signal,
category, finding, safety rating, recommended value); runtime corroboration from
FreeableMemory, CPUUtilization, and DatabaseConnections; and a ranked,
read-only-safe list of safe parameter changes (recommend-only), with a GREEN,
YELLOW, or RED safety rating and YELLOW or RED flagged for human approval since a
change can require a reboot. Reference identifiers and parameter values, not
database contents.
