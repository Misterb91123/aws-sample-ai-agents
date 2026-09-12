# Catalog - Browse by operational domain

Locate agents and skills by the operational domain they address.

**Agents** execute autonomously on a schedule or on demand, producing reports and recommendations.

**Skills** provide investigation procedures and domain knowledge that agents load during execution.

To browse agents by the AWS service they cover instead of by operational domain, see [Index by AWS service](#index-by-aws-service) at the end of this file.

---

## Incident management

| Type | Name | Description |
|------|------|-------------|
| Agent | [incident-postmortem-generator](agents/09-incident-postmortem-generator/) | Generates blameless post-mortems from resolved investigations |
| Skill | [incident-triage-classifier](skills/incident-management/incident-triage-classifier/) | Classifies severity based on alarm patterns and customer impact |
| Skill | [blast-radius-assessment](skills/incident-management/blast-radius-assessment/) | Maps all affected services and quantifies customer impact |
| Skill | [escalation-path-navigator](skills/incident-management/escalation-path-navigator/) | Determines correct escalation path based on severity and ownership |
| Skill | [incident-communication-drafter](skills/incident-management/incident-communication-drafter/) | Drafts status page updates, executive briefings, and customer communications |
| Skill | [runbook-executor-guide](skills/incident-management/runbook-executor-guide/) | Guides operators through standard runbooks for common failures |

---

## Release and deployment management

| Type | Name | Description |
|------|------|-------------|
| Agent | [deployment-rollback-analyzer](agents/05-deployment-rollback-analyzer/) | Detects failed deployments and recommends rollbacks |
| Agent | [pipeline-failure-analyzer](agents/13-pipeline-failure-analyzer/) | Analyzes CI/CD failures, flaky tests, and DORA metrics |
| Agent | [deployment-velocity-reporter](agents/34-deployment-velocity-reporter/) | Tracks DORA metrics and delivery performance |
| Agent | [codepipeline-stage-failure-analyzer](agents/170-codepipeline-stage-failure-analyzer/) | Analyzes CodePipeline stage failures and recovery time |
| Agent | [codedeploy-deployment-health-monitor](agents/171-codedeploy-deployment-health-monitor/) | Monitors CodeDeploy deployment health and rollbacks |
| Skill | [release-changelog-generator](skills/release-management/release-changelog-generator/) | Generates structured changelogs from deployments and commits |
| Skill | [rollback-decision-framework](skills/release-management/rollback-decision-framework/) | Structured framework for rollback, forward-fix, or monitor decisions |
| Skill | [canary-deployment-analysis](skills/release-management/canary-deployment-analysis/) | Analyzes canary metrics to determine promote or rollback |
| Skill | [pre-deployment-readiness-check](skills/release-management/pre-deployment-readiness-check/) | Validates all preconditions before production deployment |
| Skill | [deployment-freeze-enforcer](skills/release-management/deployment-freeze-enforcer/) | Enforces freeze windows and manages exception approvals |

---

## Security operations

| Type | Name | Description |
|------|------|-------------|
| Agent | [security-group-auditor](agents/03-security-group-auditor/) | Audits security groups for overly permissive rules |
| Agent | [iam-least-privilege-auditor](agents/07-iam-least-privilege-auditor/) | Identifies wildcard IAM policies and unused permissions |
| Agent | [unused-permissions-revoker](agents/11-unused-permissions-revoker/) | IAM Access Advisor scan for unused service permissions |
| Agent | [s3-bucket-security-scanner](agents/15-s3-bucket-security-scanner/) | Scans S3 for public access, missing encryption, broad policies |
| Agent | [network-flow-anomaly-detector](agents/19-network-flow-anomaly-detector/) | Analyzes VPC Flow Logs for exfiltration and lateral movement |
| Agent | [waf-rule-effectiveness-analyzer](agents/21-waf-rule-effectiveness-analyzer/) | Evaluates WAF rule effectiveness and protection gaps |
| Agent | [cloudtrail-anomaly-hunter](agents/22-cloudtrail-anomaly-hunter/) | Detects suspicious API activity and privilege escalation |
| Agent | [ec2-metadata-security-checker](agents/48-ec2-metadata-security-checker/) | Audits IMDSv1 exposure and metadata service configuration |
| Agent | [cross-account-role-trust-auditor](agents/49-cross-account-role-trust-auditor/) | Audits IAM trust policies for unauthorized access |
| Agent | [public-exposure-surface-scanner](agents/82-public-exposure-surface-scanner/) | Discovers all publicly accessible resources |
| Agent | [nacl-rule-auditor](agents/84-nacl-rule-auditor/) | Audits Network ACL rules for permissive configurations |
| Agent | [waf-blocked-traffic-trend-reporter](agents/147-waf-blocked-traffic-trend-reporter/) | Reports WAF blocked-traffic trends and rule noise |
| Agent | [acm-certificate-expiry-and-renewal-monitor](agents/148-acm-certificate-expiry-and-renewal-monitor/) | Tracks ACM certificate expiry and failed renewals |
| Agent | [cloudtrail-management-event-coverage-auditor](agents/151-cloudtrail-management-event-coverage-auditor/) | Audits CloudTrail management event coverage across accounts |
| Agent | [cloudfront-security-header-auditor](agents/156-cloudfront-security-header-auditor/) | Audits CloudFront distributions for missing security response headers |
| Agent | [s3-access-point-and-policy-auditor](agents/157-s3-access-point-and-policy-auditor/) | Audits S3 access points and bucket policies for public or broad access |
| Agent | [iam-access-key-age-and-usage-auditor](agents/158-iam-access-key-age-and-usage-auditor/) | Flags aged and unused IAM access keys |
| Agent | [ssm-session-manager-audit-reporter](agents/159-ssm-session-manager-audit-reporter/) | Audits Session Manager usage, logging, and long-running sessions |
| Agent | [vpc-flow-log-coverage-auditor](agents/160-vpc-flow-log-coverage-auditor/) | Finds VPCs and subnets without flow log coverage |
| Agent | [sns-topic-encryption-and-policy-auditor](agents/162-sns-topic-encryption-and-policy-auditor/) | Audits SNS topics for encryption and permissive policies |
| Agent | [waf-managed-rule-version-drift-monitor](agents/172-waf-managed-rule-version-drift-monitor/) | Detects outdated WAF managed rule group versions |
| Agent | [guardduty-malware-scan-coverage-auditor](agents/173-guardduty-malware-scan-coverage-auditor/) | Audits GuardDuty Malware Protection coverage and scan failures |
| Agent | [securityhub-finding-aging-reporter](agents/174-securityhub-finding-aging-reporter/) | Reports Security Hub finding aging against severity SLAs |
| Agent | [inspector-vulnerability-sla-reporter](agents/175-inspector-vulnerability-sla-reporter/) | Reports Inspector vulnerabilities against remediation SLAs |
| Agent | [macie-sensitive-data-exposure-monitor](agents/177-macie-sensitive-data-exposure-monitor/) | Monitors Macie findings for sensitive data exposed in S3 |
| Agent | [kms-grant-and-policy-drift-auditor](agents/178-kms-grant-and-policy-drift-auditor/) | Audits KMS key grants and policies for drift and broad access |
| Agent | [organizations-scp-change-monitor](agents/199-organizations-scp-change-monitor/) | Monitors Organizations SCP changes for risky or unauthorized edits |
| Agent | [iam-identity-center-assignment-auditor](agents/200-iam-identity-center-assignment-auditor/) | Audits IAM Identity Center permission set assignments |
| Agent | [ecr-image-scan-and-lifecycle-auditor](agents/202-ecr-image-scan-and-lifecycle-auditor/) | Audits ECR image scan findings and lifecycle policy coverage |
| Agent | [eks-pod-security-and-rbac-auditor](agents/203-eks-pod-security-and-rbac-auditor/) | Audits EKS pod security standards and RBAC bindings |
| Agent | [rds-snapshot-sharing-and-encryption-auditor](agents/205-rds-snapshot-sharing-and-encryption-auditor/) | Audits RDS snapshots for public sharing and encryption |
| Agent | [lambda-iam-permission-scope-auditor](agents/212-lambda-iam-permission-scope-auditor/) | Audits Lambda execution role permission scope |
| Agent | [sqs-encryption-and-policy-auditor](agents/213-sqs-encryption-and-policy-auditor/) | Audits SQS encryption and access policy hygiene |
| Agent | [network-acl-and-sg-conflict-detector](agents/220-network-acl-and-sg-conflict-detector/) | Detects NACL and security group conflicts causing silent drops |
| Agent | [acm-and-elb-tls-policy-drift-monitor](agents/221-acm-and-elb-tls-policy-drift-monitor/) | Monitors TLS policy drift and weak ciphers on ELB and CloudFront |
| Agent | [waf-rate-based-rule-effectiveness-monitor](agents/222-waf-rate-based-rule-effectiveness-monitor/) | Evaluates WAF rate-based rule effectiveness against traffic |
| Agent | [guardduty-finding-severity-trend-reporter](agents/223-guardduty-finding-severity-trend-reporter/) | Reports GuardDuty finding severity trends over time |
| Skill | [lambda-execution-role-hardening](skills/security-operations/lambda-execution-role-hardening/) | Hardens Lambda execution role permissions toward least privilege |
| Skill | [sqs-access-and-encryption-hardening](skills/security-operations/sqs-access-and-encryption-hardening/) | Hardens SQS encryption and access policies |
| Skill | [tls-policy-modernization](skills/security-operations/tls-policy-modernization/) | Modernizes ELB and CloudFront TLS policies and removes weak ciphers |
| Skill | [waf-rate-based-rule-tuning](skills/security-operations/waf-rate-based-rule-tuning/) | Tunes WAF rate-based rules to observed attack volume |
| Skill | [security-incident-containment](skills/security-operations/security-incident-containment/) | Containment procedures preserving forensic evidence |
| Skill | [vulnerability-prioritization](skills/security-operations/vulnerability-prioritization/) | Prioritizes CVEs by exploitability, exposure, and business context |
| Skill | [exposed-credentials-response](skills/security-operations/exposed-credentials-response/) | Response procedure for leaked credentials |
| Skill | [guardduty-finding-investigation](skills/security-operations/guardduty-finding-investigation/) | Systematic investigation of GuardDuty findings |
| Skill | [network-anomaly-investigation](skills/security-operations/network-anomaly-investigation/) | Investigation of suspicious network traffic patterns |
| Skill | [certificate-expiry-remediation](skills/security-operations/certificate-expiry-remediation/) | Fixes expiring certificates and failed ACM renewals |
| Skill | [waf-blocked-traffic-analysis](skills/security-operations/waf-blocked-traffic-analysis/) | Separates WAF attacks from false positives and tunes rules |
| Skill | [cloudtrail-coverage-gap-analysis](skills/security-operations/cloudtrail-coverage-gap-analysis/) | Finds gaps in CloudTrail management and data event coverage |

---

## Cost management and FinOps

| Type | Name | Description |
|------|------|-------------|
| Agent | [devops-agent-usage-credit-monitor](agents/101-devops-agent-usage-credit-monitor/) | Monitors DevOps Agent usage and cost against the support-tier credit allowance and forecasts month-end net charges |
| Agent | [cost-anomaly-detector](agents/02-cost-anomaly-detector/) | Identifies cost spikes, waste, and budget breaches |
| Agent | [resource-tagging-compliance](agents/08-resource-tagging-compliance/) | Enforces tagging standards for cost allocation |
| Agent | [storage-cost-optimizer](agents/24-storage-cost-optimizer/) | Identifies EBS, S3, snapshot, and EFS savings |
| Agent | [log-retention-cost-optimizer](agents/27-log-retention-cost-optimizer/) | Optimizes CloudWatch Logs retention and class settings |
| Agent | [orphaned-resource-cleaner](agents/32-orphaned-resource-cleaner/) | Discovers unused resources left by deleted services |
| Agent | [savings-plan-utilization-tracker](agents/61-savings-plan-utilization-tracker/) | Tracks commitment utilization and expiring plans |
| Agent | [cross-region-data-transfer-auditor](agents/75-cross-region-data-transfer-auditor/) | Quantifies unexpected cross-region transfer costs |
| Agent | [monthly-cost-allocation-report](agents/80-monthly-cost-allocation-report/) | Monthly breakdown by team, service, and environment |
| Agent | [graviton-migration-opportunity-finder](agents/81-graviton-migration-opportunity-finder/) | Identifies workloads that can save 20-40% on Graviton |
| Agent | [reserved-instance-coverage-optimizer](agents/83-reserved-instance-coverage-optimizer/) | Tracks RI utilization and uncovered steady-state usage |
| Agent | [secrets-manager-cost-optimizer](agents/88-secrets-manager-cost-optimizer/) | Identifies unused secrets and cost reduction opportunities |
| Agent | [step-functions-cost-optimizer](agents/99-step-functions-cost-optimizer/) | Recommends Standard vs Express type optimizations |
| Agent | [cost-anomaly-root-cause-investigator](agents/137-cost-anomaly-root-cause-investigator/) | Traces cost anomalies to the driving service, account, and usage type |
| Agent | [quota-utilization-forecaster](agents/139-quota-utilization-forecaster/) | Forecasts quota exhaustion from utilization trend |
| Agent | [cloudwatch-metrics-cost-optimizer](agents/141-cloudwatch-metrics-cost-optimizer/) | Reduces CloudWatch custom metric and log ingestion spend |
| Agent | [carbon-footprint-efficiency-reporter](agents/143-carbon-footprint-efficiency-reporter/) | Reports sustainability and resource efficiency signals |
| Agent | [s3-lifecycle-and-tiering-optimizer](agents/145-s3-lifecycle-and-tiering-optimizer/) | Optimizes S3 storage classes and lifecycle rules |
| Agent | [lambda-provisioned-concurrency-cost-optimizer](agents/150-lambda-provisioned-concurrency-cost-optimizer/) | Right-sizes Lambda provisioned concurrency against utilization |
| Agent | [ec2-spot-savings-opportunity-reporter](agents/155-ec2-spot-savings-opportunity-reporter/) | Identifies on-demand workloads suitable for Spot and quantifies savings |
| Agent | [elasticache-serverless-cost-monitor](agents/161-elasticache-serverless-cost-monitor/) | Monitors ElastiCache Serverless storage and ECPU cost |
| Agent | [ecs-fargate-rightsizing-advisor](agents/163-ecs-fargate-rightsizing-advisor/) | Recommends Fargate task CPU and memory rightsizing from utilization |
| Agent | [lightsail-resource-inventory-reporter](agents/197-lightsail-resource-inventory-reporter/) | Reports Lightsail inventory and cost visibility gaps |
| Agent | [workspaces-utilization-and-cost-monitor](agents/198-workspaces-utilization-and-cost-monitor/) | Monitors WorkSpaces utilization and running-mode cost fit |
| Agent | [ebs-snapshot-cost-and-orphan-auditor](agents/208-ebs-snapshot-cost-and-orphan-auditor/) | Finds orphaned and costly EBS snapshots |
| Agent | [elb-idle-and-cost-optimizer](agents/209-elb-idle-and-cost-optimizer/) | Identifies idle and low-traffic load balancers wasting cost |
| Agent | [cloudtrail-lake-query-cost-monitor](agents/224-cloudtrail-lake-query-cost-monitor/) | Monitors CloudTrail Lake storage and query cost |
| Agent | [tag-coverage-and-cost-attribution-auditor](agents/225-tag-coverage-and-cost-attribution-auditor/) | Audits resource tag coverage for cost attribution |
| Skill | [ebs-snapshot-cleanup-strategy](skills/cost-management/ebs-snapshot-cleanup-strategy/) | Reclaims cost from orphaned and redundant EBS snapshots |
| Skill | [load-balancer-cost-rationalization](skills/cost-management/load-balancer-cost-rationalization/) | Rationalizes idle and low-traffic load balancers |
| Skill | [cloudtrail-lake-cost-control](skills/cost-management/cloudtrail-lake-cost-control/) | Controls CloudTrail Lake storage and query cost |
| Skill | [rightsizing-recommendation-engine](skills/cost-management/rightsizing-recommendation-engine/) | Identifies over-provisioned and under-provisioned resources |
| Skill | [data-transfer-cost-analyzer](skills/cost-management/data-transfer-cost-analyzer/) | Analyzes cross-AZ, cross-region, and internet egress costs |
| Skill | [idle-resource-hunter](skills/cost-management/idle-resource-hunter/) | Finds idle EBS, stopped instances, and unused EIPs |
| Skill | [savings-plan-advisor](skills/cost-management/savings-plan-advisor/) | Recommends optimal commitment-based discounts |
| Skill | [cost-allocation-gap-finder](skills/cost-management/cost-allocation-gap-finder/) | Identifies untagged spend that cannot be attributed |
| Skill | [cost-anomaly-root-cause-analysis](skills/cost-management/cost-anomaly-root-cause-analysis/) | Isolates the service, account, and usage type driving a cost anomaly |
| Skill | [service-quota-forecasting](skills/cost-management/service-quota-forecasting/) | Projects quota exhaustion and prepares increase requests |
| Skill | [observability-cost-optimization](skills/cost-management/observability-cost-optimization/) | Cuts CloudWatch and X-Ray spend without losing signal |
| Skill | [lambda-concurrency-cost-tuning](skills/cost-management/lambda-concurrency-cost-tuning/) | Balances provisioned concurrency cost against cold starts |
| Skill | [s3-storage-tiering-optimization](skills/cost-management/s3-storage-tiering-optimization/) | Tiers cold S3 data and cleans up incomplete uploads |

---

## Resiliency and reliability

| Type | Name | Description |
|------|------|-------------|
| Agent | [daily-infra-health-report](agents/01-infrastructure-health-report/) | Daily health summary across all AWS accounts |
| Agent | [cross-region-dr-sync-validator](agents/12-cross-region-dr-sync-validator/) | Validates DR replication lag and failover readiness |
| Agent | [service-quota-watchdog](agents/17-service-quota-watchdog/) | Monitors quotas approaching limits |
| Agent | [event-driven-architecture-health](agents/29-event-driven-architecture-health/) | Monitors SQS, SNS, EventBridge, and Kinesis health |
| Agent | [sla-breach-predictor](agents/30-sla-breach-predictor/) | Predicts SLO breaches from error budget burn rates |
| Agent | [nat-gateway-high-availability-checker](agents/96-nat-gateway-high-availability-checker/) | Verifies NAT Gateway HA across AZs |
| Agent | [aws-health-event-impact-assessor](agents/97-aws-health-event-impact-assessor/) | Assesses AWS Health event impact on your infrastructure |
| Agent | [weekly-reliability-scorecard](agents/100-weekly-reliability-scorecard/) | Comprehensive reliability scorecard for all services |
| Skill | [az-failure-readiness-assessment](skills/resiliency-reliability/az-failure-readiness-assessment/) | Validates AZ failure survivability |
| Skill | [dependency-health-analyzer](skills/resiliency-reliability/dependency-health-analyzer/) | Assesses circuit breakers, timeouts, and single points of failure |
| Skill | [error-budget-tracker](skills/resiliency-reliability/error-budget-tracker/) | Tracks SLO compliance and error budget burn rates |
| Skill | [disaster-recovery-validation](skills/resiliency-reliability/disaster-recovery-validation/) | Validates DR configurations and RTO/RPO compliance |
| Skill | [chaos-experiment-planner](skills/resiliency-reliability/chaos-experiment-planner/) | Designs controlled chaos engineering experiments |

---

## Observability and monitoring

| Type | Name | Description |
|------|------|-------------|
| Agent | [alarm-fatigue-reducer](agents/06-cloudwatch-alarm-fatigue-reducer/) | Identifies noisy, redundant, and misconfigured alarms |
| Agent | [cloudwatch-log-insights-query-library](agents/71-cloudwatch-log-insights-query-library/) | Executes diagnostic queries proactively |
| Agent | [service-health-dashboard-generator](agents/73-service-health-dashboard-generator/) | Generates consolidated service health artifacts |
| Agent | [cloudwatch-alarm-configuration-auditor](agents/95-cloudwatch-alarm-configuration-auditor/) | Audits alarm configurations for best practices |
| Agent | [xray-trace-sampling-optimizer](agents/142-xray-trace-sampling-optimizer/) | Optimizes X-Ray sampling rules for cost and coverage |
| Agent | [cloudwatch-synthetics-canary-health-monitor](agents/168-cloudwatch-synthetics-canary-health-monitor/) | Monitors Synthetics canary success rate and duration |
| Agent | [rum-and-frontend-error-trend-reporter](agents/169-rum-and-frontend-error-trend-reporter/) | Reports CloudWatch RUM frontend errors and web vitals trends |
| Agent | [apigateway-throttling-and-quota-monitor](agents/211-apigateway-throttling-and-quota-monitor/) | Monitors API Gateway throttling and stage limits |
| Skill | [guardduty-trend-analysis](skills/observability-monitoring/guardduty-trend-analysis/) | Analyzes GuardDuty severity trends and recurring finding types |
| Skill | [trace-analysis-investigator](skills/observability-monitoring/trace-analysis-investigator/) | Analyzes distributed traces for bottlenecks |
| Skill | [sli-measurement-validator](skills/observability-monitoring/sli-measurement-validator/) | Validates SLI accuracy against customer experience |
| Skill | [log-pattern-anomaly-detector](skills/observability-monitoring/log-pattern-anomaly-detector/) | Detects new error patterns before alarms fire |
| Skill | [metric-correlation-investigator](skills/observability-monitoring/metric-correlation-investigator/) | Correlates metrics to identify root causes |
| Skill | [dashboard-gap-analyzer](skills/observability-monitoring/dashboard-gap-analyzer/) | Identifies services lacking monitoring coverage |
| Skill | [cloudwatch-cost-reduction](skills/observability-monitoring/cloudwatch-cost-reduction/) | Reduces CloudWatch metric, log, and dashboard spend |
| Skill | [xray-sampling-strategy-design](skills/observability-monitoring/xray-sampling-strategy-design/) | Designs X-Ray sampling rules that balance cost and coverage |
| Skill | [distributed-tracing-gap-analysis](skills/observability-monitoring/distributed-tracing-gap-analysis/) | Finds gaps in end-to-end distributed tracing |
| Skill | [alarm-noise-reduction-strategy](skills/observability-monitoring/alarm-noise-reduction-strategy/) | Reduces alarm noise and false pages |
| Skill | [config-conformance-drift-remediation](skills/observability-monitoring/config-conformance-drift-remediation/) | Remediates Config conformance pack noncompliance and drift |

---

## Platform engineering

| Type | Name | Description |
|------|------|-------------|
| Agent | [eks-cluster-health-auditor](agents/10-kubernetes-cluster-health-auditor/) | Audits EKS cluster health, versions, and workloads |
| Agent | [auto-scaling-efficiency-auditor](agents/28-auto-scaling-efficiency-auditor/) | Identifies over/under provisioned scaling |
| Agent | [cross-service-dependency-mapper](agents/33-cross-service-dependency-mapper/) | Discovers service topology and single points of failure |
| Agent | [auto-scaling-launch-failure-investigator](agents/65-auto-scaling-launch-failure-investigator/) | Diagnoses ASG launch failures |
| Agent | [vpc-cidr-capacity-planner](agents/69-vpc-cidr-capacity-planner/) | Forecasts subnet IP exhaustion |
| Agent | [infrastructure-age-eol-tracker](agents/79-infrastructure-age-eol-tracker/) | Tracks components approaching end-of-life |
| Agent | [lambda-concurrency-forecast](agents/86-lambda-concurrency-forecast/) | Forecasts Lambda concurrency limits |
| Agent | [eks-node-group-scaling-efficiency-monitor](agents/164-eks-node-group-scaling-efficiency-monitor/) | Monitors EKS node group scaling efficiency and bin-packing |
| Agent | [lambda-runtime-deprecation-tracker](agents/165-lambda-runtime-deprecation-tracker/) | Tracks functions on deprecated or soon-to-be-deprecated runtimes |
| Agent | [dynamodb-autoscaling-effectiveness-monitor](agents/166-dynamodb-autoscaling-effectiveness-monitor/) | Monitors DynamoDB auto scaling effectiveness and throttling |
| Agent | [eks-cluster-version-eol-tracker](agents/204-eks-cluster-version-eol-tracker/) | Tracks EKS cluster version against AWS support end of life |
| Agent | [ec2-ami-hygiene-and-eol-auditor](agents/207-ec2-ami-hygiene-and-eol-auditor/) | Audits EC2 AMI hygiene and OS end of life |
| Agent | [rds-parameter-group-drift-auditor](agents/206-rds-parameter-group-drift-auditor/) | Detects RDS and Aurora parameter group drift and risky settings |
| Skill | [eks-version-upgrade-planning](skills/platform-engineering/eks-version-upgrade-planning/) | Plans EKS Kubernetes version upgrades before end of support |
| Skill | [ami-and-os-lifecycle-management](skills/platform-engineering/ami-and-os-lifecycle-management/) | Manages AMI hygiene and operating system end of life |
| Skill | [rds-parameter-baseline-management](skills/platform-engineering/rds-parameter-baseline-management/) | Manages RDS and Aurora parameter group baselines and drift |
| Skill | [capacity-planning-forecaster](skills/platform-engineering/capacity-planning-forecaster/) | Forecasts resource needs from growth trends |
| Skill | [infrastructure-drift-detector](skills/platform-engineering/infrastructure-drift-detector/) | Detects drift between IaC and actual state |
| Skill | [container-image-lifecycle-manager](skills/platform-engineering/container-image-lifecycle-manager/) | Manages ECR image lifecycle |
| Skill | [service-onboarding-checklist](skills/platform-engineering/service-onboarding-checklist/) | Validates production readiness for new services |
| Skill | [vpc-network-topology-auditor](skills/platform-engineering/vpc-network-topology-auditor/) | Audits VPC topology for misconfigurations |

---

## Compliance and governance

| Type | Name | Description |
|------|------|-------------|
| Agent | [config-rule-drift-remediator](agents/31-config-rule-drift-remediator/) | Tracks Config rule violations and chronic non-compliance |
| Agent | [compliance-evidence-collector](agents/35-compliance-evidence-collector/) | Packages audit evidence for SOC2, PCI, HIPAA |
| Agent | [multi-account-governance-scorer](agents/26-multi-account-governance-scorer/) | Scores each account against governance standards |
| Agent | [resource-lifecycle-compliance-checker](agents/74-resource-lifecycle-compliance-checker/) | Verifies resources follow lifecycle stages |
| Agent | [patch-compliance-reporter](agents/18-patch-compliance-reporter/) | Reports on EC2/EKS patching status |
| Agent | [scp-effectiveness-auditor](agents/134-scp-effectiveness-auditor/) | Audits service control policies for coverage and gaps |
| Agent | [control-tower-drift-detector](agents/135-control-tower-drift-detector/) | Detects drift from Control Tower guardrails and baselines |
| Agent | [organizations-account-baseline-auditor](agents/136-organizations-account-baseline-auditor/) | Audits member accounts against the org baseline |
| Agent | [tag-policy-compliance-auditor](agents/138-tag-policy-compliance-auditor/) | Audits resources against Organizations tag policies |
| Agent | [config-conformance-pack-reporter](agents/140-config-conformance-pack-reporter/) | Reports Config conformance pack compliance scores |
| Agent | [config-recorder-coverage-auditor](agents/201-config-recorder-coverage-auditor/) | Audits AWS Config recorder coverage across accounts and regions |
| Agent | [trusted-advisor-check-aggregator](agents/226-trusted-advisor-check-aggregator/) | Aggregates Trusted Advisor checks into a prioritized action list |
| Skill | [tag-governance-and-cost-attribution](skills/compliance-governance/tag-governance-and-cost-attribution/) | Establishes tag governance for accurate cost attribution |
| Skill | [aws-config-compliance-assessor](skills/compliance-governance/aws-config-compliance-assessor/) | Assesses compliance via Config rules and conformance packs |
| Skill | [change-management-audit-trail](skills/compliance-governance/change-management-audit-trail/) | Validates changes follow change management process |
| Skill | [access-review-auditor](skills/compliance-governance/access-review-auditor/) | Performs periodic access reviews |
| Skill | [data-residency-validator](skills/compliance-governance/data-residency-validator/) | Validates data stays in approved geographic regions |
| Skill | [encryption-compliance-validator](skills/compliance-governance/encryption-compliance-validator/) | Validates encryption at rest and in transit |
| Skill | [scp-guardrail-design](skills/compliance-governance/scp-guardrail-design/) | Designs service control policy guardrails for the organization |
| Skill | [control-tower-remediation](skills/compliance-governance/control-tower-remediation/) | Remediates Control Tower guardrail violations |
| Skill | [multi-account-baseline-hardening](skills/compliance-governance/multi-account-baseline-hardening/) | Hardens the security baseline across member accounts |
| Skill | [tag-policy-enforcement-strategy](skills/compliance-governance/tag-policy-enforcement-strategy/) | Defines and enforces an organization tag policy strategy |

---

## Certificate and secrets management

| Type | Name | Description |
|------|------|-------------|
| Agent | [certificate-expiration-checker](agents/04-certificate-expiration-checker/) | Tracks TLS cert expiry and failed renewals |
| Agent | [secrets-rotation-compliance](agents/14-secrets-rotation-compliance/) | Audits secrets and keys for rotation compliance |
| Agent | [kms-key-usage-rotation-auditor](agents/55-kms-key-usage-rotation-auditor/) | Audits KMS key rotation, usage, and policies |
| Agent | [secrets-manager-rotation-drift-monitor](agents/152-secrets-manager-rotation-drift-monitor/) | Detects Secrets Manager rotation failures and overdue rotation |
| Agent | [acm-private-ca-health-monitor](agents/179-acm-private-ca-health-monitor/) | Monitors AWS Private CA health, expiry, and CRL generation |

---

## Performance engineering

| Type | Name | Description |
|------|------|-------------|
| Agent | [database-performance-weekly-report](agents/16-database-performance-weekly-report/) | Weekly RDS/Aurora performance digest |
| Agent | [ebs-performance-bottleneck-detector](agents/52-ebs-performance-bottleneck-detector/) | Detects EBS volumes hitting IOPS limits |
| Agent | [elasticache-cluster-health-monitor](agents/60-elasticache-cluster-health-monitor/) | Monitors ElastiCache for memory and eviction issues |
| Agent | [codebuild-cost-duration-optimizer](agents/68-codebuild-cost-duration-optimizer/) | Identifies slow and expensive CodeBuild projects |
| Agent | [efs-throughput-utilization-auditor](agents/89-efs-throughput-utilization-auditor/) | Monitors EFS throughput mode efficiency |
| Agent | [aurora-cluster-optimization-advisor](agents/91-aurora-cluster-optimization-advisor/) | Aurora cost and performance optimization |
| Agent | [redshift-cluster-utilization-reporter](agents/94-redshift-cluster-utilization-reporter/) | Redshift performance and pause/resume recommendations |
| Agent | [rds-proxy-connection-health-monitor](agents/153-rds-proxy-connection-health-monitor/) | Monitors RDS Proxy connection pooling health and borrow latency |
| Agent | [aurora-serverless-v2-scaling-monitor](agents/154-aurora-serverless-v2-scaling-monitor/) | Monitors Aurora Serverless v2 ACU scaling and capacity fit |
| Agent | [cloudfront-cache-hit-ratio-optimizer](agents/210-cloudfront-cache-hit-ratio-optimizer/) | Optimizes CloudFront cache hit ratio to cut origin load and cost |
| Agent | [dynamodb-hot-partition-detector](agents/216-dynamodb-hot-partition-detector/) | Detects DynamoDB hot partitions and throttling from key skew |
| Agent | [redshift-wlm-and-queue-monitor](agents/218-redshift-wlm-and-queue-monitor/) | Monitors Redshift WLM queue waits and query concurrency |
| Skill | [cloudfront-cache-optimization](skills/performance-engineering/cloudfront-cache-optimization/) | Raises CloudFront cache hit ratio to cut origin load and cost |
| Skill | [apigateway-throttling-tuning](skills/performance-engineering/apigateway-throttling-tuning/) | Tunes API Gateway throttling and quota limits |
| Skill | [dynamodb-hot-partition-remediation](skills/performance-engineering/dynamodb-hot-partition-remediation/) | Remediates DynamoDB hot partitions and throttling |
| Skill | [load-test-results-analyzer](skills/performance-engineering/load-test-results-analyzer/) | Interprets load test results and identifies bottlenecks |
| Skill | [database-query-optimizer](skills/performance-engineering/database-query-optimizer/) | Identifies slow queries and recommends optimizations |
| Skill | [lambda-cold-start-investigator](skills/performance-engineering/lambda-cold-start-investigator/) | Diagnoses and optimizes Lambda cold starts |
| Skill | [caching-strategy-advisor](skills/performance-engineering/caching-strategy-advisor/) | Designs caching strategies for AWS services |
| Skill | [throttling-rate-limit-investigator](skills/performance-engineering/throttling-rate-limit-investigator/) | Diagnoses AWS and application throttling |

---

## Networking and DNS

| Type | Name | Description |
|------|------|-------------|
| Agent | [transit-gateway-cost-routing-auditor](agents/44-transit-gateway-cost-routing-auditor/) | Audits TGW routing and cost efficiency |
| Agent | [vpc-endpoint-usage-optimizer](agents/50-vpc-endpoint-usage-optimizer/) | Identifies VPC endpoint savings opportunities |
| Agent | [route53-health-check-validator](agents/54-route53-health-check-validator/) | Validates Route53 health checks and failover DNS |
| Agent | [elastic-ip-waste-detector](agents/45-elastic-ip-waste-detector/) | Identifies unassociated and unnecessary EIPs |
| Agent | [dns-record-hygiene-auditor](agents/85-dns-record-hygiene-auditor/) | Audits DNS records for dangling entries |
| Agent | [vpc-security-group-rule-count-monitor](agents/98-vpc-security-group-rule-count-monitor/) | Monitors SGs approaching rule limits |
| Agent | [direct-connect-link-health-monitor](agents/127-direct-connect-link-health-monitor/) | Monitors Direct Connect link state, light levels, and BGP health |
| Agent | [vpn-tunnel-stability-monitor](agents/128-vpn-tunnel-stability-monitor/) | Monitors Site-to-Site VPN tunnel state and flap frequency |
| Agent | [global-accelerator-endpoint-health-monitor](agents/129-global-accelerator-endpoint-health-monitor/) | Monitors Global Accelerator endpoint health and traffic dials |
| Agent | [network-firewall-rule-effectiveness-monitor](agents/130-network-firewall-rule-effectiveness-monitor/) | Evaluates Network Firewall rule hits and dropped traffic |
| Agent | [privatelink-endpoint-connection-monitor](agents/131-privatelink-endpoint-connection-monitor/) | Monitors PrivateLink endpoint connection state and rejections |
| Agent | [cloudwan-core-network-monitor](agents/132-cloudwan-core-network-monitor/) | Monitors Cloud WAN core network segments and attachments |
| Agent | [route53-resolver-endpoint-monitor](agents/133-route53-resolver-endpoint-monitor/) | Monitors Route 53 Resolver endpoint health and query volume |
| Agent | [route53-dnssec-validation-monitor](agents/180-route53-dnssec-validation-monitor/) | Monitors Route 53 DNSSEC signing status and validation failures |
| Agent | [cloudmap-namespace-health-monitor](agents/195-cloudmap-namespace-health-monitor/) | Monitors Cloud Map service discovery namespace and instance health |
| Agent | [vpc-peering-and-tgw-route-auditor](agents/219-vpc-peering-and-tgw-route-auditor/) | Audits VPC peering and Transit Gateway route tables for blackholes |
| Skill | [vpc-route-and-peering-troubleshooting](skills/networking-dns/vpc-route-and-peering-troubleshooting/) | Troubleshoots VPC peering and Transit Gateway routing |
| Skill | [nacl-and-sg-conflict-resolution](skills/networking-dns/nacl-and-sg-conflict-resolution/) | Resolves NACL and security group conflicts causing drops |
| Skill | [dns-resolution-troubleshooter](skills/networking-dns/dns-resolution-troubleshooter/) | Diagnoses DNS failures in VPCs and private zones |
| Skill | [cross-account-connectivity-debugger](skills/networking-dns/cross-account-connectivity-debugger/) | Debugs peering, TGW, and PrivateLink issues |
| Skill | [load-balancer-health-investigator](skills/networking-dns/load-balancer-health-investigator/) | Investigates ALB/NLB health checks and errors |
| Skill | [latency-path-analyzer](skills/networking-dns/latency-path-analyzer/) | Traces latency hop-by-hop across the network path |
| Skill | [tls-handshake-failure-debugger](skills/networking-dns/tls-handshake-failure-debugger/) | Debugs TLS certificate and protocol failures |
| Skill | [direct-connect-failover-troubleshooting](skills/networking-dns/direct-connect-failover-troubleshooting/) | Diagnoses Direct Connect failover, BGP path selection, and asymmetric routing |
| Skill | [transit-gateway-routing-debugging](skills/networking-dns/transit-gateway-routing-debugging/) | Debugs Transit Gateway route tables, propagation, and blackholes |
| Skill | [privatelink-connectivity-troubleshooting](skills/networking-dns/privatelink-connectivity-troubleshooting/) | Troubleshoots PrivateLink endpoint and service connectivity |
| Skill | [network-firewall-false-positive-tuning](skills/networking-dns/network-firewall-false-positive-tuning/) | Tunes Network Firewall rules to reduce false positives |
| Skill | [dns-failover-and-latency-routing-design](skills/networking-dns/dns-failover-and-latency-routing-design/) | Designs Route 53 failover and latency-based routing |

---

## Backup and data protection

| Type | Name | Description |
|------|------|-------------|
| Agent | [aws-backup-job-failure-investigator](agents/58-aws-backup-job-failure-investigator/) | Investigates failed backup jobs and unprotected resources |
| Agent | [backup-restore-test-validator](agents/144-backup-restore-test-validator/) | Validates restore tests against RTO and RPO targets |
| Agent | [dynamodb-backup-and-pitr-auditor](agents/146-dynamodb-backup-and-pitr-auditor/) | Audits DynamoDB PITR and backup coverage |
| Agent | [backup-vault-lock-and-compliance-auditor](agents/176-backup-vault-lock-and-compliance-auditor/) | Audits AWS Backup Vault Lock and retention compliance |
| Agent | [s3-replication-lag-and-failure-monitor](agents/181-s3-replication-lag-and-failure-monitor/) | Monitors S3 replication lag and failures against the RTC SLA |
| Agent | [efs-backup-and-lifecycle-auditor](agents/182-efs-backup-and-lifecycle-auditor/) | Audits EFS backup coverage and lifecycle transitions |
| Agent | [fsx-backup-and-dr-auditor](agents/183-fsx-backup-and-dr-auditor/) | Audits FSx backup retention and multi-AZ DR posture |
| Skill | [rds-snapshot-security-review](skills/backup-data-protection/rds-snapshot-security-review/) | Reviews RDS snapshot sharing and encryption posture |
| Skill | [backup-coverage-auditor](skills/backup-data-protection/backup-coverage-auditor/) | Identifies unprotected critical resources |
| Skill | [retention-policy-optimizer](skills/backup-data-protection/retention-policy-optimizer/) | Balances cost, compliance, and recovery needs |
| Skill | [restore-testing-validator](skills/backup-data-protection/restore-testing-validator/) | Validates backup restorability |
| Skill | [data-lifecycle-manager](skills/backup-data-protection/data-lifecycle-manager/) | Designs storage tier lifecycle policies |
| Skill | [rpo-rto-gap-calculator](skills/backup-data-protection/rpo-rto-gap-calculator/) | Calculates actual vs target RPO/RTO |
| Skill | [backup-restore-test-planning](skills/backup-data-protection/backup-restore-test-planning/) | Plans and measures periodic restore tests against RTO |
| Skill | [dynamodb-pitr-and-backup-audit](skills/backup-data-protection/dynamodb-pitr-and-backup-audit/) | Audits DynamoDB point-in-time recovery and backup coverage |

---

## Automation and operational efficiency

| Type | Name | Description |
|------|------|-------------|
| Agent | [toil-automation-progress-tracker](agents/20-toil-automation-progress-tracker/) | Tracks toil metrics and automation adoption |
| Agent | [incident-frequency-trend-analyzer](agents/77-incident-frequency-trend-analyzer/) | Analyzes incident patterns over 30/60/90 days |
| Agent | [weekly-executive-summary](agents/40-weekly-executive-summary/) | One-page platform health for leadership |
| Agent | [oncall-burnout-monitor](agents/39-oncall-burnout-monitor/) | Monitors on-call page volume and fatigue indicators |
| Agent | [remediation-orchestrator](agents/227-remediation-orchestrator/) | Validates and safety-gates recommendation records into a human-approval-ready change plan without executing |
| Skill | [toil-identification-analyzer](skills/automation-toil-reduction/toil-identification-analyzer/) | Identifies and quantifies operational toil |
| Skill | [automation-opportunity-scorer](skills/automation-toil-reduction/automation-opportunity-scorer/) | Ranks automation candidates by ROI |
| Skill | [runbook-to-automation-converter](skills/automation-toil-reduction/runbook-to-automation-converter/) | Converts runbooks to automated workflows |
| Skill | [self-healing-pattern-designer](skills/automation-toil-reduction/self-healing-pattern-designer/) | Designs auto-remediation for recurring failures |
| Skill | [operational-metrics-dashboard-builder](skills/automation-toil-reduction/operational-metrics-dashboard-builder/) | Designs actionable operational dashboards |

---

## Container and serverless operations

| Type | Name | Description |
|------|------|-------------|
| Agent | [ecs-task-failure-investigator](agents/23-ecs-task-failure-investigator/) | Investigates OOM kills, image pulls, and crash loops |
| Agent | [lambda-error-pattern-analyzer](agents/41-lambda-error-pattern-analyzer/) | Analyzes Lambda error patterns and timeout trends |
| Agent | [ecs-capacity-provider-optimizer](agents/66-ecs-capacity-provider-optimizer/) | Optimizes ECS capacity provider strategies |
| Agent | [container-vulnerability-digest](agents/38-container-vulnerability-digest/) | Daily ECR CVE digest prioritized by runtime risk |
| Agent | [ecs-service-discovery-health](agents/87-ecs-service-discovery-health/) | Monitors Cloud Map registrations and health |
| Agent | [sqs-dlq-accumulation-alert](agents/90-sqs-dlq-accumulation-alert/) | Monitors DLQ accumulation and traces failures |
| Agent | [eventbridge-rule-health-monitor](agents/93-eventbridge-rule-health-monitor/) | Monitors EventBridge delivery failures |
| Agent | [ecs-service-deployment-stability-monitor](agents/149-ecs-service-deployment-stability-monitor/) | Monitors ECS deployment rollouts, rollbacks, and task churn |
| Agent | [apigateway-usage-plan-and-key-auditor](agents/167-apigateway-usage-plan-and-key-auditor/) | Audits API Gateway usage plans, keys, and throttling |
| Agent | [transfer-family-server-health-monitor](agents/185-transfer-family-server-health-monitor/) | Monitors Transfer Family server health and auth failures |
| Agent | [mq-broker-health-monitor](agents/187-mq-broker-health-monitor/) | Monitors Amazon MQ broker state, heap, and queue depth |
| Agent | [msk-connect-connector-health-monitor](agents/188-msk-connect-connector-health-monitor/) | Monitors MSK Connect connector and task health |
| Agent | [batch-job-queue-efficiency-monitor](agents/193-batch-job-queue-efficiency-monitor/) | Monitors AWS Batch job queue and compute environment efficiency |
| Agent | [apprunner-service-health-monitor](agents/196-apprunner-service-health-monitor/) | Monitors App Runner service health, scaling, and error rates |
| Agent | [eventbridge-rule-target-failure-monitor](agents/214-eventbridge-rule-target-failure-monitor/) | Monitors EventBridge rule target delivery failures |
| Agent | [stepfunctions-execution-failure-analyzer](agents/215-stepfunctions-execution-failure-analyzer/) | Analyzes Step Functions execution failures and state errors |
| Skill | [ecr-image-scan-remediation](skills/container-operations/ecr-image-scan-remediation/) | Triages ECR image scan findings and enforces lifecycle policies |
| Skill | [eks-rbac-least-privilege-review](skills/container-operations/eks-rbac-least-privilege-review/) | Reviews EKS RBAC and pod security for least privilege |
| Skill | [eventbridge-dlq-and-retry-design](skills/messaging-integration/eventbridge-dlq-and-retry-design/) | Designs EventBridge DLQ and retry for reliable delivery |
| Skill | [step-functions-error-handling-design](skills/messaging-integration/step-functions-error-handling-design/) | Designs Step Functions retry, catch, and error handling |
| Skill | [ecs-task-failure-diagnosis](skills/container-operations/ecs-task-failure-diagnosis/) | Systematic diagnosis of ECS task failures |
| Skill | [event-driven-troubleshooting](skills/container-operations/event-driven-troubleshooting/) | Troubleshooting SQS, SNS, EventBridge, and Kinesis |
| Skill | [api-gateway-troubleshooting](skills/container-operations/api-gateway-troubleshooting/) | Diagnosing API Gateway errors and latency |
| Skill | [spot-interruption-handling](skills/container-operations/spot-interruption-handling/) | Designing fault-tolerant Spot architectures |
| Skill | [container-image-security-scanning](skills/container-operations/container-image-security-scanning/) | Interpreting scan results and building secure pipelines |
| Skill | [ecs-deployment-stability-troubleshooting](skills/container-operations/ecs-deployment-stability-troubleshooting/) | Diagnoses unstable ECS deployments and task churn |

---

## Well-Architected Framework

| Type | Name | Description |
|------|------|-------------|
| Agent | [well-architected-review-automator](agents/36-well-architected-review-automator/) | Automated checks against all six pillars |
| Skill | [operational-excellence-reviewer](skills/well-architected/operational-excellence-reviewer/) | Evaluates operational excellence practices |
| Skill | [security-reviewer](skills/well-architected/security-reviewer/) | Evaluates security controls and practices |
| Skill | [reliability-reviewer](skills/well-architected/reliability-reviewer/) | Evaluates fault tolerance and recovery |
| Skill | [performance-efficiency-reviewer](skills/well-architected/performance-efficiency-reviewer/) | Evaluates resource selection and optimization |
| Skill | [cost-optimization-reviewer](skills/well-architected/cost-optimization-reviewer/) | Evaluates cost efficiency practices |
| Skill | [trusted-advisor-remediation-prioritization](skills/well-architected/trusted-advisor-remediation-prioritization/) | Prioritizes Trusted Advisor findings into an action plan |

---

## Migration and modernization

| Type | Name | Description |
|------|------|-------------|
| Agent | [terraform-state-drift-reporter](agents/72-terraform-state-drift-reporter/) | Detects manual changes to IaC-managed resources |
| Agent | [spot-instance-interruption-analyzer](agents/37-spot-instance-interruption-analyzer/) | Analyzes Spot interruption patterns and diversification |
| Skill | [lift-and-shift-assessment](skills/migration-modernization/lift-and-shift-assessment/) | Assesses workloads for rehosting to AWS |
| Skill | [containerization-readiness](skills/migration-modernization/containerization-readiness/) | Evaluates applications for container migration |
| Skill | [database-migration-planner](skills/migration-modernization/database-migration-planner/) | Plans database migrations with DMS and native tools |
| Skill | [serverless-migration-evaluator](skills/migration-modernization/serverless-migration-evaluator/) | Evaluates workloads for serverless with cost comparison |
| Skill | [legacy-dependency-mapper](skills/migration-modernization/legacy-dependency-mapper/) | Discovers hidden dependencies in legacy applications |

---

## Data and analytics

| Type | Name | Description |
|------|------|-------------|
| Skill | [glue-job-failure-diagnosis](skills/data-analytics/glue-job-failure-diagnosis/) | Diagnoses Glue ETL failures including OOM, data skew, and IAM gaps |
| Skill | [kinesis-data-pipeline-lag-investigation](skills/data-analytics/kinesis-data-pipeline-lag-investigation/) | Investigates Kinesis stream lag and throughput bottlenecks |
| Skill | [athena-query-performance-optimizer](skills/data-analytics/athena-query-performance-optimizer/) | Optimizes Athena scan volume, partitioning, and file formats |
| Skill | [redshift-query-tuning-advisor](skills/data-analytics/redshift-query-tuning-advisor/) | Tunes Redshift distribution keys, sort keys, and WLM |
| Agent | [datasync-task-health-monitor](agents/184-datasync-task-health-monitor/) | Monitors DataSync task execution health and transfer failures |
| Agent | [appflow-flow-failure-monitor](agents/186-appflow-flow-failure-monitor/) | Monitors AppFlow flow run failures and record errors |
| Agent | [glue-data-catalog-hygiene-auditor](agents/189-glue-data-catalog-hygiene-auditor/) | Audits Glue Data Catalog crawlers, tables, and stale partitions |
| Agent | [lakeformation-permission-auditor](agents/190-lakeformation-permission-auditor/) | Audits Lake Formation data permissions and broad grants |
| Agent | [quicksight-spice-capacity-monitor](agents/191-quicksight-spice-capacity-monitor/) | Monitors QuickSight SPICE capacity and dataset refresh health |
| Agent | [emr-serverless-cost-monitor](agents/194-emr-serverless-cost-monitor/) | Monitors EMR Serverless usage and cost efficiency |
| Agent | [opensearch-index-and-storage-optimizer](agents/217-opensearch-index-and-storage-optimizer/) | Optimizes OpenSearch index lifecycle and storage |
| Skill | [opensearch-index-lifecycle-optimization](skills/data-analytics/opensearch-index-lifecycle-optimization/) | Optimizes OpenSearch index lifecycle and storage |
| Skill | [redshift-wlm-tuning](skills/data-analytics/redshift-wlm-tuning/) | Tunes Redshift WLM queues and concurrency |
| Skill | [emr-cluster-cost-performance-optimizer](skills/data-analytics/emr-cluster-cost-performance-optimizer/) | Optimizes EMR utilization, Spot usage, and job efficiency |

---

## ML and AI operations

| Type | Name | Description |
|------|------|-------------|
| Skill | [sagemaker-endpoint-health-investigation](skills/ml-ai-operations/sagemaker-endpoint-health-investigation/) | Investigates SageMaker endpoint latency, errors, and capacity |
| Skill | [sagemaker-training-job-cost-optimizer](skills/ml-ai-operations/sagemaker-training-job-cost-optimizer/) | Optimizes training job cost, Spot usage, and utilization |
| Skill | [bedrock-usage-cost-monitor](skills/ml-ai-operations/bedrock-usage-cost-monitor/) | Monitors Bedrock token consumption, cost, and throttling |
| Skill | [ml-model-drift-monitor](skills/ml-ai-operations/ml-model-drift-monitor/) | Monitors deployed models for data and quality drift |
| Agent | [sagemaker-notebook-idle-cost-monitor](agents/192-sagemaker-notebook-idle-cost-monitor/) | Identifies idle SageMaker notebook instances and Studio apps wasting cost |
| Skill | [feature-store-freshness-auditor](skills/ml-ai-operations/feature-store-freshness-auditor/) | Audits Feature Store freshness and online/offline consistency |

---

## Developer experience

| Type | Name | Description |
|------|------|-------------|
| Skill | [build-pipeline-bottleneck-analyzer](skills/developer-experience/build-pipeline-bottleneck-analyzer/) | Finds CI/CD stage bottlenecks that slow feedback loops |
| Skill | [developer-environment-drift-detector](skills/developer-experience/developer-environment-drift-detector/) | Detects config drift across dev, staging, and prod |
| Skill | [artifact-repository-hygiene-auditor](skills/developer-experience/artifact-repository-hygiene-auditor/) | Audits CodeArtifact and ECR for stale artifacts and gaps |
| Skill | [sandbox-account-cleanup-advisor](skills/developer-experience/sandbox-account-cleanup-advisor/) | Identifies stale sandbox resources for cleanup |
| Skill | [iac-template-quality-checker](skills/developer-experience/iac-template-quality-checker/) | Reviews CloudFormation and CDK templates for quality issues |

---

## Messaging and integration

| Type | Name | Description |
|------|------|-------------|
| Skill | [sqs-queue-processing-investigation](skills/messaging-integration/sqs-queue-processing-investigation/) | Investigates SQS lag, message age, and poison messages |
| Skill | [eventbridge-event-flow-debugger](skills/messaging-integration/eventbridge-event-flow-debugger/) | Traces EventBridge event delivery failures |
| Skill | [api-gateway-integration-latency-analyzer](skills/messaging-integration/api-gateway-integration-latency-analyzer/) | Separates gateway overhead from backend integration latency |
| Skill | [step-functions-workflow-optimizer](skills/messaging-integration/step-functions-workflow-optimizer/) | Optimizes state machines for cost and performance |
| Skill | [cross-region-replication-lag-monitor](skills/messaging-integration/cross-region-replication-lag-monitor/) | Monitors S3, DynamoDB, and Aurora replication lag for DR |

---

## Index by AWS service

Find agents by the primary AWS service they cover. An agent appears under one primary service; many agents also read adjacent services.

- **EC2 and Auto Scaling**: [28-auto-scaling-efficiency-auditor](agents/28-auto-scaling-efficiency-auditor/), [37-spot-instance-interruption-analyzer](agents/37-spot-instance-interruption-analyzer/), [45-elastic-ip-waste-detector](agents/45-elastic-ip-waste-detector/), [48-ec2-metadata-security-checker](agents/48-ec2-metadata-security-checker/), [65-auto-scaling-launch-failure-investigator](agents/65-auto-scaling-launch-failure-investigator/), [155-ec2-spot-savings-opportunity-reporter](agents/155-ec2-spot-savings-opportunity-reporter/), [185-transfer-family-server-health-monitor](agents/185-transfer-family-server-health-monitor/), [207-ec2-ami-hygiene-and-eol-auditor](agents/207-ec2-ami-hygiene-and-eol-auditor/)
- **EBS**: [52-ebs-performance-bottleneck-detector](agents/52-ebs-performance-bottleneck-detector/), [208-ebs-snapshot-cost-and-orphan-auditor](agents/208-ebs-snapshot-cost-and-orphan-auditor/)
- **Lambda**: [41-lambda-error-pattern-analyzer](agents/41-lambda-error-pattern-analyzer/), [86-lambda-concurrency-forecast](agents/86-lambda-concurrency-forecast/), [126-secrets-rotation-lambda-failure-monitor](agents/126-secrets-rotation-lambda-failure-monitor/), [150-lambda-provisioned-concurrency-cost-optimizer](agents/150-lambda-provisioned-concurrency-cost-optimizer/), [165-lambda-runtime-deprecation-tracker](agents/165-lambda-runtime-deprecation-tracker/), [212-lambda-iam-permission-scope-auditor](agents/212-lambda-iam-permission-scope-auditor/)
- **ECS and Fargate**: [23-ecs-task-failure-investigator](agents/23-ecs-task-failure-investigator/), [66-ecs-capacity-provider-optimizer](agents/66-ecs-capacity-provider-optimizer/), [87-ecs-service-discovery-health](agents/87-ecs-service-discovery-health/), [149-ecs-service-deployment-stability-monitor](agents/149-ecs-service-deployment-stability-monitor/), [163-ecs-fargate-rightsizing-advisor](agents/163-ecs-fargate-rightsizing-advisor/)
- **EKS**: [10-kubernetes-cluster-health-auditor](agents/10-kubernetes-cluster-health-auditor/), [164-eks-node-group-scaling-efficiency-monitor](agents/164-eks-node-group-scaling-efficiency-monitor/), [203-eks-pod-security-and-rbac-auditor](agents/203-eks-pod-security-and-rbac-auditor/), [204-eks-cluster-version-eol-tracker](agents/204-eks-cluster-version-eol-tracker/)
- **ECR**: [56-ecr-repository-governance](agents/56-ecr-repository-governance/), [202-ecr-image-scan-and-lifecycle-auditor](agents/202-ecr-image-scan-and-lifecycle-auditor/)
- **App Runner**: [196-apprunner-service-health-monitor](agents/196-apprunner-service-health-monitor/)
- **Elastic Beanstalk**: [124-elastic-beanstalk-environment-health-monitor](agents/124-elastic-beanstalk-environment-health-monitor/)
- **Lightsail**: [197-lightsail-resource-inventory-reporter](agents/197-lightsail-resource-inventory-reporter/)
- **Batch**: [193-batch-job-queue-efficiency-monitor](agents/193-batch-job-queue-efficiency-monitor/)
- **RDS and Aurora**: [42-rds-connection-pool-monitor](agents/42-rds-connection-pool-monitor/), [91-aurora-cluster-optimization-advisor](agents/91-aurora-cluster-optimization-advisor/), [153-rds-proxy-connection-health-monitor](agents/153-rds-proxy-connection-health-monitor/), [154-aurora-serverless-v2-scaling-monitor](agents/154-aurora-serverless-v2-scaling-monitor/), [205-rds-snapshot-sharing-and-encryption-auditor](agents/205-rds-snapshot-sharing-and-encryption-auditor/), [206-rds-parameter-group-drift-auditor](agents/206-rds-parameter-group-drift-auditor/)
- **DynamoDB**: [51-dynamodb-capacity-throttle-monitor](agents/51-dynamodb-capacity-throttle-monitor/), [146-dynamodb-backup-and-pitr-auditor](agents/146-dynamodb-backup-and-pitr-auditor/), [166-dynamodb-autoscaling-effectiveness-monitor](agents/166-dynamodb-autoscaling-effectiveness-monitor/), [216-dynamodb-hot-partition-detector](agents/216-dynamodb-hot-partition-detector/)
- **ElastiCache**: [60-elasticache-cluster-health-monitor](agents/60-elasticache-cluster-health-monitor/), [161-elasticache-serverless-cost-monitor](agents/161-elasticache-serverless-cost-monitor/)
- **Redshift**: [94-redshift-cluster-utilization-reporter](agents/94-redshift-cluster-utilization-reporter/), [105-redshift-cluster-efficiency-reporter](agents/105-redshift-cluster-efficiency-reporter/), [218-redshift-wlm-and-queue-monitor](agents/218-redshift-wlm-and-queue-monitor/)
- **OpenSearch**: [120-opensearch-cluster-health-monitor](agents/120-opensearch-cluster-health-monitor/), [217-opensearch-index-and-storage-optimizer](agents/217-opensearch-index-and-storage-optimizer/)
- **S3**: [15-s3-bucket-security-scanner](agents/15-s3-bucket-security-scanner/), [145-s3-lifecycle-and-tiering-optimizer](agents/145-s3-lifecycle-and-tiering-optimizer/), [157-s3-access-point-and-policy-auditor](agents/157-s3-access-point-and-policy-auditor/), [181-s3-replication-lag-and-failure-monitor](agents/181-s3-replication-lag-and-failure-monitor/)
- **EFS and FSx**: [89-efs-throughput-utilization-auditor](agents/89-efs-throughput-utilization-auditor/), [122-fsx-file-system-capacity-monitor](agents/122-fsx-file-system-capacity-monitor/), [182-efs-backup-and-lifecycle-auditor](agents/182-efs-backup-and-lifecycle-auditor/), [183-fsx-backup-and-dr-auditor](agents/183-fsx-backup-and-dr-auditor/)
- **AWS Backup**: [58-aws-backup-job-failure-investigator](agents/58-aws-backup-job-failure-investigator/), [144-backup-restore-test-validator](agents/144-backup-restore-test-validator/), [176-backup-vault-lock-and-compliance-auditor](agents/176-backup-vault-lock-and-compliance-auditor/)
- **DataSync and Transfer**: [184-datasync-task-health-monitor](agents/184-datasync-task-health-monitor/)
- **Glue, Lake Formation, Athena, EMR**: [102-glue-etl-cost-reliability-reporter](agents/102-glue-etl-cost-reliability-reporter/), [104-athena-cost-governance-monitor](agents/104-athena-cost-governance-monitor/), [106-emr-cluster-waste-detector](agents/106-emr-cluster-waste-detector/), [189-glue-data-catalog-hygiene-auditor](agents/189-glue-data-catalog-hygiene-auditor/), [190-lakeformation-permission-auditor](agents/190-lakeformation-permission-auditor/), [194-emr-serverless-cost-monitor](agents/194-emr-serverless-cost-monitor/)
- **Kinesis**: [67-kinesis-shard-utilization-monitor](agents/67-kinesis-shard-utilization-monitor/), [103-kinesis-stream-scaling-advisor](agents/103-kinesis-stream-scaling-advisor/)
- **QuickSight**: [191-quicksight-spice-capacity-monitor](agents/191-quicksight-spice-capacity-monitor/)
- **SageMaker and Bedrock**: [107-sagemaker-endpoint-cost-rightsizer](agents/107-sagemaker-endpoint-cost-rightsizer/), [108-bedrock-token-spend-tracker](agents/108-bedrock-token-spend-tracker/), [109-ml-model-drift-scheduled-reporter](agents/109-ml-model-drift-scheduled-reporter/), [110-feature-store-freshness-monitor](agents/110-feature-store-freshness-monitor/), [192-sagemaker-notebook-idle-cost-monitor](agents/192-sagemaker-notebook-idle-cost-monitor/)
- **API Gateway**: [25-api-gateway-health-monitor](agents/25-api-gateway-health-monitor/), [117-api-gateway-latency-decomposition-reporter](agents/117-api-gateway-latency-decomposition-reporter/), [167-apigateway-usage-plan-and-key-auditor](agents/167-apigateway-usage-plan-and-key-auditor/), [211-apigateway-throttling-and-quota-monitor](agents/211-apigateway-throttling-and-quota-monitor/)
- **SQS, SNS, EventBridge**: [46-sns-delivery-failure-monitor](agents/46-sns-delivery-failure-monitor/), [90-sqs-dlq-accumulation-alert](agents/90-sqs-dlq-accumulation-alert/), [93-eventbridge-rule-health-monitor](agents/93-eventbridge-rule-health-monitor/), [115-sqs-consumer-lag-monitor](agents/115-sqs-consumer-lag-monitor/), [116-eventbridge-delivery-failure-monitor](agents/116-eventbridge-delivery-failure-monitor/), [162-sns-topic-encryption-and-policy-auditor](agents/162-sns-topic-encryption-and-policy-auditor/), [213-sqs-encryption-and-policy-auditor](agents/213-sqs-encryption-and-policy-auditor/), [214-eventbridge-rule-target-failure-monitor](agents/214-eventbridge-rule-target-failure-monitor/)
- **Step Functions**: [47-step-functions-execution-auditor](agents/47-step-functions-execution-auditor/), [99-step-functions-cost-optimizer](agents/99-step-functions-cost-optimizer/), [118-step-functions-cost-efficiency-reporter](agents/118-step-functions-cost-efficiency-reporter/), [215-stepfunctions-execution-failure-analyzer](agents/215-stepfunctions-execution-failure-analyzer/)
- **CloudFront**: [43-cloudfront-cache-efficiency-auditor](agents/43-cloudfront-cache-efficiency-auditor/), [156-cloudfront-security-header-auditor](agents/156-cloudfront-security-header-auditor/), [210-cloudfront-cache-hit-ratio-optimizer](agents/210-cloudfront-cache-hit-ratio-optimizer/)
- **Route 53 and DNS**: [54-route53-health-check-validator](agents/54-route53-health-check-validator/), [85-dns-record-hygiene-auditor](agents/85-dns-record-hygiene-auditor/), [133-route53-resolver-endpoint-monitor](agents/133-route53-resolver-endpoint-monitor/), [180-route53-dnssec-validation-monitor](agents/180-route53-dnssec-validation-monitor/), [195-cloudmap-namespace-health-monitor](agents/195-cloudmap-namespace-health-monitor/)
- **VPC and networking**: [19-network-flow-anomaly-detector](agents/19-network-flow-anomaly-detector/), [44-transit-gateway-cost-routing-auditor](agents/44-transit-gateway-cost-routing-auditor/), [50-vpc-endpoint-usage-optimizer](agents/50-vpc-endpoint-usage-optimizer/), [69-vpc-cidr-capacity-planner](agents/69-vpc-cidr-capacity-planner/), [84-nacl-rule-auditor](agents/84-nacl-rule-auditor/), [96-nat-gateway-high-availability-checker](agents/96-nat-gateway-high-availability-checker/), [98-vpc-security-group-rule-count-monitor](agents/98-vpc-security-group-rule-count-monitor/), [127-direct-connect-link-health-monitor](agents/127-direct-connect-link-health-monitor/), [128-vpn-tunnel-stability-monitor](agents/128-vpn-tunnel-stability-monitor/), [129-global-accelerator-endpoint-health-monitor](agents/129-global-accelerator-endpoint-health-monitor/), [130-network-firewall-rule-effectiveness-monitor](agents/130-network-firewall-rule-effectiveness-monitor/), [131-privatelink-endpoint-connection-monitor](agents/131-privatelink-endpoint-connection-monitor/), [132-cloudwan-core-network-monitor](agents/132-cloudwan-core-network-monitor/), [160-vpc-flow-log-coverage-auditor](agents/160-vpc-flow-log-coverage-auditor/), [219-vpc-peering-and-tgw-route-auditor](agents/219-vpc-peering-and-tgw-route-auditor/), [220-network-acl-and-sg-conflict-detector](agents/220-network-acl-and-sg-conflict-detector/)
- **Load balancing**: [64-load-balancer-ssl-policy-auditor](agents/64-load-balancer-ssl-policy-auditor/), [92-elb-access-log-security-analyzer](agents/92-elb-access-log-security-analyzer/), [209-elb-idle-and-cost-optimizer](agents/209-elb-idle-and-cost-optimizer/), [221-acm-and-elb-tls-policy-drift-monitor](agents/221-acm-and-elb-tls-policy-drift-monitor/)
- **IAM and access**: [07-iam-least-privilege-auditor](agents/07-iam-least-privilege-auditor/), [11-unused-permissions-revoker](agents/11-unused-permissions-revoker/), [49-cross-account-role-trust-auditor](agents/49-cross-account-role-trust-auditor/), [70-iam-policy-simulator-validator](agents/70-iam-policy-simulator-validator/), [158-iam-access-key-age-and-usage-auditor](agents/158-iam-access-key-age-and-usage-auditor/), [200-iam-identity-center-assignment-auditor](agents/200-iam-identity-center-assignment-auditor/)
- **KMS and Secrets**: [14-secrets-rotation-compliance](agents/14-secrets-rotation-compliance/), [55-kms-key-usage-rotation-auditor](agents/55-kms-key-usage-rotation-auditor/), [88-secrets-manager-cost-optimizer](agents/88-secrets-manager-cost-optimizer/), [152-secrets-manager-rotation-drift-monitor](agents/152-secrets-manager-rotation-drift-monitor/), [178-kms-grant-and-policy-drift-auditor](agents/178-kms-grant-and-policy-drift-auditor/)
- **Certificates**: [04-certificate-expiration-checker](agents/04-certificate-expiration-checker/), [148-acm-certificate-expiry-and-renewal-monitor](agents/148-acm-certificate-expiry-and-renewal-monitor/), [179-acm-private-ca-health-monitor](agents/179-acm-private-ca-health-monitor/)
- **GuardDuty, Security Hub, Inspector, Macie**: [63-guardduty-finding-trend-reporter](agents/63-guardduty-finding-trend-reporter/), [173-guardduty-malware-scan-coverage-auditor](agents/173-guardduty-malware-scan-coverage-auditor/), [174-securityhub-finding-aging-reporter](agents/174-securityhub-finding-aging-reporter/), [175-inspector-vulnerability-sla-reporter](agents/175-inspector-vulnerability-sla-reporter/), [177-macie-sensitive-data-exposure-monitor](agents/177-macie-sensitive-data-exposure-monitor/), [223-guardduty-finding-severity-trend-reporter](agents/223-guardduty-finding-severity-trend-reporter/)
- **WAF**: [21-waf-rule-effectiveness-analyzer](agents/21-waf-rule-effectiveness-analyzer/), [147-waf-blocked-traffic-trend-reporter](agents/147-waf-blocked-traffic-trend-reporter/), [172-waf-managed-rule-version-drift-monitor](agents/172-waf-managed-rule-version-drift-monitor/), [222-waf-rate-based-rule-effectiveness-monitor](agents/222-waf-rate-based-rule-effectiveness-monitor/)
- **CloudTrail**: [22-cloudtrail-anomaly-hunter](agents/22-cloudtrail-anomaly-hunter/), [151-cloudtrail-management-event-coverage-auditor](agents/151-cloudtrail-management-event-coverage-auditor/), [224-cloudtrail-lake-query-cost-monitor](agents/224-cloudtrail-lake-query-cost-monitor/)
- **AWS Config**: [31-config-rule-drift-remediator](agents/31-config-rule-drift-remediator/), [140-config-conformance-pack-reporter](agents/140-config-conformance-pack-reporter/), [201-config-recorder-coverage-auditor](agents/201-config-recorder-coverage-auditor/)
- **Organizations and Control Tower**: [134-scp-effectiveness-auditor](agents/134-scp-effectiveness-auditor/), [135-control-tower-drift-detector](agents/135-control-tower-drift-detector/), [136-organizations-account-baseline-auditor](agents/136-organizations-account-baseline-auditor/), [199-organizations-scp-change-monitor](agents/199-organizations-scp-change-monitor/)
- **CloudWatch and observability**: [06-cloudwatch-alarm-fatigue-reducer](agents/06-cloudwatch-alarm-fatigue-reducer/), [27-log-retention-cost-optimizer](agents/27-log-retention-cost-optimizer/), [59-cloudwatch-contributor-insights-reporter](agents/59-cloudwatch-contributor-insights-reporter/), [71-cloudwatch-log-insights-query-library](agents/71-cloudwatch-log-insights-query-library/), [95-cloudwatch-alarm-configuration-auditor](agents/95-cloudwatch-alarm-configuration-auditor/), [141-cloudwatch-metrics-cost-optimizer](agents/141-cloudwatch-metrics-cost-optimizer/), [142-xray-trace-sampling-optimizer](agents/142-xray-trace-sampling-optimizer/), [168-cloudwatch-synthetics-canary-health-monitor](agents/168-cloudwatch-synthetics-canary-health-monitor/), [169-rum-and-frontend-error-trend-reporter](agents/169-rum-and-frontend-error-trend-reporter/)
- **CodePipeline, CodeDeploy, CodeBuild**: [13-pipeline-failure-analyzer](agents/13-pipeline-failure-analyzer/), [68-codebuild-cost-duration-optimizer](agents/68-codebuild-cost-duration-optimizer/), [111-build-pipeline-lead-time-reporter](agents/111-build-pipeline-lead-time-reporter/), [170-codepipeline-stage-failure-analyzer](agents/170-codepipeline-stage-failure-analyzer/), [171-codedeploy-deployment-health-monitor](agents/171-codedeploy-deployment-health-monitor/)
- **CloudFormation and IaC**: [53-cloudformation-stack-health-checker](agents/53-cloudformation-stack-health-checker/), [72-terraform-state-drift-reporter](agents/72-terraform-state-drift-reporter/)
- **Cost and billing**: [02-cost-anomaly-detector](agents/02-cost-anomaly-detector/), [17-service-quota-watchdog](agents/17-service-quota-watchdog/), [24-storage-cost-optimizer](agents/24-storage-cost-optimizer/), [61-savings-plan-utilization-tracker](agents/61-savings-plan-utilization-tracker/), [80-monthly-cost-allocation-report](agents/80-monthly-cost-allocation-report/), [81-graviton-migration-opportunity-finder](agents/81-graviton-migration-opportunity-finder/), [83-reserved-instance-coverage-optimizer](agents/83-reserved-instance-coverage-optimizer/), [114-sandbox-cost-cleanup-reporter](agents/114-sandbox-cost-cleanup-reporter/), [137-cost-anomaly-root-cause-investigator](agents/137-cost-anomaly-root-cause-investigator/), [139-quota-utilization-forecaster](agents/139-quota-utilization-forecaster/), [198-workspaces-utilization-and-cost-monitor](agents/198-workspaces-utilization-and-cost-monitor/), [225-tag-coverage-and-cost-attribution-auditor](agents/225-tag-coverage-and-cost-attribution-auditor/)
- **Trusted Advisor and Health**: [97-aws-health-event-impact-assessor](agents/97-aws-health-event-impact-assessor/), [226-trusted-advisor-check-aggregator](agents/226-trusted-advisor-check-aggregator/)
- **Tagging**: [08-resource-tagging-compliance](agents/08-resource-tagging-compliance/), [138-tag-policy-compliance-auditor](agents/138-tag-policy-compliance-auditor/)
- **Cross-service and reporting**: [01-infrastructure-health-report](agents/01-infrastructure-health-report/), [03-security-group-auditor](agents/03-security-group-auditor/), [05-deployment-rollback-analyzer](agents/05-deployment-rollback-analyzer/), [09-incident-postmortem-generator](agents/09-incident-postmortem-generator/), [12-cross-region-dr-sync-validator](agents/12-cross-region-dr-sync-validator/), [16-database-performance-weekly-report](agents/16-database-performance-weekly-report/), [18-patch-compliance-reporter](agents/18-patch-compliance-reporter/), [20-toil-automation-progress-tracker](agents/20-toil-automation-progress-tracker/), [26-multi-account-governance-scorer](agents/26-multi-account-governance-scorer/), [29-event-driven-architecture-health](agents/29-event-driven-architecture-health/), [30-sla-breach-predictor](agents/30-sla-breach-predictor/), [32-orphaned-resource-cleaner](agents/32-orphaned-resource-cleaner/), [33-cross-service-dependency-mapper](agents/33-cross-service-dependency-mapper/), [34-deployment-velocity-reporter](agents/34-deployment-velocity-reporter/), [35-compliance-evidence-collector](agents/35-compliance-evidence-collector/), [36-well-architected-review-automator](agents/36-well-architected-review-automator/), [38-container-vulnerability-digest](agents/38-container-vulnerability-digest/), [39-oncall-burnout-monitor](agents/39-oncall-burnout-monitor/), [40-weekly-executive-summary](agents/40-weekly-executive-summary/), [57-ssm-patch-baseline-drift-detector](agents/57-ssm-patch-baseline-drift-detector/), [62-multi-region-latency-comparator](agents/62-multi-region-latency-comparator/), [73-service-health-dashboard-generator](agents/73-service-health-dashboard-generator/), [74-resource-lifecycle-compliance-checker](agents/74-resource-lifecycle-compliance-checker/), [75-cross-region-data-transfer-auditor](agents/75-cross-region-data-transfer-auditor/), [76-container-runtime-security-monitor](agents/76-container-runtime-security-monitor/), [77-incident-frequency-trend-analyzer](agents/77-incident-frequency-trend-analyzer/), [78-api-throttling-pattern-reporter](agents/78-api-throttling-pattern-reporter/), [79-infrastructure-age-eol-tracker](agents/79-infrastructure-age-eol-tracker/), [82-public-exposure-surface-scanner](agents/82-public-exposure-surface-scanner/), [100-weekly-reliability-scorecard](agents/100-weekly-reliability-scorecard/), [101-devops-agent-usage-credit-monitor](agents/101-devops-agent-usage-credit-monitor/), [112-environment-parity-drift-reporter](agents/112-environment-parity-drift-reporter/), [113-artifact-repository-hygiene-reporter](agents/113-artifact-repository-hygiene-reporter/), [119-dr-replication-readiness-monitor](agents/119-dr-replication-readiness-monitor/), [121-msk-kafka-cluster-health-monitor](agents/121-msk-kafka-cluster-health-monitor/), [123-cognito-user-pool-security-monitor](agents/123-cognito-user-pool-security-monitor/), [125-appsync-graphql-api-monitor](agents/125-appsync-graphql-api-monitor/), [143-carbon-footprint-efficiency-reporter](agents/143-carbon-footprint-efficiency-reporter/), [159-ssm-session-manager-audit-reporter](agents/159-ssm-session-manager-audit-reporter/), [186-appflow-flow-failure-monitor](agents/186-appflow-flow-failure-monitor/), [187-mq-broker-health-monitor](agents/187-mq-broker-health-monitor/), [188-msk-connect-connector-health-monitor](agents/188-msk-connect-connector-health-monitor/), [227-remediation-orchestrator](agents/227-remediation-orchestrator/)
