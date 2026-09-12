---
name: transit-gateway-routing-debugging
agent_type: "Incident RCA"
description: Use this skill when connectivity across a Transit Gateway breaks or routes unexpectedly, including missing route propagation, blackhole routes, or traffic that reaches one attachment but not another. It triggers on reports of VPC-to-VPC, VPC-to-VPN, or cross-region peering reachability failures and guides analysis of route table associations, propagations, static versus propagated routes, and appliance mode.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Transit Gateway Routing Debugging

This skill diagnoses AWS Transit Gateway routing problems where attachments cannot reach each other, routes fail to propagate, or traffic is silently dropped by blackhole routes. It separates association behavior from propagation behavior and validates stateful inspection paths.

## When to Activate

- Traffic between two VPC attachments on the same Transit Gateway fails while other pairs work.
- A VPN or Direct Connect attachment does not appear in a Transit Gateway route table.
- Reachability Analyzer or VPC Flow Logs show traffic dropped at the Transit Gateway.
- A route shows state "blackhole" in a Transit Gateway route table.
- Cross-region Transit Gateway peering routes are not resolving.
- Stateful inspection via a firewall VPC drops return traffic (suspected asymmetric flow).

## Step 1: Map attachments, associations, and propagations

- List attachments with describe-transit-gateway-attachments and record each attachment ID, resource type, and state (must be "available").
- For each attachment, determine which route table it is associated with using get-transit-gateway-attachment-propagations and the route table associations. An attachment is associated with exactly one route table (which route table it uses for its own lookups) but can propagate into many.
- Build a matrix of which attachments associate with which route table and which attachments propagate routes into which route table. Most connectivity gaps trace to an attachment associated with the wrong route table.

## Step 2: Distinguish static from propagated routes

- Dump each route table with search-transit-gateway-routes and record route type (static or propagated), the target attachment, and state.
- Propagated routes appear automatically when propagation is enabled from an attachment; if a route is missing, confirm propagation is enabled from the source attachment into that route table.
- Static routes override propagated routes for the same or more-specific prefix. A static route pointing at a detached or unavailable attachment becomes a blackhole.

## Step 3: Investigate blackhole routes

- A route in state "blackhole" silently drops all matching traffic. This happens when the target attachment is deleted or unavailable while a static route still points to it.
- Confirm whether the blackhole is intentional (used to deliberately drop a CIDR) or accidental (orphaned static route). Remove or repoint orphaned static routes.
- Check for overly broad static routes (for example 0.0.0.0/0 as blackhole) that swallow traffic intended for more-specific propagated routes.

## Step 4: Validate appliance mode for stateful inspection

- When a centralized inspection VPC hosts stateful firewalls, enable appliance mode on that VPC attachment. Without appliance mode, the Transit Gateway may select different AZ paths for forward and return traffic, breaking flow symmetry and causing the firewall to drop return packets.
- Confirm appliance mode is enabled with describe-transit-gateway-vpc-attachments (applianceModeSupport equals "enable").
- Verify the inspection VPC has subnets and Transit Gateway ENIs in every AZ used by the workload, since appliance mode keeps a flow pinned to the AZ where it entered.

## Step 5: Trace cross-region peering routes

- Cross-region Transit Gateway peering does not support route propagation; peering routes must be added statically in each region's route table pointing at the peering attachment.
- Confirm a static route for the remote region CIDR exists in the local route table and vice versa in the remote region.
- Verify both peering attachment sides are in state "available" and that security appliances or NACLs are not blocking the inter-region traffic.

## Step 6: Confirm end-to-end path

- Run Reachability Analyzer from a source ENI to a destination ENI across the Transit Gateway to get the exact hop where traffic is dropped.
- Correlate with VPC Flow Logs (action FIELD equals REJECT) and Transit Gateway Flow Logs to confirm whether the drop is at the Transit Gateway, a security group, or a NACL.

## Output

Produce a Transit Gateway Routing Report containing: the association-and-propagation matrix, a per-route-table listing that separates static from propagated routes, all blackhole routes with an intentional-versus-orphaned classification, appliance-mode status for inspection attachments with AZ coverage findings, cross-region peering static route validation, and the Reachability Analyzer result identifying the exact drop point. Include a prioritized remediation list that names the specific route table and route to change.