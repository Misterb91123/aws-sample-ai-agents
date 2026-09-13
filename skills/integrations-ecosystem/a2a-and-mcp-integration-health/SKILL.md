---
name: a2a-and-mcp-integration-health
agent_type: "Generic"
description: >
  Audits registered remote A2A agents, custom MCP servers, and generic webhooks for
  health, staleness, over-broad scope, and security posture. Use this skill to keep
  the extension surface of the Agent Space clean: authenticated, least-privilege,
  and still in use.
version: "1.0.0"
last_updated: "2026-09-12"
---

# A2A and MCP Integration Health

Extension points are where an agent platform grows both capability and risk. Every
registered remote A2A agent, custom MCP server, and generic webhook widens the
attack surface and adds something that can silently break or quietly outlive its
purpose. This skill audits those extension points for whether they are healthy,
still used, properly scoped, and securely configured.

## Sources

Read-only reasoning over platform-surfaced data:

- The Agent Space registration records for remote A2A agents, custom MCP servers,
  and generic webhooks surfaced by the platform: endpoints, scopes, and auth
  configuration.
- Recent invocation and investigation history (list_investigations) to judge
  whether each extension is still exercised.
- Any health or reachability signals the platform surfaces for these endpoints.

This skill audits and recommends only. It does not deregister, disable, or
reconfigure any extension.

## Method

1. Inventory the extension surface. List every registered A2A agent, MCP server,
   and generic webhook with its endpoint, purpose, owner, and registration date.
2. Check health and reachability. For each, note whether the endpoint is reachable
   and responding, using the health signals the platform surfaces. Flag endpoints
   that appear down or erroring.
3. Assess staleness. Compare each extension against recent invocation history. Flag
   ones with no recent use as candidates for removal.
4. Assess scope. Review the permissions and data each extension can reach. Flag
   over-broad scope where a narrow one would suffice, and any extension that can
   reach more than its purpose requires.
5. Assess authentication. Flag extensions with no authentication, shared or
   long-lived secrets, or endpoints that are not using transport encryption.
6. Assess ownership. Flag extensions with no identifiable owner, since unowned
   integrations are the ones that rot.
7. Rank by risk. Combine security posture, scope breadth, and staleness into a
   priority order, with unauthenticated broadly-scoped extensions at the top.

## Output

Produce an extension-health report:

1. Extension Inventory: A2A agents, MCP servers, and webhooks with endpoint,
   purpose, owner, and age.
2. Health Findings: unreachable or erroring endpoints.
3. Staleness: extensions with no recent use.
4. Security Posture: over-broad scope, weak or missing authentication, unencrypted
   transport, and missing ownership.
5. Recommendations: extensions to review for removal, re-scope, or re-secure,
   ranked by risk. All recommend-only.
