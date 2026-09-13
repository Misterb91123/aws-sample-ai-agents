---
name: trusted-advisor-remediation-and-migration-playbook
agent_type: "Evaluation"
description: Turns each AWS Trusted Advisor red or yellow check into a concrete, per-check remediation and migration playbook that goes beyond prioritization. For every check it quantifies the actual impact (dollars, risk, blast radius), lays out step-by-step remediation, and gives the migration path when the fix is a change of approach rather than a toggle. Use this skill when a Trusted Advisor finding stops at "action recommended" and you need the full HOW, including safety ratings and which steps must stay with a human. This is read-only guidance the agent applies; it never performs destructive changes itself.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Trusted Advisor Remediation and Migration Playbook

Trusted Advisor tells you WHAT is wrong but not the full HOW. It reports a status of red (action recommended) or yellow (investigation recommended) and an estimated saving, then stops. This skill encodes, per Trusted Advisor category and common check, how to quantify the real impact, the concrete step-by-step remediation, and the migration path where the correct fix is a change of approach rather than a single toggle.

All guidance here is read-only analysis. Recommendations carry a GREEN, YELLOW, or RED safety rating, and destructive or irreversible actions (delete, terminate, revoke, rotate) are described so a human can perform them. The agent never proposes prohibited actions.

## When to Activate
- DescribeTrustedAdvisorCheckResult returns checks with status red or yellow and you need remediation, not just a ranking.
- A cost optimization check reports estimatedMonthlySavings and you need to validate it and produce the rightsizing or migration path.
- A security check flags open access, exposed keys, missing MFA, or weak TLS and you need the exact scoping and modernization steps.
- A fault tolerance check flags single-AZ resources, missing backups, or missing versioning and you need the resilience migration path.
- A performance check flags high utilization or a missing CDN or cache and you need the scale-up or scale-out path.
- A service limit (quota) check shows usage above 80 percent of a quota and you need a sized increase or an architecture change.
- Any Trusted Advisor check appears that is not explicitly cataloged here and you need the generic quantify-owner-remediate-verify loop.

## Step 1: Cost Optimization checks
Quantify the impact from the check's estimatedMonthlySavings, then validate it yourself with utilization data over at least 14 days. Always state that the number is an estimate; Cost Explorer and AWS Pricing are authoritative. Deletes and terminations are human-performed.

Per-check playbook:

- Low Utilization Amazon EC2 Instances
  - Impact: sum estimatedMonthlySavings per instance; confirm with CloudWatch CPU, network, and (via CloudWatch agent) memory over 14+ days. Report as an estimate.
  - Remediation: tag the instance for owner review; validate it is not a periodic batch or month-end workload; stop non-production instances off-hours; rightsize using Compute Optimizer recommendations. Termination stays with a human.
  - Migration path: idle or oversized on-demand instance -> rightsize to a smaller or current-generation family, or move to a Graviton family for equivalent performance at lower cost; steady-state workloads -> cover with a Savings Plan after rightsizing. Sequencing: validate utilization -> tag or notify owner -> stop or rightsize -> monitor 1-2 weeks -> decommission (human).

- Idle Load Balancers
  - Impact: fixed hourly plus LCU or data charges for an LB with no healthy targets or near-zero requests; report the estimate.
  - Remediation: confirm no backend targets and no request traffic over 14+ days; tag for owner review. Deletion stays with a human.
  - Migration path: consolidate multiple low-traffic LBs behind one ALB using host or path based routing; decommission the redundant LB after cutover.

- Underutilized Amazon EBS Volumes
  - Impact: monthly cost of provisioned but barely used capacity or IOPS; report the estimate.
  - Remediation: identify volumes with low IOPS and throughput over 14+ days; snapshot before any change (human confirms). Snapshot-then-delete of orphaned volumes stays with a human.
  - Migration path: over-provisioned gp2 or io1/io2 -> migrate to gp3 and set IOPS and throughput to the observed peak plus a buffer, decoupling them from size to cut cost.

- Unassociated Elastic IP Addresses
  - Impact: hourly charge per unattached EIP; small per address but adds up; report the estimate.
  - Remediation: confirm the EIP is not reserved for an imminent launch or DNS dependency; tag for review. Release stays with a human.
  - Migration path: where a static public IP is not actually required, migrate to a load balancer DNS name or CloudFront and release the EIP.

- Idle Amazon RDS DB Instances
  - Impact: instance plus storage cost for a database with no or near-zero connections; report the estimate.
  - Remediation: confirm zero connections over 14+ days; take a final snapshot (human confirms) to preserve data. Stop or delete stays with a human.
  - Migration path: intermittent workloads -> migrate to Aurora Serverless v2 so capacity scales to zero-cost-idle behavior; dev/test databases -> schedule stop/start windows.

- Savings Plans and Reserved Instance optimization
  - Impact: on-demand spend that a commitment would reduce, or unused commitment being wasted; report as an estimate and confirm in Cost Explorer.
  - Remediation: for recommended purchases, size the commitment to the stable baseline of usage, not the peak; for underused existing RIs, identify the mismatch. Purchases and modifications stay with a human.
  - Migration path: rightsize first, then commit; shift RI coverage or adjust future Savings Plan commitment to match the rightsized baseline; prefer Compute Savings Plans for flexibility across families and regions.

- Amazon S3 Bucket Lifecycle / storage optimization
  - Impact: cost of objects sitting in Standard that are rarely accessed, or incomplete multipart uploads accruing storage; report the estimate.
  - Remediation: review access patterns via S3 Storage Lens; propose a lifecycle policy. Applying lifecycle rules that expire or delete data stays with a human.
  - Migration path: infrequently accessed data -> transition to S3 Standard-IA or One Zone-IA; archival data -> Glacier Instant Retrieval, Flexible Retrieval, or Deep Archive; unknown or shifting patterns -> S3 Intelligent-Tiering.

## Step 2: Security checks
Impact is exposure and blast radius: is the resource internet-reachable, how sensitive is the data, and what privilege is exposed. Map each fix to the directed-action file where applicable (agent-actions/mappings/security.md), but this skill stays focused on the steps. Revoke, rotate, and deactivate actions stay with a human.

Per-check playbook:

- Security Groups - Unrestricted Access (0.0.0.0/0)
  - Impact: any port open to 0.0.0.0/0 is internet-reachable; RED for SSH (22), RDP (3389), and database ports; assess what is behind the port.
  - Remediation: scope the rule to a corporate CIDR or specific security group; revoke the 0.0.0.0/0 rule after the scoped rule is in place and verified. Rule changes on production paths stay with a human.
  - Migration path: instead of open SSH or RDP, migrate to AWS Systems Manager Session Manager or a hardened bastion, then remove the inbound rule entirely; front public web tiers with an ALB and restrict instances to the LB security group.

- Exposed Access Keys
  - Impact: RED and time-critical; a leaked key can grant broad account access; treat as active compromise.
  - Remediation: deactivate the exposed key immediately (human), create a replacement if still needed, then delete the exposed key; review CloudTrail for unauthorized use. Rotation and deletion stay with a human.
  - Migration path: eliminate long-lived keys by migrating workloads to IAM roles (instance profiles, IRSA for EKS, roles for Lambda) and users to IAM Identity Center or federation.

- IAM Use
  - Impact: absence of IAM users, groups, roles, or policies signals credentials may be shared or root is in use.
  - Remediation: establish IAM users or federation, group-based permissions, and roles for workloads.
  - Migration path: migrate from shared credentials to IAM Identity Center with permission sets and short-lived sessions.

- MFA on Root Account
  - Impact: RED; the root account without MFA is a single point of total account compromise.
  - Remediation: enable MFA on the root user; store the device securely; stop using root for daily tasks. Performed by a human with root access.
  - Migration path: reserve root for break-glass only; move all operations to IAM Identity Center roles.

- Amazon S3 Bucket Permissions
  - Impact: public or overly broad bucket policies or ACLs can expose data; severity scales with data sensitivity.
  - Remediation: enable S3 Block Public Access at the account and bucket level; tighten bucket policy to least privilege. Changes to buckets that are intentionally public (static sites) stay with a human after confirmation.
  - Migration path: for public website buckets, migrate to CloudFront with Origin Access Control and turn on Block Public Access on the origin bucket.

- AWS CloudTrail Logging
  - Impact: without CloudTrail there is no audit trail; blast radius is the whole account for forensics and compliance.
  - Remediation: enable a multi-region CloudTrail trail delivering to a dedicated, access-controlled S3 bucket with log file validation.
  - Migration path: migrate per-account trails to a centralized organization trail managed in the management or a delegated administrator account.

- ELB Security Groups / Listener Security
  - Impact: load balancers accepting weak TLS or wide-open security groups expose the application tier.
  - Remediation: attach a scoped security group; modernize the HTTPS listener to a current TLS security policy; redirect HTTP to HTTPS.
  - Migration path: migrate legacy Classic Load Balancers to ALB or NLB, then apply a modern TLS policy and ACM-managed certificates.

## Step 3: Fault Tolerance checks
Impact is RTO and RPO exposure, single-AZ risk, and data-loss risk. Enabling resilience features is generally safe; note failover timing and any restart windows.

Per-check playbook:

- Amazon EBS Snapshots
  - Impact: volumes without recent snapshots risk data loss on failure.
  - Remediation: create a snapshot now; schedule ongoing snapshots.
  - Migration path: migrate ad-hoc snapshots to an AWS Backup plan or Data Lifecycle Manager policy with defined retention.

- Amazon RDS Multi-AZ
  - Impact: single-AZ databases have no automatic failover; an AZ outage means downtime and possible data loss up to the last backup.
  - Remediation: enable Multi-AZ (YELLOW; triggers a brief failover and a maintenance action, schedule in a window).
  - Migration path: single-AZ -> Multi-AZ instance or Multi-AZ DB cluster; for higher availability migrate to Aurora with multiple readers across AZs. Note failover is typically under a couple of minutes but plan for a short interruption.

- Amazon EC2 Availability Zone Balance
  - Impact: instances concentrated in one AZ create correlated failure risk.
  - Remediation: launch replacement capacity in under-represented AZs.
  - Migration path: migrate standalone instances into an Auto Scaling group spanning multiple AZs behind a load balancer.

- Auto Scaling Group health
  - Impact: unhealthy or single-AZ ASGs undermine self-healing.
  - Remediation: enable ELB health checks, span the ASG across AZs, set sane min and max.
  - Migration path: migrate fixed fleets to an ASG with target tracking scaling.

- ELB Cross-Zone Load Balancing / Connection Draining
  - Impact: without cross-zone balancing, load is uneven; without draining, in-flight requests are dropped on deregistration.
  - Remediation: enable cross-zone load balancing and connection draining (deregistration delay).
  - Migration path: adopt ALB or NLB defaults and tune deregistration delay to the longest expected request.

- Amazon S3 Bucket Versioning
  - Impact: without versioning, overwrites and deletes are unrecoverable.
  - Remediation: enable versioning on buckets holding important data.
  - Migration path: add versioning plus lifecycle rules to expire noncurrent versions, and replication for critical buckets.

- Amazon Route 53 failover
  - Impact: without health checks and failover records, DNS keeps sending traffic to a dead endpoint.
  - Remediation: add Route 53 health checks and failover routing to a standby.
  - Migration path: migrate single-record DNS to failover or latency routing with a warm standby or active-active setup.

## Step 4: Performance checks
Impact is latency and throttling risk to users. Scaling and caching changes are generally safe; validate headroom before and after.

Per-check playbook:

- High Utilization Amazon EC2 Instances
  - Impact: sustained high CPU risks throttling and slow responses.
  - Remediation: scale up to a larger size or scale out behind a load balancer.
  - Migration path: migrate to a current-generation or compute-optimized family, or to an ASG with target tracking for elastic scale-out.

- Overutilized / Overprovisioned Amazon EBS Volumes (throughput or IOPS bound)
  - Impact: I/O saturation causes application latency.
  - Remediation: raise IOPS and throughput.
  - Migration path: migrate gp2 to gp3 and set IOPS and throughput explicitly; for very high needs move to io2 Block Express.

- Content Delivery / CDN Optimization
  - Impact: serving static or global content from origin adds latency and origin load.
  - Remediation: identify cacheable content.
  - Migration path: add Amazon CloudFront in front of S3 or the ALB with appropriate cache policies.

- Amazon EC2 to EBS Throughput Optimization
  - Impact: instance EBS bandwidth caps the volume, bottlenecking I/O.
  - Remediation: match instance EBS bandwidth to volume throughput.
  - Migration path: migrate to an EBS-optimized, current-generation instance sized for the required bandwidth.

- Large Number of Rules on a Security Group / Rules per ENI
  - Impact: approaching the rules limit risks failed changes and slower evaluation.
  - Remediation: consolidate and remove redundant rules.
  - Migration path: split responsibilities across multiple security groups referenced by group id, and use prefix lists for shared CIDR sets.

## Step 5: Service Limits (Quotas) checks
Impact is imminent failure when the limit is hit: launches, API calls, or scaling actions start failing.

Per-check playbook:

- Any check reporting usage above 80 percent of a quota
  - Impact: state which service and quota, the current usage and limit, and the failure mode when reached (for example, RunInstances denied, cannot add subnets).
  - Remediation: for adjustable quotas, request a targeted Service Quotas increase sized to the observed peak plus a reasonable buffer; never request the maximum. Submission stays with a human where approval is required.
  - Migration path: for non-adjustable (hard) limits, architect around them - shard load across multiple resources or accounts, distribute across regions, or move to a service without the constraining limit.

## Step: Build the remediation and migration record per finding
For EACH Trusted Advisor check in red or yellow, produce a record containing:
- check name (the real Trusted Advisor check title and category)
- actual impact, quantified (dollars for cost with the estimate caveat, or risk and blast radius for security and fault tolerance, or latency and throttling for performance, or the failure mode for limits)
- step-by-step remediation
- safety rating: GREEN (safe, reversible, low blast radius), YELLOW (proceed with care, may cause brief disruption or needs validation), or RED (destructive, irreversible, or high blast radius)
- whether it needs human approval (all deletes, terminates, revokes, rotations, and production path changes do)
- the migration path if the correct fix is a change of approach rather than a toggle

## Step: Handle any check not in the catalog
For any Trusted Advisor recommendation not explicitly listed above, apply the generic loop so coverage is complete for every check:
- Quantify: read the check status, category, and flaggedResources; translate them into a concrete impact (cost with estimate caveat, risk and blast radius, performance, or limit-breach failure mode).
- Owner: identify the resource owner via tags or account context and route the finding to them.
- Remediate: derive the least-blast-radius corrective step; if it is destructive or irreversible, mark it RED and leave it to a human.
- Verify: state how to confirm the fix (re-run the check, check the metric, or confirm the config) and monitor for regression.
This covers operational excellence and configuration or tagging hygiene checks (for example missing tags, documentation, or config drift), which map to a quantify-owner-remediate-verify pass even when there is no dollar figure.

## Output
For every flagged Trusted Advisor check (red and yellow, across cost optimization, security, fault tolerance, performance, service limits, and operational excellence), produce a remediation-and-migration record: the check name, the quantified actual impact, the step-by-step remediation, the migration path where the fix is a change of approach, a GREEN/YELLOW/RED safety rating, and whether human approval is required. Include the estimate caveat that any savings figure is an estimate and that Cost Explorer and AWS Pricing are authoritative. State clearly that destructive fixes (delete, terminate, revoke, rotate, release) remain with a human; this skill provides read-only guidance and never performs those actions itself.
