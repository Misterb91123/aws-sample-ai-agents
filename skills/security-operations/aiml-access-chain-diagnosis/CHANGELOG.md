# Changelog

## [1.0.0] - 2026-09-12
### Added
- Initial release of the AI/ML access-chain diagnosis skill.
- Traces the full AWS AI/ML authorization chain (caller identity, IAM identity
  policy, execution/service role, role trust, iam:PassRole, resource and service
  policies including Bedrock model access, S3 bucket policy, and KMS key policy,
  and permission boundary or SCP) for an AccessDenied failure.
- Identifies the single deciding layer (explicit deny versus missing allow) using
  the IAM policy simulator and the CloudTrail AccessDenied event.
- Generates the minimal least-privilege IAM fix with no wildcard action or
  resource. Read-only and recommend-only.
