---
name: certificate-expiry-remediation
agent_type: "Evaluation"
description: Use this skill to prevent outages from expiring ACM and imported certificates and to fix failed or stalled renewals. It inventories certificates, checks expiry windows and renewal state, and recommends specific fixes for imported certificates, DNS validation failures, and certificates in use on live endpoints.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Certificate Expiry Remediation

This skill finds certificates that are about to expire or failing to renew and drives them to a healthy state before TLS on a live endpoint breaks.

## When to Activate

- An ACM certificate has NotAfter within 30 days.
- An imported certificate (no auto-renew) has NotAfter within 45 days.
- DescribeCertificate shows RenewalSummary RenewalStatus FAILED or PENDING_VALIDATION.
- A certificate is attached to an in-use load balancer, CloudFront, or API Gateway endpoint.
- A certificate has RenewalEligibility INELIGIBLE and manual action is required.

## Step 1: Inventory Certificates

- Call ACM ListCertificates across every region to enumerate certificates and their ARNs.
- Call DescribeCertificate for each to read DomainName, NotAfter, Type (AMAZON_ISSUED or IMPORTED), Status, and InUseBy.
- Prioritize certificates whose InUseBy list is non-empty.

## Step 2: Compute Expiry Windows

- Compute days-to-expiry as NotAfter minus now for every certificate.
- Flag CRITICAL for AMAZON_ISSUED certificates expiring within 30 days.
- Flag CRITICAL for IMPORTED certificates expiring within 45 days, since these do not auto-renew.

## Step 3: Assess Renewal Health

- Read RenewalEligibility and RenewalSummary.RenewalStatus from DescribeCertificate.
- Flag FAILED renewals and PENDING_VALIDATION renewals stuck beyond 72 hours.
- For DNS-validated certificates, check that the required CNAME validation records exist in Route 53.

## Step 4: Remediate

- For failed DNS validation, add or correct the ACM-provided CNAME validation record and let renewal retry.
- For imported certificates near expiry, reissue or import a fresh certificate and update the ARN on every endpoint in InUseBy.
- For INELIGIBLE certificates, request a new AMAZON_ISSUED certificate and migrate the binding.

## Step 5: Verify and Monitor

- Re-run DescribeCertificate to confirm Status ISSUED and a refreshed NotAfter.
- Confirm the endpoint serves the new certificate chain.
- Recommend an EventBridge rule on the ACM Certificate Approaching Expiration event and a CloudWatch DaysToExpiry alarm at 30 days.

## Output

The skill produces a titled "Certificate Expiry and Renewal Assessment" listing each certificate with its domain, type, days-to-expiry, renewal status, in-use bindings, and a CRITICAL, WARNING, or OK verdict. It concludes with a prioritized remediation list ordered by days-to-expiry and blast radius, such as fixing DNS validation records for failed renewals, reissuing and rebinding imported certificates within 45 days, migrating ineligible certificates, and adding expiry alarms and EventBridge notifications.