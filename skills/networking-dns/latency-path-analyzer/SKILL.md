---
name: latency-path-analyzer
agent_type: "Incident RCA"
description: Analyzes network latency along the path between source and destination
  to identify where delays are introduced. Use this skill when investigating
  unexplained latency between services, comparing expected vs actual network
  performance, or when diagnosing whether latency is network-layer, application-layer,
  or infrastructure-layer (NAT, TGW, VPN).
version: "1.0.0"
last_updated: "2026-08-14"
---

# Latency Path Analyzer

Use this skill to break down network latency between two points and identify
where delay is being introduced along the path.

## When to Activate

- Service-to-service latency higher than expected.
- Cross-region or cross-AZ communication slower than benchmarks.
- VPN or Direct Connect latency exceeds SLA.
- Investigating whether latency is network or application.
- New network component added (NAT, TGW, proxy) and latency increased.

## Step 1: Establish Expected Latency Baselines

Know what's normal for each network segment:

| Path Type | Expected Latency |
|-----------|-----------------|
| Same AZ (within VPC) | < 0.5ms |
| Cross-AZ (same region) | 1-2ms |
| Cross-region (continental) | 10-70ms (depends on distance) |
| Cross-region (intercontinental) | 100-300ms |
| VPN over internet | 20-100ms (variable, depends on ISP) |
| Direct Connect | 5-50ms (depends on distance, consistent) |
| NAT Gateway overhead | 0.1-0.5ms added |
| Transit Gateway overhead | 0.5-1ms added |
| VPC Peering overhead | ~0ms (negligible) |
| Proxy/middlebox | 1-10ms added per hop |

## Step 2: Map the Network Path

Trace the complete path from source to destination:

```
[Source Instance]
-> Security Group (no latency, just allow/deny)
-> Subnet NACL (no latency)
-> Route Table decision
-> [NAT Gateway] (if outbound internet or cross-VPC via NAT)
-> [VPC Peering / Transit Gateway / VPN Gateway]
-> [Internet / AWS Backbone / Direct Connect]
-> [Destination NAT / LB / Endpoint]
-> Destination Security Group
-> [Destination Instance]
```

Identify every network component in the path that adds latency.

## Step 3: Measure Segment by Segment

Break down latency at each segment:

1. **Application-level measurement:**
   - Client-perceived latency (total round-trip including processing).
   - Server-side processing time (from application metrics).
   - Network latency = client perceived - server processing time.

2. **Network-level measurement:**
   - TCP handshake time (SYN -> SYN-ACK): pure network RTT.
   - TLS handshake time: adds 1-2 RTTs.
   - VPC Flow Logs: no direct latency, but can show packet counts and timing.
   - CloudWatch metrics: NATGateway, TransitGateway, VPN connection latency.

3. **Per-hop measurement:**
   - If possible, test source -> each intermediate hop:
     - Source -> NAT Gateway: test by pinging a target through NAT.
     - Source -> TGW: test by reaching a target in another VPC via TGW.
     - Source -> VPN endpoint: test with target on other side of VPN.

## Step 4: Identify Latency Contributors

Common sources of unexpected latency:

### NAT Gateway Latency
- Expected: < 0.5ms added latency.
- If higher: NAT Gateway is processing excessive traffic (check BytesProcessed).
- Fix: Ensure NAT Gateway is in the same AZ as the source (cross-AZ NAT adds 1-2ms).

### Transit Gateway Latency
- Expected: ~0.5-1ms per TGW hop.
- Multiple TGW hops (inter-region peering): accumulates.
- Fix: Direct peering for latency-sensitive paths, avoid unnecessary TGW hops.

### VPN Latency
- Expected: internet RTT + encryption overhead (5-20ms added).
- If higher: internet path congestion, VPN tunnel renegotiation.
- Fix: Direct Connect for consistent low latency. Redundant VPN tunnels.

### DNS Resolution Latency
- First request to a new hostname includes DNS resolution (50-200ms).
- Subsequent requests use cache (until TTL expires).
- Fix: DNS caching, connection pooling (reuse connections, skip DNS on subsequent calls).

### TLS Handshake Latency
- Full handshake: 2 RTTs (ClientHello -> ServerHello -> Finished).
- Session resumption: 1 RTT.
- Fix: Enable TLS session reuse, connection keep-alive, TLS 1.3 (1-RTT handshake).

### Connection Pool Exhaustion
- When all pooled connections are busy, new requests wait for a free connection.
- Appears as latency spike, but it's actually queuing.
- Fix: Increase pool size, reduce connection hold time, add circuit breaker.

### Cross-AZ Communication
- 1-2ms per cross-AZ hop.
- If service makes 10 sequential cross-AZ calls = 10-20ms added.
- Fix: AZ-affinity for internal service communication, co-locate communicating services.

## Step 5: Analyze Latency Patterns

Look for patterns in when latency occurs:

| Pattern | Likely Cause |
|---------|-------------|
| Constant high latency | Structural issue (wrong path, unnecessary hops) |
| Periodic spikes (every N minutes) | Background jobs, GC pauses, health checks causing interference |
| Latency increases with traffic | Saturation (bandwidth, connection pool, CPU) |
| Latency spikes at specific times | Shared infrastructure contention (noisy neighbor) |
| First request slow, subsequent fast | Cold start (DNS, TLS, connection establishment) |
| Gradually increasing over days | Resource exhaustion (memory leak, connection leak) |

## Step 6: Optimize the Path

Based on findings, recommend optimizations:

**Reduce hops:**
- Use VPC endpoints (avoids NAT Gateway for AWS service calls).
- Direct VPC peering instead of TGW for latency-sensitive pairs.
- Co-locate in same AZ for tightest latency requirement.

**Reduce per-hop latency:**
- Ensure NAT Gateway is in same AZ as source.
- Use Direct Connect instead of VPN for consistent latency.
- Enable TCP keep-alive to avoid repeated connection setup.
- Use connection pooling with warm connections.

**Reduce application-layer overhead:**
- HTTP/2 or gRPC multiplexing (avoid head-of-line blocking).
- Compress payloads (less data = less network time).
- Batch requests (fewer round trips).
- Pre-fetch data (overlap network time with processing).

## Output

Produce a latency path analysis:
1. **End-to-End Latency**: Measured total RTT vs expected baseline.
2. **Path Diagram**: Visual showing each hop with measured/expected latency per segment.
3. **Latency Breakdown Table**: Segment, expected latency, measured latency, delta, component.
4. **Bottleneck Identified**: The segment contributing most excess latency.
5. **Latency Pattern Analysis**: When/how latency varies (constant, periodic, traffic-correlated).
6. **Optimization Recommendations**: Path changes or configuration fixes with expected improvement.
7. **Before/After Projections**: Expected total latency after recommended optimizations.