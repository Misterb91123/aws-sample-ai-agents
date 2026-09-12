---
name: cloudtrail-coverage-gap-analysis
agent_type: "Generic"
description: Use this skill to find gaps in AWS CloudTrail management and data event coverage across accounts and regions. It inspects trails, event selectors, and logging status to detect unlogged regions, incomplete read/write coverage, and disabled log file validation, then recommends an organization-wide logging baseline.
version: "1.0.0"
last_updated: "2026-08-14"
---

# CloudTrail Coverage Gap Analysis

This skill audits CloudTrail configuration across the organization to ensure every account and region records the management and data events needed for security and forensics.

## When to Activate

- Any region lacks an active trail delivering logs.
- GetEventSelectors shows management events not logging both read and write activity.
- A trail has log file validation disabled.
- A new account was added to the organization without an org trail applied.
- An incident investigation reveals missing API history for a resource.

## Step 1: Enumerate Trails

- Call CloudTrail DescribeTrails with includeShadowTrails to list all trails, noting IsMultiRegionTrail and IsOrganizationTrail.
- Call Organizations ListAccounts to enumerate member accounts that should be covered.
- Map which accounts and regions are covered by an existing multi-region or org trail.

## Step 2: Check Logging Status

- Call GetTrailStatus for each trail and read IsLogging, LatestDeliveryTime, and LatestDeliveryError.
- Flag any trail where IsLogging is false or delivery has failed.
- Flag any region with no trail actively delivering logs.

## Step 3: Audit Event Selectors

- Call GetEventSelectors and GetInsightSelectors for each trail.
- Flag management events not set to log ALL read and write activity (ReadWriteType All).
- Flag sensitive resources (S3 object-level, Lambda invoke, DynamoDB) lacking data event selectors.

## Step 4: Verify Integrity Controls

- Read LogFileValidationEnabled from DescribeTrails and flag trails where it is disabled.
- Confirm the destination S3 bucket has a restrictive policy and, where required, SSE-KMS encryption.
- Confirm CloudWatch Logs integration exists for real-time alerting where required.

## Step 5: Define the Baseline

- Recommend a single organization multi-region trail capturing all management read/write events.
- Recommend targeted data event selectors for sensitive S3 buckets and Lambda functions.
- Recommend enabling log file validation and locking down the log bucket on every trail.

## Output

The skill produces a titled "CloudTrail Coverage Gap Analysis" mapping accounts and regions to trail coverage and listing each gap: unlogged regions, trails not logging, incomplete read/write selectors, missing data events, and disabled log file validation. It concludes with a prioritized remediation list ordered by forensic risk, such as deploying an org-wide multi-region trail, enabling ALL read/write management logging, adding data event selectors for sensitive resources, enabling log file validation, and hardening the destination bucket.