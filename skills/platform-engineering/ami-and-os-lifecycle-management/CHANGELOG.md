# Changelog

## [1.1.0] - 2026-09-12
### Added
- End-of-support cost-and-risk attribution step: separates third-party OS and
  database vendor extended-support and licensing cost, security exposure from
  unpatched software, and previous-generation price-performance premium, and
  states that EC2 has no AWS OS extended-support surcharge.
- OS lifecycle reference section (common EOS milestones, deregistered-AMI
  recovery risk, SSM patch-compliance signals).
- SSM-first OS detection (DescribeInstanceInformation) with AMI-metadata
  fallback marked inferred.
- Open-spec metadata (metadata.version, metadata.author) in SKILL.md frontmatter.
- README with IAM prerequisites, CHANGELOG, and behavioral evals.

## [1.0.0] - 2026-08-14
### Added
- Initial release of the AMI and OS lifecycle management skill.
- Inventories AMI age, maps instances to AMI and OS, detects launch-template and
  ASG drift, verifies SSM patch compliance, and plans a refresh-and-deprecation
  cadence. Read-only and recommend-only.
