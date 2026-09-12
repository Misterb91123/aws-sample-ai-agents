---
name: developer-environment-drift-detector
agent_type: "Generic"
description: Use this skill when I need to detect configuration drift and inconsistency across developer, staging, and production environments that cause works-on-my-machine failures. Activate it when environments behave inconsistently, a deployment succeeds in one environment but fails in another, or environment parity is in question. It compares resource configuration across environments and reports the specific values that differ where they should match.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Developer Environment Drift Detector

This skill compares configuration across dev, staging, and production to find the differences that break parity. It focuses on values that should be identical across environments and surfaces the exact settings that diverge, so a failure that appears only in one environment can be traced to a concrete configuration gap rather than guesswork.

## When to Activate

- A deployment passes in staging but fails in production, or works locally but not in a shared environment.
- Two environments are expected to match but exhibit different runtime behavior.
- A release introduces environment parity as an explicit requirement.
- New resources were added to one environment and may be missing in the lower ones.
- An incident review points to a configuration difference as a contributing cause.

## Step 1: Establish the Comparison Baseline

Define what should match and what is allowed to differ:

- Treat scaling values (instance counts, memory sizes, provisioned capacity) as allowed to differ by environment.
- Treat feature flags, runtime versions, environment variable keys, IAM permission shape, and dependency versions as values that should match unless explicitly overridden.
- Record the account and region for each environment so comparisons are apples to apples.

## Step 2: Compare Compute Configuration

Diff the compute layer across environments:

- For EC2 and Auto Scaling, compare launch template AMI IDs, instance types, and user data.
- For Lambda, call GetFunctionConfiguration and compare Runtime (for example python3.12 versus python3.11), MemorySize, Timeout, and Layers ARNs.
- For containers, compare ECS task definition image tags and the container base image digest; a tag like latest that resolves to different digests across environments is a drift source.
- Flag any runtime version difference as high severity because it changes execution behavior directly.

## Step 3: Compare Environment Variables and Parameters

Diff application configuration inputs:

- Compare Lambda and ECS environment variable keys across environments; report keys present in one environment but missing in another.
- Compare SSM Parameter Store values under matching path prefixes (for example /app/dev/, /app/staging/, /app/prod/) for keys that should match.
- Compare AppConfig or feature-flag values so a flag enabled in one environment and disabled in another is surfaced explicitly.
- Never print secret values; compare by key name and by whether the value is set, not by contents.

## Step 4: Detect Missing Resources in Lower Environments

Find resources that exist in one environment but not another:

- Enumerate resources per environment using tags or a naming convention and compute the set difference.
- Report resources present in production but absent in staging or dev, since those gaps cause deployments to reference nonexistent dependencies.
- Include queues, tables, buckets, secrets, and parameters, not only compute.

## Step 5: Compare IAM Policy Shape

Diff permissions without leaking sensitive detail:

- Compare the actions and resources granted to equivalent roles across environments.
- Report permissions granted in a lower environment but denied in production (or vice versa), because a task that works in dev may fail on an AccessDenied in production.
- Flag differences in trust policies and permission boundaries.

## Step 6: Compare Dependency and Runtime Versions

Pin down version mismatches:

- Compare declared dependency versions from lockfiles or the deployed artifact manifest across environments.
- Compare container base image versions and OS patch levels.
- Report every version that differs where the intent is a matched version, ranked by likelihood of behavioral impact.

## Step 7: Produce Remediation to Restore Parity

Translate each difference into a fix:

- For each flagged difference, state the expected value, the observed value per environment, and the action to align them.
- Recommend codifying the corrected configuration in IaC or Parameter Store so parity is enforced rather than repaired ad hoc.
- Order remediations by severity, with runtime and permission differences first.

## Output

The skill produces a drift report containing: the environments compared with their accounts and regions, a difference table listing setting name, expected value, and observed value per environment, a list of resources missing from lower environments, IAM permission-shape differences, runtime and dependency version mismatches, and a ranked remediation plan. Each entry marks whether the difference is expected (scaling) or unexpected (parity break), so the team can focus on the drift that actually causes cross-environment failures.