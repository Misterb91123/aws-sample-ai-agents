---
name: eks-version-upgrade-planning
agent_type: "Generic"
description: Use when planning Amazon EKS Kubernetes version upgrades ahead of end of support. It detects clusters near EOL, control plane to node version skew, and incompatible add-on versions, then sequences a safe upgrade path. Apply during quarterly platform maintenance or when EKS announces version deprecation.
version: "1.1.0"
last_updated: "2026-09-12"
metadata:
  version: "1.1"
  author: solair
---

# EKS Version Upgrade Planning

Plan EKS control plane and node upgrades before versions reach end of standard support and avoid unsafe version skew.

## When to Activate
- DescribeCluster reports a cluster version within 60 days of its end of standard support date.
- Control plane version and node group version skew is greater than 2 minor versions.
- DescribeAddonVersions shows the running add-on version is not compatible with the target cluster version.
- Managed node groups run an AMI release version behind the control plane.
- A cluster runs a version that has already entered extended support and is incurring extra cost.

## Step 1: Assess Current Versions
- Call DescribeCluster to read version and platformVersion for every cluster.
- Compare each version against the published EKS end of standard support calendar.
- Flag clusters within 60 days of EOL as upgrade candidates.

## Step 2: Measure Version Skew
- Call DescribeNodegroup and read version and releaseVersion for each managed node group.
- Compute skew between control plane minor version and node minor version.
- Flag any skew greater than 2 minor versions as unsupported and requiring node upgrade first.

## Step 3: Validate Add-on Compatibility
- Call DescribeAddonVersions for vpc-cni, coredns, kube-proxy, and ebs-csi-driver against the target version.
- Flag any add-on whose current version is absent from the target version compatibility list.
- Record the required add-on version bumps to apply during the upgrade.

## Step 4: Check Deprecated APIs and Workloads
- Review deprecated API usage using cluster insights or kubectl warnings before upgrade.
- Flag manifests using API groups removed in the target version.
- Confirm Pod Disruption Budgets allow rolling node replacement.

## Step 5: Sequence the Upgrade
- Order steps as control plane upgrade one minor version at a time, then add-ons, then node groups.
- Recommend surge upgrade settings with maxUnavailable of 1 and a canary node group.
- Schedule upgrades to complete at least 30 days before EOL.

## Step 6: Quantify Extended-Support Exposure
- A cluster that reaches end of standard support enters EKS extended support, which raises the control-plane per-cluster-hour charge for up to 12 months, after which the cluster is auto-upgraded.
- Read the cluster upgrade policy (DescribeCluster) to see whether the cluster will auto-enter extended support at standard-support end, so the charge begins without any action.
- Estimate the monthly delta = (extended-support per-cluster-hour minus standard per-cluster-hour) x 730 per cluster. State the assumed rates as estimates; authoritative pricing is in AWS Pricing and Cost Explorer.
- Use this to rank clusters: those already in extended support (incurring now) and those set to auto-enter soonest lead the plan.

## Version skew and support reference

- EKS supports a node kubelet up to 3 minor versions older than the control plane on recent versions (historically 2); treat skew greater than the supported window as unsupported and upgrade nodes first.
- Upgrades move one minor version at a time; you cannot skip a minor version on the control plane.
- Standard support for an EKS minor version runs about 14 months from release; extended support adds up to 12 months at a higher control-plane rate. Use the AWS published EKS version lifecycle calendar for the exact dates per minor version; do not assume dates.
- Core managed add-ons to validate against the target version: vpc-cni, coredns, kube-proxy, and aws-ebs-csi-driver.

## Output
Produce a titled "EKS Version Upgrade Plan" listing each cluster version with its EOL date and days remaining, control plane to node skew, incompatible add-on versions, deprecated API usage, and the extended-support cost exposure (already incurring, or the monthly delta that begins if the cluster auto-enters extended support). Include a prioritized remediation list: upgrade clusters already in or nearest to extended support first, resolve version skew greater than the supported window by upgrading nodes, apply required add-on version bumps, then schedule remaining upgrades in one-minor-version increments to complete at least 30 days before EOL. Label every cost figure an estimate.