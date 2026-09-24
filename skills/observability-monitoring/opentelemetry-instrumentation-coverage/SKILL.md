---
name: opentelemetry-instrumentation-coverage
agent_type: "Generic"
description: Reports OpenTelemetry instrumentation coverage that feeds Amazon
  CloudWatch Omni - which services emit telemetry over OTLP or the CloudWatch
  OTel/ADOT path (traces, metrics, logs) versus which appear in the topology or
  resource inventory with missing or partial telemetry (no traces, no custom
  metrics, logs only). Use this skill to find the instrumentation gaps that leave
  Omni's automatic discovery and DevOps Agent investigations blind, so
  application-centric observability rests on real telemetry. It reasons over
  CloudWatch-native reads plus Omni-surfaced context; it recommends
  instrumentation, it does not change services or collectors.
version: "1.0.0"
last_updated: "2026-09-12"
---

# OpenTelemetry Instrumentation Coverage

Use this skill to check that the services CloudWatch Omni should see are actually
emitting telemetry. Omni is OTLP-native: it auto-discovers services and maps
dependencies from the traces, metrics, and logs they emit, so its discovery is
only as good as instrumentation. The gap this skill finds is the service that
appears in the topology or resource inventory but emits no traces, no custom
metrics, or logs only - a blind spot for Omni and for DevOps Agent
investigations that looks present but is shallow.

## Sources

Read-only. CloudWatch Omni does not expose a confirmed dedicated use_aws action
set today, so treat the Omni-specific reads as data the platform surfaces and
lean on the CloudWatch-native signals below; do not assume an Omni API that has
not been verified.

- use_aws for the CloudWatch-native inventory Omni builds on: Application Signals
  services, X-Ray or OTel-backed trace presence, and the resource inventory from
  tags and AWS Config used for discovery.
- query_cloudwatch_metrics for custom or OTel-backed metric emission per service,
  beyond default infrastructure metrics.
- query_cloudwatch_logs for structured log emission, separating a logs-only
  service from a fully instrumented one.
- The Omni topology and telemetry context the platform surfaces, where available.

## Method

1. Build the service inventory: the services Omni would discover from telemetry
   and AWS Config (Application Signals services, tagged workloads, topology nodes).
2. Classify trace emission: for each service, whether Application Signals or
   X-Ray/OTel-backed traces are present, or none.
3. Classify metric emission: whether the service publishes custom or OTel-backed
   metrics over OTLP or the CloudWatch OTel/ADOT path, or only default metrics.
4. Classify log emission: whether structured logs are shipped, and flag a
   logs-only service as partially instrumented rather than fully covered.
5. Derive the per-service telemetry profile and flag gaps: no traces, no custom
   metrics, logs only, or nothing at all - each a blind spot for Omni discovery.
6. Rank gaps by criticality: uninstrumented production services first, then
   partial production, then non-production; recommend the specific instrumentation
   action per gap (add ADOT/OTel tracing, publish OTel metrics, enable structured
   logs) for a human to apply; do not change services or collectors.

## MCP augmentation

CloudWatch Omni is reached through its own workspace and the blog points to the
AWS MCP Server for Omni APIs, documentation, and regional availability. Where a
CloudWatch or Omni MCP server is available, connect it to the Agent Space to read
topology and telemetry context directly, and use the AWS Documentation MCP Server
for current OpenTelemetry and Omni guidance. Use any MCP in addition to the
CloudWatch-native use_aws reads, never instead of them, and do not assume an Omni
API that the MCP does not actually expose. AWS MCP server names and availability
evolve; verify before relying on one.

## Output

Produce a coverage report: the discovered-service inventory; a per-service table
of traces, custom metrics, logs, and the telemetry profile; the gaps ranked by
criticality (uninstrumented, partial, logs-only, non-production); and a
recommended instrumentation action per gap. State that the skill recommends
instrumentation and does not change services or collectors. Reference services
and accounts by identifier.
