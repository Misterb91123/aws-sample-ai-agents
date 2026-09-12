# Custom Agents

This directory contains 227 custom agents for AWS DevOps Agent. Agents 01 through 226 are read-only monitors and auditors. Agent 227 is a read-only orchestrator that turns their recommendations into a human-approval-ready change plan. Each agent executes autonomously on a schedule or on demand, invoking MCP tools to analyze infrastructure and produce artifacts and recommendations.

## Agent execution model

```
Schedule trigger
  -> Load system prompt, assigned tools, and skills
  -> Reason through the task
  -> Invoke MCP tools (use_aws, query_cloudwatch_metrics, etc.)
  -> Produce artifacts (tables, charts, topology diagrams)
  -> Create recommendations (actionable findings)
  -> Record invocation trajectory
```

## File structure per agent

```
XX-agent-name/
  system-prompt.md # Agent instructions (Goal, Approach, Exception Handling,
                        # Data Validation, Constraints, Output)
  agent-config.json # Name, description, tools, trigger schedule
```

## Setup instructions

1. Open the DevOps Agent web app.
2. Navigate to **Agents > Custom Agents > Create agent**.
3. Choose **Chat** (recommended) or **Form**.
4. Enter the `name` value from `agent-config.json`.
5. Paste the contents of `system-prompt.md` into the system prompt field.
6. Assign the tools listed in `agent-config.json` via Chat.
7. Configure the trigger using the `expression` from `agent-config.json`.

## Schedule expression reference

| Expression | Meaning |
|-----------|---------|
| `cron(0 7 * * ? *)` | Every day at 7:00 AM UTC |
| `cron(0 6 ? * MON *)` | Every Monday at 6:00 AM UTC |
| `cron(0 5 ? * WED *)` | Every Wednesday at 5:00 AM UTC |
| `cron(0 4 1 * ? *)` | Monthly on the 1st at 4:00 AM UTC |
| `rate(4 hours)` | Every 4 hours |
| `rate(6 hours)` | Every 6 hours |

## Complete agent list

| # | Name | Schedule | Tools |
|---|------|----------|-------|
| 01 | daily-infra-health-report | Daily 7 AM | use_aws, query_cloudwatch_metrics, list_cloudwatch_alarms, list_investigations |
| 02 | cost-anomaly-detector | Daily 8 AM | use_aws, list_investigations |
| 03 | security-group-auditor | Weekly Mon | use_aws |
| 04 | certificate-expiration-checker | Daily 9 AM | use_aws |
| 05 | deployment-rollback-analyzer | Every 4h | use_aws, query_cloudwatch_metrics, query_cloudwatch_logs |
| 06 | alarm-fatigue-reducer | Weekly Mon | use_aws, list_cloudwatch_alarms, query_cloudwatch_metrics |
| 07 | iam-least-privilege-auditor | Weekly Wed | use_aws |
| 08 | resource-tagging-compliance | Weekly Mon | use_aws |
| 09 | incident-postmortem-generator | Weekly Mon | use_aws, list_investigations, query_cloudwatch_metrics, query_cloudwatch_logs |
| 10 | eks-cluster-health-auditor | Daily 7 AM | use_aws, use_kubectl, query_cloudwatch_metrics |
| 11 | unused-permissions-revoker | Weekly Mon | use_aws |
| 12 | cross-region-dr-sync-validator | Daily 6 AM | use_aws, query_cloudwatch_metrics |
| 13 | pipeline-failure-analyzer | Weekly Mon | use_aws, query_cloudwatch_logs |
| 14 | secrets-rotation-compliance | Daily 7 AM | use_aws |
| 15 | s3-bucket-security-scanner | Weekly Wed | use_aws |
| 16 | database-performance-weekly-report | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 17 | service-quota-watchdog | Daily 7 AM | use_aws |
| 18 | patch-compliance-reporter | Weekly Mon | use_aws |
| 19 | network-flow-anomaly-detector | Every 6h | use_aws, query_cloudwatch_logs |
| 20 | toil-automation-progress-tracker | Weekly Mon | use_aws, list_investigations, list_cloudwatch_alarms, query_cloudwatch_metrics |
| 21 | waf-rule-effectiveness-analyzer | Weekly Mon | use_aws, query_cloudwatch_metrics, query_cloudwatch_logs |
| 22 | cloudtrail-anomaly-hunter | Every 6h | use_aws, query_cloudwatch_logs |
| 23 | ecs-task-failure-investigator | Every 4h | use_aws, query_cloudwatch_logs |
| 24 | storage-cost-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 25 | api-gateway-health-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 26 | multi-account-governance-scorer | Weekly Mon | use_aws |
| 27 | log-retention-cost-optimizer | Weekly Mon | use_aws |
| 28 | auto-scaling-efficiency-auditor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 29 | event-driven-architecture-health | Every 4h | use_aws, query_cloudwatch_metrics |
| 30 | sla-breach-predictor | Every 6h | use_aws, query_cloudwatch_metrics, list_investigations |
| 31 | config-rule-drift-remediator | Daily 8 AM | use_aws |
| 32 | orphaned-resource-cleaner | Weekly Mon | use_aws |
| 33 | cross-service-dependency-mapper | Weekly Sun | use_aws, query_cloudwatch_metrics |
| 34 | deployment-velocity-reporter | Weekly Mon | use_aws, list_investigations |
| 35 | compliance-evidence-collector | Monthly 1st | use_aws |
| 36 | well-architected-review-automator | Monthly 1st | use_aws, query_cloudwatch_metrics |
| 37 | spot-instance-interruption-analyzer | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 38 | container-vulnerability-digest | Daily 7 AM | use_aws |
| 39 | oncall-burnout-monitor | Weekly Mon | use_aws, list_investigations, list_cloudwatch_alarms, query_cloudwatch_metrics |
| 40 | weekly-executive-summary | Weekly Mon | use_aws, query_cloudwatch_metrics, list_investigations, list_cloudwatch_alarms |
| 41 | lambda-error-pattern-analyzer | Daily 7 AM | use_aws, query_cloudwatch_metrics, query_cloudwatch_logs |
| 42 | rds-connection-pool-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 43 | cloudfront-cache-efficiency-auditor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 44 | transit-gateway-cost-routing-auditor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 45 | elastic-ip-waste-detector | Weekly Mon | use_aws |
| 46 | sns-delivery-failure-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 47 | step-functions-execution-auditor | Every 6h | use_aws, query_cloudwatch_metrics |
| 48 | ec2-metadata-security-checker | Weekly Wed | use_aws |
| 49 | cross-account-role-trust-auditor | Weekly Mon | use_aws |
| 50 | vpc-endpoint-usage-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 51 | dynamodb-capacity-throttle-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 52 | ebs-performance-bottleneck-detector | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 53 | cloudformation-stack-health-checker | Daily 8 AM | use_aws |
| 54 | route53-health-check-validator | Every 6h | use_aws, query_cloudwatch_metrics |
| 55 | kms-key-usage-rotation-auditor | Weekly Mon | use_aws |
| 56 | ecr-repository-governance | Weekly Mon | use_aws |
| 57 | ssm-patch-baseline-drift-detector | Weekly Mon | use_aws |
| 58 | aws-backup-job-failure-investigator | Daily 7 AM | use_aws |
| 59 | cloudwatch-contributor-insights-reporter | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 60 | elasticache-cluster-health-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 61 | savings-plan-utilization-tracker | Weekly Mon | use_aws |
| 62 | multi-region-latency-comparator | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 63 | guardduty-finding-trend-reporter | Weekly Mon | use_aws |
| 64 | load-balancer-ssl-policy-auditor | Weekly Wed | use_aws |
| 65 | auto-scaling-launch-failure-investigator | Every 4h | use_aws, query_cloudwatch_metrics |
| 66 | ecs-capacity-provider-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 67 | kinesis-shard-utilization-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 68 | codebuild-cost-duration-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 69 | vpc-cidr-capacity-planner | Weekly Mon | use_aws |
| 70 | iam-policy-simulator-validator | Weekly Wed | use_aws |
| 71 | cloudwatch-log-insights-query-library | Daily 8 AM | use_aws, query_cloudwatch_logs |
| 72 | terraform-state-drift-reporter | Weekly Mon | use_aws, query_cloudwatch_logs |
| 73 | service-health-dashboard-generator | Daily 7 AM | use_aws, query_cloudwatch_metrics, list_investigations, list_cloudwatch_alarms |
| 74 | resource-lifecycle-compliance-checker | Weekly Mon | use_aws |
| 75 | cross-region-data-transfer-auditor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 76 | container-runtime-security-monitor | Every 6h | use_aws, query_cloudwatch_logs |
| 77 | incident-frequency-trend-analyzer | Weekly Mon | use_aws, list_investigations |
| 78 | api-throttling-pattern-reporter | Daily 8 AM | use_aws, query_cloudwatch_logs |
| 79 | infrastructure-age-eol-tracker | Weekly Mon | use_aws |
| 80 | monthly-cost-allocation-report | Monthly 1st | use_aws |
| 81 | graviton-migration-opportunity-finder | Weekly Mon | use_aws |
| 82 | public-exposure-surface-scanner | Daily 5 AM | use_aws |
| 83 | reserved-instance-coverage-optimizer | Weekly Mon | use_aws |
| 84 | nacl-rule-auditor | Weekly Wed | use_aws |
| 85 | dns-record-hygiene-auditor | Weekly Mon | use_aws |
| 86 | lambda-concurrency-forecast | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 87 | ecs-service-discovery-health | Every 4h | use_aws, query_cloudwatch_metrics |
| 88 | secrets-manager-cost-optimizer | Weekly Mon | use_aws |
| 89 | efs-throughput-utilization-auditor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 90 | sqs-dlq-accumulation-alert | Every 4h | use_aws, query_cloudwatch_metrics |
| 91 | aurora-cluster-optimization-advisor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 92 | elb-access-log-security-analyzer | Every 6h | use_aws, query_cloudwatch_logs |
| 93 | eventbridge-rule-health-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 94 | redshift-cluster-utilization-reporter | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 95 | cloudwatch-alarm-configuration-auditor | Weekly Mon | use_aws, list_cloudwatch_alarms |
| 96 | nat-gateway-high-availability-checker | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 97 | aws-health-event-impact-assessor | Every 4h | use_aws |
| 98 | vpc-security-group-rule-count-monitor | Weekly Wed | use_aws |
| 99 | step-functions-cost-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 100 | weekly-reliability-scorecard | Weekly Mon | use_aws, query_cloudwatch_metrics, list_investigations, list_cloudwatch_alarms |
| 101 | devops-agent-usage-credit-monitor | Daily 12 PM | use_aws |
| 102 | glue-etl-cost-reliability-reporter | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 103 | kinesis-stream-scaling-advisor | Every 6h | use_aws, query_cloudwatch_metrics |
| 104 | athena-cost-governance-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 105 | redshift-cluster-efficiency-reporter | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 106 | emr-cluster-waste-detector | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 107 | sagemaker-endpoint-cost-rightsizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 108 | bedrock-token-spend-tracker | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 109 | ml-model-drift-scheduled-reporter | Weekly Mon | use_aws |
| 110 | feature-store-freshness-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 111 | build-pipeline-lead-time-reporter | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 112 | environment-parity-drift-reporter | Weekly Mon | use_aws |
| 113 | artifact-repository-hygiene-reporter | Weekly Mon | use_aws |
| 114 | sandbox-cost-cleanup-reporter | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 115 | sqs-consumer-lag-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 116 | eventbridge-delivery-failure-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 117 | api-gateway-latency-decomposition-reporter | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 118 | step-functions-cost-efficiency-reporter | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 119 | dr-replication-readiness-monitor | Daily 6 AM | use_aws, query_cloudwatch_metrics |
| 120 | opensearch-cluster-health-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 121 | msk-kafka-cluster-health-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 122 | fsx-file-system-capacity-monitor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 123 | cognito-user-pool-security-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 124 | elastic-beanstalk-environment-health-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 125 | appsync-graphql-api-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 126 | secrets-rotation-lambda-failure-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 127 | direct-connect-link-health-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 128 | vpn-tunnel-stability-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 129 | global-accelerator-endpoint-health-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 130 | network-firewall-rule-effectiveness-monitor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 131 | privatelink-endpoint-connection-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 132 | cloudwan-core-network-monitor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 133 | route53-resolver-endpoint-monitor | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 134 | scp-effectiveness-auditor | Weekly Mon | use_aws |
| 135 | control-tower-drift-detector | Weekly Mon | use_aws |
| 136 | organizations-account-baseline-auditor | Weekly Mon | use_aws |
| 137 | cost-anomaly-root-cause-investigator | Daily 9 AM | use_aws |
| 138 | tag-policy-compliance-auditor | Weekly Mon | use_aws |
| 139 | quota-utilization-forecaster | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 140 | config-conformance-pack-reporter | Weekly Mon | use_aws |
| 141 | cloudwatch-metrics-cost-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 142 | xray-trace-sampling-optimizer | Weekly Mon | use_aws |
| 143 | carbon-footprint-efficiency-reporter | Monthly 1st | use_aws, query_cloudwatch_metrics |
| 144 | backup-restore-test-validator | Weekly Mon | use_aws |
| 145 | s3-lifecycle-and-tiering-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 146 | dynamodb-backup-and-pitr-auditor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 147 | waf-blocked-traffic-trend-reporter | Daily 8 AM | use_aws, query_cloudwatch_metrics |
| 148 | acm-certificate-expiry-and-renewal-monitor | Daily 7 AM | use_aws |
| 149 | ecs-service-deployment-stability-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 150 | lambda-provisioned-concurrency-cost-optimizer | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 151 | cloudtrail-management-event-coverage-auditor | Weekly Mon | use_aws |
| 152 | secrets-manager-rotation-drift-monitor | Daily 6 AM | use_aws, query_cloudwatch_metrics |
| 153 | rds-proxy-connection-health-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 154 | aurora-serverless-v2-scaling-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 155 | ec2-spot-savings-opportunity-reporter | Weekly Mon | use_aws |
| 156 | cloudfront-security-header-auditor | Weekly Mon | use_aws |
| 157 | s3-access-point-and-policy-auditor | Weekly Mon | use_aws |
| 158 | iam-access-key-age-and-usage-auditor | Weekly Mon | use_aws |
| 159 | ssm-session-manager-audit-reporter | Weekly Mon | use_aws |
| 160 | vpc-flow-log-coverage-auditor | Weekly Mon | use_aws |
| 161 | elasticache-serverless-cost-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 162 | sns-topic-encryption-and-policy-auditor | Weekly Mon | use_aws |
| 163 | ecs-fargate-rightsizing-advisor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 164 | eks-node-group-scaling-efficiency-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 165 | lambda-runtime-deprecation-tracker | Weekly Mon | use_aws |
| 166 | dynamodb-autoscaling-effectiveness-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 167 | apigateway-usage-plan-and-key-auditor | Weekly Mon | use_aws |
| 168 | cloudwatch-synthetics-canary-health-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 169 | rum-and-frontend-error-trend-reporter | Every 6h | use_aws, query_cloudwatch_metrics |
| 170 | codepipeline-stage-failure-analyzer | Weekly Mon | use_aws |
| 171 | codedeploy-deployment-health-monitor | Every 6h | use_aws |
| 172 | waf-managed-rule-version-drift-monitor | Weekly Mon | use_aws |
| 173 | guardduty-malware-scan-coverage-auditor | Weekly Mon | use_aws |
| 174 | securityhub-finding-aging-reporter | Weekly Mon | use_aws |
| 175 | inspector-vulnerability-sla-reporter | Weekly Mon | use_aws |
| 176 | backup-vault-lock-and-compliance-auditor | Weekly Mon | use_aws |
| 177 | macie-sensitive-data-exposure-monitor | Every 6h | use_aws |
| 178 | kms-grant-and-policy-drift-auditor | Weekly Mon | use_aws |
| 179 | acm-private-ca-health-monitor | Every 6h | use_aws |
| 180 | route53-dnssec-validation-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 181 | s3-replication-lag-and-failure-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 182 | efs-backup-and-lifecycle-auditor | Weekly Mon | use_aws |
| 183 | fsx-backup-and-dr-auditor | Weekly Mon | use_aws |
| 184 | datasync-task-health-monitor | Every 4h | use_aws |
| 185 | transfer-family-server-health-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 186 | appflow-flow-failure-monitor | Every 6h | use_aws |
| 187 | mq-broker-health-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 188 | msk-connect-connector-health-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 189 | glue-data-catalog-hygiene-auditor | Weekly Mon | use_aws |
| 190 | lakeformation-permission-auditor | Weekly Mon | use_aws |
| 191 | quicksight-spice-capacity-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 192 | sagemaker-notebook-idle-cost-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 193 | batch-job-queue-efficiency-monitor | Every 4h | use_aws |
| 194 | emr-serverless-cost-monitor | Daily 7 AM | use_aws, query_cloudwatch_metrics |
| 195 | cloudmap-namespace-health-monitor | Every 6h | use_aws |
| 196 | apprunner-service-health-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 197 | lightsail-resource-inventory-reporter | Weekly Mon | use_aws |
| 198 | workspaces-utilization-and-cost-monitor | Weekly Mon | use_aws, query_cloudwatch_metrics |
| 199 | organizations-scp-change-monitor | Daily 7 AM | use_aws |
| 200 | iam-identity-center-assignment-auditor | Weekly Mon | use_aws |
| 201 | config-recorder-coverage-auditor | Weekly Mon | use_aws |
| 202 | ecr-image-scan-and-lifecycle-auditor | Weekly Mon | use_aws |
| 203 | eks-pod-security-and-rbac-auditor | Weekly Mon | use_aws, use_kubectl |
| 204 | eks-cluster-version-eol-tracker | Weekly Mon | use_aws |
| 205 | rds-snapshot-sharing-and-encryption-auditor | Weekly Mon | use_aws |
| 206 | rds-parameter-group-drift-auditor | Weekly Mon | use_aws |
| 207 | ec2-ami-hygiene-and-eol-auditor | Weekly Mon | use_aws |
| 208 | ebs-snapshot-cost-and-orphan-auditor | Weekly Mon | use_aws |
| 209 | elb-idle-and-cost-optimizer | Every 6h | use_aws, query_cloudwatch_metrics |
| 210 | cloudfront-cache-hit-ratio-optimizer | Every 6h | use_aws, query_cloudwatch_metrics |
| 211 | apigateway-throttling-and-quota-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 212 | lambda-iam-permission-scope-auditor | Weekly Mon | use_aws |
| 213 | sqs-encryption-and-policy-auditor | Weekly Mon | use_aws |
| 214 | eventbridge-rule-target-failure-monitor | Every 4h | use_aws, query_cloudwatch_metrics |
| 215 | stepfunctions-execution-failure-analyzer | Every 4h | use_aws, query_cloudwatch_metrics |
| 216 | dynamodb-hot-partition-detector | Every 4h | use_aws, query_cloudwatch_metrics |
| 217 | opensearch-index-and-storage-optimizer | Every 6h | use_aws, query_cloudwatch_metrics |
| 218 | redshift-wlm-and-queue-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 219 | vpc-peering-and-tgw-route-auditor | Weekly Mon | use_aws |
| 220 | network-acl-and-sg-conflict-detector | Weekly Mon | use_aws |
| 221 | acm-and-elb-tls-policy-drift-monitor | Every 6h | use_aws |
| 222 | waf-rate-based-rule-effectiveness-monitor | Every 6h | use_aws, query_cloudwatch_metrics |
| 223 | guardduty-finding-severity-trend-reporter | Weekly Mon | use_aws |
| 224 | cloudtrail-lake-query-cost-monitor | Every 6h | use_aws |
| 225 | tag-coverage-and-cost-attribution-auditor | Weekly Mon | use_aws |
| 226 | trusted-advisor-check-aggregator | Weekly Mon | use_aws |
| 227 | remediation-orchestrator | Daily 1 PM | use_aws |
