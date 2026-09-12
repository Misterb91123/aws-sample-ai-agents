---
name: exposed-credentials-response
agent_type: "Incident Mitigation"
description: Provides an immediate response procedure when credentials are found
  exposed in code repositories, logs, or public locations. Use this skill when
  AWS access keys, database passwords, API tokens, or other secrets are discovered
  in unauthorized locations and need immediate containment and rotation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Exposed Credentials Response

Use this skill when credentials are found exposed and need immediate
containment to prevent unauthorized access.

## When to Activate

- AWS access keys found in a public GitHub repository.
- Secrets detected in CloudWatch Logs or application output.
- AWS Health notification for exposed credentials.
- GuardDuty finding indicating credential compromise.
- Secret scanning tool (GitHub, GitLeaks, TruffleHog) flags an exposure.

## Step 1: Identify the Exposure

Gather details about the exposed credential:
1. **Credential type**: AWS access key, database password, API token, SSH key, TLS private key.
2. **Where found**: Public repo, internal repo, logs, S3 bucket, error message.
3. **Exposure duration**: How long has it been exposed? (commit date, log timestamp)
4. **Scope**: What does this credential provide access to?
5. **Public or internal**: Is the exposure internet-accessible?

## Step 2: Immediate Containment (Within Minutes)

**Priority 1 - Revoke or rotate immediately:**

For AWS Access Keys:
1. Identify the IAM user/role associated with the key.
2. Deactivate the access key immediately: `aws iam update-access-key --status Inactive`.
3. Do NOT delete yet - you need it for forensics.
4. Check if other access keys exist for this user.

For Database Credentials:
1. Rotate the password immediately in the database.
2. Update the secret in Secrets Manager / Parameter Store.
3. Restart application instances to pick up new credentials.

For API Tokens / OAuth:
1. Revoke the token at the issuing service.
2. Generate a new token.
3. Update all consumers.

For SSH Keys:
1. Remove the public key from all authorized_keys files.
2. Generate a new keypair.
3. Distribute new public key to required hosts.

## Step 3: Assess Unauthorized Usage

Determine if the credential was used maliciously:

For AWS Access Keys:
1. Check CloudTrail for API calls made with the key ID after the exposure timestamp.
2. Look for unusual activity: new resources created, data accessed, IAM changes.
3. Check regions you don't normally operate in.
4. Look for credential usage from unexpected IP addresses.

For Database Credentials:
1. Check database audit logs for connections after exposure.
2. Look for unusual queries: bulk data exports, schema changes, privilege escalation.

For any credential:
1. Compare activity patterns before and after exposure date.
2. Flag any activity from IP addresses outside your known ranges.

## Step 4: Contain Blast Radius

If unauthorized usage is detected:
1. Immediately escalate to SEV1 security incident.
2. If IAM user: attach a deny-all policy to prevent further actions.
3. If resources were created by the attacker: document but do not delete (forensics).
4. If data was accessed: begin data breach assessment.
5. If the compromised credential had broad permissions: assume worst-case access.

## Step 5: Remove the Exposure

1. **Git repository**: Force-push to remove the commit (rewriting history). Note: credential is still in git reflog and may be cached by GitHub/mirrors.
2. **Logs**: Purge the log entries containing credentials.
3. **S3 bucket**: Remove the file or add appropriate access controls.
4. **Docker image**: Remove and republish without credentials.
5. **Public cache**: Request removal from GitHub cache, Google cache if applicable.

**Important**: Removal does not replace rotation. Always assume the credential was captured.

## Step 6: Rotate and Restore Service

1. Create new credentials with equivalent permissions.
2. Update all systems using the old credential:
   - Secrets Manager / Parameter Store
   - Environment variables
   - Configuration files
   - CI/CD pipeline secrets
3. Deploy updated configuration to all consumers.
4. Verify service health after rotation.
5. Delete the old (deactivated) credential after confirming rotation success.

## Step 7: Document and Prevent Recurrence

1. Document the full incident timeline.
2. Identify how the credential was exposed (root cause):
   - Committed accidentally by developer
   - Logged by application code
   - Stored in unencrypted location
3. Implement preventive controls:
   - Enable git pre-commit hooks for secret scanning
   - Add secret detection to CI/CD pipelines
   - Audit logging configuration to prevent credential leakage
   - Enable AWS Config rule for exposed access keys

## Output

Provide:
1. Containment status: credential revoked/rotated confirmation
2. Forensics summary: was the credential used maliciously (yes/no/unknown)
3. Impact assessment: what was potentially accessed
4. Service restoration: all consumers updated and healthy
5. Prevention recommendations to avoid recurrence