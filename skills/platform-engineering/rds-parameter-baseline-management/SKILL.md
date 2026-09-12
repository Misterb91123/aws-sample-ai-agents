---
name: rds-parameter-baseline-management
agent_type: "Generic"
description: Use when managing RDS and Aurora parameter group baselines and detecting drift. It finds instances on default parameter groups, disabled TLS enforcement, and missing logging, then recommends a hardened baseline. Apply during database hardening reviews or before compliance audits.
version: "1.0.0"
last_updated: "2026-08-14"
---

# RDS Parameter Baseline Management

Establish and enforce hardened RDS and Aurora parameter group baselines and detect drift from them.

## When to Activate
- DescribeDBInstances shows instances attached to a default parameter group.
- DescribeDBParameters reveals force_ssl or rds.force_ssl set to 0 (TLS not enforced).
- Slow query, general, or audit logging parameters are disabled.
- Two instances of the same engine use divergent parameter values (drift).
- log_statement or log_min_duration_statement is unset on a production database.

## Step 1: Inventory Parameter Group Attachments
- Call DescribeDBInstances and DescribeDBClusters to read the attached parameter and cluster parameter groups.
- Flag any instance or cluster using a default.* parameter group.
- Group instances by engine and version for baseline comparison.

## Step 2: Read Current Parameter Values
- Call DescribeDBParameters and DescribeDBClusterParameters for each group.
- Extract security and logging parameters including force_ssl, log_statement, log_min_duration_statement, and audit settings.
- Record ParameterValue and ApplyMethod for each.

## Step 3: Check TLS Enforcement
- Confirm force_ssl (PostgreSQL) or require_secure_transport (MySQL) equals 1.
- Flag any group where TLS enforcement is off as a security gap.
- Recommend ModifyDBParameterGroup to enable it with pending-reboot apply.

## Step 4: Validate Logging and Auditing
- Confirm log_min_duration_statement is set (for example 1000 ms) to capture slow queries.
- Confirm general or audit logging is enabled per policy.
- Flag groups where logging parameters are disabled.

## Step 5: Detect Drift and Define Baseline
- Compare each group against the engine baseline and list divergent parameters.
- Flag drift greater than 0 divergent security parameters as action required.
- Recommend a single hardened custom parameter group per engine version.

## Output
Produce a titled "RDS Parameter Baseline Report" listing instances on default parameter groups, groups with TLS enforcement disabled, missing logging parameters, and parameter drift across same-engine instances. Include a prioritized remediation list: enable TLS enforcement first, migrate instances off default parameter groups second, enable logging and auditing parameters, then converge divergent groups onto one hardened baseline.