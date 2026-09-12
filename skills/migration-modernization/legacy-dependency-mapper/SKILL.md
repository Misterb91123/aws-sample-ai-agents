---
name: legacy-dependency-mapper
agent_type: "Generic"
description: Maps hidden and undocumented dependencies in legacy applications by
  analyzing network traffic, configuration files, and runtime behavior. Use this
  skill when preparing legacy applications for migration where documentation is
  incomplete, when untangling tightly coupled systems, or when decommissioning
  old infrastructure and needing to understand what depends on it.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Legacy Dependency Mapper

Use this skill to discover and document dependencies in legacy applications
where documentation is missing, outdated, or incomplete.

## When to Activate

- Migrating a legacy application with poor or no documentation.
- Decommissioning old infrastructure - need to know what depends on it.
- Application team reports unexpected failures after "unrelated" changes.
- Planning modernization and need a complete dependency graph first.
- New team inheriting a legacy system they don't fully understand.

## Step 1: Network-Based Discovery

Use network traffic analysis to find connections:

**VPC Flow Logs analysis:**
1. Query flow logs for the legacy resource's ENI/IP.
2. Identify all unique source/destination IP:port combinations.
3. Group by direction (inbound = things that depend on us, outbound = things we depend on).
4. Map IPs to resources (EC2 instances, RDS endpoints, external services).
5. Identify the protocols and port patterns.

**Key patterns to capture:**
- Database connections (port 3306/MySQL, 5432/PostgreSQL, 1521/Oracle, 1433/SQL Server)
- HTTP/HTTPS calls (port 80, 443, custom API ports)
- Message queue connections (5672/RabbitMQ, 9092/Kafka, various/SQS)
- Cache connections (6379/Redis, 11211/Memcached)
- File sharing (445/SMB, 2049/NFS)
- LDAP/AD authentication (389/LDAP, 636/LDAPS)
- SMTP/email (25, 587)
- SSH/management (22)
- Custom/proprietary protocols (document port and purpose)

**Duration**: Analyze at minimum 7 days of traffic to capture periodic connections (nightly jobs, weekly reports).

## Step 2: Configuration-Based Discovery

Examine application configuration for declared dependencies:

1. **Application config files**: Connection strings, URLs, hostnames.
2. **Environment variables**: Endpoints, credentials, feature flags.
3. **Service discovery registration**: Consul, Eureka, Route53 service entries.
4. **Load balancer targets**: What's behind load balancers that this app calls.
5. **/etc/hosts**: Hardcoded host entries (common in legacy systems).
6. **Cron tables**: Scheduled jobs calling other systems.
7. **Init scripts**: Services started at boot that indicate dependencies.
8. **DNS resolution logs**: What hostnames does the application resolve?

## Step 3: Runtime-Based Discovery

Analyze runtime behavior for dynamic dependencies:

1. **DNS queries**: Monitor DNS lookups from the host (reveals dynamically resolved dependencies).
2. **Process inspection**: What ports are open, what connections are established.
3. **System calls**: File access patterns (shared file systems, mounted drives).
4. **Library loading**: Shared libraries, DLLs, JARs loaded at runtime.
5. **X-Ray/APM traces**: If instrumented, analyze call graphs.
6. **Thread dumps/stack traces**: Show connection patterns during execution.

## Step 4: Classify Dependencies

For each discovered dependency:

| Classification | Criteria |
|---------------|----------|
| **Hard runtime** | Application fails immediately if dependency unavailable |
| **Soft runtime** | Application degrades but continues (feature disabled, cached fallback) |
| **Startup** | Required during initialization only (config server, license server) |
| **Periodic** | Used at scheduled intervals (batch jobs, nightly sync) |
| **Conditional** | Used only for specific operations or code paths |
| **Transitive** | Not directly called, but depends on something that does |

**Criticality assessment:**
- What happens if this dependency is unavailable for 5 minutes? 1 hour? 1 day?
- Is there an existing fallback or does the app crash?
- How many users/features are affected?

## Step 5: Identify Undocumented Dependencies

Look for hidden dependencies often missed:

1. **DNS dependencies**: Application resolves DNS names hardcoded in source code.
2. **Time dependencies**: NTP servers, time sync requirements.
3. **Certificate dependencies**: CA trust stores, client certificates.
4. **License servers**: FlexLM or similar floating license dependencies.
5. **Shared state**: Temp files, lock files, IPC mechanisms between processes.
6. **Infrastructure services**: DHCP, DNS forwarders, proxy servers.
7. **Monitoring agents**: APM agents, log collectors that the app depends on.
8. **Sidecar processes**: Helper services running on the same host.

## Step 6: Build the Dependency Graph

Organize findings into a structured graph:

```
[Legacy App]
+-- OUTBOUND (we depend on):
| +-- RDS MySQL (10.0.1.50:3306) - HARD RUNTIME
| +-- Redis Cache (10.0.1.100:6379) - SOFT RUNTIME
| +-- Auth API (auth.internal:443) - HARD RUNTIME
| +-- SMTP Server (mail.corp:587) - SOFT RUNTIME (notifications)
| +-- NFS Share (10.0.2.5:/exports/shared) - HARD RUNTIME
| +-- External Payment API (api.stripe.com:443) - CONDITIONAL
|
+-- INBOUND (depends on us):
| +-- Web Frontend (via ALB on port 8080) - 500 req/min
| +-- Mobile API Gateway (port 8080) - 200 req/min
| +-- Reporting Service (port 8080, /api/reports) - nightly
| +-- Monitoring (port 9090, /metrics) - every 30s
|
+-- SHARED (co-dependencies):
    +-- Shared NFS volume (also used by reporting-service)
    +-- Shared Redis (also used by session-service)
```

## Step 7: Migration Impact Analysis

For each dependency, assess migration implications:

| Dependency | Migration Consideration |
|------------|----------------------|
| On-prem database | Must migrate or establish hybrid connectivity |
| Shared file system | Must be replaced (EFS, S3) or accessed via VPN |
| Internal service | Must be migrated first (or accessed via VPN temporarily) |
| External API | No change (ensure network path exists from AWS) |
| LDAP/Active Directory | AD Connector, hybrid connectivity, or migrate to Cognito |
| License server | Must be reachable from AWS (VPN) or cloud-compatible license |

## Output

Produce a dependency map:
1. **Dependency Graph Visualization**: Topology diagram showing all dependencies with direction and criticality.
2. **Dependency Inventory Table**: Dependency, type (inbound/outbound), protocol, port, criticality, documented (yes/no).
3. **Undocumented Findings**: Dependencies discovered that were not in existing documentation.
4. **Migration Sequencing Impact**: Which dependencies must be migrated first, co-migrated, or bridged.
5. **Risk Assessment**: Dependencies that create migration blockers or require hybrid connectivity.
6. **Decommission Checklist**: For shutting down the source, all dependents that must be redirected.