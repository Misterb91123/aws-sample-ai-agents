---
name: glue-job-failure-diagnosis
agent_type: "Incident RCA"
description: Diagnoses AWS Glue ETL job failures by analyzing job run status,
  error messages, DPU and worker utilization, memory pressure, data skew, job
  bookmark behavior, connection issues, and IAM permission gaps. Use this skill
  when Glue jobs fail, run significantly longer than expected, or produce
  incomplete output, and when Spark executors report out-of-memory or the job
  cannot reach its S3 or Data Catalog sources.
version: "1.0.0"
last_updated: "2026-08-14"
---

# AWS Glue Job Failure Diagnosis

Use this skill to systematically diagnose why an AWS Glue ETL job failed or
degraded, isolate the root cause by error category, and recommend targeted
remediation.

## When to Activate

- A Glue job run ends in state FAILED, TIMEOUT, or STOPPED.
- A job succeeds but writes fewer records or partitions than expected.
- Job duration grows beyond its historical baseline (for example, a 20 minute
  job now runs longer than 2 hours).
- Spark executors report OutOfMemoryError or the driver is killed.
- The job cannot connect to a JDBC source, S3 path, or the Glue Data Catalog.

## Step 1: Retrieve Job Run Status and Error Detail

For the failing run, collect:
1. Job name, JobRunId, and terminal state (FAILED, TIMEOUT, STOPPED).
2. Glue version (2.0, 3.0, 4.0) and worker type (Standard, G.1X, G.2X, G.4X,
   G.8X) with NumberOfWorkers.
3. The ErrorMessage field from GetJobRun.
4. ExecutionTime versus Timeout (default 2880 minutes; note if the run hit it).
5. MaxRetries and whether prior attempts failed identically.
6. Continuous logging output in CloudWatch Logs groups
   /aws-glue/jobs/output and /aws-glue/jobs/error.

Classify the error string into one of the categories in the steps below.

## Step 2: Diagnose Memory and OOM Failures

Look for executor or driver OutOfMemory signals:
1. Error text containing "java.lang.OutOfMemoryError", "Container killed by
   YARN for exceeding memory limits", or exit code 137.
2. Enable the Spark UI and Glue job metrics; inspect
   glue.driver.jvm.heap.usage and glue.ALL.jvm.heap.usage approaching 1.0.
3. Determine whether the OOM is on the driver (large collect(), broadcast, or
   many partitions) or executors (skewed or oversized partitions).

Remediation:
- Move from G.1X (4 vCPU, 16 GB) to G.2X (8 vCPU, 32 GB) or higher.
- Avoid collect() and toPandas() on large DataFrames; write directly to S3.
- Increase parallelism with repartition() so no single partition exceeds a few
  hundred MB.
- Enable Glue auto scaling and set a realistic NumberOfWorkers.

## Step 3: Detect Data Skew

Uneven partition processing causes a few tasks to run far longer than the rest:
1. In the Spark UI stage view, compare max task duration to the median; a ratio
   above 5x indicates skew.
2. Check shuffle read size per task for outliers.
3. Identify skewed join or groupBy keys (for example, a null or default key
   holding most rows).

Remediation:
- Add salting to skewed join keys.
- Use broadcast joins for small dimension tables.
- Repartition on a higher-cardinality column before wide transformations.

## Step 4: Investigate Timeout and Long Runtime

For TIMEOUT or slow runs:
1. Compare ExecutionTime to historical average from GetJobRuns.
2. Check whether input data volume grew (new partitions, backfill).
3. Confirm worker count is not the bottleneck (CPU and memory below 60 percent
   suggests too few tasks, not undersized workers).
4. Look for slow JDBC reads without predicate pushdown or partitioning.

Remediation:
- Raise Timeout only after confirming the job is progressing, not stuck.
- Increase NumberOfWorkers or enable auto scaling.
- Push filters into source reads and partition JDBC reads with
  hashfield/hashpartitions.

## Step 5: Review Job Bookmark Behavior

Bookmarks can silently skip or reprocess data:
1. Confirm whether bookmarks are Enabled, Disabled, or Paused.
2. If output is incomplete, a bookmark may be skipping already-seen files even
   though downstream data changed.
3. If data is duplicated, a reset or misconfigured bookmark may reprocess.
4. Verify the transformation_ctx is set consistently on source readers.

Remediation:
- Reset the bookmark (ResetJobBookmark) for a controlled full reprocess.
- Ensure stable transformation_ctx names across code changes.

## Step 6: Diagnose Connection and Source Failures

For source or sink connectivity errors:
1. JDBC errors: check the Glue Connection, VPC subnet, route table, and that a
   NAT gateway or VPC endpoint exists for outbound access.
2. Confirm the security group allows the database port (for example, 5432,
   3306) and that a self-referencing rule exists for Glue elastic network
   interfaces.
3. S3 errors ("Access Denied", "NoSuchBucket"): verify bucket, prefix, and
   Region.
4. Data Catalog errors ("EntityNotFoundException"): confirm the database and
   table exist and the crawler has run.

## Step 7: Check IAM Permission Gaps

For AccessDenied failures, verify the job role grants:
1. s3:GetObject, s3:PutObject, s3:ListBucket on the input and output prefixes.
2. glue:GetTable, glue:GetPartitions, glue:GetDatabase for Catalog reads and
   glue:CreatePartition or glue:BatchCreatePartition for writes.
3. logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents for logging.
4. kms:Decrypt and kms:GenerateDataKey when S3 or Catalog data is
   KMS-encrypted.
5. secretsmanager:GetSecretValue when connections use Secrets Manager.

Cross-check S3 bucket policies and KMS key policies, which can deny access even
when the role policy allows it.

## Output

Provide a diagnosis summary:
1. Root cause category: OOM, data skew, timeout, bookmark, connection, or IAM.
2. Supporting evidence (error message, metric values, task-skew ratio).
3. Specific remediation steps with exact configuration or code changes.
4. Recommended worker type and count if resizing is advised.
5. Preventive measures (auto scaling, monitoring alarms on
   glue.driver.aggregate.numFailedTasks) to reduce recurrence.