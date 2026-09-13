---
name: topology-drift-detection
agent_type: "Generic"
description: Detects drift between the architecture AWS DevOps Agent has
  discovered (the managed understanding-agent-space topology) and the
  architecture the team expects, as expressed through resource tags, naming
  conventions, and standing directives. Use this skill to find newly appeared or
  disappeared components, unexpected cross-environment or cross-account edges,
  components missing required ownership or environment tags, and services that
  standing directives say should not exist. It reports divergence as findings; it
  does not modify topology or resources.
version: "1.0.0"
last_updated: "2026-09-12"
---

# Topology Drift Detection

Use this skill to compare the discovered topology against expectation and report
where reality has drifted. The platform continuously learns the environment; the
value here is catching the moments discovery reveals something the team did not
intend or no longer expects.

## Memory stores this skill reads

Read-only. Managed stores maintained by the platform, plus any custom store the
operator attached that records expected architecture.

- `understanding-agent-space`: the current discovered topology - containers,
  components, physical identifiers, deployment environments (account and Region
  pairs), and request paths.
- `directives`: user-authored standing instructions (for example "Lambdas are no
  longer used, the service uses Fargate"), which encode what the team expects to
  be true.
- Optional custom store (if attached): an expected-architecture or
  service-catalog store the operator maintains.

## Method

1. Read the current topology from `understanding-agent-space`: enumerate
   components, their environments, and the cross-component edges.
2. Read expectation signals: standing statements in `directives`, plus tag and
   naming conventions confirmed with `use_aws` (for example a required `owner`,
   `environment`, or `cost-center` tag, and a naming prefix per environment).
3. Detect drift categories:
   - Unexpected components: a discovered component that a directive says should
     not exist (for example Lambda functions after a directive states the service
     moved to Fargate).
   - Missing governance tags: components absent a required ownership or
     environment tag, so they cannot be routed or charged back.
   - Cross-boundary edges: an edge that crosses an account or environment
     boundary where the team expects isolation (for example a pre-production
     component calling a production data store).
   - Appeared or disappeared: components present now that were not in the prior
     topology version, or gone from it, without a corresponding change record.
4. Corroborate with live reads. Use `use_aws` to confirm the drifting resource
   still exists and to read its tags before reporting, so a stale topology version
   does not produce a false finding.
5. Rate severity: cross-boundary production exposure highest, then missing
   ownership on production components, then informational appeared/disappeared
   deltas.

## Output

Report each drift with the component, the drift category, the expected state and
the observed state, the corroborating live read, and a severity. Note the
topology store's freshness and treat any delta the live read could not confirm as
a hypothesis. Do not modify tags, resources, or the topology; recommend the
correction for a human to apply.
