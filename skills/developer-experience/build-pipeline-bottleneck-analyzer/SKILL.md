---
name: build-pipeline-bottleneck-analyzer
agent_type: "Generic"
description: Use this skill when I need to analyze CI/CD pipeline stage timing to find bottlenecks that slow the developer feedback loop across AWS CodePipeline and CodeBuild. Activate it when pipeline lead time is high, builds sit in a queue, or a specific stage dominates total execution duration. It breaks total pipeline time into stage-level segments and isolates the critical path so I can target the slowest stage first.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Build Pipeline Bottleneck Analyzer

This skill measures where time goes in a CI/CD pipeline and identifies the single stage on the critical path that most delays developer feedback. It separates time spent waiting (queue) from time spent working (execution), then produces ranked recommendations to shorten the loop from commit to deployable artifact.

## When to Activate

- Pipeline lead time (commit to deploy) exceeds the team target, for example greater than 20 minutes.
- CodeBuild builds queue because concurrent build limits are reached and projects wait to start.
- One stage consistently accounts for more than 40 percent of total pipeline duration.
- Developers report slow feedback and pull requests wait on green builds.
- Build duration has grown more than 25 percent over the trailing 30 days.

## Step 1: Collect Stage-by-Stage Duration

Pull execution history and compute per-stage timing:

- Call CodePipeline ListPipelineExecutions and GetPipelineExecution for the last 50 to 100 executions.
- Use ListActionExecutions to get startTime and lastUpdateTime for each action.
- Compute per-stage duration as the sum of its action durations, plus total pipeline duration.
- Report p50 and p95 per stage. Use p95 for capacity planning because tail latency drives developer frustration.

## Step 2: Separate Queue Wait From Execution Time

Distinguish waiting from working so fixes target the right cause:

- For CodeBuild, call BatchGetBuilds and read the phases array. QUEUED phase durationInSeconds is queue wait; the SUBMITTED, PROVISIONING, INSTALL, PRE_BUILD, BUILD, POST_BUILD, UPLOAD_ARTIFACTS phases are execution.
- Flag queue wait greater than 60 seconds as a concurrency problem, not a build-speed problem.
- If queue wait is high, check the account concurrent build limit and project-level concurrentBuildLimit, and consider raising the service quota for concurrent CodeBuild builds.

## Step 3: Correlate Compute Type With Build Duration

Check whether the build is compute-starved:

- Read the CodeBuild project environment.computeType (for example BUILD_GENERAL1_SMALL at 3 GB memory and 2 vCPU, MEDIUM at 7 GB and 4 vCPU, LARGE at 15 GB and 8 vCPU).
- If BUILD phase CPU or memory utilization stays above 80 percent, a larger compute type can cut wall-clock time.
- Estimate cost impact: larger compute costs more per build minute, so justify the upgrade only when it reduces total billed minutes or clears a critical-path bottleneck.

## Step 4: Assess Cache Effectiveness

Determine whether caching is actually saving time:

- Inspect buildspec cache paths and the project cache type (NO_CACHE, LOCAL, or S3).
- For LOCAL cache, confirm LOCAL_DOCKER_LAYER_CACHE and LOCAL_CUSTOM_CACHE modes are enabled where relevant.
- Compare INSTALL and PRE_BUILD phase duration on cache-hit versus cache-miss runs. A dependency cache that saves less than 10 percent is misconfigured or has poor key locality.
- For container builds, verify Docker layer caching so unchanged layers are not rebuilt each run.

## Step 5: Analyze Test Stage Duration and Parallelization

Tests are often the largest single segment:

- Measure the test action duration as a share of total pipeline time.
- Check whether tests run serially in one CodeBuild project versus split across parallel projects or a batch build (buildspec batch configuration).
- Recommend sharding when a single test phase exceeds 5 minutes and tests are independent.

## Step 6: Measure Approval and Handoff Waits

Account for time the pipeline is idle waiting on humans or transfers:

- For manual approval actions, compute wait time from action startTime to the approval event.
- Flag approval waits greater than 15 minutes as a process bottleneck rather than an engineering one.
- Measure artifact upload and download time (UPLOAD_ARTIFACTS phase and DOWNLOAD_SOURCE) between stages; large artifacts moving through S3 add latency to every stage transition.

## Step 7: Identify the Critical Path Stage

Rank stages and name the one bottleneck:

- Sort stages by p95 duration and by share of total duration.
- The critical path stage is the highest-contribution stage that cannot overlap with others.
- State the expected reduction in total lead time if that one stage is optimized, so effort is spent where it moves the metric.

## Output

The skill produces a pipeline timing report containing: a per-stage p50 and p95 duration table, queue wait versus execution time split for each CodeBuild action, compute-type utilization findings, cache hit-rate and time-saved analysis, test parallelization assessment, approval and artifact-transfer wait times, the single critical path stage, and a ranked list of remediations with the estimated lead-time reduction for each. Each recommendation is tied to a specific API-observed metric and threshold so the developer can act without further investigation.