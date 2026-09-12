---
name: database-migration-planner
agent_type: "Generic"
description: Plans database migrations to AWS by assessing schema compatibility,
  data volume, replication strategies, and cutover approaches. Use this skill when
  migrating databases to RDS, Aurora, DynamoDB, or other AWS data services,
  evaluating migration tools (DMS, native replication), and planning zero-downtime
  or minimal-downtime migration strategies.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Database Migration Planner

Use this skill to plan safe, well-structured database migrations that minimize
downtime and data loss risk.

## When to Activate

- Planning migration of on-premises databases to AWS.
- Migrating between AWS database engines (RDS MySQL -> Aurora, RDS -> DynamoDB).
- Upgrading major database versions requiring migration.
- Evaluating DMS vs native replication approaches.
- Customer requires zero-downtime database migration plan.

## Step 1: Profile the Source Database

Gather complete source database information:

**Engine and version:**
- Database engine (MySQL, PostgreSQL, Oracle, SQL Server, MongoDB, etc.)
- Exact version number
- Edition (Standard, Enterprise)
- Character set and collation settings

**Size and performance:**
- Total data size (GB/TB)
- Number of schemas/databases
- Largest tables (top 10 by size)
- Row counts for critical tables
- Index count and total index size
- Transaction rate (TPS) - peak and average
- Read/write ratio

**Schema complexity:**
- Stored procedures, functions, triggers count
- Views (simple and complex/materialized)
- User-defined types
- Partitioned tables
- Foreign keys and constraints
- Sequences/auto-increment patterns
- Full-text search usage
- Spatial data types
- LOB (Large Object) columns and sizes

**Dependencies:**
- Applications connecting to this database (and connection method)
- Linked servers or cross-database queries
- ETL jobs reading from or writing to this database
- Reporting tools connecting directly
- Replication (existing replicas, subscribers)

## Step 2: Select Target Database

Based on source profile, recommend target:

| Source Engine | Target Options | Best For |
|--------------|---------------|----------|
| MySQL 5.7+ | Aurora MySQL, RDS MySQL | Compatible migration, Aurora for scale |
| PostgreSQL 10+ | Aurora PostgreSQL, RDS PostgreSQL | Compatible migration |
| Oracle | RDS Oracle, Aurora PostgreSQL, RDS PostgreSQL | RDS Oracle for BYOL; Aurora/RDS PG for cost savings |
| SQL Server | RDS SQL Server, Aurora PostgreSQL | RDS SQL Server for BYOL; Aurora PG for modernization |
| MongoDB | DocumentDB, DynamoDB | DocumentDB for compatibility; DynamoDB for scale |
| Redis | ElastiCache Redis/Valkey | Direct migration |

**Decision factors:**
- Homogeneous migration (same engine): faster, lower risk, DMS full compatibility.
- Heterogeneous migration (different engine): schema conversion needed (SCT), higher effort.
- Compatibility: check feature usage against target engine support.
- Cost: Aurora vs RDS pricing, license implications.

## Step 3: Assess Schema Compatibility

For heterogeneous migrations, identify conversion issues:

1. Run AWS Schema Conversion Tool (SCT) assessment.
2. Categorize conversion items:
   - **Auto-converted**: SCT handles automatically (80%+ is common for well-supported paths).
   - **Manual conversion needed**: Stored procedures with engine-specific syntax.
   - **No equivalent**: Features without target engine equivalent (require redesign).

**Common conversion challenges:**
| Feature | Oracle -> PostgreSQL | SQL Server -> PostgreSQL |
|---------|--------------------|-----------------------|
| Stored procedures | PL/SQL -> PL/pgSQL (moderate effort) | T-SQL -> PL/pgSQL (moderate) |
| Sequences | Compatible | IDENTITY -> SERIAL/SEQUENCE |
| Materialized views | Supported (different refresh syntax) | Manual implementation |
| Linked databases | Requires FDW (Foreign Data Wrapper) | Requires FDW |
| Proprietary functions | Rewrite using PG equivalents | Rewrite using PG equivalents |

## Step 4: Select Migration Method

Choose the migration approach:

| Method | Downtime | Complexity | Best For |
|--------|----------|-----------|----------|
| AWS DMS (full load + CDC) | Minutes | Medium | Most migrations, continuous replication |
| Native logical replication | Minutes | Medium | Homogeneous, PostgreSQL logical replication |
| Native binary replication | Seconds | Low | RDS read replica promotion (same engine) |
| Backup and restore | Hours | Low | Small databases, acceptable downtime |
| AWS DMS + SCT | Minutes | High | Heterogeneous migrations |
| Application-level dual-write | Zero | Very High | Zero-downtime requirement, complex |

**DMS considerations:**
- Full load: bulk copy of all data (downtime proportional to data size).
- CDC (Change Data Capture): continuous replication after full load (enables low-downtime cutover).
- DMS limitations: some data types, large LOBs, DDL changes may need special handling.
- DMS instance sizing: sufficient for peak transaction rate.

## Step 5: Plan Data Migration Logistics

For large databases:

1. **Data volume**: How long will full load take?
   - Network bandwidth between source and AWS (Direct Connect recommended for > 100GB)
   - DMS instance throughput (typically 50-100 MB/s for large instances)
   - Estimated full load time = data size / throughput

2. **LOB handling strategy**:
   - Full LOB mode: migrates complete LOB data (slower)
   - Limited LOB mode: truncates at specified size (faster, may lose data)
   - Separate LOB tables: migrate LOBs in a second pass

3. **Table-level parallelism**: Large tables can be migrated in parallel segments.

4. **Pre-migration data cleanup**: Archive unused data before migration to reduce size and time.

## Step 6: Plan Cutover Strategy

**Minimal-downtime cutover:**
1. Full load completes (source continues operating).
2. CDC replication catches up (lag approaches zero).
3. Schedule cutover window.
4. Stop application writes to source.
5. Wait for CDC lag = 0 (all changes replicated).
6. Redirect application connections to target.
7. Validate application functionality.
8. Monitor for issues.

**Cutover timing:**
- Time from "stop writes" to "application on target": target < 5 minutes.
- Schedule during lowest traffic period.
- Have rollback plan ready (point applications back to source).

**Validation during cutover:**
- Row counts match between source and target (sampling for large tables).
- Application smoke tests pass.
- Critical queries return expected results.
- Performance is comparable to source.

## Step 7: Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data loss during cutover | CDC ensures all changes replicated; validate row counts |
| Performance regression | Load test on target before cutover; keep source as fallback |
| Schema conversion errors | Test thoroughly in staging; run application integration tests |
| Replication lag too high | Size DMS instance appropriately; reduce source load during migration |
| Rollback needed | Keep source operational for agreed rollback window (48-72 hours) |
| Application connection issues | Pre-configure target connection strings; use DNS CNAME for switchover |

## Output

Produce a database migration plan:
1. **Source Profile Summary**: Engine, version, size, TPS, schema complexity, dependencies.
2. **Target Recommendation**: Selected target with justification.
3. **Schema Conversion Assessment**: Automated vs manual items, estimated effort.
4. **Migration Method**: Selected approach with timeline estimate.
5. **Cutover Procedure**: Step-by-step cutover and rollback runbook.
6. **Timeline**: Phase-by-phase schedule (prep -> test -> migrate -> validate -> optimize).
7. **Risk Register**: Identified risks with probability, impact, and mitigation.