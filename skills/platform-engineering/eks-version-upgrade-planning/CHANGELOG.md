# Changelog

## [1.1.0] - 2026-09-12
### Added
- Extended-support exposure step: detect clusters already in or set to
  auto-enter EKS extended support, and estimate the monthly control-plane
  per-cluster-hour delta (labeled an estimate).
- Version skew and support reference section: minor-version-at-a-time upgrade
  rule, supported kubelet skew window, standard/extended support duration, and
  the core managed add-ons to validate.
- Open-spec metadata (metadata.version, metadata.author) in SKILL.md frontmatter.
- README with IAM prerequisites, CHANGELOG, and behavioral evals.

## [1.0.0] - 2026-08-14
### Added
- Initial release of the EKS version upgrade planning skill.
- Detects clusters near end of standard support, control-plane-to-node version
  skew, and incompatible add-on versions, and sequences a safe upgrade path
  (control plane, then add-ons, then node groups) one minor version at a time.
