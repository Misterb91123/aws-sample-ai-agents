---
name: network-anomaly-investigation
agent_type: "Incident RCA"
description: Investigates anomalous network traffic patterns detected in VPC Flow
  Logs, WAF logs, or network monitoring tools. Use this skill when unusual traffic
  patterns are detected such as data exfiltration indicators, unexpected cross-region
  traffic, lateral movement, or communication with known malicious endpoints.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Network Anomaly Investigation

Use this skill to investigate unusual network traffic patterns that may
indicate security threats, data exfiltration, or infrastructure misconfiguration.

## When to Activate

- VPC Flow Logs show unusual traffic patterns (volume spikes, new destinations).
- WAF blocks surge or unusual request patterns detected.
- GuardDuty reports network-based findings.
- Unexpected cross-account or cross-region traffic observed.
- Data transfer costs spike unexpectedly (possible exfiltration indicator).

## Step 1: Characterize the Anomaly

Determine what is abnormal:
1. **Volume anomaly**: Significantly more traffic than baseline.
2. **Destination anomaly**: Traffic to IP addresses or regions never seen before.
3. **Port anomaly**: Traffic on unusual ports (crypto mining: 3333, 4444, 8333).
4. **Protocol anomaly**: Unexpected protocols (DNS tunneling, ICMP data channels).
5. **Timing anomaly**: Traffic at unusual hours (3 AM data transfers).
6. **Pattern anomaly**: Regular beaconing intervals (command & control).

## Step 2: Analyze VPC Flow Logs

Query VPC Flow Logs for the anomalous traffic:

**Key fields to examine:**
- Source/destination IP and port
- Bytes transferred (volume)
- Packets count
- Action (ACCEPT/REJECT) - rejected traffic may indicate scanning
- Direction (ingress/egress)

**Investigation queries:**

1. Top talkers (highest data volume):
   - Which internal IPs are sending the most data externally?
   - Is this consistent with their service function?

2. New destinations (never-before-seen):
   - Filter for destination IPs not seen in the previous 30 days.
   - Cross-reference with threat intelligence feeds.

3. Port analysis:
   - What ports are being used for external communication?
   - Are there connections on non-standard ports?

4. Beaconing detection:
   - Look for regular intervals (every 60s, 300s) to the same destination.
   - C2 beacons often have consistent packet sizes.

## Step 3: Identify the Source

Determine which resource is generating the traffic:
1. Map the source IP to a specific ENI (via VPC Flow Logs or EC2 describe).
2. Identify the resource attached to the ENI (EC2, Lambda, ECS task, NAT Gateway).
3. Determine the resource's purpose and expected traffic pattern.
4. Check if the resource was recently modified (new deployment, configuration change).

## Step 4: Assess Threat Indicators

Check for specific threat patterns:

**Data Exfiltration Indicators:**
- Large outbound transfers to external IPs (> 1GB unusual for the service)
- DNS queries with encoded data in subdomain labels (DNS tunneling)
- HTTPS connections to blob storage services (pastebin, transfer.sh, S3 in other accounts)
- Traffic to Tor exit nodes or known proxy services

**Command & Control Indicators:**
- Regular beaconing (consistent interval connections)
- Communication with IPs on threat intelligence blocklists
- Encrypted traffic on non-standard ports
- Domain generation algorithm (DGA) patterns in DNS queries

**Lateral Movement Indicators:**
- Internal scanning (one host connecting to many internal IPs on same port)
- SMB/RDP connections between workloads that don't normally communicate
- SSH connections from non-bastion hosts

**Cryptomining Indicators:**
- Connections to known mining pools (ports 3333, 4444, 8333, 14444)
- Sustained high CPU with corresponding network to mining IPs
- Stratum protocol patterns in traffic

## Step 5: Correlate with Other Data Sources

Cross-reference network anomaly with:
1. CloudTrail - any API calls from the source around the same time?
2. GuardDuty - any related findings for the same resource?
3. CloudWatch metrics - CPU/memory spike coinciding with traffic anomaly?
4. Application logs - any unusual application behavior?
5. Recent deployments - did a deployment introduce the anomaly?
6. DNS logs (Route53 resolver) - unusual DNS queries from the resource?

## Step 6: Determine Verdict

| Verdict | Criteria |
|---------|----------|
| **Confirmed Threat** | Malicious indicators confirmed (known bad IP, C2 pattern, exfiltration) |
| **Suspicious - Investigate Further** | Anomalous but not confirmed malicious (needs deeper analysis) |
| **Misconfiguration** | Traffic caused by misconfigured service (wrong endpoint, debug mode left on) |
| **Expected Behavior** | Traffic is normal for the service (new feature, batch job, backup) |

## Step 7: Response Actions

**If Confirmed Threat:**
1. Isolate the resource (modify security groups to deny all outbound except logging).
2. Capture network evidence (packet capture if available, flow log export).
3. Do NOT terminate the instance - preserve for forensics.
4. Block the external IP/CIDR at WAF and NACL level.
5. Escalate to security incident response.
6. Check if other instances communicate with the same external IP.

**If Misconfiguration:**
1. Identify the misconfiguration and correct it.
2. Document the root cause.
3. Add monitoring to detect recurrence.

## Output

Provide an investigation report:
1. Anomaly characterization (type, volume, duration)
2. Source identification (resource, owner, purpose)
3. Threat assessment (indicators found or ruled out)
4. Verdict: confirmed threat / suspicious / benign / misconfiguration
5. Recommended actions based on verdict
6. Network forensics evidence summary