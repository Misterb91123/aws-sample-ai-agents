---
name: dns-resolution-troubleshooter
agent_type: "Incident RCA"
description: Diagnoses DNS resolution failures and inconsistencies in AWS environments
  including Route53 hosted zones, VPC DNS settings, private hosted zones, resolver
  rules, and split-horizon configurations. Use this skill when services cannot
  resolve hostnames, DNS propagation is incomplete, or when private/public DNS
  responses are inconsistent.
version: "1.0.0"
last_updated: "2026-08-14"
---

# DNS Resolution Troubleshooter

Use this skill to diagnose and resolve DNS resolution issues in AWS
networking environments.

## When to Activate

- Service cannot resolve a hostname (NXDOMAIN, SERVFAIL, timeout).
- DNS returns the wrong IP address (stale record, wrong zone).
- Intermittent DNS failures from specific resources.
- Cross-VPC or cross-account DNS resolution not working.
- Private hosted zone records not resolving for expected resources.
- DNS propagation delay after record change.

## Step 1: Identify the Failure Mode

Characterize the DNS problem:

| Symptom | Likely Cause |
|---------|-------------|
| NXDOMAIN (name not found) | Record doesn't exist, wrong hosted zone, zone not associated |
| SERVFAIL | Resolver error, DNSSEC validation failure, upstream issue |
| Timeout | Resolver unreachable, security group blocking UDP/53 |
| Wrong IP returned | Stale cache, wrong hosted zone priority, split-horizon issue |
| Works from some instances, not others | VPC association, resolver rule scope, DHCP options |
| Works intermittently | TTL caching, resolver flapping, partial propagation |

## Step 2: Verify DNS Infrastructure

Check the DNS resolution path:

1. **VPC DNS Settings:**
   - `enableDnsSupport`: Must be `true` for VPC DNS resolver (AmazonProvidedDNS).
   - `enableDnsHostnames`: Must be `true` for EC2 instances to receive public DNS names.
   - DHCP options set: Verify DNS server settings (default = AmazonProvidedDNS at VPC+2 address).

2. **Route53 Resolver:**
   - Inbound endpoints: For on-premises -> AWS DNS resolution.
   - Outbound endpoints: For AWS -> on-premises DNS resolution.
   - Resolver rules: Forwarding rules for specific domains.
   - Rule associations: Which VPCs the rules are shared with.

3. **Security Groups / NACLs:**
   - Resolver endpoints need UDP/TCP port 53 inbound/outbound.
   - NACLs must allow UDP 53 and TCP 53 (for large responses).
   - Ephemeral port range (1024-65535) must be open for return traffic.

## Step 3: Diagnose Private Hosted Zone Issues

Private hosted zones are the most common DNS problem source:

1. **Zone-VPC Association:**
   - Is the private hosted zone associated with the VPC making the query?
   - Cross-account? Use RAM (Resource Access Manager) to share or manually authorize.
   - Check: `aws route53 get-hosted-zone` -> list VPC associations.

2. **Record existence:**
   - Does the record actually exist in the zone?
   - Is it the correct record type (A, AAAA, CNAME, ALIAS)?
   - Check for typos in the record name.

3. **Zone overlap / priority:**
   - If multiple zones match a query, Route53 uses the most specific zone.
   - Example: `api.example.com` in zone `example.com` AND zone `api.example.com` -> the `api.example.com` zone wins.
   - If the more specific zone doesn't have the record -> NXDOMAIN (doesn't fall back to less specific zone).

4. **Public vs Private resolution:**
   - Private hosted zone takes priority over public for associated VPCs.
   - If private zone exists but record is only in public zone -> NXDOMAIN from within the VPC.

## Step 4: Diagnose Cross-VPC DNS Issues

For services in different VPCs needing to resolve each other:

1. **VPC Peering DNS:**
   - VPC peering enables network connectivity but NOT DNS resolution by default.
   - Must enable "DNS resolution from accepter/requester VPC" on the peering connection.
   - Only resolves public DNS names to private IPs across the peering.

2. **Private Hosted Zone + Multiple VPC Association:**
   - Associate the private hosted zone with all VPCs that need to resolve it.
   - For cross-account: authorize the VPC first, then create association.

3. **Route53 Resolver Rules (RAM shared):**
   - Create resolver forwarding rules and share via RAM.
   - Associate rules with VPCs in other accounts.

4. **Transit Gateway DNS:**
   - Centralized DNS via Transit Gateway + shared resolver endpoints.
   - Hub-and-spoke model: all DNS resolves through central VPC.

## Step 5: Diagnose Propagation Issues

If DNS was recently changed but old values persist:

1. **TTL:** Check the TTL of the record that was changed.
   - Resolvers cache for the TTL duration.
   - Local OS caches (varies: 30s-5min typically).
   - Application-level DNS caching (JVM caches DNS for 30s by default, some forever).

2. **Negative caching:** NXDOMAIN responses are also cached (SOA record minimum TTL).
   - If you queried before the record existed, the NXDOMAIN is cached.

3. **NS record delegation:** For subdomain delegation, parent zone NS records must be correct.

4. **Route53 health checks + failover:**
   - If health check is failing, failover record won't be returned.
   - Check health check status in Route53 console.

## Step 6: Diagnose Resolver Rule Issues

For custom forwarding (hybrid DNS):

1. **Rule matching:** Rules match by longest suffix. `corp.example.com` is more specific than `example.com`.
2. **Forwarding targets:** Are the target DNS servers reachable from the resolver endpoint?
3. **Endpoint subnet placement:** Is the resolver endpoint in a subnet that can route to the target?
4. **Target server responsiveness:** Is the on-premises DNS server responding within timeout?
5. **Rule association:** Is the rule associated with the correct VPC(s)?

## Step 7: Common Fixes

| Problem | Fix |
|---------|-----|
| Private zone not resolving | Associate zone with VPC; verify record exists |
| Cross-account resolution failing | Authorize VPC association via CLI; create association |
| On-prem names not resolving | Create outbound resolver endpoint + forwarding rule |
| AWS names not resolving from on-prem | Create inbound resolver endpoint; configure on-prem forwarder |
| Application caching stale DNS | Set JVM flag `-Dsun.net.inetaddr.ttl=30`; use DNS-aware connection pools |
| DNSSEC validation failures | Check DS records in parent zone; validate DNSSEC chain |
| Split-horizon inconsistency | Ensure private zone has all records that public zone has (for internal access) |

## Output

Produce a DNS troubleshooting report:
1. **Problem Summary**: Query, expected result, actual result, affected resources.
2. **Resolution Path Traced**: VPC -> Resolver -> Zone -> Record (showing where it breaks).
3. **Root Cause**: Specific misconfiguration identified.
4. **Fix Applied/Recommended**: Configuration change to resolve the issue.
5. **Verification**: Confirmation that resolution now works correctly.
6. **Prevention**: Monitoring or automation to catch similar issues early.