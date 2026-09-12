---
name: eks-version-upgrade-planning
agent_type: "Generic"
description: Use when planning Amazon EKS Kubernetes version upgrades ahead of end of support. It detects clusters near EOL, control plane to node version skew, and incompatible add-on versions, then sequences a safe upgrade path. Apply during quarterly platform maintenance or when EKS announces version deprecation.
version: "1.0.0"
last_updated: "2026-08-14"
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

## Output
Produce a titled "EKS Version Upgrade Plan" listing each cluster version with its EOL date and days remaining, control plane to node skew, incompatible add-on versions, and deprecated API usage. Include a prioritized remediation list: upgrade clusters within 60 days of EOL first, resolve version skew greater than 2 by upgrading nodes, apply required add-on version bumps, then schedule remaining upgrades in one-minor-version increments.