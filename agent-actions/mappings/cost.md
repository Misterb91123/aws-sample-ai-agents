# Cost and FinOps findings to directed actions

This file maps the read-only COST and FinOps findings the agents and skills in
this repository produce to the specific AWS DevOps Agent directed action that
remediates each one, with guardrail status, safety, approval scope, and rollback.
The most important teaching point is that the classic cost fix is often a
deletion (delete an idle NAT gateway, release an Elastic IP, delete an orphaned
snapshot or volume, delete an idle load balancer), and deletion is a delete-class
operation the agent refuses regardless of approval. For those findings the
available directed action is limited to the non-destructive precursor (tag for
review, stop, downsize, tier, retention), while the deletion itself stays a
manual step a human performs with their own credentials.

## Idle or orphaned resource (idle NAT gateway, unattached EIP, idle ELB, orphaned EBS snapshot or volume)

| Field | Value |
| --- | --- |
| Read-only finding | A resource is idle or orphaned and is billing with no workload value: NAT gateway with no traffic, unattached Elastic IP, idle load balancer, or an EBS snapshot/volume with no owning resource. |
| Source | 32-orphaned-resource-cleaner, 45-elastic-ip-waste-detector, 208-ebs-snapshot-cost-and-orphan-auditor, 209-elb-idle-and-cost-optimizer, 24-storage-cost-optimizer, skill idle-resource-hunter |
| Directed action | ec2:CreateTags to mark the resource for review (or ec2:StopInstances where a stoppable compute resource is the waste source). The deletion or release (ec2:DeleteNatGateway, ec2:ReleaseAddress, ec2:DeleteSnapshot, ec2:DeleteVolume, elasticloadbalancing:DeleteLoadBalancer) is NOT performed by the agent. |
| Parameters | Tag: cost-review=candidate (plus an owner or ticket tag). Stop: instance-id of the idle instance only. |
| Guardrail status | allowed for the ec2:CreateTags tagging (and ec2:StopInstances stop); refused-delete-class for the delete or release. |
| Safety | YELLOW |
| Approval scope | One resource id per approval: the specific NAT gateway, EIP allocation, load balancer, snapshot, or volume being tagged, or the single instance being stopped. Approval cannot be reused for another resource. |
| Rollback | Remove the tag with ec2:DeleteTags; start a stopped instance with ec2:StartInstances. Tagging and stopping are fully recoverable. |
| Notes | Tagging does not reduce spend by itself; it routes the resource to a human for the actual delete or release. The deletion stays manual because it is delete-class. Do not treat the tag as remediation complete. |

## Over-provisioned EBS or instance (right-sizing)

| Field | Value |
| --- | --- |
| Read-only finding | A volume or instance is over-provisioned for its observed usage: excess IOPS/throughput, an expensive volume type where gp3 would serve, or an instance type larger than utilization requires. |
| Source | 52-ebs-performance-bottleneck-detector, skill rightsizing-recommendation-engine, 163-ecs-fargate-rightsizing-advisor |
| Directed action | ec2:ModifyVolume to reduce IOPS/throughput or change the volume type (for example to gp3). Instance resize (ec2:ModifyInstanceAttribute for instance type) requires a stop/start cycle. |
| Parameters | Volume: volume-id, target VolumeType=gp3, target Iops, target Throughput. Instance: instance-id, target InstanceType. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | One volume id (or one instance id) per approval, with the exact target attributes named in the approval. |
| Rollback | Re-run ec2:ModifyVolume with the previous type/IOPS/throughput; ec2:ModifyInstanceAttribute back to the prior instance type. Volume modifications are recoverable but ModifyVolume has a cooldown before the next change. |
| Notes | Instance resize is not a live operation: the instance must be stopped, modified, then started, which is a service interruption. Confirm the workload tolerates the stop and that any instance-store data is expendable before approving. Downsizing a volume's provisioned performance is safe; shrinking a volume's size is not offered here. |

## S3 cold data not tiered

| Field | Value |
| --- | --- |
| Read-only finding | Objects that are infrequently accessed remain in S3 Standard, or incomplete multipart uploads accumulate, with no lifecycle policy transitioning or expiring them. |
| Source | 24-storage-cost-optimizer, 145-s3-lifecycle-and-tiering-optimizer, skill s3-storage-tiering-optimization |
| Directed action | s3:PutLifecycleConfiguration to add transitions to Standard-IA or Glacier and to expire incomplete multipart uploads. |
| Parameters | Bucket name, lifecycle rules: transition days and target storage class, AbortIncompleteMultipartUpload DaysAfterInitiation. No Expiration action that deletes current object versions. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | One bucket per approval, with the rule set named in the approval. |
| Rollback | Re-apply the prior lifecycle configuration with s3:PutLifecycleConfiguration, or remove it with s3:DeleteBucketLifecycle. Transitions to a colder class are reversible by restoring/copying, though retrieval from Glacier has cost and latency. |
| Notes | Keep lifecycle scoped to transitions and incomplete-upload cleanup. Avoid expiration rules that delete live data through this path; object deletion is a human decision. This does not disable Block Public Access or any bucket control. |

## CloudWatch Logs retention set to Never expire or too long

| Field | Value |
| --- | --- |
| Read-only finding | A log group has retention set to Never expire (or a retention far longer than the data is useful), accumulating storage cost indefinitely. |
| Source | 27-log-retention-cost-optimizer, 141-cloudwatch-metrics-cost-optimizer, skill observability-cost-optimization |
| Directed action | logs:PutRetentionPolicy to set a specific retention in days. |
| Parameters | logGroupName, retentionInDays (a supported value, for example 30, 90, 365). |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | One log group per approval, with the target retention days named in the approval. |
| Rollback | Re-run logs:PutRetentionPolicy with the prior value, or logs:DeleteRetentionPolicy to return to Never expire. Note: logs already past the new retention window age out and cannot be recovered, so the reduction is only partly reversible. |
| Notes | This changes retention, it does not stop log delivery. It is not disabling logging: log ingestion and delivery continue. Choose a retention that satisfies audit and compliance needs before approving, because expired log data is gone. |

## Lambda over-provisioned provisioned concurrency

| Field | Value |
| --- | --- |
| Read-only finding | A Lambda function has provisioned concurrency configured above its observed need, paying for warm capacity that goes unused. |
| Source | 150-lambda-provisioned-concurrency-cost-optimizer, 86-lambda-concurrency-forecast, skill lambda-concurrency-cost-tuning |
| Directed action | lambda:PutProvisionedConcurrencyConfig to lower the provisioned count, or lambda:DeleteProvisionedConcurrencyConfig to remove the provisioned-concurrency setting. |
| Parameters | FunctionName, Qualifier (alias or version), ProvisionedConcurrentExecutions (new lower value) for the put. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | One function qualifier (alias/version) per approval, with the target concurrency value named in the approval. |
| Rollback | Re-run lambda:PutProvisionedConcurrencyConfig with the prior count to restore warm capacity. |
| Notes | Nuance: lambda:DeleteProvisionedConcurrencyConfig removes a configuration setting on the function, it does not delete the function or any resource. It is therefore treated as allowed (a modify), not refused-delete-class. Lowering or removing provisioned concurrency can increase cold-start latency; confirm the latency budget before approving. |

## DynamoDB over-provisioned capacity

| Field | Value |
| --- | --- |
| Read-only finding | A DynamoDB table (or index) is provisioned with more RCU/WCU than utilization requires, or would be cheaper on on-demand for its access pattern. |
| Source | 51-dynamodb-capacity-throttle-monitor, 166-dynamodb-autoscaling-effectiveness-monitor |
| Directed action | dynamodb:UpdateTable to lower provisioned RCU/WCU or switch the billing mode to on-demand (PAY_PER_REQUEST). |
| Parameters | TableName, ProvisionedThroughput ReadCapacityUnits/WriteCapacityUnits, or BillingMode=PAY_PER_REQUEST. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | One table per approval, with the target capacity or billing mode named in the approval. |
| Rollback | Re-run dynamodb:UpdateTable with the prior capacity or billing mode. Note billing-mode switches are limited in frequency (once per 24 hours), so the reversal may be time-constrained. |
| Notes | Lowering capacity too far risks throttling under load; base the target on peak observed consumption, not the average. UpdateTable modifies settings only and is not a delete-class operation. |

## Missing cost allocation tags

| Field | Value |
| --- | --- |
| Read-only finding | Resources lack the required cost allocation tags (for example owner, cost-center, environment), so spend cannot be attributed. |
| Source | 08-resource-tagging-compliance, 138-tag-policy-compliance-auditor, 225-tag-coverage-and-cost-attribution-auditor, skill tag-governance-and-cost-attribution |
| Directed action | Apply the required tags with the per-service tagging call: ec2:CreateTags, rds:AddTagsToResource, s3:PutBucketTagging, lambda:TagResource. |
| Parameters | Resource identifier (per service) and the required tag key/value pairs (for example cost-center=<value>, owner=<value>, environment=<value>). |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | One resource per approval, with the tag keys and values named in the approval. |
| Rollback | Remove or correct tags with the per-service untag call (ec2:DeleteTags, rds:RemoveTagsFromResource, s3:PutBucketTagging with the prior set, lambda:UntagResource). |
| Notes | s3:PutBucketTagging replaces the full tag set on the bucket, so include existing tags in the payload to avoid dropping them. Tagging is additive and low-risk. Cost allocation tags must also be activated in Billing before they appear in cost reports; that activation is a separate account-level step. |

## Detailed monitoring enabled unnecessarily

| Field | Value |
| --- | --- |
| Read-only finding | An EC2 instance has detailed (1-minute) CloudWatch monitoring enabled where 5-minute basic monitoring would suffice, adding avoidable per-instance metric cost. |
| Source | 141-cloudwatch-metrics-cost-optimizer |
| Directed action | ec2:UnmonitorInstances to disable detailed monitoring (return to basic 5-minute metrics). |
| Parameters | instance-id (or list of instance ids). |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | One instance id (or an explicit list) per approval. |
| Rollback | Re-enable with ec2:MonitorInstances to restore 1-minute detailed monitoring. |
| Notes | Important distinction: this disables 1-minute metric monitoring granularity, it does NOT disable security or audit logging. It is not a refused-prohibited-action "disable logging" change. Basic 5-minute EC2 metrics continue and CloudTrail, VPC Flow Logs, and application logs are unaffected. |

## Refused and manual remediations

The deletes and releases that would produce the largest direct savings stay
MANUAL because the agent refuses delete-class operations regardless of approval:

- Delete an idle NAT gateway (ec2:DeleteNatGateway) - refused-delete-class.
- Release an unattached Elastic IP (ec2:ReleaseAddress) - refused-delete-class.
- Delete an orphaned EBS snapshot (ec2:DeleteSnapshot) - refused-delete-class.
- Delete an orphaned EBS volume (ec2:DeleteVolume) - refused-delete-class.
- Delete an idle load balancer (elasticloadbalancing:DeleteLoadBalancer) - refused-delete-class.

For each of these the directed action available to the agent is only the
non-destructive precursor: tag the resource for review (ec2:CreateTags), stop a
stoppable instance (ec2:StopInstances), tier storage (s3:PutLifecycleConfiguration),
shorten retention (logs:PutRetentionPolicy), or downsize provisioned capacity
(ec2:ModifyVolume, dynamodb:UpdateTable, lambda:PutProvisionedConcurrencyConfig).
The agent prepares and narrows the change; it does not delete. A human still
performs the actual delete or release with their own credentials, so the cost is
only fully recovered by that manual, human-attributed step.
