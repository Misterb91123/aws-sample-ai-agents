---
name: artifact-repository-hygiene-auditor
agent_type: "Generic"
description: Use this skill when I need to audit AWS CodeArtifact and Amazon ECR repositories for stale artifacts, missing retention policies, security scanning gaps, and cost from accumulated versions. Activate it when artifact storage keeps growing, old package or image versions pile up, or dependency provenance is unclear. It reports version counts, age, retention gaps, and the storage cost of unused artifacts.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Artifact Repository Hygiene Auditor

This skill audits artifact stores for accumulation, weak provenance controls, and missing lifecycle management. It quantifies how many versions and images exist, how old they are, and what they cost, then recommends retention and origin controls so repositories stay lean and trustworthy.

## When to Activate

- CodeArtifact or ECR storage cost is rising month over month.
- Old package versions or container images accumulate with no cleanup.
- Dependency provenance is unclear or dependency-confusion risk needs review.
- No ECR lifecycle policy exists on active repositories.
- A supply-chain review requires evidence of scanning and origin controls.

## Step 1: Inventory CodeArtifact Package Versions

Count and age the packages:

- Call ListPackages, then ListPackageVersions for each package in the domain and repository.
- Record the total version count per package and the publishedTime of each version.
- Flag packages with more than 50 retained versions and versions older than 180 days that are not the latest.

## Step 2: Identify Unused Package Versions

Separate versions that are still consumed from dead weight:

- Cross-reference retained versions against the versions referenced by current builds and deployed artifacts.
- Mark versions with status Unlisted or Archived and any version not referenced in the last 90 days as cleanup candidates.
- Preserve at least the latest 2 stable versions per package to protect rollback.

## Step 3: Inventory ECR Image Accumulation

Count and age container images:

- Call DescribeRepositories, then DescribeImages for each repository.
- Record image count, total sizeInBytes, and imagePushedAt per image.
- Flag repositories where untagged images exceed 20 or total size exceeds a team threshold, for example 50 GB.

## Step 4: Check Lifecycle and Retention Policies

Find repositories with no automated cleanup:

- Call GetLifecyclePolicy for each ECR repository; report repositories with no lifecycle policy configured.
- Recommend rules such as expire untagged images older than 14 days and keep only the most recent 10 tagged images per prefix.
- For CodeArtifact, report the absence of a documented retention practice, since CodeArtifact relies on explicit version disposal.

## Step 5: Verify Security Scanning Coverage

Confirm images are scanned for vulnerabilities:

- Check ECR registry scanning configuration (basic or enhanced with Amazon Inspector) via GetRegistryScanningConfiguration.
- Report repositories where scanOnPush is disabled.
- Summarize open findings by severity (CRITICAL, HIGH, MEDIUM) from DescribeImageScanFindings and flag any CRITICAL finding older than 30 days.

## Step 6: Review Package Origin Controls

Assess dependency-confusion protection:

- Inspect CodeArtifact package origin controls (publish and upstream settings) via DescribePackage.
- Flag internal package names that allow upstream resolution, since that permits a public package of the same name to be pulled instead of the internal one.
- Recommend setting origin control to block upstream for internal-only package namespaces.

## Step 7: Detect Deprecated and Costly Artifacts

Surface risk and cost:

- Flag packages marked deprecated that are still referenced by builds.
- Estimate storage cost from total stored bytes in ECR and CodeArtifact against current per-GB pricing.
- Rank cleanup candidates by reclaimable bytes so the highest-cost items are addressed first.

## Output

The skill produces a hygiene report containing: CodeArtifact package version counts and age distribution, a list of unused version cleanup candidates with rollback-safe retention noted, ECR image counts and total size per repository, repositories missing lifecycle policies with recommended rules, scanning coverage and open critical findings, package origin-control gaps that create dependency-confusion risk, deprecated-package usage, and an estimated storage cost with reclaimable bytes ranked. Each finding includes a concrete remediation and the threshold that triggered it.