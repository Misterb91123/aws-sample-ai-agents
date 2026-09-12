---
name: eks-rbac-least-privilege-review
agent_type: "Evaluation"
description: Use when reviewing Amazon EKS RBAC bindings and pod security for least privilege. It finds excessive cluster-admin bindings, privileged pods, and permissive pod security admission settings, then recommends scoped roles. Apply during cluster security audits or before onboarding new workloads.
version: "1.0.0"
last_updated: "2026-08-14"
---

# EKS RBAC Least Privilege Review

Review EKS role-based access control and pod security to remove excessive privilege and enforce least privilege across namespaces.

## When to Activate
- kubectl get clusterrolebindings shows subjects bound to cluster-admin beyond the platform team.
- Pods run with securityContext.privileged true or allowPrivilegeEscalation true.
- A namespace has no pod security admission label (pod-security.kubernetes.io/enforce) set.
- The aws-auth ConfigMap maps broad IAM principals to system:masters.
- ServiceAccounts use automountServiceAccountToken true without needing API access.

## Step 1: Enumerate RBAC Bindings
- Run kubectl get clusterrolebindings and kubectl get rolebindings --all-namespaces in output form.
- Identify every subject bound to cluster-admin or roles granting wildcard verbs and resources.
- Flag any binding where more than 3 human users share cluster-admin.

## Step 2: Audit the aws-auth Mapping
- Read the aws-auth ConfigMap in kube-system and list mapRoles and mapUsers entries.
- Flag any IAM principal mapped to the system:masters group.
- Recommend mapping to scoped groups tied to namespaced Roles instead.

## Step 3: Inspect Pod Security Posture
- Run kubectl get pods --all-namespaces and inspect securityContext for privileged, hostNetwork, hostPID, and runAsUser 0.
- Flag any pod with privileged true or running as UID 0 as high risk.
- Confirm pod security admission enforce level is set to restricted or baseline per namespace.

## Step 4: Review ServiceAccount Tokens and IRSA
- List ServiceAccounts and check automountServiceAccountToken and IRSA role annotations.
- Flag IRSA roles with wildcard IAM actions or AdministratorAccess attached.
- Recommend disabling token automount for workloads that do not call the Kubernetes API.

## Step 5: Recommend Scoped Roles
- Draft namespaced Roles that grant only the verbs and resources each workload uses.
- Replace cluster-admin bindings for teams with least-privilege ClusterRoles limited to their namespaces.
- Propose an audit cadence of every 30 days for new bindings.

## Output
Produce a titled "EKS RBAC and Pod Security Review" listing all cluster-admin bindings and their subjects, aws-auth entries mapped to system:masters, privileged or root pods per namespace, and namespaces missing pod security admission enforcement. Include a prioritized remediation list: revoke unnecessary cluster-admin and system:masters access first, remediate privileged and root-running pods second, then set pod security admission and scope ServiceAccount tokens.