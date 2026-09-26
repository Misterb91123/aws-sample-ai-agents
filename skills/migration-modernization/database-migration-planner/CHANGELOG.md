# Changelog

## [1.0.0] - 2026-08-14
### Added
- Initial release of the database migration planner skill.
- Profiles the source database (engine, version, size, transaction rate, schema
  complexity, dependencies) and recommends a homogeneous or heterogeneous target.
- Assesses schema conversion (auto-converted vs manual effort), selects a
  migration method (DMS full load + CDC, native replication, or backup/restore)
  against the downtime tolerance, and plans data-migration logistics.
- Produces a minimal-downtime cutover and rollback runbook and a risk register.
- Read-only and recommend-only; supports major-version upgrades including moving
  off engine versions in RDS extended support.
