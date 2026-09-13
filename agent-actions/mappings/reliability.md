# Reliability finding to directed action mappings

This file maps the read-only reliability findings that the agents and skills in
this repository produce to the specific AWS DevOps Agent directed action that
remediates each one. Every directed action listed here is a mutating operation
run through use_aws, gated by per-action operator approval in chat and executed
under a scoped elevated IAM role. Directed actions are never GREEN; each is
classified YELLOW (recoverable) or RED (hard to reverse), and refused cases stay
manual.

## Auto Scaling group max capacity too low / no headroom for peak

| Field | Value |
| --- | --- |
| Read-only finding | An Auto Scaling group has a MaxSize (or DesiredCapacity) that leaves no headroom for peak load, so scaling saturates before demand is met. |
| Source | 28-auto-scaling-efficiency-auditor, 65-auto-scaling-launch-failure-investigator, skill capacity-planning-forecaster. |
| Directed action | autoscaling:UpdateAutoScalingGroup (raise MaxSize and/or DesiredCapacity). |
| Parameters | AutoScalingGroupName=<asg>, MaxSize=<new-max>, DesiredCapacity=<new-desired> (MinSize left unchanged unless justified). |
| Guardrail status | allowed - modifies an existing ASG; changing scaling settings on a resource that already exists does not require iam:PassRole. |
| Safety | YELLOW - capacity change is recoverable; higher capacity increases spend and may launch instances. |
| Approval scope | One UpdateAutoScalingGroup call on the named ASG with the named MaxSize/DesiredCapacity. Operator can narrow the numbers, never widen. |
| Rollback | Call UpdateAutoScalingGroup again to restore the prior MaxSize/DesiredCapacity. |
| Notes | This is the modify-existing case. Creating a NEW ASG or launch template that references an instance profile is a different, refused case (see below). |

## Application Auto Scaling not configured for a scalable target

| Field | Value |
| --- | --- |
| Read-only finding | A scalable target (for example an ECS service or a DynamoDB table/index) has no Application Auto Scaling configured, so it cannot track load. |
| Source | 166-dynamodb-autoscaling-effectiveness-monitor, 164-eks-node-group-scaling-efficiency-monitor. |
| Directed action | application-autoscaling:RegisterScalableTarget then application-autoscaling:PutScalingPolicy. |
| Parameters | ServiceNamespace=<ns>, ResourceId=<id>, ScalableDimension=<dim>, MinCapacity=<min>, MaxCapacity=<max>; PolicyName=<name>, PolicyType=TargetTrackingScaling, TargetTrackingScalingPolicyConfiguration=<target+metric>. |
| Guardrail status | allowed - registers and configures scaling on an existing target; no resource deletion and no iam:PassRole. |
| Safety | YELLOW - adds automated scaling that is recoverable; can increase provisioned capacity and spend under load. |
| Approval scope | Two scoped calls (RegisterScalableTarget, PutScalingPolicy) on the named resource with the named min/max and target. Operator can narrow bounds. |
| Rollback | application-autoscaling:DeleteScalingPolicy and DeregisterScalableTarget to return the target to its prior unmanaged state. |
| Notes | Application Auto Scaling uses a service-linked role, which the service manages; this path does not require the operator to pass a role, so it stays allowed. |

## Lambda hitting concurrency limits

| Field | Value |
| --- | --- |
| Read-only finding | A Lambda function is throttling against concurrency limits (spillover / Throttles metric), risking dropped or delayed invocations. |
| Source | 86-lambda-concurrency-forecast, 41-lambda-error-pattern-analyzer. |
| Directed action | lambda:PutFunctionConcurrency (reserved concurrency) or lambda:PutProvisionedConcurrencyConfig (provisioned concurrency). |
| Parameters | FunctionName=<fn>, ReservedConcurrentExecutions=<n>; or FunctionName=<fn>, Qualifier=<version/alias>, ProvisionedConcurrentExecutions=<n>. |
| Guardrail status | allowed - modifies concurrency settings on an existing function; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; reserved concurrency draws from the account pool and can starve other functions if set too high. |
| Approval scope | One PutFunctionConcurrency (or PutProvisionedConcurrencyConfig) call on the named function with the named value. Operator can narrow the value. |
| Rollback | lambda:DeleteFunctionConcurrency (or DeleteProvisionedConcurrencyConfig) to restore the prior setting. |
| Notes | Setting concurrency differs from creating a function; creating a Lambda with an execution role would require iam:PassRole and is refused (see below). |

## DynamoDB table without Point-in-Time Recovery

| Field | Value |
| --- | --- |
| Read-only finding | A DynamoDB table has Point-in-Time Recovery (PITR) disabled, leaving no continuous backup for recovery. |
| Source | 146-dynamodb-backup-and-pitr-auditor. |
| Directed action | dynamodb:UpdateContinuousBackups (enable PITR). |
| Parameters | TableName=<table>, PointInTimeRecoverySpecification={PointInTimeRecoveryEnabled=true}. |
| Guardrail status | allowed - enables a backup control on an existing table; not a delete, not a disabling of a control, no iam:PassRole. |
| Safety | YELLOW - enabling PITR is recoverable and adds a small ongoing cost; it strengthens rather than weakens protection. |
| Approval scope | One UpdateContinuousBackups call on the named table enabling PITR. |
| Rollback | UpdateContinuousBackups with PointInTimeRecoveryEnabled=false, though disabling a backup control is generally discouraged. |
| Notes | The repository prohibits disabling logging/encryption/backup controls; enabling PITR is the safe direction and is never the prohibited case. The related deletion-protection and TTL fixes from the same agent (146) are mapped in [data-protection-encryption.md](data-protection-encryption.md). |

## DynamoDB throttling from under-provisioned capacity

| Field | Value |
| --- | --- |
| Read-only finding | A DynamoDB table (or index) is throttling reads/writes because provisioned capacity is too low, or on-demand would suit its bursty pattern. |
| Source | 51-dynamodb-capacity-throttle-monitor, 216-dynamodb-hot-partition-detector. |
| Directed action | dynamodb:UpdateTable (raise ProvisionedThroughput, or switch BillingMode to PAY_PER_REQUEST). |
| Parameters | TableName=<table>, ProvisionedThroughput={ReadCapacityUnits=<r>, WriteCapacityUnits=<w>}; or TableName=<table>, BillingMode=PAY_PER_REQUEST. |
| Guardrail status | allowed - modifies an existing table's capacity; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; raising capacity or moving to on-demand changes cost, and billing-mode switches are rate-limited. |
| Approval scope | One UpdateTable call on the named table with the named capacity or billing mode. Operator can narrow the numbers. |
| Rollback | UpdateTable again to restore prior ProvisionedThroughput or BillingMode (subject to the once-per-24h billing-mode switch limit). |
| Notes | A hot-partition finding may call for a schema/key change instead; that is a design change, not a directed action, and stays manual. |

## SQS queue without a dead-letter queue / short retention risking message loss

| Field | Value |
| --- | --- |
| Read-only finding | An SQS queue has no dead-letter queue (no RedrivePolicy) or a MessageRetentionPeriod short enough to risk losing messages during consumer outages. |
| Source | 90-sqs-dlq-accumulation-alert, 115-sqs-consumer-lag-monitor, skill sqs-queue-processing-investigation. |
| Directed action | sqs:SetQueueAttributes (set RedrivePolicy pointing at an existing DLQ, adjust MessageRetentionPeriod). |
| Parameters | QueueUrl=<queue>, Attributes={RedrivePolicy={deadLetterTargetArn=<existing-dlq-arn>, maxReceiveCount=<n>}, MessageRetentionPeriod=<seconds>}. |
| Guardrail status | allowed - modifies attributes on an existing queue; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; retention and redrive changes affect message durability and downstream handling. |
| Approval scope | One SetQueueAttributes call on the named queue with the named RedrivePolicy/retention. Operator can narrow values. |
| Rollback | SetQueueAttributes again to restore the prior RedrivePolicy and MessageRetentionPeriod. |
| Notes | Creating the DLQ itself is sqs:CreateQueue - allowed (a create, not a delete, no PassRole) - but wiring the RedrivePolicy needs the DLQ ARN, so create the DLQ first, then set attributes. |

## RDS/Aurora single-AZ or short backup retention

| Field | Value |
| --- | --- |
| Read-only finding | An RDS instance or Aurora cluster runs single-AZ or with a short BackupRetentionPeriod, below the reliability/DR bar. |
| Source | 16-database-performance-weekly-report, 91-aurora-cluster-optimization-advisor, skill disaster-recovery-validation. |
| Directed action | rds:ModifyDBInstance (MultiAZ=true and/or BackupRetentionPeriod=N). |
| Parameters | DBInstanceIdentifier=<db>, MultiAZ=true, BackupRetentionPeriod=<days>, ApplyImmediately=<true|false>. |
| Guardrail status | allowed - modifies an existing DB instance; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; the Multi-AZ conversion can trigger a brief failover and I/O impact, so schedule it in a maintenance window. |
| Approval scope | One ModifyDBInstance call on the named instance with the named MultiAZ/retention and ApplyImmediately choice. |
| Rollback | ModifyDBInstance again to restore prior MultiAZ/BackupRetentionPeriod (another maintenance-window failover applies when reverting Multi-AZ). |
| Notes | Call out timing: a Multi-AZ change causes a short failover. For Aurora, the equivalent is rds:ModifyDBCluster for BackupRetentionPeriod; per-AZ resilience comes from adding reader instances. |

## New ASG / launch template that must reference an instance profile

| Field | Value |
| --- | --- |
| Read-only finding | Remediation would require creating a new Auto Scaling group or launch template/configuration that attaches an instance profile (IAM role) to launched instances. |
| Source | 28-auto-scaling-efficiency-auditor, 65-auto-scaling-launch-failure-investigator. |
| Directed action | autoscaling:CreateLaunchConfiguration / ec2:CreateLaunchTemplate (with an IamInstanceProfile), or autoscaling:CreateAutoScalingGroup referencing it. |
| Parameters | Would include IamInstanceProfile=<arn/name> on the launch template/configuration - the parameter that triggers the PassRole requirement. |
| Guardrail status | refused-passrole - attaching an instance profile passes an IAM role to a service, which requires iam:PassRole; the agent refuses regardless of approval. |
| Safety | N/A - not executed by the agent. |
| Approval scope | None - cannot be proposed or approved. |
| Rollback | N/A. |
| Notes | Explicit refused example. Contrast with the first finding: modifying an EXISTING ASG's scaling settings needs no PassRole and is allowed; creating/updating a launch config or template that passes an instance profile does need PassRole and stays manual. |

## Missing / mis-set CloudWatch alarm for a reliability signal

| Field | Value |
| --- | --- |
| Read-only finding | A reliability signal has no alarm or a mis-set alarm - for example no alarm on 5xx error rate or on ASG UnHealthyHostCount - so degradation goes unnoticed. |
| Source | 95-cloudwatch-alarm-configuration-auditor, 30-sla-breach-predictor, 100-weekly-reliability-scorecard. |
| Directed action | cloudwatch:PutMetricAlarm (create or correct the alarm). |
| Parameters | AlarmName=<name>, Namespace=<ns>, MetricName=<metric>, Dimensions=<dims>, Statistic/Period/EvaluationPeriods, Threshold=<t>, ComparisonOperator=<op>, AlarmActions=[<existing-sns-topic-arn>]. |
| Guardrail status | allowed - creates/updates an alarm; PutMetricAlarm is idempotent and passes an SNS topic ARN as an action target, which does not require iam:PassRole. |
| Safety | YELLOW - recoverable; a mis-tuned threshold can add noise or miss events, so validate the threshold and period. |
| Approval scope | One PutMetricAlarm call for the named alarm with the named metric, threshold, and existing action target. Operator can adjust threshold/period. |
| Rollback | PutMetricAlarm again to restore the prior definition; the alarm is not deleted by the agent (delete stays manual). |
| Notes | AlarmActions reference an existing SNS topic ARN; the agent does not pass an IAM role here, so this stays allowed rather than refused-passrole. |

## Refused and manual remediations

Some reliability fixes cannot be executed as directed actions and stay MANUAL,
performed by a human with their own credentials:

- iam:PassRole cases. Any remediation that passes an IAM role to a service is
  refused regardless of operator approval. This includes creating or updating a
  launch template or launch configuration that attaches an instance profile,
  creating a new Auto Scaling group that references such a launch template, and
  creating a Lambda function with an execution role. The agent refuses these and
  the change is completed manually.
- Resource deletion. Deleting an instance, table, function, queue, alarm, launch
  template, or similar is a delete-class operation the agent refuses; a human
  performs the deletion.

The PassRole boundary, stated precisely: the trigger is whether the operation
passes an IAM role to a service, not whether the resource is new or existing.
Modifying an EXISTING resource's scaling or capacity settings
(autoscaling:UpdateAutoScalingGroup, dynamodb:UpdateTable,
application-autoscaling:RegisterScalableTarget on an existing target,
lambda:PutFunctionConcurrency) does not pass a role and is allowed. Creating or
updating a resource in a way that attaches a role - an instance profile on a
launch template/configuration, or an execution role on a new Lambda - does pass
a role, needs iam:PassRole, and is refused. When in doubt, check whether the
parameters carry a role ARN (IamInstanceProfile, Role) that is being handed to a
service; if so, it is refused-passrole and stays manual.
