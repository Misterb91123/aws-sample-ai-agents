---
name: database-connectivity-path-trace
agent_type: "Generic"
description: Traces the complete network path from a failing client to a database
  endpoint (Aurora, RDS, DocumentDB, or DynamoDB via VPC endpoint) and finds the
  break point - security group egress and inbound, NACLs, route tables, VPC
  endpoints or PrivateLink for DynamoDB, DNS resolution of the endpoint, TLS
  certificate validation, and cross-VPC or cross-account reachability. Use this
  skill when a client cannot reach a database to isolate the exact layer that
  blocks the connection, cross-engine.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Database Connectivity Path Trace

Use this skill to isolate where a client-to-database connection breaks. It is
database-scoped and distinct from generic networking skills because it maps the
path specifically for database endpoints - Aurora and RDS instance and cluster
endpoints, DocumentDB, and DynamoDB reached through a gateway or interface VPC
endpoint - and checks the database-specific layers (endpoint DNS, TLS validation,
and PrivateLink) alongside the generic ones. Build once, apply across engines.
Reason over read-only reads; never modify a route, rule, or endpoint.

## Sources

Read-only.

- Database describe calls via use_aws: RDS DescribeDBInstances and
  DescribeDBClusters, DocDB DescribeDBClusters, and the DynamoDB endpoint the
  client uses; read the resolved endpoint address, port, and attached security
  groups.
- EC2 via use_aws: DescribeSecurityGroups and DescribeSecurityGroupRules (client
  egress and database inbound), DescribeNetworkAcls, DescribeRouteTables,
  DescribeVpcEndpoints and DescribeVpcEndpointServiceConfigurations for
  PrivateLink and DynamoDB gateway/interface endpoints, and DescribeSubnets.
- VPC Reachability Analyzer via use_aws: CreateNetworkInsightsPath analysis
  results where already available, or read prior analyses, to confirm the path.
- VPC Flow Logs via query_cloudwatch_logs: filter for REJECT records on the
  client ENI and database ENI on the database port to observe the actual drop.

## Method

1. Resolve the target: the database endpoint DNS name, port, VPC, subnets, and
   security groups, plus the client's ENI, subnet, and security group.
2. Check DNS: confirm the endpoint name resolves to the expected private address
   from the client's VPC (private hosted zone or the DynamoDB endpoint DNS).
3. Check the security-group pair: client SG egress on the database port to the
   database SG, and database SG inbound on that port from the client SG or CIDR.
4. Check stateless NACLs on both subnets for the ephemeral and database ports in
   both directions.
5. Check route tables: the client subnet has a route to the database subnet, or
   to the gateway/interface VPC endpoint for DynamoDB, or across a peering,
   Transit Gateway, or PrivateLink path.
6. For DynamoDB, confirm the VPC endpoint exists, its route or DNS is in effect,
   and its endpoint policy allows the action.
7. Check TLS: confirm the client trusts the certificate chain the endpoint
   presents (correct CA bundle, endpoint name match) when the connection uses TLS.
8. Confirm the break point with Reachability Analyzer and Flow Log REJECT
   records, and rank findings from the first blocking layer outward.

## MCP augmentation

No AWS-managed MCP server is required here - every layer is readable through
native AWS APIs the assigned tools already expose. Where richer topology
correlation across many accounts is wanted, recommend a custom database-endpoint
MCP server used in addition to the native reads, never instead of them. AWS MCP
server names and availability evolve; verify before relying on one.

## Output

Produce a connectivity path trace: the resolved endpoint and client identity; a
per-layer pass/fail table (DNS, client SG egress, database SG inbound, NACLs,
route tables, VPC endpoint or PrivateLink, TLS); the first blocking layer with the
observed evidence (Reachability Analyzer result or Flow Log REJECT); and a
ranked, read-only-safe remediation list naming the exact rule or route to change.
Reference ARNs, endpoints, and account IDs by identifier only.
