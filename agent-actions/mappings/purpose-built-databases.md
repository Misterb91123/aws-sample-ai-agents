# Purpose-built database finding to directed action mappings

This file maps the read-only purpose-built database findings that the skills in
this repository produce (skills/purpose-built-databases/: documentdb-cluster-health,
neptune-graph-performance-and-failover, timestream-ingestion-and-query-health,
memorydb-redis-cluster-health, keyspaces-capacity-and-throttling) to the specific
AWS DevOps Agent directed action that remediates each one. Every directed action
listed here is a mutating operation run through use_aws, gated by per-action
operator approval in chat and executed under a scoped elevated IAM role.
Directed actions are never GREEN; each is classified YELLOW (recoverable) or RED
(hard to reverse or disruptive), failovers are called out explicitly, and refused
cases stay manual.

## DocumentDB instance under-sized / high CPU or connections

| Field | Value |
| --- | --- |
| Read-only finding | A DocumentDB instance is saturated - high CPUUtilization, high DatabaseConnections, or memory pressure - because its instance class is too small for the load. |
| Source | documentdb-cluster-health. |
| Directed action | docdb:ModifyDBInstance (move to a larger DBInstanceClass) or docdb:CreateDBInstance (add a read replica to the existing cluster to shed load). |
| Parameters | DBInstanceIdentifier=<instance>, DBInstanceClass=<larger-class>, ApplyImmediately=<true|false>; or DBInstanceIdentifier=<new-replica>, DBClusterIdentifier=<existing-cluster>, DBInstanceClass=<class>, AvailabilityZone=<az>. |
| Guardrail status | allowed - modifies an existing instance, or adds an instance to an existing cluster; neither passes an IAM role, so iam:PassRole is not required. |
| Safety | YELLOW - adding a replica is recoverable and non-disruptive to the writer; a ModifyDBInstance class change with ApplyImmediately reboots the instance, so rate it YELLOW with a brief impact note and schedule it in a maintenance window. |
| Approval scope | One ModifyDBInstance call on the named instance with the named class, or one CreateDBInstance call adding the named replica to the named cluster. Operator can narrow the class, never widen the blast radius. |
| Rollback | ModifyDBInstance again to restore the prior DBInstanceClass. For the added replica, removing it is a docdb:DeleteDBInstance (delete-class) and is a manual human step, not an agent action. |
| Notes | Adding a replica does not pass a role, which is why CreateDBInstance stays allowed here; deleting the replica to undo is the refused delete-class case (see below). |

## DocumentDB no replica / no high availability

| Field | Value |
| --- | --- |
| Read-only finding | A DocumentDB cluster runs with a single instance (writer only) and no reader in another AZ, so it has no failover target and no HA. |
| Source | documentdb-cluster-health. |
| Directed action | docdb:CreateDBInstance (add a reader instance in a second Availability Zone to the existing cluster). |
| Parameters | DBInstanceIdentifier=<new-reader>, DBClusterIdentifier=<existing-cluster>, DBInstanceClass=<class>, AvailabilityZone=<second-az>. |
| Guardrail status | allowed - adds an instance to an existing cluster; adding a DB instance to an existing cluster does not pass a role, so iam:PassRole is not required. |
| Safety | YELLOW - recoverable; adding a reader is non-disruptive to the writer and increases spend by one instance. |
| Approval scope | One CreateDBInstance call adding the named reader in the named AZ to the named cluster. Operator can narrow the class. |
| Rollback | Removing the added reader is a docdb:DeleteDBInstance (delete-class) and stays a manual human step, not an agent action. |
| Notes | This is the add-an-instance-to-an-existing-cluster case, which is allowed. Creating a brand new cluster is a different path and is out of scope here. |

## Neptune replica lag / needs failover to promote a healthy replica

| Field | Value |
| --- | --- |
| Read-only finding | A Neptune writer is degraded or a reader is lagging, and a controlled failover is needed to promote a healthy replica to writer. |
| Source | neptune-graph-performance-and-failover. |
| Directed action | neptune:FailoverDBCluster (trigger a controlled failover, optionally targeting a specific healthy replica). |
| Parameters | DBClusterIdentifier=<cluster>, TargetDBInstanceIdentifier=<healthy-replica> (optional; omit to let Neptune choose). |
| Guardrail status | allowed - operates on an existing cluster; a failover does not pass an IAM role, so iam:PassRole is not required. |
| Safety | YELLOW-to-RED - a failover causes a short outage with connection resets while the endpoint moves to the promoted replica; treat it as disruptive. Call out the brief interruption, require a maintenance window, and escalate before running it. |
| Approval scope | One FailoverDBCluster call on the named cluster, optionally to the named target replica. Operator confirms the maintenance window and the target. |
| Rollback | None - the failover is itself the action and cannot be "undone"; a subsequent failover would move the writer again and cause another interruption. Note the interruption up front. |
| Notes | Blast radius is real: in-flight connections drop and clients must reconnect. This is why it is rated toward RED and needs escalation plus a maintenance window even though it is technically allowed. |

## Neptune under-provisioned / needs a bigger writer or added replica

| Field | Value |
| --- | --- |
| Read-only finding | A Neptune cluster is under-provisioned - the writer instance class is too small, or there are too few replicas to serve read load. |
| Source | neptune-graph-performance-and-failover. |
| Directed action | neptune:ModifyDBInstance (move the writer to a larger DBInstanceClass) or neptune:CreateDBInstance (add a replica to the existing cluster). |
| Parameters | DBInstanceIdentifier=<instance>, DBInstanceClass=<larger-class>, ApplyImmediately=<true|false>; or DBInstanceIdentifier=<new-replica>, DBClusterIdentifier=<existing-cluster>, DBInstanceClass=<class>, AvailabilityZone=<az>. |
| Guardrail status | allowed - modifies an existing instance, or adds an instance to an existing cluster; neither passes an IAM role, so iam:PassRole is not required. |
| Safety | YELLOW - adding a replica is recoverable and non-disruptive; a ModifyDBInstance class change with ApplyImmediately reboots that instance, so schedule it in a maintenance window. |
| Approval scope | One ModifyDBInstance call on the named instance, or one CreateDBInstance call adding the named replica to the named cluster. Operator can narrow the class. |
| Rollback | ModifyDBInstance again to restore the prior DBInstanceClass. Removing an added replica is a neptune:DeleteDBInstance (delete-class) and stays a manual human step. |
| Notes | Adding a replica does not pass a role and is allowed; deleting a replica to undo is the refused delete-class case (see below). |

## Timestream magnetic-store write errors / memory-store retention too short

| Field | Value |
| --- | --- |
| Read-only finding | A Timestream table is rejecting late-arriving writes - MemoryStoreRetentionPeriod is too short for the ingestion lag, and/or MagneticStoreWrites are disabled so late records error out. |
| Source | timestream-ingestion-and-query-health. |
| Directed action | timestream-write:UpdateTable (extend memory-store retention, set magnetic-store retention, and enable magnetic-store writes with a rejected-data location). |
| Parameters | DatabaseName=<db>, TableName=<table>, RetentionProperties={MemoryStoreRetentionPeriodInHours=<hours>, MagneticStoreRetentionPeriodInDays=<days>}, MagneticStoreWriteProperties={EnableMagneticStoreWrites=true, MagneticStoreRejectedDataLocation={S3Configuration={BucketName=<existing-bucket>, EncryptionOption=<sse>}}}. |
| Guardrail status | allowed - modifies an existing table's retention and write properties; no deletion, no disabling of a control, and no iam:PassRole. |
| Safety | YELLOW - recoverable; extending retention and enabling magnetic-store writes strengthens durability of late data and adds storage cost. It does not disable any logging or encryption control. |
| Approval scope | One UpdateTable call on the named table with the named retention and magnetic-store write properties. Operator can narrow the retention values. |
| Rollback | UpdateTable again to restore prior RetentionProperties; disabling magnetic-store writes after enabling them is discouraged and is the weaker direction. |
| Notes | Sizes are set to the observed ingestion lag, not to the maximum retention. The rejected-data S3 location must reference an existing bucket; the agent does not create it as part of this action. |

## MemoryDB memory pressure / needs a larger node type or more shards

| Field | Value |
| --- | --- |
| Read-only finding | A MemoryDB for Redis cluster is under memory pressure - high memory utilization or evictions - and needs a larger node type or additional shards/replicas. |
| Source | memorydb-redis-cluster-health. |
| Directed action | memorydb:UpdateCluster (move to a larger NodeType, or scale NumShards / NumReplicasPerShard). |
| Parameters | ClusterName=<cluster>, NodeType=<larger-type>; or ClusterName=<cluster>, NumShards=<n>; or ClusterName=<cluster>, NumReplicasPerShard=<n>. |
| Guardrail status | allowed - modifies an existing cluster's sizing; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; scaling node type or shard count triggers a rebalancing/resharding operation that redistributes slots and can briefly affect latency, so schedule it in a maintenance window. |
| Approval scope | One UpdateCluster call on the named cluster with the named NodeType or shard/replica counts. Operator can narrow the target sizing. |
| Rollback | UpdateCluster again to restore the prior NodeType or counts; a scale-down triggers another rebalancing and can be disruptive, so rate the reverse carefully. |
| Notes | Scaling out adds shards and rebalances slots; scaling in removes them. Removing shards or replicas is a reduction, not a delete of the cluster, and is allowed, but its rebalancing impact is why it stays YELLOW with a maintenance window. |

## MemoryDB failover test / unhealthy primary

| Field | Value |
| --- | --- |
| Read-only finding | A MemoryDB shard has an unhealthy primary, or a failover test is needed to validate HA and promote a healthy replica within the shard. |
| Source | memorydb-redis-cluster-health. |
| Directed action | memorydb:FailoverShard (trigger a controlled failover of a single shard). |
| Parameters | ClusterName=<cluster>, ShardName=<shard>. |
| Guardrail status | allowed - operates on an existing cluster/shard; a failover does not pass an IAM role, so iam:PassRole is not required. |
| Safety | YELLOW-to-RED - the failover causes a brief connection reset on the affected shard while a replica is promoted; call out the interruption, require a maintenance window, and escalate before running it. |
| Approval scope | One FailoverShard call on the named shard of the named cluster. Operator confirms the maintenance window. |
| Rollback | None - the failover is itself the action; a subsequent failover would move the primary again and cause another interruption. Note the interruption up front. |
| Notes | Blast radius is limited to the one shard, but clients pinned to that shard's primary must reconnect. This is why it is rated toward RED and needs escalation even though it is allowed. |

## Keyspaces throttling from under-provisioned capacity or wrong capacity mode

| Field | Value |
| --- | --- |
| Read-only finding | An Amazon Keyspaces table is throttling - the capacity mode is wrong for the traffic (fixed provisioned RCU/WCU too low, or on-demand would fit a bursty pattern). |
| Source | keyspaces-capacity-and-throttling. |
| Directed action | keyspaces:UpdateTable (adjust capacitySpecification: throughputMode PAY_PER_REQUEST, or PROVISIONED with readCapacityUnits/writeCapacityUnits). |
| Parameters | keyspaceName=<ks>, tableName=<table>, capacitySpecification={throughputMode=PAY_PER_REQUEST}; or capacitySpecification={throughputMode=PROVISIONED, readCapacityUnits=<r>, writeCapacityUnits=<w>}. |
| Guardrail status | allowed - modifies an existing table's capacity; no deletion, no iam:PassRole. |
| Safety | YELLOW - recoverable; raising provisioned capacity or moving to on-demand changes cost, and capacity-mode changes are rate-limited. |
| Approval scope | One UpdateTable call on the named table with the named capacity mode and units. Operator can narrow the numbers. |
| Rollback | UpdateTable again to restore the prior capacitySpecification (subject to the capacity-mode change rate limit). |
| Notes | Keyspaces capacity can also be changed via the Cassandra CQL ALTER TABLE ... WITH custom_properties (capacity mode/throughput), but the directed action uses the Keyspaces API keyspaces:UpdateTable for a scoped, auditable call. Sizes are set to observed throughput, not to the maximum. |

## Refused and manual remediations

Some purpose-built database fixes cannot be executed as directed actions and stay
MANUAL, performed by a human with their own credentials:

- Delete-class operations. Deleting a DB instance, cluster, or table
  (docdb:DeleteDBInstance, neptune:DeleteDBInstance, deleting a MemoryDB cluster,
  keyspaces:DeleteTable), or dropping a snapshot, is a delete-class operation the
  agent refuses regardless of approval; a human performs the deletion.
- Reducing or removing an added replica. Undoing a DocumentDB or Neptune replica
  that was added is a delete (docdb/neptune:DeleteDBInstance), so it is delete-class
  and stays manual, even though adding the replica was allowed.
- iam:PassRole cases. Any remediation that passes an IAM role to a service is
  refused regardless of approval. Adding an instance to an existing docdb/neptune
  cluster does not pass a role and is allowed; creating a new cluster or resource
  that attaches a role does pass one and stays manual.
- Prohibited controls. The repository prohibits disabling logging or encryption
  and prohibits wildcard IAM; the agent will not propose any action that weakens
  those controls.

Failovers are a special case. Neptune (neptune:FailoverDBCluster) and MemoryDB
(memorydb:FailoverShard) failovers are technically allowed - they do not pass a
role and operate on existing resources - but they are disruptive. A Neptune
cluster failover resets connections across the whole cluster endpoint; a MemoryDB
shard failover resets connections on the affected shard. Be honest about the
blast radius: in-flight clients drop and must reconnect, and there is no rollback
because the failover is the action. For that reason these are rated YELLOW-to-RED
and require operator escalation plus a scheduled maintenance window before the
agent runs them.
