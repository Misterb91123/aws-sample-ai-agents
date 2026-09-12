---
name: ml-model-drift-monitor
agent_type: "Generic"
description: Monitor deployed machine learning models for data drift and quality degradation using Amazon SageMaker Model Monitor. I use this skill to compare live traffic against a baseline, classify data quality and model quality violations, assess feature attribution drift, and decide when retraining is warranted. I activate it when model predictions degrade, input data distributions shift, or monitoring schedules report constraint violations.
version: "1.0.0"
last_updated: "2026-08-14"
---

# ML Model Drift Monitor

This skill provides a procedure for detecting and responding to drift in deployed machine learning models using Amazon SageMaker Model Monitor. It compares live inference data against an established baseline, categorizes violations by type and severity, and translates findings into retraining or alerting actions.

## When to Activate

- Downstream metrics indicate model predictions are degrading in production.
- Input feature distributions shift relative to the training set.
- A SageMaker Model Monitor scheduled run reports constraint violations.
- Feature attribution or explainability reports change materially between runs.
- Business stakeholders report declining accuracy, precision, or recall.

## Step 1: Confirm Baseline and Monitoring Setup

Verify the monitoring foundation is in place:

- A baseline was generated from a representative dataset, producing statistics.json and constraints.json in the configured S3 location.
- Data capture is enabled on the endpoint so live requests and responses are recorded to S3.
- A monitoring schedule exists (hourly or daily) and points at the captured data and the baseline constraints.

## Step 2: Compare Live Data Against Baseline

For the most recent monitoring execution, load the produced statistics and compare them against the baseline:

- Feature-level distribution shifts using the baseline constraints (mean, standard deviation, and distribution distance measures).
- Flag features whose live distribution diverges beyond the baseline-defined thresholds.

## Step 3: Classify Data Quality Violations

Data quality monitoring detects schema and distribution problems. Classify each violation:

- Missing features: expected columns absent from live records.
- Type mismatches: a feature arriving as a different data type than the baseline.
- Range or completeness violations: values outside baseline min/max, or null rates above the baseline completeness threshold.

These often indicate upstream data pipeline breakage rather than genuine model drift, and should be triaged first.

## Step 4: Assess Model Quality Degradation

If model quality monitoring is configured (which requires ground-truth labels merged with predictions), compare live metrics against baseline:

- Regression metrics such as MAE or RMSE.
- Classification metrics such as accuracy, precision, recall, and F1.

Flag metrics that degrade beyond the configured threshold (for example accuracy dropping more than 5 percentage points from baseline). Genuine, sustained degradation is a strong retraining signal.

## Step 5: Evaluate Feature Attribution Drift

If SageMaker Clarify explainability monitoring is enabled, compare the live feature attribution ranking against the baseline. A large change in which features drive predictions indicates concept drift even when input distributions look stable. Use the normalized discounted cumulative gain (NDCG) comparison Clarify produces to quantify the shift.

## Step 6: Review Schedule Execution and Severity

Check the monitoring schedule execution status:

- Confirm executions are Completed rather than Failed or Stopped; failed executions leave blind spots.
- Read the constraint_violations.json output and rank violations by severity and by the number of records affected.
- Distinguish transient single-run violations from persistent multi-run trends.

## Step 7: Set Alerting and Retraining Triggers

Translate findings into automated action:

- Route violation events (via CloudWatch and EventBridge) to notify the owning team when thresholds are breached.
- Define retraining triggers: for example, sustained data drift on key features across N consecutive runs, or model quality dropping below an agreed floor.
- For data quality violations rooted in pipeline errors, trigger a data pipeline fix rather than retraining.

## Output

The skill produces a drift assessment report containing: a baseline-versus-live comparison summary, a classified list of data quality violations (missing, type mismatch, range/completeness), a model quality metric comparison against baseline where labels exist, a feature attribution drift finding, monitoring schedule execution health, a severity-ranked violation list, and a recommendation on whether to fix the data pipeline, retrain the model, or continue monitoring.