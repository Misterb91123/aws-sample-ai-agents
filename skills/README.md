# AWS DevOps Agent - Skills Library for SRE, Platform & DevOps

A curated library of **190 skills** organized across **26 operational dimensions** for [AWS DevOps Agent](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-devops-agent-skills.html). Each skill provides domain-specific investigation procedures, decision frameworks, and operational knowledge that the agent loads automatically when relevant to a task.

---

## What Are Skills?

Skills are modular instruction sets (Markdown files) that extend AWS DevOps Agent with specialized domain knowledge. Unlike one-time chat instructions, skills are reusable capabilities that load automatically during investigations and custom agent invocations.

Each skill contains:
- **Frontmatter** - name and description the agent uses to decide when to activate the skill.
- **Step-by-step procedures** - investigation workflows, decision trees, and analysis approaches.
- **Reference tables** - thresholds, severity classifications, and comparison criteria.
- **Output format** - what the skill should produce (reports, recommendations, action items).

---

## Categories & Skills

### 1. Incident Management

Skills for detecting, triaging, responding to, and communicating during incidents.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [incident-triage-classifier](incident-management/incident-triage-classifier/) | Classifies incoming incidents by severity based on alarm patterns and customer impact | Incident Triage |
| [blast-radius-assessment](incident-management/blast-radius-assessment/) | Maps service dependencies to determine full scope of impact during an incident | Incident RCA |
| [escalation-path-navigator](incident-management/escalation-path-navigator/) | Determines correct escalation path based on severity, service ownership, and time | Incident Mitigation |
| [incident-communication-drafter](incident-management/incident-communication-drafter/) | Drafts status page updates, executive briefings, and customer communications | Generic |
| [runbook-executor-guide](incident-management/runbook-executor-guide/) | Guides operators through standard runbooks for common failure scenarios | Incident Mitigation |

---

### 2. Release Management

Skills for safe, reliable software delivery and deployment lifecycle.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [release-changelog-generator](release-management/release-changelog-generator/) | Generates structured changelogs from deployments, commits, and config changes | Generic |
| [rollback-decision-framework](release-management/rollback-decision-framework/) | Structured framework for deciding rollback vs forward-fix vs monitor | Incident Mitigation |
| [canary-deployment-analysis](release-management/canary-deployment-analysis/) | Analyzes canary metrics to determine promote, extend, or rollback decisions | Generic |
| [pre-deployment-readiness-check](release-management/pre-deployment-readiness-check/) | Validates all preconditions before deploying to production | Generic |
| [deployment-freeze-enforcer](release-management/deployment-freeze-enforcer/) | Enforces freeze windows and manages exception approval workflows | Generic |

---

### 3. Security Operations

Skills for detecting, investigating, and responding to security threats.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [security-incident-containment](security-operations/security-incident-containment/) | Containment procedures for active security incidents while preserving forensic evidence | Incident Mitigation |
| [vulnerability-prioritization](security-operations/vulnerability-prioritization/) | Prioritizes CVEs by exploitability, exposure, and business context beyond CVSS | Generic |
| [exposed-credentials-response](security-operations/exposed-credentials-response/) | Immediate response procedure when credentials are found exposed | Incident Mitigation |
| [guardduty-finding-investigation](security-operations/guardduty-finding-investigation/) | Investigates GuardDuty findings to determine real threats vs false positives | Incident RCA |
| [network-anomaly-investigation](security-operations/network-anomaly-investigation/) | Investigates anomalous network traffic for exfiltration, C2, and lateral movement | Incident RCA |
| [certificate-expiry-remediation](security-operations/certificate-expiry-remediation/) | Fixes expiring ACM and imported certificates and failed renewals before endpoints break | Evaluation |
| [waf-blocked-traffic-analysis](security-operations/waf-blocked-traffic-analysis/) | Separates WAF attacks from false positives and tunes rules and rate limits | Incident RCA |
| [cloudtrail-coverage-gap-analysis](security-operations/cloudtrail-coverage-gap-analysis/) | Finds gaps in CloudTrail management and data event coverage across accounts and regions | Generic |
| [lambda-execution-role-hardening](security-operations/lambda-execution-role-hardening/) | Hardens Lambda execution role permissions toward least privilege | Evaluation |
| [sqs-access-and-encryption-hardening](security-operations/sqs-access-and-encryption-hardening/) | Hardens SQS encryption and access policies | Evaluation |
| [tls-policy-modernization](security-operations/tls-policy-modernization/) | Modernizes ELB and CloudFront TLS policies and removes weak ciphers | Evaluation |
| [waf-rate-based-rule-tuning](security-operations/waf-rate-based-rule-tuning/) | Tunes WAF rate-based rules to observed attack volume | Generic |

---

### 4. Cost Management

Skills for optimizing AWS spend and maintaining financial accountability.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [rightsizing-recommendation-engine](cost-management/rightsizing-recommendation-engine/) | Identifies over/under-provisioned resources with specific sizing recommendations | Generic |
| [data-transfer-cost-analyzer](cost-management/data-transfer-cost-analyzer/) | Analyzes data transfer costs across cross-AZ, cross-region, and internet egress | Generic |
| [idle-resource-hunter](cost-management/idle-resource-hunter/) | Finds idle and orphaned resources accruing costs without providing value | Generic |
| [savings-plan-advisor](cost-management/savings-plan-advisor/) | Recommends optimal Savings Plans and Reserved Instance commitments | Generic |
| [cost-allocation-gap-finder](cost-management/cost-allocation-gap-finder/) | Identifies gaps in cost allocation for accurate team/service chargeback | Generic |
| [cost-anomaly-root-cause-analysis](cost-management/cost-anomaly-root-cause-analysis/) | Isolates the service, account, and usage type driving a cost anomaly | Incident RCA |
| [service-quota-forecasting](cost-management/service-quota-forecasting/) | Projects quota exhaustion from utilization trend and prepares increase requests | Generic |
| [observability-cost-optimization](cost-management/observability-cost-optimization/) | Cuts CloudWatch and X-Ray spend without losing needed signal | Generic |
| [lambda-concurrency-cost-tuning](cost-management/lambda-concurrency-cost-tuning/) | Balances Lambda provisioned concurrency cost against cold-start performance | Generic |
| [s3-storage-tiering-optimization](cost-management/s3-storage-tiering-optimization/) | Tiers cold S3 data and cleans up incomplete multipart uploads | Generic |
| [ebs-snapshot-cleanup-strategy](cost-management/ebs-snapshot-cleanup-strategy/) | Reclaims cost from orphaned and redundant EBS snapshots | Generic |
| [load-balancer-cost-rationalization](cost-management/load-balancer-cost-rationalization/) | Rationalizes idle and low-traffic load balancers | Generic |
| [cloudtrail-lake-cost-control](cost-management/cloudtrail-lake-cost-control/) | Controls CloudTrail Lake storage and query cost | Generic |

---

### 5. Resiliency & Reliability

Skills for validating and improving infrastructure resilience.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [az-failure-readiness-assessment](resiliency-reliability/az-failure-readiness-assessment/) | Assesses readiness to survive an AZ failure without customer impact | Generic |
| [dependency-health-analyzer](resiliency-reliability/dependency-health-analyzer/) | Analyzes service dependency health, circuit breakers, timeouts, and SPoF | Incident RCA |
| [error-budget-tracker](resiliency-reliability/error-budget-tracker/) | Tracks SLO compliance and error budget burn rates for release decisions | Generic |
| [disaster-recovery-validation](resiliency-reliability/disaster-recovery-validation/) | Validates DR configurations, backup integrity, and RTO/RPO compliance | Generic |
| [chaos-experiment-planner](resiliency-reliability/chaos-experiment-planner/) | Designs controlled chaos experiments to validate resilience hypotheses | Generic |

---

### 6. Observability & Monitoring

Skills for understanding system behavior and detecting issues early.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [trace-analysis-investigator](observability-monitoring/trace-analysis-investigator/) | Analyzes distributed traces to identify bottlenecks and error sources | Incident RCA |
| [sli-measurement-validator](observability-monitoring/sli-measurement-validator/) | Validates that SLI definitions accurately represent customer experience | Generic |
| [log-pattern-anomaly-detector](observability-monitoring/log-pattern-anomaly-detector/) | Detects new error patterns and log anomalies before alarms fire | Generic |
| [metric-correlation-investigator](observability-monitoring/metric-correlation-investigator/) | Correlates metrics to distinguish root causes from cascading effects | Incident RCA |
| [dashboard-gap-analyzer](observability-monitoring/dashboard-gap-analyzer/) | Identifies gaps in monitoring coverage across services | Generic |
| [cloudwatch-cost-reduction](observability-monitoring/cloudwatch-cost-reduction/) | Reduces CloudWatch metric, log, and dashboard spend | Generic |
| [xray-sampling-strategy-design](observability-monitoring/xray-sampling-strategy-design/) | Designs X-Ray sampling rules that balance cost and coverage | Generic |
| [distributed-tracing-gap-analysis](observability-monitoring/distributed-tracing-gap-analysis/) | Finds gaps in end-to-end distributed tracing | Generic |
| [alarm-noise-reduction-strategy](observability-monitoring/alarm-noise-reduction-strategy/) | Reduces alarm noise and false pages | Generic |
| [config-conformance-drift-remediation](observability-monitoring/config-conformance-drift-remediation/) | Remediates Config conformance pack noncompliance and rule drift | Evaluation |
| [guardduty-trend-analysis](observability-monitoring/guardduty-trend-analysis/) | Analyzes GuardDuty severity trends and recurring finding types | Incident RCA |

---

### 7. Platform Engineering

Skills for managing infrastructure platforms and enabling development teams.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [capacity-planning-forecaster](platform-engineering/capacity-planning-forecaster/) | Forecasts resource needs based on growth trends and upcoming events | Generic |
| [infrastructure-drift-detector](platform-engineering/infrastructure-drift-detector/) | Detects configuration drift between IaC and actual deployed state | Generic |
| [container-image-lifecycle-manager](platform-engineering/container-image-lifecycle-manager/) | Manages ECR image lifecycle: stale images, vulnerabilities, retention policies | Generic |
| [service-onboarding-checklist](platform-engineering/service-onboarding-checklist/) | Validates new service readiness across infra, security, observability, and ops | Generic |
| [vpc-network-topology-auditor](platform-engineering/vpc-network-topology-auditor/) | Audits VPC topology for misconfigurations, routing issues, and connectivity problems | Generic |
| [eks-version-upgrade-planning](platform-engineering/eks-version-upgrade-planning/) | Plans EKS Kubernetes version upgrades before end of support | Generic |
| [ami-and-os-lifecycle-management](platform-engineering/ami-and-os-lifecycle-management/) | Manages AMI hygiene and operating system end-of-life | Generic |
| [rds-parameter-baseline-management](platform-engineering/rds-parameter-baseline-management/) | Manages RDS and Aurora parameter group baselines and drift | Generic |

---

### 8. Compliance & Governance

Skills for maintaining regulatory compliance and organizational governance.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [aws-config-compliance-assessor](compliance-governance/aws-config-compliance-assessor/) | Assesses compliance using AWS Config rules and conformance packs | Generic |
| [change-management-audit-trail](compliance-governance/change-management-audit-trail/) | Validates changes follow change management process via CloudTrail correlation | Generic |
| [access-review-auditor](compliance-governance/access-review-auditor/) | Performs periodic access reviews for stale permissions and excessive privilege | Generic |
| [data-residency-validator](compliance-governance/data-residency-validator/) | Validates data storage complies with geographic residency requirements | Generic |
| [encryption-compliance-validator](compliance-governance/encryption-compliance-validator/) | Validates encryption-at-rest and in-transit across all services | Generic |
| [scp-guardrail-design](compliance-governance/scp-guardrail-design/) | Designs service control policy guardrails for the organization | Generic |
| [control-tower-remediation](compliance-governance/control-tower-remediation/) | Remediates Control Tower guardrail violations and drift | Evaluation |
| [multi-account-baseline-hardening](compliance-governance/multi-account-baseline-hardening/) | Hardens the security baseline across member accounts | Generic |
| [tag-policy-enforcement-strategy](compliance-governance/tag-policy-enforcement-strategy/) | Defines and enforces an organization tag policy strategy | Generic |
| [tag-governance-and-cost-attribution](compliance-governance/tag-governance-and-cost-attribution/) | Establishes tag governance for accurate cost attribution | Generic |

---

### 9. Migration & Modernization

Skills for planning and executing workload migrations to AWS and modernization initiatives.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [lift-and-shift-assessment](migration-modernization/lift-and-shift-assessment/) | Assesses workloads for direct rehosting to AWS with sizing and sequencing | Generic |
| [containerization-readiness](migration-modernization/containerization-readiness/) | Evaluates applications for containerization, identifying refactoring needs | Generic |
| [database-migration-planner](migration-modernization/database-migration-planner/) | Plans database migrations with schema compatibility, DMS strategy, and cutover procedures | Generic |
| [serverless-migration-evaluator](migration-modernization/serverless-migration-evaluator/) | Evaluates workloads for serverless migration with cost comparison and architecture design | Generic |
| [legacy-dependency-mapper](migration-modernization/legacy-dependency-mapper/) | Discovers hidden dependencies in legacy applications via network, config, and runtime analysis | Generic |

---

### 10. Performance Engineering

Skills for diagnosing, optimizing, and validating application and infrastructure performance.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [load-test-results-analyzer](performance-engineering/load-test-results-analyzer/) | Interprets load test results to identify bottlenecks and validate capacity readiness | Generic |
| [database-query-optimizer](performance-engineering/database-query-optimizer/) | Identifies slow queries and recommends index, schema, and query optimizations | Incident RCA |
| [lambda-cold-start-investigator](performance-engineering/lambda-cold-start-investigator/) | Diagnoses and optimizes Lambda cold start latency with provisioned concurrency guidance | Incident RCA |
| [caching-strategy-advisor](performance-engineering/caching-strategy-advisor/) | Designs and optimizes caching strategies across CloudFront, ElastiCache, DAX, and API Gateway | Generic |
| [throttling-rate-limit-investigator](performance-engineering/throttling-rate-limit-investigator/) | Diagnoses AWS service and application throttling with rate limit mitigation strategies | Incident RCA |
| [cloudfront-cache-optimization](performance-engineering/cloudfront-cache-optimization/) | Raises CloudFront cache hit ratio to cut origin load and cost | Generic |
| [apigateway-throttling-tuning](performance-engineering/apigateway-throttling-tuning/) | Tunes API Gateway throttling and quota limits | Incident RCA |
| [dynamodb-hot-partition-remediation](performance-engineering/dynamodb-hot-partition-remediation/) | Remediates DynamoDB hot partitions and throttling | Incident RCA |

---

### 11. Networking & DNS

Skills for troubleshooting network connectivity, DNS resolution, and TLS issues.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [dns-resolution-troubleshooter](networking-dns/dns-resolution-troubleshooter/) | Diagnoses DNS failures including private hosted zones, resolver rules, and split-horizon issues | Incident RCA |
| [cross-account-connectivity-debugger](networking-dns/cross-account-connectivity-debugger/) | Debugs cross-account connectivity via VPC peering, Transit Gateway, and PrivateLink | Incident RCA |
| [load-balancer-health-investigator](networking-dns/load-balancer-health-investigator/) | Investigates ALB/NLB health check failures, 5xx errors, and traffic distribution issues | Incident RCA |
| [latency-path-analyzer](networking-dns/latency-path-analyzer/) | Analyzes network latency hop-by-hop to identify where delays are introduced | Incident RCA |
| [tls-handshake-failure-debugger](networking-dns/tls-handshake-failure-debugger/) | Debugs TLS failures including cert validation, cipher mismatches, and mTLS issues | Incident RCA |
| [direct-connect-failover-troubleshooting](networking-dns/direct-connect-failover-troubleshooting/) | Diagnoses Direct Connect failover, BGP path selection, and asymmetric routing | Incident RCA |
| [transit-gateway-routing-debugging](networking-dns/transit-gateway-routing-debugging/) | Debugs Transit Gateway route tables, propagation, and blackhole routes | Incident RCA |
| [privatelink-connectivity-troubleshooting](networking-dns/privatelink-connectivity-troubleshooting/) | Troubleshoots PrivateLink endpoint and endpoint service connectivity | Incident RCA |
| [network-firewall-false-positive-tuning](networking-dns/network-firewall-false-positive-tuning/) | Tunes Network Firewall rules to reduce false positives | Generic |
| [dns-failover-and-latency-routing-design](networking-dns/dns-failover-and-latency-routing-design/) | Designs Route 53 failover and latency-based routing | Generic |
| [vpc-route-and-peering-troubleshooting](networking-dns/vpc-route-and-peering-troubleshooting/) | Troubleshoots VPC peering and Transit Gateway routing | Incident RCA |
| [nacl-and-sg-conflict-resolution](networking-dns/nacl-and-sg-conflict-resolution/) | Resolves NACL and security group conflicts causing drops | Incident RCA |

---

### 12. Backup & Data Protection

Skills for ensuring data is protected, recoverable, and compliant with retention requirements.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [backup-coverage-auditor](backup-data-protection/backup-coverage-auditor/) | Audits backup coverage to identify unprotected critical resources | Generic |
| [retention-policy-optimizer](backup-data-protection/retention-policy-optimizer/) | Optimizes retention policies to balance cost, compliance, and recovery needs | Generic |
| [restore-testing-validator](backup-data-protection/restore-testing-validator/) | Validates backup restorability with test procedures and RTO/RPO measurement | Generic |
| [data-lifecycle-manager](backup-data-protection/data-lifecycle-manager/) | Designs data lifecycle policies for transitioning between storage tiers | Generic |
| [rpo-rto-gap-calculator](backup-data-protection/rpo-rto-gap-calculator/) | Calculates actual RPO/RTO capabilities and identifies gaps against targets | Generic |
| [backup-restore-test-planning](backup-data-protection/backup-restore-test-planning/) | Plans and measures periodic restore tests against RTO and RPO | Generic |
| [dynamodb-pitr-and-backup-audit](backup-data-protection/dynamodb-pitr-and-backup-audit/) | Audits DynamoDB point-in-time recovery and backup coverage | Generic |
| [rds-snapshot-security-review](backup-data-protection/rds-snapshot-security-review/) | Reviews RDS snapshot sharing and encryption posture | Evaluation |

---

### 13. Automation & Toil Reduction

Skills for identifying, measuring, and eliminating operational toil through automation.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [toil-identification-analyzer](automation-toil-reduction/toil-identification-analyzer/) | Identifies and quantifies operational toil by analyzing repetitive manual tasks | Generic |
| [automation-opportunity-scorer](automation-toil-reduction/automation-opportunity-scorer/) | Scores and ranks automation candidates by ROI, feasibility, and risk | Generic |
| [runbook-to-automation-converter](automation-toil-reduction/runbook-to-automation-converter/) | Converts manual runbooks into automated Step Functions/Lambda/SSM workflows | Generic |
| [self-healing-pattern-designer](automation-toil-reduction/self-healing-pattern-designer/) | Designs auto-detection and remediation patterns for recurring failure modes | Generic |
| [operational-metrics-dashboard-builder](automation-toil-reduction/operational-metrics-dashboard-builder/) | Designs actionable operational dashboards with proper metric hierarchy and alerting | Generic |

---

### 14. Well-Architected Framework

Skills for evaluating workloads against the AWS Well-Architected Framework pillars.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [operational-excellence-reviewer](well-architected/operational-excellence-reviewer/) | Evaluates operational excellence practices and processes | Evaluation |
| [security-reviewer](well-architected/security-reviewer/) | Evaluates security controls, identity, and data protection | Evaluation |
| [reliability-reviewer](well-architected/reliability-reviewer/) | Evaluates fault tolerance, recovery, and change management | Evaluation |
| [performance-efficiency-reviewer](well-architected/performance-efficiency-reviewer/) | Evaluates resource selection and performance optimization | Evaluation |
| [cost-optimization-reviewer](well-architected/cost-optimization-reviewer/) | Evaluates cost efficiency and financial management practices | Evaluation |
| [trusted-advisor-remediation-prioritization](well-architected/trusted-advisor-remediation-prioritization/) | Prioritizes Trusted Advisor findings into an action plan | Evaluation |
| [trusted-advisor-remediation-and-migration-playbook](well-architected/trusted-advisor-remediation-and-migration-playbook/) | Adds the concrete remediation steps, quantified impact, and migration path per Trusted Advisor check | Evaluation |

---

### 15. Container & Service Operations

Skills for troubleshooting containerized and serverless service operations.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [ecs-task-failure-diagnosis](container-operations/ecs-task-failure-diagnosis/) | Diagnoses ECS task failures including OOM, image pulls, and health checks | Incident RCA |
| [event-driven-troubleshooting](container-operations/event-driven-troubleshooting/) | Troubleshoots SQS, SNS, EventBridge, and Kinesis event flows | Incident RCA |
| [api-gateway-troubleshooting](container-operations/api-gateway-troubleshooting/) | Diagnoses API Gateway errors, latency, throttling, and CORS | Incident RCA |
| [spot-interruption-handling](container-operations/spot-interruption-handling/) | Designs fault-tolerant Spot Instance architectures | Generic |
| [container-image-security-scanning](container-operations/container-image-security-scanning/) | Interprets scan results and builds secure image pipelines | Generic |
| [ecs-deployment-stability-troubleshooting](container-operations/ecs-deployment-stability-troubleshooting/) | Diagnoses unstable ECS deployments, rollbacks, and task churn | Incident RCA |
| [ecr-image-scan-remediation](container-operations/ecr-image-scan-remediation/) | Triages ECR image scan findings and enforces lifecycle policies | Generic |
| [eks-rbac-least-privilege-review](container-operations/eks-rbac-least-privilege-review/) | Reviews EKS RBAC and pod security for least privilege | Evaluation |

---

### 16. Data & Analytics

Skills for diagnosing and optimizing data processing and analytics workloads.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [glue-job-failure-diagnosis](data-analytics/glue-job-failure-diagnosis/) | Diagnoses Glue ETL failures including OOM, data skew, and IAM gaps | Incident RCA |
| [kinesis-data-pipeline-lag-investigation](data-analytics/kinesis-data-pipeline-lag-investigation/) | Investigates Kinesis stream lag and throughput bottlenecks | Incident RCA |
| [athena-query-performance-optimizer](data-analytics/athena-query-performance-optimizer/) | Optimizes Athena scan volume, partitioning, and file formats | Generic |
| [redshift-query-tuning-advisor](data-analytics/redshift-query-tuning-advisor/) | Tunes Redshift distribution keys, sort keys, and WLM | Generic |
| [emr-cluster-cost-performance-optimizer](data-analytics/emr-cluster-cost-performance-optimizer/) | Optimizes EMR utilization, Spot usage, and job efficiency | Generic |
| [opensearch-index-lifecycle-optimization](data-analytics/opensearch-index-lifecycle-optimization/) | Optimizes OpenSearch index lifecycle and storage | Generic |
| [redshift-wlm-tuning](data-analytics/redshift-wlm-tuning/) | Tunes Redshift WLM queues and concurrency | Generic |

---

### 17. ML & AI Operations

Skills for operating machine learning and generative AI workloads on AWS.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [sagemaker-endpoint-health-investigation](ml-ai-operations/sagemaker-endpoint-health-investigation/) | Investigates SageMaker endpoint latency, errors, and capacity | Incident RCA |
| [sagemaker-training-job-cost-optimizer](ml-ai-operations/sagemaker-training-job-cost-optimizer/) | Optimizes training job cost, Spot usage, and utilization | Generic |
| [bedrock-usage-cost-monitor](ml-ai-operations/bedrock-usage-cost-monitor/) | Monitors Bedrock token consumption, cost, and throttling | Generic |
| [ml-model-drift-monitor](ml-ai-operations/ml-model-drift-monitor/) | Monitors deployed models for data and quality drift | Generic |
| [feature-store-freshness-auditor](ml-ai-operations/feature-store-freshness-auditor/) | Audits Feature Store freshness and online/offline consistency | Generic |

---

### 18. Developer Experience

Skills for improving developer productivity, environment consistency, and tooling hygiene.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [build-pipeline-bottleneck-analyzer](developer-experience/build-pipeline-bottleneck-analyzer/) | Finds CI/CD stage bottlenecks that slow feedback loops | Generic |
| [developer-environment-drift-detector](developer-experience/developer-environment-drift-detector/) | Detects config drift across dev, staging, and prod | Generic |
| [artifact-repository-hygiene-auditor](developer-experience/artifact-repository-hygiene-auditor/) | Audits CodeArtifact and ECR for stale artifacts and gaps | Generic |
| [sandbox-account-cleanup-advisor](developer-experience/sandbox-account-cleanup-advisor/) | Identifies stale sandbox resources for cleanup | Generic |
| [iac-template-quality-checker](developer-experience/iac-template-quality-checker/) | Reviews CloudFormation and CDK templates for quality issues | Generic |

---

### 19. Messaging & Integration

Skills for diagnosing messaging, event routing, and cross-region integration.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [sqs-queue-processing-investigation](messaging-integration/sqs-queue-processing-investigation/) | Investigates SQS lag, message age, and poison messages | Incident RCA |
| [eventbridge-event-flow-debugger](messaging-integration/eventbridge-event-flow-debugger/) | Traces EventBridge event delivery failures | Incident RCA |
| [api-gateway-integration-latency-analyzer](messaging-integration/api-gateway-integration-latency-analyzer/) | Separates gateway overhead from backend integration latency | Incident RCA |
| [step-functions-workflow-optimizer](messaging-integration/step-functions-workflow-optimizer/) | Optimizes state machines for cost and performance | Generic |
| [cross-region-replication-lag-monitor](messaging-integration/cross-region-replication-lag-monitor/) | Monitors S3, DynamoDB, and Aurora replication lag for DR | Generic |
| [eventbridge-dlq-and-retry-design](messaging-integration/eventbridge-dlq-and-retry-design/) | Designs EventBridge DLQ and retry for reliable delivery | Generic |
| [step-functions-error-handling-design](messaging-integration/step-functions-error-handling-design/) | Designs Step Functions retry, catch, and error handling | Generic |

---

### 20. Contact Center (Amazon Connect)

Skills for operating and troubleshooting Amazon Connect contact centers.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [connect-contact-flow-troubleshooting](contact-center/connect-contact-flow-troubleshooting/) | Diagnoses contact flows that fail, loop, drop callers, or misroute, including flow-invoked Lambda and Lex failures | Incident RCA |
| [connect-queue-and-routing-health](contact-center/connect-queue-and-routing-health/) | Diagnoses queue backlogs, service-level breaches, abandonment, and routing-profile misconfiguration | Incident RCA |
| [connect-telephony-and-voice-quality-investigation](contact-center/connect-telephony-and-voice-quality-investigation/) | Diagnoses call setup failures, concurrency-quota throttling, packet loss, and phone number problems | Incident RCA |
| [connect-capacity-and-concurrency-planning](contact-center/connect-capacity-and-concurrency-planning/) | Forecasts and right-sizes Connect capacity against Service Quotas with targeted increase recommendations | Generic |
| [connect-security-and-compliance-audit](contact-center/connect-security-and-compliance-audit/) | Audits instance access, recording and CTR encryption, storage configs, and security-profile least privilege | Evaluation |
| [connect-integration-and-lambda-reliability](contact-center/connect-integration-and-lambda-reliability/) | Diagnoses reliability of Lambda data dips, Lex, Customer Profiles, Contact Lens, and Kinesis CTR streaming | Incident RCA |

---

### 21. IoT

Skills for operating AWS IoT Core, Greengrass, and FleetWise device fleets.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [iot-core-connectivity-and-throttling](iot/iot-core-connectivity-and-throttling/) | Diagnoses MQTT connect failures, auth rejections, broker throttling, and reconnect storms | Incident RCA |
| [iot-rules-engine-action-failures](iot/iot-rules-engine-action-failures/) | Diagnoses Rules Engine action failures and throttling to Lambda, SQS, DynamoDB, Kinesis, and Republish | Incident RCA |
| [iot-device-certificate-expiry-fleet](iot/iot-device-certificate-expiry-fleet/) | Grades fleet X.509 certificate lifecycle: expiry buckets, revoked/inactive certs still attached, CA expiry | Evaluation |
| [greengrass-deployment-and-core-health](iot/greengrass-deployment-and-core-health/) | Diagnoses Greengrass v2 unhealthy cores, failed deployments, and broken components | Incident RCA |
| [iot-fleetwise-ingestion-health](iot/iot-fleetwise-ingestion-health/) | Diagnoses FleetWise campaign, vehicle reporting, and decode/manifest ingestion issues | Generic |

---

### 22. Messaging Deliverability

Skills for email, messaging, and real-time communications deliverability.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [ses-deliverability-and-reputation](messaging-deliverability/ses-deliverability-and-reputation/) | Diagnoses SES bounce/complaint spikes, reputation risk, and DKIM/SPF/DMARC alignment | Incident RCA |
| [ses-sending-quota-and-throttle](messaging-deliverability/ses-sending-quota-and-throttle/) | Tracks SES sending quota utilization and throttling with targeted increase sizing | Generic |
| [pinpoint-campaign-delivery-health](messaging-deliverability/pinpoint-campaign-delivery-health/) | Diagnoses Pinpoint per-channel delivery failures, opt-out surges, and throttling | Incident RCA |
| [chime-sdk-media-session-quality](messaging-deliverability/chime-sdk-media-session-quality/) | Diagnoses Chime SDK join failures and in-call media quality (packet loss, jitter) | Incident RCA |

---

### 23. Media

Skills for AWS Elemental live and file-based media pipelines.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [medialive-channel-and-input-health](media/medialive-channel-and-input-health/) | Diagnoses MediaLive input loss, channel alerts, and pipeline failover | Incident RCA |
| [mediaconvert-job-failure-and-backlog](media/mediaconvert-job-failure-and-backlog/) | Diagnoses MediaConvert transcode job failures and queue backlog | Incident RCA |
| [mediapackage-origin-and-packaging-health](media/mediapackage-origin-and-packaging-health/) | Diagnoses MediaPackage origin errors, egress latency, and ingest health | Incident RCA |
| [mediatailor-ad-insertion-health](media/mediatailor-ad-insertion-health/) | Diagnoses MediaTailor ad decision server errors, timeouts, and ad fill rate | Generic |

---

### 24. Purpose-Built Databases

Skills for AWS purpose-built database engines beyond RDS, Aurora, DynamoDB, and ElastiCache.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [documentdb-cluster-health](purpose-built-databases/documentdb-cluster-health/) | Diagnoses DocumentDB CPU, connections, replica lag, cache hit ratio, and storage | Incident RCA |
| [neptune-graph-performance-and-failover](purpose-built-databases/neptune-graph-performance-and-failover/) | Diagnoses Neptune query latency, request queue backlog, errors, and failover | Incident RCA |
| [timestream-ingestion-and-query-health](purpose-built-databases/timestream-ingestion-and-query-health/) | Diagnoses Timestream ingestion throttling, write errors, and query cost/latency | Incident RCA |
| [memorydb-redis-cluster-health](purpose-built-databases/memorydb-redis-cluster-health/) | Diagnoses MemoryDB node/shard health, memory pressure, evictions, and failover | Incident RCA |
| [keyspaces-capacity-and-throttling](purpose-built-databases/keyspaces-capacity-and-throttling/) | Diagnoses Keyspaces throttling, capacity mode fit, and hot partitions | Generic |

---

### 25. Agent-Space Memory

Skills for leveraging AWS DevOps Agent memory - the managed stores (topology, dependencies, monitors, directives, reflections) and custom stores - to enrich findings, detect drift, recall recurring causes, and keep memory accurate and within limits.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [dependency-graph-blast-radius-enrichment](agent-space-memory/dependency-graph-blast-radius-enrichment/) | Enriches a finding with upstream/downstream blast radius from the dependency and topology stores | Generic |
| [topology-drift-detection](agent-space-memory/topology-drift-detection/) | Detects drift between the discovered topology and expected architecture (directives, tags, naming) | Generic |
| [monitor-root-cause-recall](agent-space-memory/monitor-root-cause-recall/) | Summarizes per-monitor recurring root-cause history into repeat-offender and fix-at-the-source lists | Generic |
| [report-context-store-curation](agent-space-memory/report-context-store-curation/) | Curates a custom report-context store so a recurring report stays consistent; recommends memory edits | Generic |
| [known-noise-and-quirks-curation](agent-space-memory/known-noise-and-quirks-curation/) | Recommends recording confirmed noisy alarms and environmental quirks into a custom store | Generic |
| [directives-store-hygiene](agent-space-memory/directives-store-hygiene/) | Audits the directives store for stale, contradictory, falsified, vague, or unsafe standing instructions | Generic |
| [memory-store-hygiene-and-limits](agent-space-memory/memory-store-hygiene-and-limits/) | Audits memory against the 50/200/100KB limits and retrieval-quality best practices | Generic |

---

### 26. Integrations Ecosystem

Skills for getting more from AWS DevOps Agent integrations - multi-tool telemetry (Datadog, Dynatrace, Splunk, Grafana, New Relic, CloudWatch), code and pipeline connectors (GitHub, GitLab, Azure DevOps), comms and ticketing (PagerDuty, Slack, ServiceNow), hybrid AWS + Azure estates, and extension points (webhooks, custom MCP servers, remote A2A agents). Read-only, reasoning over data the platform surfaces from connected sources.

| Skill | Description | Agent Type |
|-------|-------------|-----------|
| [cross-telemetry-signal-reconciliation](integrations-ecosystem/cross-telemetry-signal-reconciliation/) | Reconciles a service's signals across CloudWatch and connected third-party telemetry; classifies disagreements and gaps | Generic |
| [observability-tool-overlap-and-cost](integrations-ecosystem/observability-tool-overlap-and-cost/) | Finds services double-instrumented across paid telemetry tools and licence/ingest waste | Generic |
| [telemetry-coverage-and-webhook-health](integrations-ecosystem/telemetry-coverage-and-webhook-health/) | Audits telemetry coverage of critical paths and the health of investigation-trigger webhooks | Generic |
| [deployment-to-incident-correlation](integrations-ecosystem/deployment-to-incident-correlation/) | Correlates GitHub/GitLab/Azure DevOps deploys with health and incident timelines | Generic |
| [multi-pipeline-dora-consolidation](integrations-ecosystem/multi-pipeline-dora-consolidation/) | Computes DORA four keys unified across GitHub + GitLab + Azure DevOps | Generic |
| [release-freeze-and-change-collision-detection](integrations-ecosystem/release-freeze-and-change-collision-detection/) | Flags deploys against freeze windows and ServiceNow change tickets | Generic |
| [incident-notification-routing-audit](integrations-ecosystem/incident-notification-routing-audit/) | Audits severity-to-PagerDuty/Slack/ServiceNow routing and severities that route nowhere | Generic |
| [ticket-hygiene-and-mttr-reconciliation](integrations-ecosystem/ticket-hygiene-and-mttr-reconciliation/) | Reconciles ServiceNow records against the resource timeline for missing/stale tickets and MTTR gaps | Generic |
| [alert-to-page-noise-analysis](integrations-ecosystem/alert-to-page-noise-analysis/) | Measures alert-to-page conversion per routing target | Generic |
| [hybrid-estate-inventory-and-drift](integrations-ecosystem/hybrid-estate-inventory-and-drift/) | Unified AWS + Azure inventory and tag/ownership drift | Generic |
| [cross-cloud-dependency-and-egress-cost](integrations-ecosystem/cross-cloud-dependency-and-egress-cost/) | Maps AWS<->Azure dependencies and cross-cloud egress cost/latency | Generic |
| [a2a-and-mcp-integration-health](integrations-ecosystem/a2a-and-mcp-integration-health/) | Audits remote A2A agents, custom MCP servers, and webhooks for health, staleness, scope, and security | Generic |
| [webhook-trigger-coverage](integrations-ecosystem/webhook-trigger-coverage/) | Ensures incident-triggering webhooks are present, authenticated, and invoking investigations | Generic |

---

## How to Use

### Option 1: Create in the UI

1. Navigate to **Knowledge -> Skills -> Add skill -> Create skill** in the DevOps Agent web app.
2. Enter the skill **name** and **description** from the SKILL.md frontmatter.
3. Paste the SKILL.md content (below the frontmatter) into the **Instructions** field.
4. Select the appropriate **Agent Type** (see tables above).
5. Click **Create**.

### Option 2: Upload as ZIP

1. Zip each skill directory (containing the SKILL.md file).
2. Navigate to **Knowledge -> Skills -> Add skill -> Upload skill**.
3. Upload the ZIP file and select the appropriate agent type.

### Option 3: Import from GitHub

1. Push this repository to GitHub.
2. Navigate to **Knowledge -> Skills -> Add skill -> Import from repository**.
3. Paste the GitHub directory URL (e.g., `https://github.com/your-org/devops-agent-skills/tree/main/skills/incident-management/blast-radius-assessment`).
4. Select the agent type and click **Import**.

The agent will automatically sync from the repository whenever you push updates.

---

## Agent Type Targeting

Skills can be targeted to specific agent types to reduce context consumption:

| Agent Type | When It Runs |
|-----------|-------------|
| **Generic** | Available to all agent types (default) |
| **On-demand** | Conversational queries in Chat |
| **Incident Triage** | Initial incident assessment and severity classification |
| **Incident RCA** | Root cause analysis during investigations |
| **Incident Mitigation** | Active incident response and remediation |
| **Evaluation** | Proactive recommendations and prevention |

The "Agent Type" column in each category table above shows the recommended targeting for each skill. Use Generic if unsure.

---

## Assigning Skills to Custom Agents

Skills complement the [custom agents](../agents/) in this repository. Recommended skill assignments:

| Custom Agent | Recommended Skills |
|-------------|-------------------|
| daily-infra-health-report | dashboard-gap-analyzer, az-failure-readiness-assessment |
| cost-anomaly-detector | rightsizing-recommendation-engine, idle-resource-hunter, data-transfer-cost-analyzer |
| security-group-auditor | guardduty-finding-investigation, network-anomaly-investigation |
| certificate-expiration-checker | encryption-compliance-validator |
| deployment-rollback-analyzer | rollback-decision-framework, canary-deployment-analysis |
| alarm-fatigue-reducer | sli-measurement-validator, metric-correlation-investigator |
| iam-least-privilege-auditor | access-review-auditor, aws-config-compliance-assessor |
| resource-tagging-compliance | cost-allocation-gap-finder |
| incident-postmortem-generator | blast-radius-assessment, metric-correlation-investigator, incident-communication-drafter |
| eks-cluster-health-auditor | capacity-planning-forecaster, service-onboarding-checklist |

---

## Customization

Each skill is designed to be customized to your environment:

- **Thresholds**: Adjust severity thresholds, SLO targets, and timeframes to match your standards.
- **Naming conventions**: Update tag names, team names, and resource naming patterns.
- **Tool references**: Add specific tool names from your Agent Space MCP toolbox.
- **Procedures**: Modify runbook steps to match your actual operational procedures.
- **Decision trees**: Adjust escalation rules and approval requirements.

---

## Directory Structure

```
skills/
+-- README.md <- You are here
+-- incident-management/
| +-- incident-triage-classifier/SKILL.md
| +-- blast-radius-assessment/SKILL.md
| +-- escalation-path-navigator/SKILL.md
| +-- incident-communication-drafter/SKILL.md
| +-- runbook-executor-guide/SKILL.md
+-- release-management/
| +-- release-changelog-generator/SKILL.md
| +-- rollback-decision-framework/SKILL.md
| +-- canary-deployment-analysis/SKILL.md
| +-- pre-deployment-readiness-check/SKILL.md
| +-- deployment-freeze-enforcer/SKILL.md
+-- security-operations/
| +-- security-incident-containment/SKILL.md
| +-- vulnerability-prioritization/SKILL.md
| +-- exposed-credentials-response/SKILL.md
| +-- guardduty-finding-investigation/SKILL.md
| +-- network-anomaly-investigation/SKILL.md
| +-- certificate-expiry-remediation/SKILL.md
| +-- waf-blocked-traffic-analysis/SKILL.md
| +-- cloudtrail-coverage-gap-analysis/SKILL.md
| +-- lambda-execution-role-hardening/SKILL.md
| +-- sqs-access-and-encryption-hardening/SKILL.md
| +-- tls-policy-modernization/SKILL.md
| +-- waf-rate-based-rule-tuning/SKILL.md
+-- cost-management/
| +-- rightsizing-recommendation-engine/SKILL.md
| +-- data-transfer-cost-analyzer/SKILL.md
| +-- idle-resource-hunter/SKILL.md
| +-- savings-plan-advisor/SKILL.md
| +-- cost-allocation-gap-finder/SKILL.md
| +-- cost-anomaly-root-cause-analysis/SKILL.md
| +-- service-quota-forecasting/SKILL.md
| +-- observability-cost-optimization/SKILL.md
| +-- lambda-concurrency-cost-tuning/SKILL.md
| +-- s3-storage-tiering-optimization/SKILL.md
| +-- ebs-snapshot-cleanup-strategy/SKILL.md
| +-- load-balancer-cost-rationalization/SKILL.md
| +-- cloudtrail-lake-cost-control/SKILL.md
+-- resiliency-reliability/
| +-- az-failure-readiness-assessment/SKILL.md
| +-- dependency-health-analyzer/SKILL.md
| +-- error-budget-tracker/SKILL.md
| +-- disaster-recovery-validation/SKILL.md
| +-- chaos-experiment-planner/SKILL.md
+-- observability-monitoring/
| +-- trace-analysis-investigator/SKILL.md
| +-- sli-measurement-validator/SKILL.md
| +-- log-pattern-anomaly-detector/SKILL.md
| +-- metric-correlation-investigator/SKILL.md
| +-- dashboard-gap-analyzer/SKILL.md
| +-- cloudwatch-cost-reduction/SKILL.md
| +-- xray-sampling-strategy-design/SKILL.md
| +-- distributed-tracing-gap-analysis/SKILL.md
| +-- alarm-noise-reduction-strategy/SKILL.md
| +-- config-conformance-drift-remediation/SKILL.md
| +-- guardduty-trend-analysis/SKILL.md
+-- platform-engineering/
| +-- capacity-planning-forecaster/SKILL.md
| +-- infrastructure-drift-detector/SKILL.md
| +-- container-image-lifecycle-manager/SKILL.md
| +-- service-onboarding-checklist/SKILL.md
| +-- vpc-network-topology-auditor/SKILL.md
| +-- eks-version-upgrade-planning/SKILL.md
| +-- ami-and-os-lifecycle-management/SKILL.md
| +-- rds-parameter-baseline-management/SKILL.md
+-- compliance-governance/
| +-- aws-config-compliance-assessor/SKILL.md
| +-- change-management-audit-trail/SKILL.md
| +-- access-review-auditor/SKILL.md
| +-- data-residency-validator/SKILL.md
| +-- encryption-compliance-validator/SKILL.md
| +-- scp-guardrail-design/SKILL.md
| +-- control-tower-remediation/SKILL.md
| +-- multi-account-baseline-hardening/SKILL.md
| +-- tag-policy-enforcement-strategy/SKILL.md
| +-- tag-governance-and-cost-attribution/SKILL.md
+-- migration-modernization/
| +-- lift-and-shift-assessment/SKILL.md
| +-- containerization-readiness/SKILL.md
| +-- database-migration-planner/SKILL.md
| +-- serverless-migration-evaluator/SKILL.md
| +-- legacy-dependency-mapper/SKILL.md
+-- performance-engineering/
| +-- load-test-results-analyzer/SKILL.md
| +-- database-query-optimizer/SKILL.md
| +-- lambda-cold-start-investigator/SKILL.md
| +-- caching-strategy-advisor/SKILL.md
| +-- throttling-rate-limit-investigator/SKILL.md
| +-- cloudfront-cache-optimization/SKILL.md
| +-- apigateway-throttling-tuning/SKILL.md
| +-- dynamodb-hot-partition-remediation/SKILL.md
+-- networking-dns/
| +-- dns-resolution-troubleshooter/SKILL.md
| +-- cross-account-connectivity-debugger/SKILL.md
| +-- load-balancer-health-investigator/SKILL.md
| +-- latency-path-analyzer/SKILL.md
| +-- tls-handshake-failure-debugger/SKILL.md
| +-- direct-connect-failover-troubleshooting/SKILL.md
| +-- transit-gateway-routing-debugging/SKILL.md
| +-- privatelink-connectivity-troubleshooting/SKILL.md
| +-- network-firewall-false-positive-tuning/SKILL.md
| +-- dns-failover-and-latency-routing-design/SKILL.md
| +-- vpc-route-and-peering-troubleshooting/SKILL.md
| +-- nacl-and-sg-conflict-resolution/SKILL.md
+-- backup-data-protection/
| +-- backup-coverage-auditor/SKILL.md
| +-- retention-policy-optimizer/SKILL.md
| +-- restore-testing-validator/SKILL.md
| +-- data-lifecycle-manager/SKILL.md
| +-- rpo-rto-gap-calculator/SKILL.md
| +-- backup-restore-test-planning/SKILL.md
| +-- dynamodb-pitr-and-backup-audit/SKILL.md
| +-- rds-snapshot-security-review/SKILL.md
+-- automation-toil-reduction/
    +-- toil-identification-analyzer/SKILL.md
| +-- automation-opportunity-scorer/SKILL.md
| +-- runbook-to-automation-converter/SKILL.md
| +-- self-healing-pattern-designer/SKILL.md
| +-- operational-metrics-dashboard-builder/SKILL.md
+-- well-architected/
| +-- operational-excellence-reviewer/SKILL.md
| +-- security-reviewer/SKILL.md
| +-- reliability-reviewer/SKILL.md
| +-- performance-efficiency-reviewer/SKILL.md
| +-- cost-optimization-reviewer/SKILL.md
| +-- trusted-advisor-remediation-prioritization/SKILL.md
+-- container-operations/
| +-- ecs-task-failure-diagnosis/SKILL.md
| +-- event-driven-troubleshooting/SKILL.md
| +-- api-gateway-troubleshooting/SKILL.md
| +-- spot-interruption-handling/SKILL.md
| +-- container-image-security-scanning/SKILL.md
| +-- ecs-deployment-stability-troubleshooting/SKILL.md
| +-- ecr-image-scan-remediation/SKILL.md
| +-- eks-rbac-least-privilege-review/SKILL.md
+-- data-analytics/
| +-- glue-job-failure-diagnosis/SKILL.md
| +-- kinesis-data-pipeline-lag-investigation/SKILL.md
| +-- athena-query-performance-optimizer/SKILL.md
| +-- redshift-query-tuning-advisor/SKILL.md
| +-- emr-cluster-cost-performance-optimizer/SKILL.md
| +-- opensearch-index-lifecycle-optimization/SKILL.md
| +-- redshift-wlm-tuning/SKILL.md
+-- ml-ai-operations/
| +-- sagemaker-endpoint-health-investigation/SKILL.md
| +-- sagemaker-training-job-cost-optimizer/SKILL.md
| +-- bedrock-usage-cost-monitor/SKILL.md
| +-- ml-model-drift-monitor/SKILL.md
| +-- feature-store-freshness-auditor/SKILL.md
+-- developer-experience/
| +-- build-pipeline-bottleneck-analyzer/SKILL.md
| +-- developer-environment-drift-detector/SKILL.md
| +-- artifact-repository-hygiene-auditor/SKILL.md
| +-- sandbox-account-cleanup-advisor/SKILL.md
| +-- iac-template-quality-checker/SKILL.md
+-- messaging-integration/
    +-- sqs-queue-processing-investigation/SKILL.md
    +-- eventbridge-event-flow-debugger/SKILL.md
    +-- api-gateway-integration-latency-analyzer/SKILL.md
    +-- step-functions-workflow-optimizer/SKILL.md
    +-- cross-region-replication-lag-monitor/SKILL.md
    +-- eventbridge-dlq-and-retry-design/SKILL.md
    +-- step-functions-error-handling-design/SKILL.md
+-- agent-space-memory/
    +-- dependency-graph-blast-radius-enrichment/SKILL.md
    +-- topology-drift-detection/SKILL.md
    +-- monitor-root-cause-recall/SKILL.md
    +-- report-context-store-curation/SKILL.md
    +-- known-noise-and-quirks-curation/SKILL.md
    +-- directives-store-hygiene/SKILL.md
    +-- memory-store-hygiene-and-limits/SKILL.md
+-- integrations-ecosystem/
    +-- cross-telemetry-signal-reconciliation/SKILL.md
    +-- observability-tool-overlap-and-cost/SKILL.md
    +-- telemetry-coverage-and-webhook-health/SKILL.md
    +-- deployment-to-incident-correlation/SKILL.md
    +-- multi-pipeline-dora-consolidation/SKILL.md
    +-- release-freeze-and-change-collision-detection/SKILL.md
    +-- incident-notification-routing-audit/SKILL.md
    +-- ticket-hygiene-and-mttr-reconciliation/SKILL.md
    +-- alert-to-page-noise-analysis/SKILL.md
    +-- hybrid-estate-inventory-and-drift/SKILL.md
    +-- cross-cloud-dependency-and-egress-cost/SKILL.md
    +-- a2a-and-mcp-integration-health/SKILL.md
    +-- webhook-trigger-coverage/SKILL.md
```

---

## Contributing

1. Fork the repository.
2. Create a new skill directory under the appropriate category.
3. Write a SKILL.md with proper frontmatter (name, description).
4. Follow the existing structure: When to Activate -> Steps -> Output.
5. Update this README with the new skill entry.
6. Submit a pull request.

---

## References

- [DevOps Agent Skills Documentation](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-devops-agent-skills.html)
- [Creating Custom Agents](https://docs.aws.amazon.com/devopsagent/latest/userguide/custom-agents-creating-a-custom-agent.html)
- [Agent Skills Specification (Open Standard)](https://github.com/awslabs/agent-skills-spec)
- [Community Skills Gallery](https://github.com/awslabs/devops-agent-tools)
