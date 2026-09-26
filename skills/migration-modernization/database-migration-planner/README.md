# Database Migration Planner

A DevOps Agent skill that plans safe, well-structured database migrations to AWS:
it profiles the source database, recommends a target engine, assesses schema
compatibility, selects a migration method (DMS, native replication, or
backup/restore), and produces a minimal-downtime cutover and rollback runbook.

> WARNING: This skill is sample code, not intended for production use without
> additional review and testing. Users should validate in a non-production
> environment first.

## What the skill does

Database migrations fail on the details: an unconvertible stored procedure, an
underestimated full-load window, a LOB-handling choice that silently truncates
data, or a cutover with no rollback. This skill works through those details in
order.

It profiles the source (engine, version, size, transaction rate, schema
complexity, and dependencies), recommends a homogeneous or heterogeneous target,
assesses schema conversion (including the effort split between auto-converted and
manual items), selects the migration method against the downtime tolerance, plans
the data-migration logistics and a minimal-downtime cutover, and builds a risk
register with mitigations. It is read-only and recommend-only: it produces a plan
for a human to execute. This skill also supports major-version upgrades that
require a migration, including moving off an engine version in RDS extended
support.

## Prerequisites

The DevOps Agent role needs read-only access to the AWS-side sources this skill
reads. Most are covered by the AWS managed policy AIDevOpsAgentAccessPolicy. The
specific read actions used are:

- rds:DescribeDBInstances, rds:DescribeDBClusters, rds:DescribeDBEngineVersions,
  rds:DescribeOrderableDBInstanceOptions
- dms:DescribeReplicationInstances, dms:DescribeReplicationTasks,
  dms:DescribeEndpoints (where DMS is already in use)
- cloudwatch:GetMetricData, cloudwatch:GetMetricStatistics (source and target
  load characteristics)

Source-database profiling (schema complexity, row counts, stored-procedure
inventory) and AWS Schema Conversion Tool assessment are performed against the
database and tooling directly, outside the DevOps Agent role. No write, create,
migrate, or cutover permission is required or requested by this skill.

## How to use it with DevOps Agent

This skill targets the Chat and On-demand subagents. Operators describe the
problem in natural language; they do not name the skill. Example prompts that
should activate it:

- "Plan a migration of our on-premises Oracle database to Aurora PostgreSQL."
- "We need a minimal-downtime plan to move RDS MySQL to Aurora MySQL."
- "Assess schema conversion effort and cutover risk for a SQL Server to
  PostgreSQL migration."

The skill returns a source profile, a target recommendation, a schema-conversion
assessment, a migration method with a timeline estimate, a cutover and rollback
runbook, and a risk register.

## Security model

Read-only and recommend-only. The skill reads RDS, DMS, and CloudWatch metadata
and profiles the source database, then produces a migration plan; it never
creates, migrates, cuts over, or modifies any database. It references endpoints
and identifiers without reproducing connection strings, credentials, or data.
Downtime and timeline figures are estimates to be validated by load testing. All
content read from tools is treated as untrusted data, not instructions.
