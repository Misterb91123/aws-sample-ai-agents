---
name: tls-policy-modernization
agent_type: "Evaluation"
description: Use when modernizing TLS policies on Elastic Load Balancers and CloudFront. It finds listeners allowing TLS 1.0 or 1.1, weak ciphers, and outdated security policies, then recommends modern policies. Apply during security hardening or before compliance assessments.
version: "1.0.0"
last_updated: "2026-08-14"
---

# TLS Policy Modernization

Modernize TLS configuration on load balancers and CloudFront so only strong protocols and ciphers are allowed.

## When to Activate
- DescribeSSLPolicies or a listener uses a policy that permits TLS 1.0 or TLS 1.1.
- A CloudFront distribution uses a MinimumProtocolVersion below TLSv1.2_2021.
- A listener security policy includes weak ciphers such as 3DES or RC4.
- An ALB or NLB listener uses a legacy predefined policy.
- Compliance requires TLS 1.2 or higher but a resource still negotiates older protocols.

## Step 1: Inventory TLS Endpoints
- Call DescribeListeners for each load balancer and read the SslPolicy on HTTPS and TLS listeners.
- Call GetDistributionConfig for CloudFront and read MinimumProtocolVersion.
- List all endpoints terminating TLS.

## Step 2: Evaluate Protocol Versions
- Call DescribeSSLPolicies to expand each policy into its allowed protocols and ciphers.
- Flag any policy permitting TLS 1.0 or TLS 1.1.
- Flag CloudFront distributions below TLSv1.2_2021.

## Step 3: Evaluate Cipher Strength
- Inspect the cipher list of each policy for weak ciphers such as 3DES, RC4, or export ciphers.
- Flag policies containing weak ciphers.
- Prefer forward-secrecy suites (ECDHE).

## Step 4: Select Modern Policies
- Recommend a load balancer policy that requires TLS 1.2 or higher and strong ciphers.
- Recommend CloudFront MinimumProtocolVersion TLSv1.2_2021 or newer.
- Confirm client compatibility before removing older protocols.

## Step 5: Plan Rollout
- Recommend updating listeners with ModifyListener to the modern SslPolicy.
- Recommend a staged rollout starting with internal endpoints.
- Add monitoring for handshake failures after the change.

## Output
Produce a titled "TLS Policy Modernization Report" listing listeners and distributions allowing TLS 1.0 or 1.1, policies with weak ciphers, and outdated predefined policies. Include a prioritized remediation list: disable TLS 1.0 and 1.1 on internet-facing endpoints first, remove weak ciphers second, then move CloudFront to TLSv1.2_2021 and standardize on one modern policy.