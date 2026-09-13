---
name: dependency-graph-blast-radius-enrichment
agent_type: "Generic"
description: Enriches a flat operational finding with upstream and downstream
  blast radius by reading the AWS DevOps Agent managed understanding-dependencies
  and understanding-agent-space memory stores. Use this skill when a finding
  names a single resource or service (an open security group, an unencrypted
  queue, a single-AZ database, a saturated table) and you need to state which
  callers, callees, shared packages, and request paths it affects, and how far a
  failure or compromise could reach. It turns "resource X has issue Y" into
  "issue Y on X puts these upstream and downstream components at risk."
version: "1.0.0"
last_updated: "2026-09-12"
---

# Dependency-Graph Blast-Radius Enrichment

Use this skill to turn an isolated finding into an impact statement grounded in
the service and package dependency graph that AWS DevOps Agent already maintains.
A finding that names one resource is only half the story; the operational
question is what else breaks or is exposed when that resource fails or is
compromised.

## Memory stores this skill reads

These are managed stores maintained by the platform. They are read-only; this
skill never writes to them.

- `understanding-dependencies`: the service-to-service and package dependency
  map - which services call which, what events flow between them, which packages
  are shared, and where infrastructure boundaries lie. This is the primary source
  for upstream and downstream reach.
- `understanding-agent-space`: the topology - logical containers and components,
  their physical identifiers (ARNs, table names, queue URLs), the request paths
  that traverse them, and the observability coverage per component.

## Method

1. Resolve the finding's resource to a component. Match the resource identifier
   in the finding (ARN, table name, queue URL, security group id) to a component
   in the `understanding-agent-space` store. If no match exists, note that the
   resource is not in the discovered topology and enrich only with what the
   finding itself provides.
2. Read the dependency edges. From `understanding-dependencies`, list the direct
   upstream callers of the component (who depends on it) and the direct
   downstream dependencies (what it depends on). Record shared packages and any
   event flows.
3. Walk the request paths. From `understanding-agent-space`, identify the
   critical request paths that traverse the component and name the entry point
   and the hops on each side.
4. Classify the blast radius by finding type:
   - Availability or fault-tolerance issue: the downstream failure domain (what
     stops working if this component degrades) and the upstream callers that feel
     it.
   - Security or exposure issue: the reachability - is the component on an
     internet-facing path, what credentials or data does a compromise of it
     expose, and which adjacent components become reachable next (lateral reach).
   - Capacity or limit issue: the callers whose traffic drives the resource
     toward the limit and the downstream work that stalls when it is hit.
5. State confidence. The dependency map is refreshed on a schedule and can lag
   recent changes; label the enrichment with the store's freshness and treat an
   edge as a hypothesis when the topology may be stale.

## Output

For each enriched finding, add: the resolved component, direct upstream callers,
direct downstream dependencies, the critical request paths it sits on, the
classified blast radius (failure domain, exposure reach, or capacity dependents),
and a freshness note. Keep resource identifiers as identifiers; do not reproduce
sensitive policy or credential content pulled in from adjacent components.
