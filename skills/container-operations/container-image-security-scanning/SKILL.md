---
name: container-image-security-scanning
agent_type: "Generic"
description: Provides procedures for interpreting ECR vulnerability scan results,
  prioritizing remediation, and implementing secure image pipelines. Use this
  skill when ECR scans reveal vulnerabilities, when building secure CI/CD
  pipelines for container images, or when deciding which CVEs to fix first.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Container Image Security Scanning

Use this skill to interpret vulnerability scan results and implement
secure container image practices.

## When to Activate

- ECR scan shows critical or high vulnerabilities in production images.
- Building a new container security pipeline.
- Deciding how to prioritize CVE remediation for container images.
- Evaluating whether an image is safe to deploy.

## Step 1: Understand Scan Types

**ECR Basic Scanning:**
- Uses Clair (open-source scanner).
- Scans OS packages only (not application dependencies).
- Must be triggered manually or on push.
- Good for catching base image OS vulnerabilities.

**ECR Enhanced Scanning (Inspector):**
- Uses Amazon Inspector engine.
- Scans OS packages AND programming language packages (npm, pip, maven, etc.).
- Continuous monitoring (rescans when new CVEs published).
- Provides more complete coverage.

## Step 2: Interpret Scan Results

For each finding:
- **CVE ID**: Cross-reference with NVD for details.
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW / UNTRIAGED.
- **Package**: The vulnerable package (e.g., openssl, libcurl).
- **Installed version**: What's in the image.
- **Fixed version**: What version patches the CVE (if available).
- **EPSS score** (if available): Probability of exploitation in the wild.

## Step 3: Prioritize Remediation

Not all CVEs are equal. Prioritize by:

| Factor | Higher Priority | Lower Priority |
|--------|----------------|----------------|
| Severity | Critical/High | Medium/Low |
| Fix available | Yes (can be patched) | No (must wait) |
| Exploitability | Known exploit, CISA KEV listed | Theoretical only |
| Exposure | Internet-facing container | Internal-only service |
| Runtime | Container is currently deployed | Image not in use |
| Attack vector | Network (remote) | Local/physical only |

**Triage decision:**
- Fix immediately: CRITICAL + fix available + deployed + internet-facing
- Fix this sprint: HIGH + fix available + deployed
- Track: CRITICAL/HIGH without fix available (monitor for fix release)
- Accept risk: LOW/MEDIUM in internal services without known exploits

## Step 4: Remediation Approaches

**Update the package (easiest):**
```dockerfile
# For OS packages, update base image or explicitly install newer version
RUN apt-get update && apt-get install -y libcurl4=7.88.1-10+deb12u5
```

**Update base image:**
```dockerfile
# Change FROM to a newer, patched base
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.4.20240611
```

**Use distroless/minimal images (reduce attack surface):**
```dockerfile
# Multi-stage: build in full image, deploy in minimal
FROM golang:1.22 AS builder
RUN go build -o /app
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app /app
```

**Suppress false positives:**
- If the vulnerable function is never called in your code.
- If the package is build-time only (not in final image).
- Document the exception with justification.

## Step 5: Prevent Future Vulnerabilities

1. **Scan in CI/CD** (before images reach production):
   - Fail the build if CRITICAL CVE with fix available.
   - Warn on HIGH CVE, allow deployment with tracking.

2. **Use image pinning** (reproducible builds):
   - Pin base images by digest (not just tag).
   - Track when base images receive patches.

3. **Rebuild regularly** (pick up base image patches):
   - Rebuild all images weekly even without code changes.
   - Automated rebuild triggered by base image update.

4. **Minimize image contents**:
   - Multi-stage builds (don't ship build tools).
   - Remove unnecessary packages.
   - Don't install debugging tools in production images.

## Output

Provide:
1. Vulnerability assessment summary (critical/high/medium/low counts).
2. Prioritized remediation list (which CVEs to fix, in what order).
3. Specific fix action per finding (package update, base image change, accept risk).
4. Pipeline recommendations to prevent vulnerable images from deploying.