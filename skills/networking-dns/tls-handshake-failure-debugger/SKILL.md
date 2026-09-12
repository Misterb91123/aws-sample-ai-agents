---
name: tls-handshake-failure-debugger
agent_type: "Incident RCA"
description: Debugs TLS/SSL handshake failures between clients and servers including
  certificate validation errors, cipher suite mismatches, and protocol version
  incompatibilities. Use this skill when connections fail with TLS errors, when
  certificate renewals cause unexpected failures, or when upgrading TLS policies
  on load balancers or CloudFront distributions.
version: "1.0.0"
last_updated: "2026-08-14"
---

# TLS Handshake Failure Debugger

Use this skill to diagnose and resolve TLS connection failures in AWS
environments.

## When to Activate

- Connection errors with "SSL handshake failed" or "certificate verify failed."
- After certificate renewal, services can't connect.
- After TLS policy upgrade on ALB/NLB/CloudFront, some clients fail.
- Mutual TLS (mTLS) authentication failing.
- Mixed content or downgrade issues.
- Certificate chain incomplete errors from clients.

## Step 1: Identify the TLS Error Type

Common TLS failure categories:

| Error Message | Category | Typical Cause |
|--------------|----------|--------------|
| `certificate verify failed` | Certificate validation | Expired cert, wrong hostname, untrusted CA |
| `handshake failure` | Protocol/cipher mismatch | Client and server have no common cipher suite |
| `no acceptable protocol` | Version mismatch | Client requires TLS 1.0/1.1, server only allows 1.2+ |
| `certificate expired` | Expiration | Certificate past its validity date |
| `hostname mismatch` | SAN/CN mismatch | Certificate doesn't cover the requested hostname |
| `unable to get local issuer certificate` | Chain incomplete | Intermediate CA cert missing from server |
| `self-signed certificate` | Trust issue | Self-signed cert not in client's trust store |
| `bad certificate` (mTLS) | Client cert issue | Client cert expired, wrong CA, or not presented |

## Step 2: Diagnose Certificate Issues

### Certificate Expiration
1. Check certificate expiry date in ACM or on the endpoint.
2. If expired: Was auto-renewal attempted? Check ACM renewal status.
3. For imported certs: manual renewal required - check when it expired.
4. Fix: Renew or reimport certificate.

### Hostname Mismatch
1. Compare the requested hostname against the certificate's Subject Alternative Names (SANs).
2. Certificate covers `www.example.com` but client connects to `api.example.com` -> fails.
3. Wildcard certs (`*.example.com`) cover one level only - not `sub.api.example.com`.
4. Fix: Ensure certificate SANs include all hostnames used to access the service.

### Incomplete Certificate Chain
1. Server must present the full chain: leaf cert + intermediate CA(s).
2. Some clients (browsers) can fetch intermediates, but SDKs/APIs often cannot.
3. ALB/CloudFront handle this automatically for ACM certs.
4. Imported certificates: you must include intermediates in the chain.
5. Fix: Reimport with full certificate chain.

### Untrusted CA
1. Client's trust store doesn't include the root CA that signed the certificate.
2. Common with private CAs (ACM Private CA) - clients need the root CA in their trust store.
3. Self-signed certificates: only trusted if explicitly added to client's trust store.
4. Fix: Add root CA to client trust store, or use a publicly trusted CA.

## Step 3: Diagnose Protocol/Cipher Issues

### TLS Version Mismatch
Server and client must agree on a TLS version:

| ALB/CloudFront Policy | TLS Versions Supported |
|----------------------|----------------------|
| ELBSecurityPolicy-TLS13-1-2-2021-06 | TLS 1.3, 1.2 |
| ELBSecurityPolicy-TLS-1-2-2017-01 | TLS 1.2 only |
| ELBSecurityPolicy-2016-08 | TLS 1.0, 1.1, 1.2 |
| ELBSecurityPolicy-TLS13-1-3-2021-06 | TLS 1.3 only |

**Problem**: Old clients (Java 7, older browsers, IoT devices) may only support TLS 1.0/1.1.
**After policy upgrade**: These clients can't connect.
**Fix**: Either upgrade clients or (temporarily) use a more permissive policy.

### Cipher Suite Mismatch
1. Server advertises supported ciphers in its TLS policy.
2. Client proposes ciphers it supports.
3. If no overlap -> handshake fails.
4. Check ALB access logs for `ssl_cipher` field - if blank, handshake failed.
5. Fix: Ensure the TLS policy includes ciphers supported by all required clients.

## Step 4: Diagnose Mutual TLS (mTLS) Issues

For API Gateway or ALB with mTLS:

1. **Client certificate not presented:**
   - Client not configured to send client cert.
   - Client cert not in the expected format (PEM).

2. **Client certificate expired:**
   - Client cert has its own validity period - check it.

3. **Client cert signed by wrong CA:**
   - Server has a trust store of accepted CAs.
   - Client cert must be signed by a CA in that trust store.

4. **Revoked client certificate:**
   - CRL (Certificate Revocation List) check fails.

5. **API Gateway mTLS specifics:**
   - Trust store is an S3 object (CA bundle in PEM format).
   - Client cert chain must be verifiable against that bundle.
   - Check API Gateway execution logs for detailed TLS error.

## Step 5: Debug Using Available Tools

### ALB Access Logs
- `ssl_cipher`: Negotiated cipher (blank = handshake failed).
- `ssl_protocol`: TLS version used.
- `actions_executed`: Shows if request reached backend or failed at TLS.

### CloudFront Access Logs
- `ssl-protocol`: TLS version.
- `ssl-cipher`: Cipher suite used.

### AWS CLI Certificate Inspection
```
# Check ACM certificate details
aws acm describe-certificate --certificate-arn <arn>

# Check expiration, SANs, renewal status
```

### OpenSSL Client Test (from EC2 instance)
```
# Test TLS connection and show certificate details
openssl s_client -connect hostname:443 -servername hostname

# Test with specific TLS version
openssl s_client -connect hostname:443 -tls1_2

# Verify certificate chain
openssl s_client -connect hostname:443 -showcerts
```

## Step 6: Common Fix Procedures

| Problem | Fix |
|---------|-----|
| Expired ACM cert | Check why auto-renewal failed (DNS validation record missing?); manually request new cert or fix validation |
| Expired imported cert | Import new cert with updated expiry and full chain |
| Hostname not in SAN | Request new certificate including all required SANs |
| Old clients failing after policy upgrade | Temporarily revert to more permissive policy; plan client upgrade |
| Incomplete chain | Reimport certificate including intermediate CA certificates |
| mTLS client cert rejected | Verify client cert CA is in the trust store; check cert expiry |
| Private CA cert not trusted | Distribute root CA to all clients needing to connect |

## Step 7: Prevention

1. Set up certificate expiration monitoring (CloudWatch, ACM events).
2. Test TLS policy changes against client inventory BEFORE applying to production.
3. Use ACM certificates where possible (auto-renewal handles expiration).
4. Monitor ALB access logs for increasing TLS handshake failures.
5. Maintain a client compatibility matrix for your TLS policy decisions.

## Output

Produce a TLS troubleshooting report:
1. **Error Summary**: Error type, affected clients/endpoints, scope.
2. **Certificate Analysis**: Validity, SANs, chain completeness, CA trust status.
3. **Protocol/Cipher Analysis**: Server policy, client capabilities, overlap (or lack thereof).
4. **Root Cause**: Specific TLS configuration issue identified.
5. **Fix Applied/Recommended**: Certificate or policy change to resolve.
6. **Client Impact Assessment**: Which clients are affected and what they need.
7. **Prevention Controls**: Monitoring and automation to prevent recurrence.