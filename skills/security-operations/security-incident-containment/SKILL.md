---
name: security-incident-containment
agent_type: "Incident Mitigation"
description: Provides structured containment procedures for active security incidents
  to limit damage while preserving forensic evidence. Use this skill when a security
  incident is confirmed and immediate containment is required to stop ongoing
  unauthorized access, data exfiltration, or lateral movement.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Security Incident Containment

Use this skill when a security incident is confirmed and containment actions
are needed to stop the threat while preserving evidence for investigation.

## When to Activate

- A security incident is confirmed (GuardDuty, manual investigation, or alert).
- Active unauthorized access is detected.
- Data exfiltration is in progress or suspected.
- Malware or unauthorized software is running on a resource.
- Lateral movement between resources is detected.

## Containment Principles

1. **Stop the bleeding first** - limit ongoing damage before investigating fully.
2. **Preserve evidence** - do not destroy or terminate resources that contain forensic data.
3. **Minimize business impact** - isolate the compromised resource, not the entire environment.
4. **Document everything** - log every action taken with timestamps.
5. **Assume wider compromise** - the visible incident may be the tip of the iceberg.

## Step 1: Confirm Scope and Type

Before containment, confirm:
- What is compromised? (EC2 instance, IAM credential, container, S3 bucket)
- How is it compromised? (credential theft, vulnerability exploit, insider threat)
- Is the attack ongoing or historical?
- What's the current blast radius?

## Step 2: Containment by Resource Type

### EC2 Instance Compromise

**Isolate (do NOT terminate):**
1. Create a new security group with NO inbound/outbound rules (isolation SG).
2. Replace ALL security groups on the instance with the isolation SG.
3. This immediately cuts all network connectivity while preserving the instance.
4. Remove the instance from any Auto Scaling groups (set to standby).
5. Detach from load balancer target groups.

**Preserve Evidence:**
1. Create EBS snapshots of all attached volumes.
2. Capture instance metadata (describe-instances output).
3. If possible, create a memory dump before the instance is fully isolated.
4. Enable termination protection to prevent accidental cleanup.

**Do NOT:**
- Terminate the instance (destroys volatile memory evidence).
- Reboot the instance (may trigger attacker's cleanup scripts).
- Run commands on the instance (may alert the attacker or alter evidence).

### IAM Credential Compromise

**Contain immediately:**
1. Attach an explicit deny-all policy to the user/role:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*"
  }]
}
```
2. Deactivate access keys (do NOT delete - needed for CloudTrail correlation).
3. Invalidate active sessions by adding a condition denying tokens issued before now.
4. If a role: update the trust policy to deny assume-role.
5. Disable console access if applicable.

**Preserve Evidence:**
1. Export CloudTrail events for the compromised credential (full history).
2. Document all policies attached at time of compromise.
3. Record all resources the credential had access to.

### Container/EKS Compromise

**Isolate:**
1. Apply a deny-all NetworkPolicy to the affected pod.
2. Scale the deployment to 0 (stops the container but preserves the pod spec).
3. If the node is compromised: cordon and drain the node.
4. Check if the service account token was exfiltrated.

**Preserve Evidence:**
1. Capture container logs before termination.
2. Export the running container's filesystem if possible.
3. Record the pod spec, image SHA, and environment variables.

### S3 Bucket Compromise

**Contain:**
1. Apply a bucket policy denying all access except from your investigation role.
2. Disable public access settings.
3. Revoke any pre-signed URLs by rotating the signing credentials.
4. Enable versioning if not already enabled (protects against deletion).

**Preserve Evidence:**
1. Enable S3 access logging if not already enabled.
2. Export CloudTrail data events for the bucket.
3. Document the current bucket policy and ACLs.

## Step 3: Block the Attacker

After isolating the target, block the attacker's access paths:
1. Block attacker IPs at WAF level (broad protection).
2. Block attacker IPs at NACL level (VPC-wide).
3. Revoke any remaining active sessions.
4. Rotate secrets that the compromised resource had access to.
5. If credentials were used from the attacker's infrastructure, consider blocking their ASN.

## Step 4: Check for Persistence

Attackers often establish persistence mechanisms:
1. Check for new IAM users, roles, or access keys created.
2. Check for modified Lambda functions (backdoor in code).
3. Check for new EC2 instances or security group changes.
4. Check for modified CloudFormation stacks.
5. Check for new EventBridge rules or scheduled actions.
6. Check for new S3 bucket policies granting external access.

**If persistence found**: contain each persistence mechanism using the same procedures above.

## Step 5: Assess and Communicate

After initial containment:
1. Confirm containment is holding (no new unauthorized activity).
2. Assess business impact of the containment actions.
3. Communicate to stakeholders:
   - What was compromised
   - Containment actions taken
   - Business services affected by containment
   - Next steps (investigation, eradication, recovery)
4. Determine if regulatory notification is required (data breach).

## Step 6: Transition to Investigation

After containment is stable:
1. Hand off to forensics/investigation team with evidence inventory.
2. Maintain isolation until investigation completes.
3. Do not restore service from compromised resources - rebuild from clean sources.
4. Plan recovery using known-good backups or fresh deployments.

## Output

Provide a containment summary:
1. Containment actions taken with timestamps
2. Evidence preserved (snapshots, logs, exports)
3. Resources currently isolated
4. Business impact of containment
5. Persistence mechanisms found (if any)
6. Recommended next steps for investigation and recovery