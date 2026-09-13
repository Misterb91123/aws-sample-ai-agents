---
name: iot-device-certificate-expiry-fleet
agent_type: "Evaluation"
description: Provides fleet-scale evaluation of AWS IoT device X.509 certificate
  lifecycle posture, including expiring and expired certificates, INACTIVE or
  REVOKED certificates still attached to things, CA certificate expiry, and
  JITP/JITR provisioning readiness. Use this skill to grade certificate health
  across the fleet, bucket certificates by days-to-expiry, and flag rotation risk
  before mass device disconnects occur.
version: "1.0.0"
last_updated: "2026-08-14"
---

# IoT Device Certificate Expiry Fleet Evaluation

Use this skill to evaluate the certificate lifecycle posture of an AWS IoT fleet
and assign a health rating. Posture is read-only investigation; reference
certificate IDs and metadata only and never read or echo private key material.

## When to Activate

- Periodic certificate lifecycle review across the device fleet.
- Concern about upcoming X.509 certificate expiry causing mass disconnects.
- Suspected INACTIVE or REVOKED certificates still attached to active things.
- CA certificate approaching expiry (which blocks new provisioning).
- Evaluating JITP (Just-In-Time Provisioning) or JITR readiness posture.

## Step 1: Enumerate Certificates and Expiry Dates

1. Call iot ListCertificates via `use_aws` (paginate fully) to collect every
   certificate ID, status (ACTIVE, INACTIVE, REVOKED, PENDING_TRANSFER), and
   creation date.
2. For each certificate call iot DescribeCertificate to read the certificatePem
   validity window (notBefore, notAfter) and the certificate ID. Record notAfter
   as the authoritative expiry.
3. Compute days-to-expiry = notAfter minus current date for every certificate.
4. Reference certificate IDs only. Do not print certificatePem contents beyond the
   validity dates needed for evaluation.

## Step 2: Bucket by Days-to-Expiry

Sort every ACTIVE certificate into buckets:

| Bucket | Days to Expiry | Meaning |
|--------|----------------|---------|
| Expired | less than 0 | Devices using this cert cannot authenticate now |
| Critical | 0 to 30 | Rotation must be in progress |
| Warning | 31 to 90 | Rotation should be scheduled |
| Watch | 91 to 180 | Plan rotation window |
| Healthy | greater than 180 | No near-term action |

Count certificates and the associated things per bucket. The distribution, not a
single cert, drives the rating.

## Step 3: Find INACTIVE or REVOKED Certificates Still Attached

A certificate that is REVOKED or INACTIVE but still attached to a thing or policy
is a posture defect: the device is either broken or a stale credential path
remains.

1. For each REVOKED or INACTIVE certificate, call iot ListPrincipalThings (or
   ListThingPrincipals per thing) to find attached things, and check attached
   policies.
2. Flag any REVOKED certificate still attached to a thing as a high-severity
   finding (revocation intent not fully enforced by detachment).
3. Flag INACTIVE certificates attached to things that are still expected to
   connect (these will produce Connect.AuthError).

## Step 4: Flag CA Certificate Expiry and Provisioning Posture

1. Call iot ListCACertificates and DescribeCACertificate to read CA notAfter and
   status. A CA within 180 days of expiry is a fleet-level risk because it blocks
   registration of new device certificates signed by that CA.
2. Check autoRegistrationStatus on the CA to understand JITR posture, and note
   whether JITP templates are configured. An expiring CA with active
   auto-registration is elevated risk because new-device onboarding will fail at
   CA expiry.
3. Record CA IDs and expiry only; do not expose CA private material.

## Step 5: Assign Rating and Recommend Rotation

Assign a single fleet rating using the worst applicable condition:

| Rating | Condition |
|--------|-----------|
| RED | Any expired ACTIVE certificate in use, any REVOKED cert still attached to a thing, or CA expiring within 30 days |
| YELLOW | Any certificate in Critical (0-30d) or Warning (31-90d) buckets, INACTIVE certs still attached, or CA expiring within 180 days |
| GREEN | All ACTIVE certs greater than 90 days to expiry, no REVOKED/INACTIVE certs attached, CA greater than 180 days |

Recommended rotation guidance (specific, least-change):
- Provision replacement certificates and attach the same scoped policy before
  detaching the old certificate, so devices never lose a valid credential.
- Detach and then deactivate superseded certificates only after devices confirm
  use of the new certificate.
- For REVOKED certs still attached, detach them from things and policies.
- Schedule CA renewal ahead of the 180-day mark to preserve JITP/JITR onboarding.

Prohibited: do not disable certificate validation, do not switch devices to
unauthenticated connectivity, and do not widen IoT policies during rotation.

## Output

Provide:
1. Fleet rating (GREEN / YELLOW / RED) with the deciding condition.
2. Days-to-expiry bucket distribution with certificate and thing counts per bucket
   (certificate IDs referenced, no key material).
3. List of REVOKED/INACTIVE certificates still attached and any CA expiry findings.
4. Specific rotation plan (provision-attach-then-detach order) and prevention steps
   (expiry monitoring, alarms ahead of the 90-day mark, CA renewal calendar).
