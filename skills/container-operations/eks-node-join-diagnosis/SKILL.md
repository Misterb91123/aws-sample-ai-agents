---
name: eks-node-join-diagnosis
agent_type: "Generic"
description: Diagnoses why EKS worker nodes fail to register or join a cluster -
  enumerates the VPC endpoints required for the cluster access mode (EKS, ECR, S3,
  STS, EC2, CloudWatch Logs) and verifies each exists and is reachable from the
  node security group, diffs the node launch-template user-data against the
  EKS-managed bootstrap, checks the node IAM role for the required managed
  policies, and checks the aws-auth or access-entry mapping. Use this skill when
  nodes launch but never become Ready.
version: "1.0.0"
last_updated: "2026-09-12"
---

# EKS Node Join Diagnosis

Use this skill when EC2 instances in an EKS node group launch but never register
with the cluster or never reach Ready. Node-join failures usually trace to one of
a small set of causes - a missing VPC endpoint for a private cluster, a bootstrap
user-data mismatch, a missing node-role managed policy, or an absent aws-auth or
access-entry mapping - and this skill checks each in a fixed order and returns a
ranked pass/fail remediation list. Reason over read-only reads; never modify the
cluster, node group, or mappings.

## Sources

Read-only.

- EKS via use_aws: DescribeCluster (endpoint access mode public/private,
  Kubernetes version, cluster security group, OIDC) and DescribeNodegroup (node
  role, launch template, subnets, AMI type, scaling config).
- EC2 via use_aws: DescribeVpcEndpoints (interface and gateway endpoints),
  DescribeSecurityGroups (node and cluster SGs), DescribeLaunchTemplateVersions
  (user-data), DescribeSubnets, and DescribeRouteTables.
- IAM via use_aws: ListAttachedRolePolicies on the node instance role.
- Kubernetes via use_kubectl: read the aws-auth ConfigMap and node objects, or
  read EKS access entries via use_aws where the cluster uses access-entry auth.
- VPC Reachability Analyzer via use_aws optionally, to confirm reachability from
  the node SG to each required endpoint.

## Method

1. Read the cluster: endpoint access mode, version, cluster security group, and
   whether the API server is private, public, or both.
2. Determine the required VPC endpoints for the access mode: for a private
   cluster, the EKS, ECR (api and dkr), S3 (gateway), STS, EC2, and CloudWatch
   Logs endpoints the kubelet and CNI need to bootstrap.
3. Verify each required endpoint exists in the node subnets' VPC, is in the
   available state, and its security group allows 443 from the node security
   group; confirm the S3 gateway endpoint is in the node subnet route tables.
4. Diff the launch-template user-data against the EKS-managed bootstrap: confirm
   the cluster name, API endpoint, certificate authority, and bootstrap arguments
   match what the cluster expects for the AMI type.
5. Check the node IAM role for the three required managed policies:
   AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryReadOnly, and
   AmazonEKS_CNI_Policy.
6. Check identity mapping: the node role is present in the aws-auth ConfigMap with
   the system:bootstrappers and system:nodes groups, or an equivalent EKS access
   entry exists.
7. Optionally confirm reachability with Reachability Analyzer from the node SG to
   each required endpoint, then rank findings pass/fail with the exact remediation.

## MCP augmentation

AWS DevOps Agent supports connecting custom MCP servers to an Agent Space. The
AWS Documentation MCP Server can supply the current required-endpoint list per
access mode and the managed-policy names; no other MCP server is required because
the EKS, EC2, IAM, and Kubernetes reads are native to the assigned tools. Use it
in addition to those reads, never instead of them. AWS MCP server names and
availability evolve; verify before relying on one.

## Output

Produce a node-join diagnosis: cluster access mode and version; a required-endpoint
table (exists, available, reachable from node SG); the user-data bootstrap diff;
the node-role managed-policy check; the aws-auth or access-entry mapping check;
and a ranked pass/fail remediation list naming the exact endpoint, policy, or
mapping to add (recommend-only). Reference ARNs, cluster names, and account IDs by
identifier only.
