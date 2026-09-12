---
name: cloudtrail-lake-cost-control
agent_type: "Generic"
description: Use when controlling AWS CloudTrail Lake storage and query cost. It finds oversized event data stores, long retention, and expensive queries scanning large data volumes, then recommends cost controls. Apply during cost optimization reviews or when CloudTrail Lake spend rises.
version: "1.0.0"
last_updated: "2026-08-14"
---

# CloudTrail Lake Cost Control

Control CloudTrail Lake cost by right-sizing retention, pricing mode, and expensive queries that scan large data volumes.

## When to Activate
- DescribeQuery shows queries with BytesScanned greater than 1 TB.
- GetEventDataStore reports a retention period longer than the compliance requirement.
- An event data store uses the one-year extendable pricing when a shorter mode fits.
- Ingested event volume grows faster than analysis needs justify.
- Frequent broad queries scan entire stores instead of filtered time ranges.

## Step 1: Inventory Event Data Stores
- Call ListEventDataStores and GetEventDataStore for each.
- Record RetentionPeriod, BillingMode, and whether multi-region and organization events are ingested.
- Flag stores retaining data longer than policy requires.

## Step 2: Analyze Query Cost
- Call ListQueries and DescribeQuery to read BytesScanned per query.
- Flag queries scanning more than 1 TB as high cost.
- Identify recurring broad queries that could be narrowed.

## Step 3: Review Ingestion Scope
- Confirm which event categories (management, data, network activity) are ingested.
- Flag data event ingestion that is broad and rarely queried.
- Recommend advanced event selectors to ingest only needed events.

## Step 4: Right-Size Retention and Pricing
- Match RetentionPeriod to the minimum compliance requirement.
- Compare one-year extendable versus seven-year pricing modes against actual retention needs.
- Recommend the pricing mode that minimizes cost for the required retention.

## Step 5: Optimize Query Patterns
- Recommend always filtering queries by eventTime range to cut BytesScanned.
- Recommend saved queries with bounded windows for common investigations.
- Add cost monitoring on CloudTrail Lake via Cost Explorer and budgets.

## Output
Produce a titled "CloudTrail Lake Cost Control Report" listing event data stores with excess retention, queries scanning more than 1 TB, broad ingestion scope, and pricing mode fit. Include a prioritized remediation list: narrow queries with time filters to cut scan cost first, reduce retention to the compliance minimum second, then trim ingestion scope and select the lowest-cost pricing mode.