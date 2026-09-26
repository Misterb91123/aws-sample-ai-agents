# Changelog

## [1.0.0] - 2026-09-12
### Added
- Initial release of the Lambda runtime Transform remediation skill.
- Detects functions on deprecated or soon-to-be-deprecated runtimes from the
  Trusted Advisor deprecated-runtime check, with a fallback to the Lambda
  deprecated-runtime data and AWS Health when the Support API is not entitled.
- Classifies each function against the AWS runtime deprecation phases (Phase 1
  create-blocked, Phase 2 update-blocked) and computes days-to-phase from AWS
  published deprecation dates, marking runtimes with no published date as
  "deprecation unknown".
- Plans the code upgrade through AWS Transform (assessment, human-approved
  transformation, verification) with per-function rollback, and the correct path
  for container-image and custom (provided.*) runtimes.
- Read-only and plan-only: every mutating step is human-approved and every
  function carries a rollback.
