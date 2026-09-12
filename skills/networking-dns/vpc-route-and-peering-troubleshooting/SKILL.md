---
name: vpc-route-and-peering-troubleshooting
agent_type: "Incident RCA"
description: Use when troubleshooting VPC peering and Transit Gateway routing problems. It finds blackhole routes, missing return routes, and overlapping CIDRs, then recommends route table fixes. Apply when cross-VPC traffic fails or during network connectivity reviews.
version: "1.0.0"
last_updated: "2026-08-14"
---

# VPC Route and Peering Troubleshooting

Troubleshoot cross-VPC and Transit Gateway connectivity by finding broken, missing, or conflicting routes.

## When to Activate
- DescribeRouteTables shows a route with State blackhole.
- Traffic reaches a peer VPC but has no return route back to the source.
- SearchTransitGatewayRoutes shows a route in blackhole state or missing an attachment.
- Peered VPCs have overlapping CIDR blocks that prevent routing.
- A subnet route table lacks a route to the peering connection or Transit Gateway.

## Step 1: Map the Intended Path
- Identify source and destination VPCs, subnets, and CIDR ranges.
- Call DescribeVpcs and DescribeSubnets to confirm CIDR allocations.
- Flag any overlapping CIDR ranges between the endpoints.

## Step 2: Inspect Route Tables
- Call DescribeRouteTables for source and destination subnets.
- Flag routes with State blackhole and routes missing for the destination CIDR.
- Confirm both directions have a route (forward and return).

## Step 3: Validate Peering and Transit Gateway
- Call DescribeVpcPeeringConnections and confirm status is active.
- Call SearchTransitGatewayRoutes on the relevant route table for the destination CIDR.
- Flag Transit Gateway routes in blackhole state or attachments not associated.

## Step 4: Check Propagation and Associations
- Confirm Transit Gateway route table associations and propagations for each attachment.
- Flag attachments that are associated but not propagating the needed routes.
- Confirm the route target (peering connection, TGW attachment) matches the intended path.

## Step 5: Recommend Route Fixes
- Add or correct routes so both directions resolve to the correct attachment.
- Remove or replace blackhole routes caused by deleted attachments.
- Where CIDRs overlap, recommend re-addressing or a NAT-based workaround.

## Output
Produce a titled "VPC Routing and Peering Report" listing blackhole routes, missing return routes, overlapping CIDRs, and Transit Gateway association or propagation gaps. Include a prioritized remediation list: add missing return routes to restore connectivity first, clear blackhole routes from deleted attachments second, then fix TGW propagation and address CIDR overlaps.