---
name: serverless-migration-evaluator
agent_type: "Generic"
description: Evaluates workloads for migration to serverless architectures (Lambda,
  Fargate, API Gateway, Step Functions, EventBridge). Use this skill when assessing
  whether applications would benefit from serverless migration, estimating cost
  impact, identifying refactoring requirements, and designing serverless target
  architectures for existing workloads.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Serverless Migration Evaluator

Use this skill to assess workloads for serverless migration and design
target architectures using AWS serverless services.

## When to Activate

- Team asks "should we go serverless?"
- Cost optimization initiative targeting over-provisioned, low-utilization services.
- New feature that could be built serverless from the start.
- Evaluating migration path for scheduled jobs, APIs, or event processors.
- Comparing serverless vs container cost/complexity for a workload.

## Step 1: Profile the Current Workload

Characterize the workload for serverless fit:

**Traffic pattern:**
- Request volume (daily, peak, minimum)
- Traffic variability: (peak / average) ratio
- Idle periods (hours with zero or near-zero traffic)
- Request duration (p50, p95, p99)
- Concurrent execution requirements

**Compute profile:**
- CPU utilization pattern (average and peak)
- Memory requirements
- Execution duration per request/invocation
- Startup/initialization time
- Stateful or stateless processing

**Integration points:**
- Synchronous (HTTP APIs, request/response)
- Asynchronous (queue processing, event-driven)
- Scheduled (cron jobs, batch processing)
- Streaming (real-time data processing)

## Step 2: Assess Serverless Fit

Rate the workload against serverless suitability criteria:

**Excellent serverless candidates (score 8-10):**
- Event-driven processing (S3 triggers, SQS consumers, DynamoDB streams)
- REST/GraphQL APIs with variable traffic (especially with idle periods)
- Scheduled jobs and cron tasks (< 15 minutes execution)
- File/image processing pipelines
- Webhook handlers
- Low-traffic microservices (< 1000 req/min average)
- Chatbots and notification handlers

**Good candidates with some refactoring (score 5-7):**
- APIs with moderate traffic and short response times
- Data transformation ETL jobs (can be chunked)
- Authentication/authorization microservices
- Search and filtering services (with external index)

**Poor serverless candidates (score 1-4):**
- Long-running processes (> 15 minutes)
- Workloads requiring persistent connections (WebSockets need API Gateway WS)
- High-throughput, steady-state workloads (cheaper on reserved EC2/Fargate)
- Applications with large binary dependencies or cold start sensitivity
- Workloads needing GPUs or specialized hardware
- Applications with complex local state management
- Latency-sensitive services that can't tolerate cold starts

## Step 3: Design Target Serverless Architecture

Map current components to serverless equivalents:

| Current Component | Serverless Equivalent |
|-------------------|---------------------|
| EC2/ECS web server | API Gateway + Lambda |
| Background worker consuming queue | Lambda triggered by SQS |
| Cron job (scheduled task) | EventBridge Scheduler + Lambda |
| Load balancer | API Gateway (HTTP API or REST API) |
| Container running periodic batch | Step Functions + Lambda |
| WebSocket server | API Gateway WebSocket + Lambda |
| File processor (S3 event) | S3 Event -> Lambda |
| Stream processor | Kinesis/DynamoDB Streams -> Lambda |
| Orchestrated workflow | Step Functions (Standard or Express) |
| Static file serving | S3 + CloudFront |

**Architecture patterns:**
- API pattern: API Gateway -> Lambda -> DynamoDB/RDS Proxy
- Event processing: EventBridge -> SQS -> Lambda -> DynamoDB
- File processing: S3 -> Lambda -> S3 (output)
- Scheduled: EventBridge Schedule -> Lambda
- Saga/Workflow: Step Functions orchestrating multiple Lambdas

## Step 4: Estimate Serverless Cost

Compare current cost vs projected serverless cost:

**Lambda pricing model:**
- Per request: $0.20 per 1M requests
- Per duration: $0.0000166667 per GB-second
- Monthly cost = (requests x $0.20/1M) + (avg_duration_sec x memory_GB x requests x $0.0000166667)

**API Gateway pricing:**
- HTTP API: $1.00 per million requests
- REST API: $3.50 per million requests

**When serverless is cheaper:**
- Traffic < 1M requests/month (Lambda free tier covers it)
- High variability: idle periods mean zero cost (vs always-on EC2)
- Low average utilization (< 20% CPU on current instance)

**When containers/EC2 is cheaper:**
- Steady high throughput (> 10M requests/month, sustained)
- Long-running request processing (> 5 seconds average duration)
- High memory requirements (> 3GB per execution)
- Predictable traffic (Savings Plans make EC2 very cost-effective)

## Step 5: Identify Refactoring Requirements

Common changes needed for serverless migration:

| Current Pattern | Serverless Refactoring |
|----------------|----------------------|
| Local file system | S3 or EFS for Lambda |
| In-memory session state | DynamoDB or ElastiCache |
| Long-running connections to DB | RDS Proxy (connection pooling for Lambda) |
| Monolithic application | Decompose into individual functions |
| Startup initialization (heavy) | Provisioned concurrency or optimize cold start |
| Synchronous chaining | Step Functions for orchestration |
| Large deployment artifact | Layers for shared dependencies; container image for Lambda |
| Environment-specific config | Parameter Store / environment variables |

## Step 6: Assess Operational Impact

How operations change with serverless:

**Benefits:**
- No patching, no capacity management, no scaling configuration.
- Pay-per-use eliminates idle cost.
- Built-in HA (Lambda runs across AZs automatically).
- Faster deployments (function-level deploys).

**New challenges:**
- Cold starts (monitor p99 latency; use provisioned concurrency for sensitive paths).
- Distributed tracing is more complex (many small functions).
- Local development/testing differs from production (use SAM/Serverless Framework).
- Vendor lock-in (heavily tied to AWS services).
- Concurrency limits (account-level Lambda concurrency).
- Debugging distributed systems is harder than monolithic.

## Output

Produce a serverless migration assessment:
1. **Workload Suitability Score**: Per-workload serverless fit rating with justification.
2. **Target Architecture Diagram**: Proposed serverless architecture using AWS services.
3. **Cost Comparison Table**: Current monthly cost vs projected serverless cost per workload.
4. **Refactoring Requirements**: Changes needed before migration, with effort estimates.
5. **Cold Start Risk Assessment**: Latency-sensitive paths and mitigation strategies.
6. **Migration Sequence**: Order of migration for multi-component applications.
7. **Operational Model Changes**: How monitoring, debugging, and deployment processes change.