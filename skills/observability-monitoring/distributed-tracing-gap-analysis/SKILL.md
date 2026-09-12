---
name: distributed-tracing-gap-analysis
agent_type: "Generic"
description: Use this skill when finding gaps in distributed tracing coverage across a microservices architecture. It triggers on incomplete service maps, traces that stop partway through a request path, missing subsegments, or broken correlation between logs and traces, and it guides detection of uninstrumented services, broken context propagation, and sampling blind spots.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Distributed Tracing Gap Analysis

This skill finds where distributed tracing coverage is incomplete across a microservices architecture so that an end-to-end request can be followed without holes. It examines instrumentation, context propagation, subsegment detail, correlation, and sampling.

## When to Activate

- The X-Ray or OpenTelemetry service map is missing services known to be in the request path.
- Traces stop partway through a request (a downstream call has no child trace).
- Subsegments for database, cache, or external HTTP calls are missing.
- Logs cannot be correlated to traces because there is no shared identifier.
- Some services never appear in traces (suspected sampling or instrumentation gap).

## Step 1: Build the expected service map

- Enumerate the services on the critical request paths from architecture docs and dependency data, and list the expected calls between them (synchronous HTTP or gRPC, queue or stream, and datastore access).
- Compare the expected map against the actual X-Ray service map or the tracing backend's map. Nodes present in the expected map but absent from the actual map are coverage gaps.

## Step 2: Find uninstrumented services

- For each missing node, determine whether the service has a tracing SDK or the OpenTelemetry or X-Ray auto-instrumentation agent installed and configured.
- Confirm the service sends spans to a collector (the X-Ray daemon, the CloudWatch agent, or an OpenTelemetry collector) and that the endpoint and permissions are correct.
- Note services behind a proxy or gateway that are represented only as a client node; they need their own instrumentation to appear as a distinct service.

## Step 3: Detect broken context propagation

- A trace breaks when the trace context header is not forwarded across a hop. For X-Ray this is the X-Amzn-Trace-Id header; for OpenTelemetry and W3C it is the traceparent header.
- Inspect each boundary where a trace stops: HTTP clients that strip headers, message queues where the trace context is not injected into and extracted from the message attributes, and async workers that start a fresh trace instead of continuing the parent.
- Confirm that both the sending side injects and the receiving side extracts the context, since one missing half breaks propagation.

## Step 4: Find missing subsegments

- Within an instrumented service, confirm outbound calls create subsegments: database queries, cache calls, external HTTP requests, and AWS SDK calls should each appear as a subsegment with timing.
- Missing subsegments usually mean the client library is not wrapped by instrumentation (for example a raw socket client, or an SDK version the auto-instrumentation does not patch). Add manual subsegments for those calls.

## Step 5: Verify correlation identifiers

- Confirm each service logs the trace ID (and span ID) so logs can be joined to traces. Without a shared correlation ID, a trace cannot be tied to its log lines.
- Standardize the correlation field name across services and confirm it flows through the same propagation headers as the trace context.

## Step 6: Rule out sampling blind spots

- A service can be fully instrumented yet rarely appear because sampling records too few of its requests. Review the sampling rules for the paths that traverse the missing service.
- Distinguish a true instrumentation gap (the service never emits spans) from a sampling gap (the service emits spans but they are usually not recorded) by temporarily raising sampling on the relevant path and checking whether the node appears.

## Output

Produce a Tracing Gap Analysis Report containing: the expected-versus-actual service map with each missing node, a classification of each gap (uninstrumented service, broken context propagation at a named boundary, missing subsegments for a named client, missing correlation ID, or sampling blind spot), the specific fix per gap (install or configure instrumentation, inject and extract context on the boundary, add manual subsegments, add trace-ID logging, or adjust sampling), and a prioritized order to close the gaps for full end-to-end coverage on the critical paths.