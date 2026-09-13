---
name: connect-security-and-compliance-audit
agent_type: "Evaluation"
description: Provides an audit procedure for Amazon Connect instance security
  posture, including instance access model (SAML versus Connect-managed), call and
  screen recording encryption with KMS, instance storage configs for recordings,
  CTRs, and Contact Lens output, S3 bucket encryption and Kinesis targets, data
  retention, security-profile least privilege, attachment and chat transcript
  storage, and PII in Contact Lens. Use this skill when reviewing a Connect instance
  for security or compliance gaps, when validating encryption and access controls, or
  when producing a posture report with safety ratings.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Amazon Connect Security and Compliance Audit

Use this skill to audit the security and compliance posture of an Amazon Connect
instance. This is a read-only evaluation. Reference HIGH-sensitivity data by
identifier only, never by value. Never recommend a prohibited action: no disabling
encryption or logging, no wildcard IAM, no public buckets, no 0.0.0.0/0.

## When to Activate

- Reviewing a Connect instance against a security or compliance baseline.
- Validating recording and CTR encryption and storage configuration.
- Checking security profiles for over-broad permissions.
- Verifying data streaming targets and retention.
- Producing a posture report with GREEN/YELLOW/RED ratings.

## Step 1: Enumerate Instance and Access Model

1. DescribeInstance / ListInstances to capture instance ARN, status, and created
   time.
2. DescribeInstanceAttribute for feature attributes (contact flow logs, Contact
   Lens, multi-party calls, early media, etc.).
3. Determine identity management: SAML 2.0, Connect-managed, or existing directory.
   SAML with a central IdP and enforced MFA rates higher than Connect-managed local
   users.

## Step 2: Enumerate Instance Storage Configs and Encryption

Use ListInstanceStorageConfigs for each resource type:
`CALL_RECORDINGS`, `CHAT_TRANSCRIPTS`, `SCHEDULED_REPORTS`,
`MEDIA_STREAMS`, `CONTACT_TRACE_RECORDS`, `AGENT_EVENTS`,
`ATTACHMENTS`, `CONTACT_EVALUATIONS`, and Contact Lens output.

For each:

- S3 targets: confirm the bucket has default encryption (SSE-KMS preferred over
  SSE-S3), Block Public Access enabled at bucket and account level, and a
  restrictive bucket policy. Reference the KMS key by ARN/alias, never expose key
  material.
- Kinesis targets (CTR / agent events): confirm the stream exists, is encrypted,
  and delivers to a controlled destination.
- Confirm recording encryption uses a customer-managed KMS key with a scoped key
  policy.

## Step 3: Review Security Profiles for Least Privilege

1. ListSecurityProfiles and inspect assigned permissions.
2. Flag profiles that grant broad administrative permission sets to large agent
   populations, or that combine sensitive views (recordings, Contact Lens
   transcripts with PII) with routine agent roles.
3. Confirm access to recordings, contact search, and Contact Lens analytics is
   limited to roles that require it.

## Step 4: Check Recording and Streaming Targets

1. Confirm call and screen recording write to an encrypted S3 location with
   lifecycle and retention aligned to policy (not indefinite unless required).
2. Confirm CTR and agent-event Kinesis streaming targets are owned accounts with
   encryption in transit and at rest.
3. Confirm chat transcripts and attachments storage are encrypted and access-
   controlled the same as recordings.

## Step 5: Assess PII and Contact Lens Handling

1. If Contact Lens is enabled, confirm redaction is configured where required and
   that transcript/analytics output lands in an encrypted, access-controlled store.
2. Treat call recordings, transcripts, and Customer Profiles data as HIGH
   sensitivity; in findings, cite them by resource identifier only.
3. Confirm retention on Contact Lens output and Customer Profiles matches the data
   retention policy.

## Step 6: Rate Findings

Assign a safety rating to each finding:

| Rating | Meaning | Example |
|--------|---------|---------|
| GREEN | Meets baseline | SSE-KMS on recordings, BPA on, SAML with MFA |
| YELLOW | Gap, contained risk | SSE-S3 instead of KMS, retention longer than policy |
| RED | Serious exposure | Unencrypted storage target, over-broad security profile, public bucket |

For each YELLOW/RED, give a specific, allowed remediation (enable SSE-KMS with a
named CMK, enable Block Public Access, scope the security profile to required
permissions, set a compliant retention period). Never propose disabling encryption
or logging, wildcard IAM, public access, or 0.0.0.0/0.

## Output

Provide:
1. Instance summary (access model, enabled features) with HIGH-sensitivity data
   referenced by identifier only.
2. Per-storage-config findings (encryption, public access, retention, streaming
   target) each with a GREEN/YELLOW/RED rating.
3. Security-profile least-privilege findings.
4. Prioritized, allowed remediations (RED first), with the specific control to set
   and no prohibited actions.
