---
name: direct-connect-failover-troubleshooting
agent_type: "Incident RCA"
description: Use this skill when a Direct Connect primary link degrades or drops and traffic must fail over to a VPN backup or a secondary Direct Connect connection. It triggers on packet loss, increased latency, BGP session flaps, or asymmetric routing reports on Direct Connect virtual interfaces, and it guides BGP path selection, failover timing, and ECMP validation.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Direct Connect Failover Troubleshooting

This skill diagnoses failover behavior when an AWS Direct Connect primary connection degrades and traffic should move to a VPN or a secondary Direct Connect connection. It focuses on BGP path selection, failover timing, and detection of asymmetric routing that survives failover.

## When to Activate

- A Direct Connect virtual interface reports rising packet loss, latency above baseline, or repeated BGP session flaps.
- Failover to a Site-to-Site VPN backup did not occur or was delayed beyond the expected window.
- Traffic returns on a different path than it left on (suspected asymmetric routing).
- ECMP is configured across multiple Direct Connect connections and load distribution looks uneven.
- CloudWatch Direct Connect metrics (ConnectionState, ConnectionBpsEgress, ConnectionLightLevelTx/Rx) show anomalies.

## Step 1: Establish the current path and BGP state

- Read CloudWatch Direct Connect metrics: ConnectionState, ConnectionErrorCount, ConnectionLightLevelTx and ConnectionLightLevelRx. Rx light levels outside -20 dBm to 0 dBm indicate a physical layer problem, not a routing problem.
- Retrieve BGP status on each virtual interface with describe-virtual-interfaces and confirm bgpStatus is "up" for primary and backup.
- On the customer gateway, capture the BGP table (show ip bgp) to identify which prefixes are learned from Direct Connect versus VPN and the selected best path.

## Step 2: Validate BGP path selection attributes

- Confirm the intended preference order. AWS evaluates inbound routes in this order: longest prefix match first, then Local Preference, then AS path length, then MED, then eBGP over iBGP.
- For the backup VPN or secondary link, apply AS path prepending on the less-preferred path (prepend 2 to 3 times) so the primary Direct Connect remains best path while both are healthy.
- On the customer side, set Local Preference higher (for example 200) on routes learned via primary Direct Connect and lower (for example 100) on the backup so egress prefers the primary.
- Confirm more-specific prefixes are not being advertised on the backup path, since longest prefix match overrides Local Preference and AS path.

## Step 3: Measure failover timing

- Determine the BGP hold timer. AWS uses a default hold time of 90 seconds with a 30-second keepalive. Failover triggers after the hold timer expires with no keepalive.
- To accelerate detection, enable BGP BFD (Bidirectional Forwarding Detection); AWS supports a 300 ms interval with a multiplier of 3, giving sub-second failure detection instead of up to 90 seconds.
- Record the observed convergence time from primary loss to backup carrying traffic and compare against the RTO. Without BFD, expect up to 90 seconds; with BFD, expect under 1 second plus reprogramming time.

## Step 4: Detect asymmetric routing

- Compare the egress path (routes AWS advertises to you) against the ingress path (routes you advertise to AWS). Asymmetry occurs when egress prefers Direct Connect but ingress prefers VPN, or the reverse.
- Confirm MED and AS path settings are consistent in both directions so both directions select the same physical path.
- Where stateful inspection appliances are in the path, asymmetric routing breaks flow state and causes silent drops. Verify appliance mode on the inspection VPC attachment if a Transit Gateway is involved.

## Step 5: Validate ECMP across parallel connections

- ECMP requires equal BGP attributes across the member connections: identical AS path length, MED, and Local Preference. Any mismatch collapses ECMP to a single active path.
- Confirm all member Direct Connect connections terminate on the same Direct Connect gateway or Transit Gateway attachment and advertise identical prefixes.
- Check that per-flow hashing is distributing sessions; a single large elephant flow will not spread across members and can saturate one link while others sit idle.

## Output

Produce a Direct Connect Failover Assessment containing: current path and BGP session state per virtual interface, the configured versus observed path selection (Local Preference, AS path prepend, MED), measured failover convergence time against the RTO, a BFD recommendation with specific interval and multiplier values, any asymmetric routing findings with the affected prefixes, and ECMP distribution status. Include a prioritized remediation list and flag any physical-layer issues (light levels, error counts) that require the connection provider rather than a routing change.