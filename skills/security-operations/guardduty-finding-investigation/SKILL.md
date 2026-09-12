---
name: guardduty-finding-investigation
agent_type: "Incident RCA"
description: Investigates Amazon GuardDuty findings by analyzing the threat type,
  affected resources, and network activity to determine if the finding represents
  a real security threat or a false positive. Use this skill when GuardDuty
  generates findings that require investigation and response determination.
version: "1.0.0"
last_updated: "2026-08-14"
---

# GuardDuty Finding Investigation

Use this skill to investigate GuardDuty findings systematically, determine
their validity, assess impact, and recommend response actions.

## When to Activate

- A new GuardDuty finding is generated (high or critical severity).
- Multiple findings correlate to the same resource or actor.
- Security team requests investigation of a GuardDuty alert.
- Periodic review of unresolved GuardDuty findings.

## Step 1: Retrieve Finding Details

For each finding, collect:
1. Finding type (e.g., `UnauthorizedAccess:IAMUser/MaliciousIPCaller`)
2. Severity (Low 1-3, Medium 4-6, High 7-8, Critical 9-10)
3. Affected resource (EC2 instance, IAM user, S3 bucket, EKS cluster)
4. Actor details (IP address, user agent, API calls)
5. Timing (first seen, last seen, count)
6. Region and account

## Step 2: Classify the Finding Type

**Reconnaissance:**
- `Recon:EC2/PortProbeUnprotectedPort` - port scanning detected
- `Recon:EC2/Portscan` - instance performing port scans
- `Discovery:S3/MaliciousIPCaller` - S3 enumeration from suspicious IP

**Credential Compromise:**
- `UnauthorizedAccess:IAMUser/MaliciousIPCaller` - API calls from known bad IP
- `UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B` - login from unusual location
- `Persistence:IAMUser/AnomalousBehavior` - unusual IAM activity

**Instance Compromise:**
- `CryptoCurrency:EC2/BitcoinTool.B` - crypto mining detected
- `Backdoor:EC2/DenialOfService` - instance participating in DDoS
- `Trojan:EC2/DNSDataExfiltration` - DNS-based data exfiltration

**Data Exfiltration:**
- `Exfiltration:S3/ObjectRead.Unusual` - unusual S3 read patterns
- `Exfiltration:S3/MaliciousIPCaller` - S3 access from malicious IP

**Container/Kubernetes:**
- `PrivilegeEscalation:Kubernetes/PrivilegedContainer` - privileged container launched
- `Execution:Kubernetes/ExecInKubeSystemPod` - exec into kube-system pod

## Step 3: Investigate the Actor

Determine who or what triggered the finding:

**For IP-based findings:**
1. Check if the IP belongs to your organization (VPN, office, CI/CD).
2. Query threat intelligence: is this IP known malicious?
3. Check geolocation: is the location consistent with expected access patterns?
4. Check if this IP has triggered other findings across accounts.

**For IAM user findings:**
1. Verify the user is a real person (not a service account acting unexpectedly).
2. Check CloudTrail for the user's recent activity pattern.
3. Determine if the activity is consistent with their role.
4. Check if MFA was used for the session.

**For EC2 instance findings:**
1. Check the instance's purpose (web server, bastion, batch processor).
2. Review recent changes: new deployments, configuration changes.
3. Check outbound network connections (VPC Flow Logs).
4. Verify the software running (is a new process present?).

## Step 4: Determine Validity

Classify the finding:

| Verdict | Criteria |
|---------|----------|
| **True Positive** | Activity is confirmed unauthorized or malicious |
| **True Positive - Benign** | Activity is real but expected/authorized (penetration test, legitimate tool) |
| **False Positive** | Finding triggered by normal business activity |
| **Needs More Investigation** | Insufficient data to determine - gather more |

**Common False Positive Patterns:**
- Security scanning tools (Nessus, Qualys) triggering port scan findings
- CI/CD systems accessing resources from varying IPs
- Legitimate crypto operations (blockchain services) triggering crypto findings
- Third-party SaaS integrations appearing as unusual access

## Step 5: Response Actions

**For True Positives (confirmed threats):**

Severity Critical/High:
1. Isolate the affected resource immediately (modify security groups to deny all).
2. Disable compromised IAM credentials.
3. Escalate to security incident process.
4. Preserve evidence (snapshots, memory dumps, logs).
5. Begin containment and eradication.

Severity Medium:
1. Investigate further within 4 hours.
2. Apply restrictive measures if risk is growing.
3. Schedule remediation within 24 hours.

Severity Low:
1. Document the finding.
2. Schedule review in next security review cycle.
3. Assess if pattern indicates early-stage attack.

**For False Positives:**
1. Document why it's a false positive.
2. Create a suppression rule if it will recur.
3. Archive the finding.

## Step 6: Check for Related Activity

A single finding may indicate broader compromise:
1. Check for other findings on the same resource in the past 30 days.
2. Check for findings from the same actor (IP, user) across all accounts.
3. Check CloudTrail for related API activity not caught by GuardDuty.
4. Check VPC Flow Logs for unusual network patterns from the resource.

## Output

Provide an investigation summary:
1. Finding classification: True Positive / False Positive / Requires Escalation
2. Actor identification and threat assessment
3. Impact assessment: what was accessed/modified
4. Recommended immediate actions
5. Suppression rule recommendation (if false positive)
6. Preventive measures to reduce future exposure