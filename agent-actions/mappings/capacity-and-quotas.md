# Capacity and quota finding to directed action mappings

This file maps the read-only capacity and quota findings that the agents and
skills in this repository produce to the specific AWS DevOps Agent directed
action that remediates each one. Every directed action listed here is a mutating
operation run through use_aws, gated by per-action operator approval in chat and
executed under a scoped elevated IAM role. Directed actions are never GREEN; each
is classified YELLOW (recoverable) or RED (hard to reverse), and refused cases
stay manual.

## API Gateway stage near rate/burst limits or missing method throttling overrides

| Field | Value |
| --- | --- |
| Read-only finding | An API Gateway stage is approaching its throttling rate/burst limits, or lacks method-level throttling overrides, so bursts risk 429s or unthrottled backend load. |
| Source | 211-apigateway-throttling-and-quota-monitor. |
| Directed action | apigateway:UpdateStage (set throttlingRateLimit/throttlingBurstLimit and method-level overrides). An account-level throttle raise goes through service-quotas:RequestServiceQuotaIncrease. |
| Parameters | restApiId=<id>, stageName=<stage>, patchOperations=[{op=replace, path=/throttle/rateLimit, value=<rate>}, {op=replace, path=/throttle/burstLimit, value=<burst>}, per-method /{resource}/{method}/throttling/* overrides]. |
| Guardrail status | allowed - modifies an existing stage's throttling settings; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; throttle changes affect request admission and can shift load to the backend or return more 429s if set too low. |
| Approval scope | One UpdateStage call on the named stage with the named rate/burst and method overrides. Operator can narrow the numbers, never widen. |
| Rollback | UpdateStage again with the prior throttlingRateLimit/throttlingBurstLimit and method-override values. |
| Notes | An account-level throttle ceiling is not a stage setting; raising it is service-quotas:RequestServiceQuotaIncrease and goes through AWS review (see the service quota finding below). |

## API Gateway usage plan without throttle/quota, or quota too low

| Field | Value |
| --- | --- |
| Read-only finding | An API Gateway usage plan has no throttle or quota, or a quota too low for legitimate consumers, so it fails to shape client traffic. |
| Source | 167-apigateway-usage-plan-and-key-auditor. |
| Directed action | apigateway:UpdateUsagePlan (set throttle rate/burst and quota limit); attaching a key uses apigateway:CreateUsagePlanKey. |
| Parameters | usagePlanId=<id>, patchOperations=[{op=replace, path=/throttle/rateLimit, value=<rate>}, {op=replace, path=/throttle/burstLimit, value=<burst>}, {op=replace, path=/quota/limit, value=<n>}, {op=replace, path=/quota/period, value=<DAY|WEEK|MONTH>}]; CreateUsagePlanKey uses usagePlanId=<id>, keyId=<id>, keyType=API_KEY. |
| Guardrail status | allowed - modifies an existing usage plan and attaches an existing key; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; tightening throttle/quota can reject legitimate clients if set too low, so calibrate to observed usage. |
| Approval scope | One UpdateUsagePlan call (and, if needed, one CreateUsagePlanKey) on the named plan with the named throttle/quota. Operator can narrow values. |
| Rollback | UpdateUsagePlan again to restore prior throttle/quota; DeleteUsagePlanKey to detach a key that was just attached. |
| Notes | Deleting unused API keys is a delete-class operation the agent refuses; that cleanup stays manual (see below). |

## WAF managed rule group on an outdated version / not tracking default

| Field | Value |
| --- | --- |
| Read-only finding | A WAF web ACL references a managed rule group pinned to an outdated version, or is not tracking the default/auto version, so it misses current rule updates. |
| Source | 172-waf-managed-rule-version-drift-monitor. |
| Directed action | wafv2:UpdateWebACL (set the current managed-rule version, or enable the default/auto version). |
| Parameters | Name=<acl>, Scope=<REGIONAL|CLOUDFRONT>, Id=<id>, LockToken=<token>, Rules=[... ManagedRuleGroupStatement with Version=<current> or version omitted to track default ...]. |
| Guardrail status | allowed - modifies an existing web ACL's rule configuration; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; a new managed-rule version can change match behavior, so review for false positives after the change. |
| Approval scope | One UpdateWebACL call on the named web ACL setting the named managed-rule version or default tracking. Operator can adjust the target version. |
| Rollback | UpdateWebACL again to restore the prior managed-rule version. |
| Notes | UpdateWebACL requires the current LockToken; fetch it immediately before the call to avoid a stale-token failure. |

## WAF rate-based rule mis-tuned or a public resource with no rate rule

| Field | Value |
| --- | --- |
| Read-only finding | A WAF rate-based rule is mis-tuned (limit too high to be effective, or too low and blocking legitimate traffic), or a public resource has no rate-based rule at all. |
| Source | 222-waf-rate-based-rule-effectiveness-monitor. |
| Directed action | wafv2:UpdateWebACL (add or tune a rate-based statement to the calibrated limit; never remove existing protection). |
| Parameters | Name=<acl>, Scope=<REGIONAL|CLOUDFRONT>, Id=<id>, LockToken=<token>, Rules=[... RateBasedStatement with Limit=<calibrated>, AggregateKeyType=<IP|FORWARDED_IP> ...]. |
| Guardrail status | allowed - modifies an existing web ACL to add or tune a rate-based statement; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; a rate limit set too low can block legitimate clients and too high is ineffective, so calibrate to observed peak. |
| Approval scope | One UpdateWebACL call on the named web ACL adding/tuning the rate-based rule to the named limit. Operator can adjust the limit; removal of protection is out of scope. |
| Rollback | UpdateWebACL again to restore the prior rate-based limit or rule set. |
| Notes | The directed action only adds or tunes protection; removing a rate-based rule is not proposed, since it would weaken a security control. |

## Kinesis shard saturation / wrong capacity mode

| Field | Value |
| --- | --- |
| Read-only finding | A Kinesis data stream is saturating its shards (write/read throughput throttling), or is in a capacity mode that does not fit its traffic pattern. |
| Source | 103-kinesis-stream-scaling-advisor. |
| Directed action | kinesis:UpdateShardCount (reshard to a new shard count) or kinesis:UpdateStreamMode (switch ON_DEMAND / PROVISIONED). |
| Parameters | StreamName=<stream>, TargetShardCount=<n>, ScalingType=UNIFORM_SCALING; or StreamName=<stream>, StreamModeDetails={StreamMode=<ON_DEMAND|PROVISIONED>}. |
| Guardrail status | allowed - modifies an existing stream's capacity or mode; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; resharding and mode changes affect cost and throughput. |
| Approval scope | One UpdateShardCount (or UpdateStreamMode) call on the named stream with the named target. Operator can narrow the shard count. |
| Rollback | UpdateShardCount to the prior count, or UpdateStreamMode back to the prior mode. |
| Notes | Resharding runs through a brief transition period and changes the per-shard cost; mode switches are rate-limited, so plan the change rather than toggling repeatedly. |

## Redshift high queue wait / concurrency scaling off

| Field | Value |
| --- | --- |
| Read-only finding | A Redshift cluster shows high WLM queue wait time, or has concurrency scaling disabled, so queries queue during peak load. |
| Source | 218-redshift-wlm-and-queue-monitor. |
| Directed action | redshift:ModifyClusterParameterGroup (wlm_json_configuration, max_concurrency_scaling_clusters) and/or redshift:ModifyCluster (resize). |
| Parameters | ParameterGroupName=<pg>, Parameters=[{ParameterName=wlm_json_configuration, ParameterValue=<json>}, {ParameterName=max_concurrency_scaling_clusters, ParameterValue=<n>}]; ModifyCluster uses ClusterIdentifier=<cluster>, NodeType=<type>, NumberOfNodes=<n>. |
| Guardrail status | allowed - modifies an existing parameter group and/or cluster; no deletion, no iam:PassRole. |
| Safety | YELLOW - a WLM/concurrency-scaling parameter change is recoverable and applies on the next reboot. RED for a resize, which is disruptive and can interrupt query availability during the operation. |
| Approval scope | One ModifyClusterParameterGroup call and/or one ModifyCluster call on the named cluster with the named settings. Operator can narrow the values and choose the maintenance timing. |
| Rollback | ModifyClusterParameterGroup again to restore the prior WLM/concurrency settings; ModifyCluster back to the prior node type/count for a resize (another disruptive operation). |
| Notes | A parameter-group change requires a cluster reboot to take effect, and a resize can be disruptive; schedule the reboot/resize in a maintenance window. |

## OpenSearch low free storage / oversized replicas

| Field | Value |
| --- | --- |
| Read-only finding | An OpenSearch domain is low on free storage, or carries more replica shards or larger instances than the workload needs. |
| Source | 217-opensearch-index-and-storage-optimizer. |
| Directed action | es:UpdateDomainConfig (grow EBSOptions volume size, adjust replica/instance count). |
| Parameters | DomainName=<domain>, EBSOptions={EBSEnabled=true, VolumeSize=<GiB>}, ClusterConfig={InstanceType=<type>, InstanceCount=<n>}. |
| Guardrail status | allowed - modifies an existing domain's storage and cluster configuration; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; growing storage or changing instance count triggers a blue/green deployment and changes cost. |
| Approval scope | One UpdateDomainConfig call on the named domain with the named storage/cluster settings. Operator can narrow the sizes. |
| Rollback | UpdateDomainConfig again to restore the prior EBS size or cluster configuration (subject to the constraint that volume size cannot be shrunk below usage). |
| Notes | Tuning replica counts at the index level via an ISM (index state management) index-lifecycle policy is a data-plane call against the OpenSearch cluster, not a control-plane AWS API, so that part stays manual (see below). |

## Service quota near exhaustion / projected exhaustion

| Field | Value |
| --- | --- |
| Read-only finding | An adjustable service quota is near exhaustion, or is projected to be exhausted, so requests will start failing when the limit is hit. |
| Source | 17-service-quota-watchdog, 139-quota-utilization-forecaster (forecasting source). |
| Directed action | service-quotas:RequestServiceQuotaIncrease (adjustable quotas only). |
| Parameters | ServiceCode=<service>, QuotaCode=<quota>, DesiredValue=<observed-peak-plus-buffer> (sized to observed peak plus a buffer, never the maximum). |
| Guardrail status | allowed - requests an increase on an adjustable quota; no resource deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable and additive; the request goes through AWS review and is not instant, and a higher ceiling can raise the potential spend. |
| Approval scope | One RequestServiceQuotaIncrease call for the named ServiceCode/QuotaCode with the named DesiredValue. Operator can lower the requested value, never raise it to the maximum. |
| Rollback | No direct rollback; a quota increase is a ceiling raise, not a resource change. Usage below the new ceiling is unaffected, and a later decrease can be requested if needed. |
| Notes | This is the general home for RequestServiceQuotaIncrease used across other mapping files. Only adjustable quotas qualify; a non-adjustable quota needs an architecture change and stays manual (see below). |

## Lambda function on an EOL runtime

| Field | Value |
| --- | --- |
| Read-only finding | A Lambda function runs on a runtime that is end-of-life or nearing deprecation (flagged by the Trusted Advisor deprecated-runtime check or the Lambda deprecated-runtime data), so it loses security patches and eventually the ability to update or invoke. |
| Source | 165-lambda-runtime-deprecation-tracker; 265-lambda-deprecated-runtime-migration-planner; 306-lambda-deprecated-runtime-transform-remediation-planner. |
| Directed action | lambda:UpdateFunctionConfiguration (Runtime=<supported>), applied only after the code has been upgraded to the target language version. |
| Parameters | FunctionName=<fn>, Runtime=<supported-runtime-identifier>. |
| Guardrail status | allowed-but-disruptive - modifies an existing function's runtime; no deletion, no iam:PassRole, but a runtime change can break code that depends on the old runtime. |
| Safety | YELLOW - recoverable by setting the prior runtime, but the new runtime may be code-incompatible; upgrade and verify the code first, and test in a non-production stage or alias before promoting. |
| Approval scope | One UpdateFunctionConfiguration call on the named function setting the named supported runtime, after the approved and verified code change. Operator chooses the target runtime and the timing. |
| Rollback | UpdateFunctionConfiguration again to set the prior runtime (Zip functions), or redeploy the prior image tag (Image functions); pair with reverting to the previous published function version. |
| Notes | Changing the runtime identifier does not run or migrate the code. When the language version needs code changes, the code upgrade is done first through AWS Transform (an AWS-managed language-version-upgrade transformation that analyzes code, updates syntax, and adjusts dependencies), reviewed and merged by a human, and verified, and only then is this runtime bump applied - never ahead of the code. Container-image functions upgrade by rebuilding to a supported base image and publishing a new tag; custom runtimes (provided.*) are a manual base-image path, not an AWS-managed transformation. Agent 306 produces this end-to-end Transform plan with the human-approval gates and the rollback. |

## EKS cluster/nodegroup past or near standard support

| Field | Value |
| --- | --- |
| Read-only finding | An EKS cluster or managed nodegroup is past or near the end of standard support for its Kubernetes version, risking forced upgrades and loss of support. |
| Source | 204-eks-cluster-version-eol-tracker. |
| Directed action | eks:UpdateClusterVersion then eks:UpdateNodegroupVersion (one minor version at a time). |
| Parameters | name=<cluster>, version=<next-minor>; then clusterName=<cluster>, nodegroupName=<ng>, version=<next-minor> (matching the cluster). |
| Guardrail status | allowed-but-disruptive - modifies existing cluster/nodegroup versions; no deletion, no iam:PassRole, but the control-plane upgrade is irreversible. |
| Safety | RED - a cluster version upgrade cannot be downgraded; verify addon and nodegroup compatibility first and run it in a maintenance window with escalation. |
| Approval scope | One UpdateClusterVersion call then one UpdateNodegroupVersion call on the named cluster/nodegroup, advancing a single minor version. Operator controls timing and the maintenance window. |
| Rollback | None for the control-plane upgrade - it is forward-only and cannot be downgraded; recovery from a failed upgrade is via a new cluster/restore, performed manually. |
| Notes | RED-leaning and forward-only: upgrade one minor version at a time, confirm addon/nodegroup compatibility before the control-plane bump, and require escalation plus a maintenance window (see below). |

## Refused and manual remediations

Some capacity and quota fixes cannot be executed as directed actions and stay
MANUAL, performed by a human with their own credentials:

- Deleting unused API keys. Removing an API Gateway API key is a delete-class
  operation the agent refuses (refused-delete-class); the directed path only
  updates usage plans and attaches keys. A human performs the deletion.
- Non-adjustable service quotas. RequestServiceQuotaIncrease applies only to
  adjustable quotas. A non-adjustable quota cannot be raised and needs an
  architecture change (sharding, a second account, a different service), which
  stays manual.
- OpenSearch ISM index-lifecycle policies. Tuning replica counts or lifecycle
  transitions through an ISM policy is a data-plane call against the OpenSearch
  cluster, not a control-plane AWS API run through use_aws, so it stays manual.

The EKS version upgrade is not refused, but it is the most disruptive directed
action here and must be treated with care: the control-plane upgrade is
forward-only and cannot be rolled back (you cannot downgrade a cluster version),
so it is classified RED, advanced one minor version at a time, and requires
escalation and a maintenance window with addon/nodegroup compatibility verified
in advance. When a capacity change only modifies an existing resource or requests
an adjustable quota, it is allowed under per-action approval; when it deletes a
resource, targets a non-adjustable quota, or reaches into the data plane, it
stays manual.
