---
name: network-firewall-false-positive-tuning
agent_type: "Generic"
description: Use this skill when AWS Network Firewall is dropping legitimate traffic and you need to reduce false positives without weakening the security posture. It triggers on reports of blocked application traffic correlated with Network Firewall, noisy Suricata alerts, or requests to safely tune stateful rule groups, domain allowlists, and rule ordering.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Network Firewall False Positive Tuning

This skill reduces false-positive drops in AWS Network Firewall while preserving detection of real threats. It uses an alert-then-block workflow, Suricata rule analysis, and flow log correlation to confirm which traffic is safe before changing enforcement.

## When to Activate

- Legitimate application traffic is being dropped and Network Firewall is a suspected cause.
- Network Firewall alert logs show a high volume of alerts on known-good flows.
- A stateful rule group is blocking traffic that should be allowed.
- A domain-based rule is blocking a required destination.
- A team requests safe tuning of Suricata rules or rule group capacity is near its limit.

## Step 1: Confirm the firewall is the drop point

- Enable and inspect Network Firewall logging: alert logs and flow logs delivered to CloudWatch Logs, S3, or Kinesis Data Firehose.
- Correlate the dropped flow (5-tuple: source IP, source port, destination IP, destination port, protocol) between VPC Flow Logs and Network Firewall flow logs to confirm the drop originates at the firewall and not a security group or NACL.
- Identify whether the drop came from the stateless engine (default action or a stateless rule) or the stateful engine (a Suricata rule action of "drop" or "reject").

## Step 2: Analyze the triggering Suricata rule

- From the alert log, extract the signature ID (sid), message (msg), and rule action for the matched rule.
- Determine whether the rule belongs to a managed rule group (AWS managed threat signatures) or a customer-defined rule group. For managed rule groups, you cannot edit the rule text; you override it instead.
- Assess whether the match is a true positive or a false positive by examining the flow context: destination reputation, expected application behavior, and whether the pattern matches known-good traffic.

## Step 3: Apply the alert-then-block workflow

- Before blocking, run new or suspected-noisy rules in alert mode (Suricata action "alert") so they log without dropping. Observe for a representative window (for example 24 to 72 hours).
- Review the alert volume and false-positive ratio. Only promote a rule from alert to drop once the false-positive rate is acceptable.
- For managed rule groups producing false positives, use rule group override to set the action order or override specific signatures to alert instead of drop, rather than disabling the whole group.

## Step 4: Tune stateful rule ordering and allowlists

- Confirm the stateful engine rule evaluation order. In strict order, rules are evaluated top to bottom and the first match wins, so a broad allow placed above a specific drop can nullify the drop. In default action order, pass rules are evaluated before drop and alert.
- For a required destination blocked by domain filtering, add the fully qualified domain name to a domain allowlist rule group (using an allow list with the specific domains) rather than switching the default to allow-all.
- Prefer narrow allowlist entries (exact domains or specific CIDRs and ports) over broad exceptions so the tuning does not open unintended paths.

## Step 5: Manage rule group capacity

- Each stateful rule group has a fixed capacity that is set at creation and cannot be increased in place; capacity is consumed by the number and complexity of rules.
- Check current capacity usage before adding rules. If a group is near its ceiling, create a new rule group and attach it to the firewall policy rather than overpacking one group.
- Remove obsolete or duplicate rules to reclaim capacity and reduce evaluation overhead.

## Step 6: Validate the change safely

- After tuning, re-run the previously dropped flow and confirm it passes, then confirm that known-bad test patterns are still dropped so the security posture is intact.
- Keep the affected rule in alert mode briefly after promoting changes to catch any regression, then re-enable drop.

## Output

Produce a Network Firewall Tuning Report containing: the confirmed drop point with the correlated 5-tuple, the triggering signature ID and rule group (managed or custom), the false-positive assessment, the specific tuning applied (rule override to alert, domain allowlist entry, or rule reordering) with justification, rule group capacity status, and the validation result confirming legitimate traffic passes while threat detection remains active. Include a rollback note for each change.