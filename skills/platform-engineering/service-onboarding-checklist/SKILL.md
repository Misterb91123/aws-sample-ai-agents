---
name: service-onboarding-checklist
agent_type: "Generic"
description: Validates that a new service meets all platform requirements before
  being promoted to production, covering infrastructure, observability, security,
  reliability, and operational readiness. Use this skill when a team is deploying
  a new service or migrating an existing one to the platform and needs a
  comprehensive readiness assessment.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Service Onboarding Checklist

Use this skill to validate production readiness for new services being
deployed to the platform for the first time.

## When to Activate

- New service requesting production deployment.
- Existing service migrating to a new platform (containers, serverless).
- Service has been in staging and team requests production promotion.
- Platform team reviewing onboarding requests in the queue.
- Post-incident reveals a service was deployed without proper onboarding.

## Step 1: Service Identity & Ownership

Validate basic service registration:

- [ ] Service has a unique, descriptive name following naming conventions.
- [ ] Service is registered in the service catalog (with description and purpose).
- [ ] Owning team is identified and has on-call rotation.
- [ ] Service has a designated tech lead and product owner.
- [ ] Contact channels defined (Slack channel, email distribution list).
- [ ] Service documentation exists (README, architecture doc, runbook).
- [ ] Repository follows org conventions (branch protection, CODEOWNERS).

## Step 2: Infrastructure Configuration

Validate infrastructure is properly configured:

- [ ] Deployed using Infrastructure-as-Code (CloudFormation, Terraform, CDK).
- [ ] No manually created resources (clickops-free).
- [ ] Multi-AZ deployment for high availability.
- [ ] Auto Scaling configured with appropriate min/max/desired.
- [ ] Health checks configured (ALB, ECS, container-level).
- [ ] Resource requests and limits defined (CPU, memory).
- [ ] Appropriate instance/task sizing validated by load testing.
- [ ] VPC networking properly configured (correct subnets, security groups).
- [ ] DNS records created and validated.
- [ ] TLS/SSL certificates provisioned and auto-renewal configured.

## Step 3: Security Requirements

Validate security posture:

- [ ] IAM role follows least privilege (no wildcard permissions).
- [ ] Secrets stored in Secrets Manager or Parameter Store (no hardcoded secrets).
- [ ] Security groups restrict access to only required ports and sources.
- [ ] Container images scanned for vulnerabilities (no critical/high unresolved).
- [ ] Base image is from approved registry and is current.
- [ ] No public endpoints unless explicitly required and approved.
- [ ] Encryption at rest enabled for all data stores.
- [ ] Encryption in transit (TLS) for all network communication.
- [ ] Input validation implemented for all external inputs.
- [ ] Authentication and authorization implemented where required.
- [ ] WAF rules applied to public-facing endpoints.
- [ ] GuardDuty monitoring active in the account.

## Step 4: Observability Requirements

Validate monitoring and alerting:

- [ ] Structured logging implemented (JSON format with correlation IDs).
- [ ] Logs shipped to CloudWatch Logs with appropriate retention.
- [ ] Key metrics published (four golden signals: latency, traffic, errors, saturation).
- [ ] CloudWatch dashboard created with essential panels.
- [ ] Alarms configured for critical conditions:
  - [ ] Error rate > threshold
  - [ ] Latency p99 > threshold
  - [ ] Health check failures
  - [ ] Resource saturation > 80%
- [ ] Alarm actions configured (SNS -> PagerDuty/OpsGenie).
- [ ] Distributed tracing enabled (X-Ray or equivalent).
- [ ] SLI/SLO defined with error budget tracking.
- [ ] Synthetic canary deployed for critical user flows.

## Step 5: Reliability Requirements

Validate resilience patterns:

- [ ] Graceful shutdown handling (drain connections on SIGTERM).
- [ ] Readiness and liveness probes configured correctly.
- [ ] Circuit breakers on downstream dependencies.
- [ ] Timeouts configured for all outbound calls (no unbounded waits).
- [ ] Retries with exponential backoff and jitter.
- [ ] Rate limiting / throttling for inbound traffic.
- [ ] Graceful degradation mode defined (what happens when dependencies fail).
- [ ] Data backup and recovery tested.
- [ ] Load testing completed (knows its breaking point).
- [ ] PodDisruptionBudget (Kubernetes) or min healthy instances configured.

## Step 6: Deployment & Release

Validate deployment pipeline:

- [ ] CI/CD pipeline configured and passing.
- [ ] Deployment strategy defined (canary, blue/green, rolling).
- [ ] Automated rollback configured (health-check-based).
- [ ] Database migrations are backward-compatible (rollback-safe).
- [ ] Feature flags available for risky changes.
- [ ] Deployment runbook documented (deploy, verify, rollback).
- [ ] Smoke tests run post-deployment automatically.
- [ ] Deployment notifications to team channel.

## Step 7: Operational Readiness

Validate the team can operate the service:

- [ ] On-call rotation configured and staffed.
- [ ] Runbook written for common operational scenarios.
- [ ] Escalation paths documented.
- [ ] Disaster recovery plan defined and tested.
- [ ] Dependency map documented (what it calls, what calls it).
- [ ] Capacity planning done (expected traffic, growth projections).
- [ ] Cost estimate reviewed and budget allocated.
- [ ] Tagging applied (Team, Service, Environment, CostCenter).

## Step 8: Compliance & Governance

Validate organizational requirements:

- [ ] Service meets data classification requirements.
- [ ] Compliant with relevant standards (PCI, HIPAA, SOC2 if applicable).
- [ ] Architecture review completed (for services above complexity threshold).
- [ ] Resource tagging policy followed.
- [ ] Cost allocation tags applied.

## Scoring & Decision

| Score | Verdict | Action |
|-------|---------|--------|
| 100% of mandatory items | [PASS] Approved | Proceed to production |
| > 80% with no critical gaps | [WARN] Conditional | Approve with remediation timeline |
| < 80% or critical gaps | [FAIL] Not Ready | Block until gaps addressed |

**Mandatory items** (cannot be waived): Security requirements, health checks, alarm actions, on-call rotation, IaC deployment.

**Recommended items** (can be deferred with timeline): Full observability, chaos testing, load testing, DR plan.

## Output

Produce an onboarding assessment:
1. **Readiness Score**: Percentage complete with breakdown by category.
2. **Checklist Results**: Full checklist with pass/fail per item.
3. **Blockers**: Items that must be resolved before production (mandatory gaps).
4. **Warnings**: Items that should be resolved soon after launch (recommended gaps).
5. **Verdict**: Approved / Conditional / Not Ready.
6. **Remediation Plan**: Timeline for addressing remaining gaps.