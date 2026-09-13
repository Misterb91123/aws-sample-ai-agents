# Observability findings to directed actions

This file maps the read-only observability findings that the agents and skills in
this repository produce to the specific AWS DevOps Agent directed action that
remediates each one. Every directed action is a mutating operation run through
use_aws, and each is executed only after per-action operator approval in chat
under the scoped elevated IAM role. Directed actions are never GREEN; each is
either YELLOW (recoverable) or RED (hard to reverse), and any operation that
attaches an IAM role or deletes a resource is refused and stays manual.

## Critical resource missing a CloudWatch alarm

| Field | Value |
| --- | --- |
| Read-only finding | A critical resource (for example an RDS instance, ALB target group, or SQS queue) has no CloudWatch alarm on a key health metric. |
| Source | 95-cloudwatch-alarm-configuration-auditor, 73-service-health-dashboard-generator, skill dashboard-gap-analyzer |
| Directed action | cloudwatch:PutMetricAlarm (create a new alarm) |
| Parameters | AlarmName, Namespace, MetricName, Dimensions, Statistic, Period (for example 300), EvaluationPeriods, DatapointsToAlarm, Threshold, ComparisonOperator, AlarmActions (existing SNS topic ARN) |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use, argument pins on operation cloudwatch:PutMetricAlarm and the target AlarmName |
| Rollback | cloudwatch:DeleteAlarms is delete-class and stays manual; the operator removes the created alarm by hand if it must be reverted. |
| Notes | Creating an alarm adds monitoring and does not disable any control, so it passes the prohibited-action check. Reuse an existing SNS topic; do not create new IAM plumbing. |

## Alarm misconfigured (missing action, no datapoints-to-alarm, wrong threshold)

| Field | Value |
| --- | --- |
| Read-only finding | An existing alarm has no AlarmActions, is missing DatapointsToAlarm, or uses an incorrect threshold or period, so it never fires or fires incorrectly. |
| Source | 95-cloudwatch-alarm-configuration-auditor, 06-cloudwatch-alarm-fatigue-reducer, skill alarm-noise-reduction-strategy |
| Directed action | cloudwatch:PutMetricAlarm (overwrite the alarm with corrected config) |
| Parameters | AlarmName (existing), corrected Threshold, Period, EvaluationPeriods, DatapointsToAlarm, ComparisonOperator, AlarmActions |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use, argument pins on operation cloudwatch:PutMetricAlarm and the existing AlarmName |
| Rollback | Re-run cloudwatch:PutMetricAlarm with the prior configuration captured before the change. |
| Notes | PutMetricAlarm overwrites in place; capture the current alarm definition first so the prior config is available for rollback. This is a correction, not a delete, so it is allowed. |

## Noisy/flapping alarm needing an anomaly-detection band

| Field | Value |
| --- | --- |
| Read-only finding | A static-threshold alarm flaps on a metric with variable baseline and should use an anomaly-detection band instead. |
| Source | 259-cloudwatch-anomaly-detector-coverage-monitor, 06-cloudwatch-alarm-fatigue-reducer |
| Directed action | cloudwatch:PutAnomalyDetector then cloudwatch:PutMetricAlarm (using ThresholdMetricId) |
| Parameters | PutAnomalyDetector: Namespace, MetricName, Dimensions, Stat. PutMetricAlarm: AlarmName, Metrics array including the anomaly-detection expression, ThresholdMetricId, ComparisonOperator (for example LessThanLowerOrGreaterThanUpperThreshold), EvaluationPeriods |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use per operation; two approvals, one for PutAnomalyDetector and one for PutMetricAlarm, each pinned to its resource |
| Rollback | Re-run cloudwatch:PutMetricAlarm to restore the static-threshold config; cloudwatch:DeleteAnomalyDetector is delete-class and stays manual. |
| Notes | Neither call attaches a role or deletes a resource, so both are allowed. Sequence matters: create the detector before the alarm that references its ThresholdMetricId. |

## High-value metric lacks an anomaly detector

| Field | Value |
| --- | --- |
| Read-only finding | A high-value metric has no anomaly detector, leaving no learned baseline for anomaly-based alarming. |
| Source | 259-cloudwatch-anomaly-detector-coverage-monitor |
| Directed action | cloudwatch:PutAnomalyDetector |
| Parameters | Namespace, MetricName, Dimensions, Stat (for example Average) |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use, argument pins on operation cloudwatch:PutAnomalyDetector and the metric identity |
| Rollback | cloudwatch:DeleteAnomalyDetector is delete-class and stays manual; the operator removes the detector by hand if needed. |
| Notes | Adds a detector only; no alarm is created by this action alone. Passes the prohibited-action check because nothing is disabled. |

## Log group with no retention (Never expire)

| Field | Value |
| --- | --- |
| Read-only finding | A CloudWatch log group has retention set to Never expire, accumulating cost indefinitely. |
| Source | 27-log-retention-cost-optimizer, 141-cloudwatch-metrics-cost-optimizer |
| Directed action | logs:PutRetentionPolicy (set a specific retention in days) |
| Parameters | logGroupName, retentionInDays (a specific allowed value, for example 90) |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use, argument pins on operation logs:PutRetentionPolicy and the logGroupName |
| Rollback | Re-run logs:PutRetentionPolicy with the prior retention, or logs:DeleteRetentionPolicy to return to Never expire. |
| Notes | This is retention tuning, not disabling logging. Setting a finite period is allowed; disabling log delivery entirely would be a prohibited action. |

## Missing logging where it is needed (for example VPC flow logs off)

| Field | Value |
| --- | --- |
| Read-only finding | Logging that should be on is missing, for example a VPC or subnet has no flow logs, or an application log group has no retention configured. |
| Source | 160-vpc-flow-log-coverage-auditor, 71-cloudwatch-log-insights-query-library |
| Directed action | ec2:CreateFlowLogs (enable flow logs to an existing log group) or logs:PutRetentionPolicy (set retention on the target group) |
| Parameters | CreateFlowLogs: ResourceIds, ResourceType (for example VPC), TrafficType, LogDestinationType (cloud-watch-logs), LogGroupName (existing). PutRetentionPolicy: logGroupName, retentionInDays |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use, argument pins on the enabling operation and the target resource |
| Rollback | ec2:DeleteFlowLogs is delete-class and stays manual; retention changes revert via logs:PutRetentionPolicy with the prior value. |
| Notes | The enabling direction is allowed. Disabling logging would be a prohibited action and is never proposed. If CreateFlowLogs needs a delivery role passed to the service, that specific variant is refused-passrole; deliver to an existing CloudWatch Logs group that does not require PassRole. |

## Missing CloudWatch metric stream for centralized metrics

| Field | Value |
| --- | --- |
| Read-only finding | No CloudWatch metric stream exists to forward metrics to a centralized destination, so centralized metric ingestion is incomplete. |
| Source | 260-metric-streams-and-emf-ingestion-health-monitor |
| Directed action | cloudwatch:PutMetricStream (would require a Firehose delivery role) |
| Parameters | Name, FirehoseArn, RoleArn (Firehose delivery role), OutputFormat, IncludeFilters |
| Guardrail status | refused-passrole |
| Safety | YELLOW (if it could run) |
| Approval scope | Not applicable; the agent refuses before approval because the operation passes an IAM role to a service. |
| Rollback | Not applicable; no action is executed. |
| Notes | Creating a metric stream requires passing a Firehose role (iam:PassRole), which the agent refuses by default. Remediation stays manual: a human creates the stream with their own credentials. |

## Missing Synthetics canary for an endpoint

| Field | Value |
| --- | --- |
| Read-only finding | A critical endpoint has no CloudWatch Synthetics canary, so there is no active uptime probe. |
| Source | 168-cloudwatch-synthetics-canary-health-monitor |
| Directed action | synthetics:CreateCanary (would require an execution role) |
| Parameters | Name, Code (handler and S3 location), ExecutionRoleArn, Schedule, RuntimeVersion, ArtifactS3Location |
| Guardrail status | refused-passrole |
| Safety | YELLOW (if it could run) |
| Approval scope | Not applicable; the agent refuses before approval because the operation passes an execution role to the service. |
| Rollback | Not applicable; no action is executed. |
| Notes | CreateCanary requires an execution role (iam:PassRole), which the agent refuses. Remediation stays manual: a human creates the canary with their own credentials. |

## Stale or broken dashboard, or a dashboard that should be deleted

| Field | Value |
| --- | --- |
| Read-only finding | A dashboard has broken or stale widgets and needs repair, or a dashboard is obsolete and should be deleted. |
| Source | 261-cloudwatch-dashboard-coverage-auditor, 73-service-health-dashboard-generator |
| Directed action | Repair: cloudwatch:PutDashboard (update widget JSON). Delete: cloudwatch:DeleteDashboards. |
| Parameters | PutDashboard: DashboardName (existing), DashboardBody (corrected widget JSON). DeleteDashboards: DashboardNames |
| Guardrail status | PutDashboard: allowed. DeleteDashboards: refused-delete-class. |
| Safety | YELLOW (for the allowed PutDashboard repair) |
| Approval scope | Repair: single-use, argument pins on operation cloudwatch:PutDashboard and the DashboardName. Delete: not applicable; refused before approval. |
| Rollback | Repair: re-run cloudwatch:PutDashboard with the DashboardBody captured before the change. Delete: not applicable; no action is executed. |
| Notes | Updating or repairing a dashboard is allowed because it overwrites config in place. Deleting a dashboard is delete-class and refused; a human performs the deletion manually. |

## Refused and manual remediations

Two guardrail boundaries keep specific observability fixes out of the automated
write path, so they remain manual steps performed by a human with their own
credentials.

- PassRole boundary. Creating a CloudWatch metric stream
  (cloudwatch:PutMetricStream) needs a Firehose delivery role, and creating a
  Synthetics canary (synthetics:CreateCanary) needs an execution role. Both pass
  an IAM role to a service (iam:PassRole), which the agent refuses by default.
  These are refused-passrole and stay manual.
- Delete-class boundary. Deleting an alarm (cloudwatch:DeleteAlarms), an anomaly
  detector (cloudwatch:DeleteAnomalyDetector), a flow log (ec2:DeleteFlowLogs), or
  a dashboard (cloudwatch:DeleteDashboards) removes a resource. Delete-class
  operations are always refused, so removals are performed manually.

Everything else here is allowed: enabling missing logging, creating and
correcting alarms, adding anomaly detectors, tuning log retention to a finite
period, and repairing dashboards. The rule of thumb is that creating, enabling,
and updating observability config is generally allowed, but anything that
attaches a role or deletes a resource is not. Note the retention distinction as
well: setting a specific log retention period for cost is allowed, while
disabling logging entirely is a prohibited action and is never proposed.
