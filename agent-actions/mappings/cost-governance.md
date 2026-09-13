# Cost governance and account contact finding to directed action mappings

This file maps the read-only COST-GOVERNANCE and ACCOUNT-CONTACT findings produced by the auditor agents in this repository to the specific AWS DevOps Agent directed action that remediates each one. A directed action is a single mutating API operation the agent runs via the use_aws tool, only after an operator approves it in chat, under a scoped elevated IAM role. Most remediations here are additive safety-net controls (creating a monitor, a budget, a notification, or setting a contact), so they rate low-risk YELLOW; but several account-management writes execute only if account:* is inside the elevated-role ceiling, and every teardown is a delete-class step that stays manual.

## No Cost Anomaly Detection monitor

| Field | Value |
| --- | --- |
| Read-only finding | The account has no AWS Cost Anomaly Detection monitor, so unexpected spend spikes are never detected. |
| Source | 267-cost-protection-controls-enablement-auditor |
| Directed action | ce:CreateAnomalyMonitor |
| Parameters | Create an AWS-services dimensional monitor (MonitorType=DIMENSIONAL, MonitorDimension=SERVICE) so spend anomalies are tracked per service. This is additive; nothing existing is modified. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Removing the monitor uses ce:DeleteAnomalyMonitor, which is a delete-class operation the agent refuses. Teardown is therefore a manual/human step performed later with a human's own credentials. |
| Notes | Creating the monitor only enables detection; alerting requires a subscription (see the next finding). No PassRole is involved. Verify by listing anomaly monitors. |

## Monitor exists but no subscription (detects, never alerts)

| Field | Value |
| --- | --- |
| Read-only finding | A Cost Anomaly Detection monitor exists but has no subscription, so anomalies are detected but no one is ever alerted. |
| Source | 267-cost-protection-controls-enablement-auditor |
| Directed action | ce:CreateAnomalySubscription |
| Parameters | Create a subscription with a spend threshold expression and a monitored recipient (an email address, or an existing SNS topic referenced by ARN) tied to the existing monitor. This is additive. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Removing the subscription uses ce:DeleteAnomalySubscription, a delete-class operation the agent refuses; teardown is a manual/human step. |
| Notes | The SNS topic must already exist - the subscription references the topic ARN, which is not a PassRole. Verify by listing anomaly subscriptions on the monitor. |

## No AWS Budget / no cost budget with notifications

| Field | Value |
| --- | --- |
| Read-only finding | The account has no AWS Budget, or no cost budget configured with notifications, so there is no spend guardrail. |
| Source | 267-cost-protection-controls-enablement-auditor |
| Directed action | budgets:CreateBudget |
| Parameters | Create a monthly cost budget (BudgetType=COST, TimeUnit=MONTHLY) with both actual and forecast NotificationsWithSubscribers pointing at a monitored destination (a role-based email alias or an existing SNS topic ARN). This is additive. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Removing the budget uses budgets:DeleteBudget, a delete-class operation the agent refuses; teardown is a manual/human step. |
| Notes | The first two budgets per account are free. Verify by describing budgets for the account. |

## Budget exists but no notification subscribers

| Field | Value |
| --- | --- |
| Read-only finding | A budget exists but has no notification subscribers, so thresholds are tracked but no alerts are ever delivered. |
| Source | 267-cost-protection-controls-enablement-auditor |
| Directed action | budgets:CreateNotification followed by budgets:CreateSubscriber |
| Parameters | Add actual and forecast notifications to the existing budget and attach a monitored subscriber (an email address or an existing SNS topic ARN). Both operations are additive. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Removing an alert uses budgets:DeleteNotification / budgets:DeleteSubscriber, which are delete-class operations the agent refuses; note that removing an alert is delete-class, so teardown is a manual/human step. |
| Notes | Two operations, each individually approved. Verify by describing the budget's notifications and subscribers. |

## RIs/SPs with no utilization or coverage budget

| Field | Value |
| --- | --- |
| Read-only finding | The account holds Reserved Instances or Savings Plans but has no utilization/coverage budget, so under-used commitments go unnoticed. |
| Source | 267-cost-protection-controls-enablement-auditor |
| Directed action | budgets:CreateBudget |
| Parameters | Create a budget of BudgetType=RI_UTILIZATION or SAVINGS_PLANS_UTILIZATION with actual/forecast notifications to a monitored destination so low utilization triggers an alert. This is additive. |
| Guardrail status | allowed |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Removing the budget uses budgets:DeleteBudget, a delete-class operation the agent refuses; teardown is a manual/human step. |
| Notes | Utilization/coverage budgets require Cost Explorer data to be available. Verify by describing the created budget. |

## Cost Explorer not enabled

| Field | Value |
| --- | --- |
| Read-only finding | Cost Explorer is not enabled on the account, so cost and usage analysis (and several budget types) are unavailable. |
| Source | 267-cost-protection-controls-enablement-auditor |
| Directed action | None executable - enabling Cost Explorer is an account/console action, not a clean mutating API the agent can call |
| Parameters | Not applicable. There is no stable single mutating API operation the agent can approve and run to enable Cost Explorer. |
| Guardrail status | refused-manual |
| Safety | Not applicable - the agent does not execute a directed action here |
| Approval scope | Not applicable |
| Rollback | Not applicable - no agent action is taken. |
| Notes | Remediation stays manual: a human enables Cost Explorer from the Billing console. Once enabled, the anomaly-detection and budget directed actions above become usable. |

## Missing alternate contact (BILLING/OPERATIONS/SECURITY not set)

| Field | Value |
| --- | --- |
| Read-only finding | One or more alternate contacts (BILLING, OPERATIONS, or SECURITY) is not set on the account, so critical notices may not reach a monitored destination. |
| Source | 268-account-alternate-contacts-and-notification-consolidation-auditor |
| Directed action | account:PutAlternateContact |
| Parameters | Set the missing alternate contact type to a role-based monitored alias (a shared team address, not a personal individual). Reference contact PII by field name; do not echo full values. |
| Guardrail status | allowed-if-ceiling-permits |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Restore the prior state with account:PutAlternateContact using the previous value, or account:DeleteAlternateContact if the contact was previously unset. |
| Notes | account:* is an account-management API commonly EXCLUDED from the elevated-role ceiling (like iam and organizations), so it is marked allowed-if-ceiling-permits and is frequently manual. Contact PII is HIGH sensitivity - do not echo full values in chat or logs. Verify by reading the alternate contact for that type. |

## Alternate contact set to a stale personal individual

| Field | Value |
| --- | --- |
| Read-only finding | An alternate contact is set to a stale personal individual (for example a former employee) rather than a durable role-based alias. |
| Source | 268-account-alternate-contacts-and-notification-consolidation-auditor |
| Directed action | account:PutAlternateContact |
| Parameters | Replace the stale contact with a role-based monitored alias for the same contact type. Reference contact PII by field name; do not echo full values. |
| Guardrail status | allowed-if-ceiling-permits |
| Safety | YELLOW |
| Approval scope | single-use |
| Rollback | Re-run account:PutAlternateContact with the prior value captured before the change. |
| Notes | Same classification as a missing contact: account:* is often excluded from the elevated-role ceiling, so this is allowed-if-ceiling-permits and frequently manual. Contact PII is HIGH sensitivity - do not echo full values. Verify by reading the alternate contact for that type. |

## Primary / root account email stale

| Field | Value |
| --- | --- |
| Read-only finding | The primary (root) account email is stale or points to an unmonitored address. |
| Source | 268-account-alternate-contacts-and-notification-consolidation-auditor |
| Directed action | None executable - the root account email cannot be changed via a directed action |
| Parameters | Not applicable. Changing the root email requires root sign-in and is not exposed as a directed-action API. |
| Guardrail status | refused-manual |
| Safety | Not applicable - the agent does not execute a directed action here |
| Approval scope | Not applicable |
| Rollback | Not applicable - no agent action is taken. |
| Notes | Remediation stays manual: a human with root access updates the primary account email through the console. The agent's role is limited to detecting and reporting the stale email. |

## Refused and manual remediations

The following findings above do not resolve to an executable directed action, or resolve to one only under a ceiling condition, and otherwise stay a manual step:

- Teardown of any created control - ce:DeleteAnomalyMonitor, ce:DeleteAnomalySubscription, budgets:DeleteBudget, budgets:DeleteNotification, and budgets:DeleteSubscriber are all delete-class operations the agent always refuses, even with approval. Removing a monitor, subscription, budget, notification, or subscriber (including removing an alert) is therefore a manual/human step. Creation of these controls is allowed and executable; only their removal is refused-delete-class.
- Cost Explorer enablement (267-cost-protection-controls-enablement-auditor) - refused-manual. There is no clean single mutating API for the agent to approve and run; a human enables Cost Explorer from the Billing console.
- Alternate-contact writes (268-account-alternate-contacts-and-notification-consolidation-auditor) - allowed-if-ceiling-permits. account:PutAlternateContact and account:DeleteAlternateContact execute only if account management is inside the elevated-role ceiling; where account:* is excluded (as it commonly is, like iam and organizations) the write stays manual. Contact PII is HIGH sensitivity and must always be referenced masked, never echoed in full.
- Primary/root account email (268-account-alternate-contacts-and-notification-consolidation-auditor) - refused-manual. The root account email cannot be changed via a directed action and requires root sign-in; a human performs the change.

For the executable findings (creating a Cost Anomaly Detection monitor and subscription, creating cost and utilization/coverage budgets, and adding budget notifications and subscribers), the directed action is allowed and additive under per-action operator approval, with teardown documented as a manual delete-class step. The alternate-contact writes are executable only when account management is inside the elevated-role ceiling.
