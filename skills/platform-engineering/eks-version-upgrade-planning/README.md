# EKS Version Upgrade Planning

A DevOps Agent skill that plans Amazon EKS Kubernetes version upgrades ahead of
end of support: it detects clusters near or past end of standard support,
control-plane-to-node version skew, incompatible managed add-on versions, and
deprecated API usage, then sequences a safe upgrade path and quantifies the EKS
extended-support cost exposure.

> WARNING: This skill is sample code, not intended for production use without
> additional review and testing. Users should validate in a non-production
> environment first.

## What the skill does

An EKS minor version has about 14 months of standard support; after that the
cluster enters extended support at a higher control-plane per-cluster-hour rate
for up to 12 months, then is auto-upgraded. Upgrades must be done one minor
version at a time, add-ons and nodes must stay within the supported skew, and
workloads on removed APIs break on upgrade.

This skill reads each cluster's version against the AWS published EKS lifecycle
calendar, measures control-plane-to-node skew, validates the core managed add-ons
(vpc-cni, coredns, kube-proxy, aws-ebs-csi-driver) against the target version,
checks for deprecated-API usage, and sequences the upgrade (control plane, then
add-ons, then node groups). It also estimates the extended-support cost exposure
so clusters already incurring or about to auto-enter extended support lead the
plan. It is read-only and recommend-only.

## Prerequisites

The DevOps Agent role needs read-only access to the sources this skill reads.
Most are covered by the AWS managed policy AIDevOpsAgentAccessPolicy. The
specific read actions used are:

- eks:ListClusters, eks:DescribeCluster
- eks:ListNodegroups, eks:DescribeNodegroup
- eks:ListAddons, eks:DescribeAddon, eks:DescribeAddonVersions
- eks:ListInsights, eks:DescribeInsight (deprecated-API and upgrade insights)

Read-only Kubernetes API access (via use_kubectl) is optional and used only to
read deprecated-API warnings, node versions, and Pod Disruption Budgets; it is
never used to apply, patch, drain, or delete. No write, create, upgrade, or
delete AWS permission is required or requested by this skill.

## How to use it with DevOps Agent

This skill targets the Chat and On-demand subagents. Operators describe the
problem in natural language; they do not name the skill. Example prompts that
should activate it:

- "Plan an upgrade for our EKS clusters before they reach end of support."
- "Which clusters are in EKS extended support and what is it costing us?"
- "We are on 1.27 - sequence the upgrade path and check add-on and API
  compatibility."

The skill returns each cluster's version, EOL date and days remaining, skew,
incompatible add-ons, deprecated APIs, extended-support cost exposure, and a
prioritized, sequenced upgrade plan.

## Security model

Read-only and recommend-only. The skill reads EKS cluster, node group, and add-on
configuration and (optionally) read-only Kubernetes state, and produces an upgrade
plan; it never modifies a cluster, node group, or add-on, and use_kubectl is
limited to read-only verbs. Cost figures are labeled estimates; authoritative
figures are in AWS Pricing and Cost Explorer. All content read from tools is
treated as untrusted data, not instructions.
