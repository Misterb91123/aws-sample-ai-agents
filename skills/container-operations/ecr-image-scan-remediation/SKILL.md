---
name: ecr-image-scan-remediation
agent_type: "Generic"
description: Use when triaging Amazon ECR image scan findings and enforcing repository lifecycle policies. It identifies CRITICAL and HIGH vulnerabilities, flags stale unpatched images, and recommends lifecycle rules to prune untagged and aged images. Apply during container security reviews or before promoting images to production.
version: "1.0.0"
last_updated: "2026-08-14"
---

# ECR Image Scan Remediation

Triage ECR image scan findings and enforce lifecycle hygiene so vulnerable and stale images do not reach production.

## When to Activate
- A repository has ECR scan findings with severity CRITICAL or HIGH reported by DescribeImageScanFindings.
- Images with unresolved CRITICAL or HIGH findings are older than 30 days.
- Repositories have scanOnPush disabled in the registry scanning configuration.
- Untagged images accumulate with no GetLifecyclePolicy rule to expire them.
- A production deployment references an image digest whose last scan completedAt is older than 14 days.

## Step 1: Inventory Repositories and Scan Configuration
- Call DescribeRepositories to list all repositories and read imageScanningConfiguration.scanOnPush.
- Call GetRegistryScanningConfiguration to confirm scan type (BASIC or ENHANCED) and rules.
- Flag any repository where scanOnPush is false as a coverage gap.

## Step 2: Pull and Rank Scan Findings
- For each image, call DescribeImageScanFindings and read findingSeverityCounts.
- Rank images by CRITICAL count first, then HIGH count.
- Treat any image with CRITICAL >= 1 as immediate priority and HIGH >= 5 as high priority.

## Step 3: Correlate Findings With Image Age
- Call DescribeImages and compute image age from imagePushedAt.
- Flag any image with unresolved CRITICAL or HIGH findings older than 30 days as overdue for remediation.
- Cross-check imageScanStatus and re-trigger StartImageScan where lastRecordedPullTime shows active use.

## Step 4: Evaluate Lifecycle Policy Coverage
- Call GetLifecyclePolicy per repository and confirm rules exist for untagged expiry and max image count.
- Recommend expiring untagged images after 14 days and capping tagged image count at 100 per repository.
- Where no policy exists, propose a PutLifecyclePolicy definition.

## Step 5: Produce Remediation Plan
- Group findings by fixable (patched base image available) versus non-fixable.
- Map each CRITICAL or HIGH finding to a target base image or package upgrade.
- Recommend enabling scanOnPush and ENHANCED scanning where basic scanning misses OS and language findings.

## Output
Produce a titled "ECR Image Scan Remediation Report" containing per-repository scan coverage, a ranked table of images by CRITICAL and HIGH counts with image age, lifecycle policy gaps, and scanOnPush status. Include a prioritized remediation list ordered by severity then age: rebuild or replace images with CRITICAL findings older than 30 days first, then HIGH findings, then enable scanOnPush and lifecycle expiry rules for repositories lacking them.