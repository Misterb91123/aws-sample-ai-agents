---
name: lambda-cold-start-investigator
agent_type: "Incident RCA"
description: Investigates and optimizes Lambda cold start latency by analyzing
  initialization patterns, dependency loading, and provisioned concurrency needs.
  Use this skill when Lambda functions have unacceptable cold start times,
  when p99 latency is significantly higher than p50 due to cold starts, or
  when evaluating provisioned concurrency as a mitigation strategy.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Lambda Cold Start Investigator

Use this skill to analyze, diagnose, and mitigate Lambda cold start latency
issues affecting user experience.

## When to Activate

- Lambda function p99 latency is 5x+ higher than p50 (cold start indicator).
- User-facing API backed by Lambda experiences intermittent slow responses.
- New Lambda function has unacceptable initialization time.
- Evaluating whether provisioned concurrency is needed.
- Investigating why cold starts are occurring more frequently than expected.

## Step 1: Quantify Cold Start Impact

Measure the actual cold start characteristics:

1. **Cold start duration**: Total initialization time (INIT phase in X-Ray/CloudWatch).
   - Init duration (from CloudWatch Logs: `REPORT ... Init Duration: Xms`)
   - What percentage of invocations are cold starts?
   - Cold start frequency pattern (after idle periods, during scale-out)

2. **Warm invocation baseline**: p50 duration when warm.

3. **Impact calculation**:
   - Cold start penalty = init duration + first invocation overhead
   - Total cold start time = init duration + warm execution time
   - User-visible impact = cold start penalty x cold start frequency

4. **When cold starts happen**:
   - After 10-15 minutes of inactivity (execution environment recycled)
   - During traffic spikes (new environments provisioned for concurrency)
   - After deployment (all environments replaced)

## Step 2: Decompose Initialization Time

Break down where time is spent during cold start:

```
[Total Cold Start]
+-- [AWS INIT phase]
| +-- Download and extract deployment package (size-dependent)
| +-- Start runtime (JVM, .NET CLR, Python interpreter)
| +-- Load extensions (if any)
|
+-- [Function INIT (your code)]
| +-- Import/require statements (loading dependencies)
| +-- SDK client initialization (AWS SDK, HTTP clients)
| +-- Database connection establishment
| +-- Configuration loading (Parameter Store, Secrets Manager)
| +-- Custom initialization logic
|
+-- [First invocation overhead]
    +-- JIT compilation, lazy loading (varies by runtime)
```

**Typical cold start durations by runtime:**
| Runtime | Typical Cold Start | Typical Range |
|---------|-------------------|---------------|
| Python | 200-500ms | 100ms-2s |
| Node.js | 150-400ms | 100ms-1.5s |
| Go | 50-100ms | 30ms-200ms |
| Java (Spring) | 3-10s | 2s-30s |
| Java (plain) | 500ms-3s | 300ms-5s |
| .NET | 500ms-2s | 300ms-5s |
| Rust | 50-100ms | 30ms-200ms |

## Step 3: Identify Cold Start Causes

Diagnose why cold starts are excessive:

**Deployment package issues:**
- Package size > 50MB (slower download and extraction)
- Bundled unnecessary dependencies
- Including dev dependencies in production
- Large ML models or data files in package

**Runtime initialization issues:**
- Java/JVM: class loading, Spring framework bootstrap, reflection
- Node.js: large node_modules tree, synchronous requires
- Python: importing heavy libraries (pandas, numpy, boto3 complete)
- .NET: assembly loading, DI container initialization

**Connection establishment:**
- Database connections (TCP + TLS + auth = 50-200ms each)
- HTTP client creation and connection pool initialization
- Parameter Store / Secrets Manager API calls during init

**VPC configuration:**
- VPC-attached Lambda: ENI creation adds 1-2s (previously 10s, now much improved with Hyperplane)
- Still adds some latency vs non-VPC Lambda

## Step 4: Optimization Strategies

Apply optimizations in order of impact:

### Package Size Reduction
- Tree-shake dependencies (webpack, esbuild for Node.js).
- Use Lambda Layers for shared dependencies.
- Remove unused imports and dead code.
- Use slim/minimal library variants where available.
- For Java: use GraalVM native image or SnapStart.
- For containers: use minimal base images.

### Code Initialization Optimization
- Lazy-load non-essential imports (only import when needed).
- Initialize SDK clients outside the handler but defer heavy work.
- Use connection pooling that connects lazily (on first use, not on import).
- Batch Parameter Store calls (get multiple parameters in one call).
- Cache initialization results in global scope (reused across warm invocations).

### Runtime Selection
- If cold start is critical and Java/Spring: consider SnapStart (Lambda-specific JVM snapshot).
- If building new: Go and Rust have fastest cold starts.
- Node.js and Python are good middle ground.
- Java with SnapStart or GraalVM native can match interpreted languages.

### Provisioned Concurrency
- Pre-warms a specified number of execution environments.
- Eliminates cold starts for up to that concurrency level.
- **When to use**: Latency-sensitive user-facing functions where cold start is unacceptable.
- **Cost consideration**: You pay for provisioned environments whether invoked or not.
- **Sizing**: Set to expected minimum concurrent executions.

### Architecture Strategies
- Use Application Auto Scaling to schedule provisioned concurrency (high during business hours, low overnight).
- Keep-alive invocations (ping every 5 minutes) - cheap but doesn't scale.
- Separate hot path (user-facing, provisioned) from cold path (background processing, no provisioning).

## Step 5: Estimate Provisioned Concurrency Need

If provisioned concurrency is the solution:

1. **Analyze concurrency pattern**: What's the typical concurrent execution count?
   - Check ConcurrentExecutions metric over 7 days.
   - Note the minimum sustained (this is your base provisioned number).
   - Note the peaks (decide if you provision for peaks or accept some cold starts).

2. **Calculate cost**:
   - Provisioned concurrency cost: ~$0.000004646/GB-second (always running)
   - Plus per-request duration cost when invoked.
   - Compare to: cost of cold start impact on users/business.

3. **Scheduling**:
   - Business hours only? Scale provisioned concurrency down overnight.
   - Use Application Auto Scaling with scheduled actions or target tracking.

## Step 6: Validate Improvements

After applying optimizations:
1. Deploy change and invoke with a cold start (new deployment forces cold start).
2. Measure Init Duration from REPORT log line.
3. Compare to previous Init Duration.
4. Monitor p99 latency over 24 hours (captures periodic cold starts).
5. Check that function still works correctly (lazy loading didn't break anything).

## Output

Produce a cold start analysis:
1. **Cold Start Profile**: Current init duration, warm duration, cold start frequency, user impact.
2. **Initialization Breakdown**: Time spent in each phase (package, runtime, your code, connections).
3. **Root Causes Identified**: What's contributing most to init time.
4. **Optimization Recommendations Table**: Optimization, estimated reduction, effort, risk.
5. **Provisioned Concurrency Assessment**: Recommended PC count, cost, scheduling strategy.
6. **Before/After Projections**: Expected p99 improvement after recommendations.
7. **Runtime Comparison**: If runtime switch is viable, expected cold start by alternative runtime.