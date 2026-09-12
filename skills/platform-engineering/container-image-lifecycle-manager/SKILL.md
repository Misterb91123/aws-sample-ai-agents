---
name: container-image-lifecycle-manager
agent_type: "Generic"
description: Manages container image lifecycle across ECR repositories including
  identifying stale images, validating image provenance, checking vulnerability
  status, and ensuring image retention policies are effective. Use this skill when
  auditing container registries, troubleshooting image pull failures, or optimizing
  ECR storage costs.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Container Image Lifecycle Manager

Use this skill to audit and manage container image lifecycle in ECR,
ensuring images are secure, efficient, and properly maintained.

## When to Activate

- ECR storage costs growing unexpectedly.
- Image pull failures in deployment (image not found, manifest unknown).
- Security audit requiring image provenance and vulnerability status.
- Implementing or validating image retention policies.
- Investigating whether production is running outdated or vulnerable images.

## Step 1: Inventory ECR Repositories

For each ECR repository, collect:
1. Repository name and URI.
2. Total image count and storage size.
3. Image tag mutability setting (mutable vs immutable).
4. Encryption configuration (AES-256 vs KMS).
5. Lifecycle policy status (configured yes/no, rules).
6. Image scanning configuration (scan on push enabled?).
7. Replication configuration (cross-region, cross-account).

## Step 2: Identify Stale Images

Find images that are no longer needed:

**Definitely stale (safe to remove):**
- Untagged images (no tag, only digest) older than 7 days.
- Images with tags matching development patterns (PR builds, branch builds) older than 14 days.
- Images not pulled in the last 90 days (check `lastRecordedPullTime`).
- Images superseded by newer versions of the same tag pattern.

**Potentially stale (verify before removing):**
- Images not referenced by any running task definition or deployment.
- Images from decommissioned services.
- Images with known critical vulnerabilities and newer patched versions available.

**Never remove:**
- Images currently deployed in any environment.
- Images tagged as release/production candidates within retention window.
- Images needed for rollback (keep last N production images).

## Step 3: Validate Image Security

For each actively used image:

1. **Vulnerability scan status:**
   - Last scan date (stale if > 7 days for critical services).
   - Critical vulnerabilities found.
   - High vulnerabilities found.
   - Are there patched versions available?

2. **Base image currency:**
   - What base image is used (e.g., `amazonlinux:2023`, `python:3.11-slim`)?
   - Is the base image the latest available version?
   - When was the base image last rebuilt?

3. **Image composition:**
   - Does it contain unnecessary packages (attack surface)?
   - Is it a minimal/distroless image?
   - Does it run as non-root?
   - Are there secrets baked into layers?

## Step 4: Validate Lifecycle Policies

Check lifecycle policy configuration:

**Recommended lifecycle rules:**
```json
[
  {
    "description": "Remove untagged images after 7 days",
    "selection": { "tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 7 }
  },
  {
    "description": "Keep only last 10 dev images",
    "selection": { "tagStatus": "tagged", "tagPatternList": ["dev-*", "pr-*"], "countType": "imageCountMoreThan", "countNumber": 10 }
  },
  {
    "description": "Keep last 25 production images",
    "selection": { "tagStatus": "tagged", "tagPatternList": ["v*", "release-*"], "countType": "imageCountMoreThan", "countNumber": 25 }
  }
]
```

**Gaps to identify:**
- Repositories with no lifecycle policy (unbounded growth).
- Policies that are too aggressive (may remove needed rollback images).
- Policies that are too relaxed (thousands of unused images accumulating).
- Missing rules for specific tag patterns (dev builds never cleaned).

## Step 5: Validate Image Provenance

Ensure images in production are trustworthy:

1. **Source verification:**
   - Was the image built by the CI/CD pipeline (trusted source)?
   - Can we trace the image back to a specific git commit?
   - Is image signing enabled (sigstore, Notary)?

2. **Tag immutability:**
   - Is tag immutability enabled? (prevents overwriting a tag with different content)
   - If mutable, has any production tag been overwritten unexpectedly?

3. **Pull-through cache:**
   - Are base images pulled from verified upstream registries?
   - Is a pull-through cache configured to avoid reliance on Docker Hub rate limits?

## Step 6: Assess Production Image Status

For currently deployed images:
1. Image age (when was it built/pushed?).
2. Vulnerability status (any critical/high since last scan?).
3. Base image age (is the base outdated?).
4. Is there a newer version available in the same repository?
5. Is the service running the image it thinks it's running? (tag vs digest verification)

**Age thresholds:**
- Images > 30 days old: should be rebuilt to pick up base image patches.
- Images > 90 days old: likely missing multiple security patches.
- Images > 180 days old: critical - needs immediate rebuild plan.

## Step 7: Calculate Storage Optimization

Estimate savings from cleanup:
1. Total current ECR storage cost.
2. Storage occupied by stale images.
3. Savings from implementing recommended lifecycle policies.
4. Storage occupied by duplicate layers across repositories (multi-stage builds sharing base).

## Output

Produce an image lifecycle report:
1. **Summary**: Total repositories, total images, storage used, stale image count, storage recoverable.
2. **Repository Health Table**: Repository, image count, storage, lifecycle policy status, last push date, scan status.
3. **Stale Images Table**: Repository, image tag/digest, last pulled, age, size, recommendation (delete/keep).
4. **Vulnerability Summary Table**: Repository, image tag, critical CVEs, high CVEs, last scanned, action needed.
5. **Production Image Age Chart**: Distribution of deployed image ages.
6. **Lifecycle Policy Gaps**: Repositories missing or having inadequate policies.
7. **Storage Optimization Potential**: Estimated savings from implementing recommendations.
8. **Recommendations**: Prioritized actions for cleanup, policy implementation, and security improvements.