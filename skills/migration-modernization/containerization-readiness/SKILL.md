---
name: containerization-readiness
agent_type: "Generic"
description: Evaluates applications for containerization by analyzing dependencies,
  state management, configuration patterns, and runtime requirements. Use this skill
  when assessing which applications are good candidates for migrating to ECS/EKS,
  identifying refactoring needed before containerization, or prioritizing a
  container migration backlog.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Containerization Readiness Assessment

Use this skill to evaluate whether applications are ready for containerization
and what changes are needed to run them effectively in containers.

## When to Activate

- Planning migration from VMs/EC2 to ECS or EKS.
- Application team requests to containerize their service.
- Prioritizing which services to containerize first.
- Post-containerization troubleshooting (why isn't it working in containers?).
- Evaluating modernization roadmap for a legacy application portfolio.

## Step 1: Assess Application Architecture

Evaluate the application's architecture patterns:

**Container-Ready Patterns (high readiness):**
- Stateless request handling (state in external stores)
- Configuration via environment variables
- Logs written to stdout/stderr
- Graceful shutdown on SIGTERM
- Health check endpoints available
- Single process per application instance
- Horizontal scalability designed-in

**Container-Hostile Patterns (need refactoring):**
- Local filesystem state (sessions on disk, local uploads, temp files)
- Hardcoded absolute paths (e.g., `/opt/app/config/prod.xml`)
- Multi-process monolith (cron + web server + background worker in one)
- Startup takes > 60 seconds (impacts scaling and deployments)
- Required persistent local storage that changes at runtime
- Relies on static hostname or IP address
- Requires specific OS-level system services (systemd, cron)

## Step 2: Evaluate State Management

Container-friendliness depends heavily on state:

| State Type | Container Strategy | Effort |
|------------|-------------------|--------|
| No state (pure compute) | [PASS] Perfect for containers | None |
| Session state in memory | Move to Redis/ElastiCache | Low-Medium |
| File uploads on local disk | Move to S3 | Low |
| SQLite or local database | Move to RDS/DynamoDB | Medium |
| Log files on local disk | Switch to stdout/stderr + CloudWatch | Low |
| Persistent config files modified at runtime | Move to Parameter Store/ConfigMap | Medium |
| Local cron jobs | Separate into scheduled ECS tasks or EventBridge | Medium |
| Shared filesystem between instances | EFS mount or refactor to S3 | Medium-High |

## Step 3: Evaluate Dependencies

Check external dependencies for container compatibility:

1. **Database connections**: Can the app handle connection pooling correctly with multiple replicas?
2. **Service discovery**: Does it use hardcoded IPs or can it use DNS-based discovery?
3. **License servers**: Can the container reach the license server? Is licensing container-friendly?
4. **Shared libraries**: Are there OS-level dependencies (specific library versions, kernel modules)?
5. **Network requirements**: Does it need specific ports, host networking, or multicast?
6. **GPU or hardware**: Does it need specialized hardware access?

## Step 4: Evaluate Configuration Management

How is the application configured?

| Configuration Method | Container Readiness | Migration Path |
|---------------------|--------------------|-|
| Environment variables | [PASS] Native container pattern | None needed |
| Command-line arguments | [PASS] Works with container CMD/ENTRYPOINT | None needed |
| Config file (read-only, injected) | [PASS] Use ConfigMap or Secrets mount | Package in image or mount |
| Config file (read-write at runtime) | [WARN] Needs refactoring | Move to external config service |
| Windows Registry | [FAIL] Not available in Linux containers | Refactor to env vars or files |
| Database-stored config | [PASS] Works naturally | None needed |

## Step 5: Evaluate Build and Image Strategy

Assess how the application can be packaged:

1. **Build reproducibility**: Can you build the app from source reliably?
2. **Dependency management**: Are all dependencies declared (package.json, requirements.txt, pom.xml)?
3. **Base image selection**: What OS/runtime is needed? (slim images preferred)
4. **Image size considerations**: Can it be under 500MB? (ideal < 200MB for fast pulls)
5. **Secret handling**: Are secrets baked in or injected at runtime?
6. **Multi-stage build**: Can build tools be separated from runtime image?

## Step 6: Evaluate Operational Readiness

For container operations:

| Requirement | Ready | Needs Work |
|-------------|-------|-----------|
| Health check endpoint | HTTP /health returning 200 | No health check, checks require custom logic |
| Graceful shutdown | Handles SIGTERM, drains connections | Requires SIGKILL to stop, no drain |
| Startup time | < 30 seconds | > 60 seconds (impacts scaling) |
| Resource predictability | Stable CPU/memory usage | Memory leaks, unpredictable spikes |
| Log format | Structured JSON to stdout | Writes to multiple log files, custom format |
| Process model | Single main process | Multiple processes managed by supervisord |
| Port configuration | Configurable listen port | Hardcoded port that conflicts with platform |

## Step 7: Score and Prioritize

Rate each application on a containerization readiness scale:

| Score | Readiness | Typical Effort | Recommendation |
|-------|-----------|---------------|----------------|
| 9-10 | Excellent | Days | Containerize immediately, minimal changes |
| 7-8 | Good | 1-2 sprints | Containerize with minor refactoring |
| 5-6 | Moderate | 1-2 months | Containerize with planned refactoring work |
| 3-4 | Low | Multiple months | Significant refactoring needed, plan carefully |
| 1-2 | Not Ready | Major rewrite | Keep on VMs or consider full modernization |

**Prioritize containerization by:**
1. Highest readiness score (quick wins first)
2. Highest deployment frequency (benefits most from containers)
3. Highest scaling needs (containers excel at horizontal scaling)
4. Team with container expertise (reduce learning curve risk)

## Output

Produce a containerization readiness report:
1. **Summary**: Applications assessed, readiness distribution, quick-win candidates.
2. **Readiness Scorecard Table**: Application, readiness score, top blockers, estimated effort, recommendation.
3. **Refactoring Requirements Table**: Application, item to change, effort, priority, strategy.
4. **State Migration Plan**: For each stateful pattern, the target solution and migration approach.
5. **Dependency Analysis**: Shared dependencies that affect migration sequencing.
6. **Container Platform Recommendation**: ECS Fargate vs ECS EC2 vs EKS based on workload characteristics.
7. **Migration Roadmap**: Phased plan for containerizing the portfolio.