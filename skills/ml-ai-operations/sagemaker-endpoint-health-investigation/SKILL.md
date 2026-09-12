---
name: sagemaker-endpoint-health-investigation
agent_type: "Incident RCA"
description: Investigate the health of Amazon SageMaker real-time inference endpoints when they exhibit high latency, invocation errors, or throttling. I use this skill to analyze latency components, error codes, capacity pressure, and auto-scaling behavior so I can pinpoint whether the problem is model performance, infrastructure sizing, or traffic distribution. I activate it whenever an endpoint shows elevated ModelLatency, 4XX/5XX errors, or throttling events.
version: "1.0.0"
last_updated: "2026-08-14"
---

# SageMaker Endpoint Health Investigation

This skill provides a structured procedure for diagnosing degraded Amazon SageMaker real-time inference endpoints. It separates latency into its component parts, correlates errors with capacity, and evaluates auto-scaling and traffic distribution so remediation targets the true root cause rather than symptoms.

## When to Activate

- An endpoint reports ModelLatency p99 above the application SLA (for example >= 500 ms for interactive workloads).
- CloudWatch shows a rising rate of Invocation4XXErrors or Invocation5XXErrors.
- Clients receive HTTP 429 responses or ThrottlingException, indicating request throttling.
- InvocationsPerInstance approaches the tested per-instance throughput ceiling.
- A multi-model endpoint (MME) shows increased latency correlated with model cache activity.
- A newly deployed endpoint variant shows regressions after a traffic shift.

## Step 1: Decompose Latency

Retrieve the CloudWatch metrics in the /aws/sagemaker/Endpoints namespace for the affected EndpointName and VariantName:

- ModelLatency: time spent inside the model container. High values point to the model or inference code.
- OverheadLatency: time added by SageMaker for request handling, download, and response. High values point to payload size, serialization, or model download on cold start.

Compare p50, p90, and p99 over the last 1 hour and 24 hours. If OverheadLatency dominates, investigate payload size and cold model loading. If ModelLatency dominates, investigate model complexity, batch size, and instance compute.

## Step 2: Classify Errors

Analyze error metrics and correlate with timestamps:

- Invocation4XXErrors: usually client-side. Inspect payload schema, content type, and request size limits (6 MB for real-time synchronous invocations).
- Invocation5XXErrors: usually server-side. Inspect container logs in CloudWatch Logs for the endpoint for out-of-memory events, model load failures, or timeouts (the container must respond within 60 seconds by default).
- ThrottlingException / HTTP 429: correlate with InvocationsPerInstance and instance count to confirm capacity exhaustion versus account-level throttling.

## Step 3: Evaluate Capacity and Utilization

Compare InvocationsPerInstance against the throughput established during load testing. Then review instance-level utilization metrics:

- CPUUtilization and MemoryUtilization for CPU-backed instances.
- GPUUtilization and GPUMemoryUtilization for GPU-backed instances (for example ml.g5 or ml.p4d).

Sustained CPUUtilization above 70 percent or GPUMemoryUtilization above 90 percent indicates the endpoint is compute or memory bound and needs scaling out or a larger instance type. Low utilization with high latency points to model code or I/O, not sizing.

## Step 4: Review Auto-Scaling and Cold Loading

Inspect the Application Auto Scaling target tracking policy attached to the variant:

- Confirm the target metric (commonly SageMakerVariantInvocationsPerInstance) and target value are set to a value below the measured saturation point.
- Verify MinCapacity, MaxCapacity, and cooldown periods (scale-out cooldown typically 60-300 seconds).
- If scaling lags demand spikes, latency will spike during the warm-up window. Consider a lower target value or provisioned baseline capacity.

For endpoints that download models on scale-out, measure the cold-start contribution to OverheadLatency and consider warm pools or smaller model artifacts.

## Step 5: Inspect Multi-Model Endpoint Cache Behavior

For multi-model endpoints, evaluate the ModelCacheHit metric and LoadedModelCount. A low cache hit ratio (for example < 0.8) means models are being evicted and reloaded from S3, adding load latency to OverheadLatency. Remediate by increasing instance memory, reducing the active model set, or sharding models across additional endpoints.

## Step 6: Check Data Capture and Traffic Distribution

- If data capture is enabled, confirm the capture sampling percentage is not adding overhead and that captured records are landing in the configured S3 destination for later drift analysis.
- For endpoints with multiple production variants, compare per-variant latency and error rates. If one variant regressed after a traffic weight change, shift weight back toward the healthy variant and roll the regressed variant back.

## Step 7: Remediate

Select remediation based on the dominant finding:

- Compute or memory bound: scale out instance count, raise MaxCapacity, or move to a larger or GPU instance family.
- Cold-start latency: enable warm pools, reduce artifact size, or maintain minimum capacity above zero.
- MME cache misses: increase memory or reduce concurrent model count.
- Client 4XX errors: fix payload schema and content type on the caller side.
- Container 5XX errors: raise container memory, increase timeout, or fix inference code.
- Variant regression: adjust traffic weights and roll back the failing variant.

## Output

The skill produces an endpoint health report containing: a latency decomposition (ModelLatency versus OverheadLatency across p50/p90/p99), an error classification with root-cause attribution, a capacity and utilization assessment against tested throughput, an auto-scaling configuration review, MME cache findings when applicable, and a prioritized remediation plan with specific metric thresholds to verify recovery.