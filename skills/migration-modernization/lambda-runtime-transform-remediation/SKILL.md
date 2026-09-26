---
name: lambda-runtime-transform-remediation
agent_type: "Generic"
description: Drives an end-to-end, human-gated remediation for AWS Lambda
  functions on deprecated or soon-to-be-deprecated runtimes, starting from the
  Trusted Advisor "deprecated or about-to-be-deprecated runtime" finding and using
  AWS Transform to assess, transform, and verify the language-version upgrade. Use
  this skill to turn a Trusted Advisor deprecated-runtime list into a prioritized,
  deadline-aware remediation plan with an AWS Transform job per function or
  repository, explicit human approval gates, verification, and a rollback plan for
  each function. Read-only and plan-only: it proposes and sequences the work; it
  does not modify functions or code itself.
version: "1.0.0"
last_updated: "2026-09-12"
metadata:
  version: "1.0"
  author: solair
---

# Lambda Runtime Transform Remediation

Use this skill to close the loop on Lambda deprecated-runtime findings: detect
from Trusted Advisor, plan the fix, and orchestrate the code upgrade through AWS
Transform with a human in the loop at every gate. A runtime bump is not a config
toggle - the code often needs syntax and dependency changes for the new language
version, which is exactly what AWS Transform automates. This skill sequences that
work safely; it never applies a change on its own.

## Sources

Read-only. Reasons over data the platform surfaces plus AWS-native reads.

- Trusted Advisor via the Support API (use_aws): the Lambda "Use of deprecated (or
  about to be deprecated) Runtime" check result, which lists the flagged
  functions. Requires a Business or Enterprise Support plan; fall back to the
  Lambda deprecated-runtime data and AWS Health notifications where the Support
  API is not entitled.
- Lambda (use_aws): ListFunctions and GetFunction/GetFunctionConfiguration for the
  runtime, last-modified, package type (Zip vs Image), and code signals.
- CloudWatch (use_aws): Invocations and error metrics to separate hot production
  functions from idle ones for prioritization.
- AWS Transform: the AWS-managed language-version-upgrade transformations (for
  example the Python, Java, and Node.js version upgrades) that analyze code,
  update syntax, adjust dependencies, and validate the result. This skill plans
  and references Transform jobs; a human starts and approves them.
- Source control association (where connected) to locate the function's repository
  for the Transform job.

## Method

1. Detect. Read the Trusted Advisor deprecated-runtime check result and cross-check
   with Lambda to build the authoritative list of functions on a deprecated or
   soon-to-be-deprecated runtime, including the $LATEST runtime per function.
2. Classify against the deprecation phases and compute the deadline: Phase 1
   (create blocked, no security patches; update and rollback still allowed) and
   Phase 2 (update blocked). Compute days-to-phase from the AWS published runtime
   deprecation dates; mark any runtime without a valid published date as
   "deprecation unknown" rather than assigning a placeholder.
3. Prioritize by deadline proximity, then by production criticality (invocation
   volume and whether the function is on a customer-facing path), so the functions
   closest to Phase 2 on hot paths lead.
4. Plan the assessment (AWS Transform). For each function or its repository, define
   an AWS Transform assessment that identifies the target runtime, the code and
   dependency changes required, and the risk and effort. Group functions that
   share a repository into one Transform job where that is more efficient.
5. Plan the transformation (AWS Transform, human-approved). Specify the AWS-managed
   upgrade transformation and the target runtime (for example Python 3.9 to a
   supported version). The plan states that a human reviews the assessment and
   approves before the transformation runs, and reviews the resulting code change
   (pull request) before it merges - Transform proposes the code change; a person
   approves it.
6. Plan the verification (AWS Transform + release testing). Define how the upgrade
   is validated: Transform's own validation, plus the team's tests and, where
   available, release testing against the deployed function, before the new runtime
   is promoted.
7. Plan the deploy and the rollback for each function. Because Phase 1 still allows
   updates and rollbacks, the runtime can be moved forward and, if verification
   fails, rolled back to the previous runtime and code version (previous published
   version or prior image tag). State the rollback explicitly per function.
8. Note the config-only vs code-change split. Bumping the runtime identifier is a
   lambda UpdateFunctionConfiguration change; when the code needs language changes
   first, the config bump must follow the approved, verified Transform output - do
   not bump the runtime ahead of the code.

## Human-in-the-loop and safety

- Every mutating step is human-approved: approve the assessment, approve the
  transformation, review and merge the code change, and approve the deploy. The
  agent and this skill produce the plan and the evidence; a person acts.
- Container-image functions (package type Image) upgrade by rebuilding the base
  image to a supported version through the same Transform-assisted code upgrade,
  then publishing a new image tag; the rollback is the prior image tag.
- Custom runtimes (provided.*) are not AWS-managed language upgrades; flag them for
  a manual base-image or runtime path rather than an AWS-managed transformation.

## Output

Produce a remediation plan:

1. Detection summary: functions on deprecated or soon-to-be-deprecated runtimes
   from Trusted Advisor, with the $LATEST runtime and phase per function.
2. Deadline and priority table: days to Phase 1 and Phase 2, invocation-based
   criticality, and the resulting priority.
3. Per-function (or per-repository) remediation: the AWS Transform assessment and
   transformation to run, the target runtime, the approval gates, the verification
   steps, and the explicit rollback plan.
4. Config-vs-code note per function: whether it is a straight runtime bump or needs
   a code upgrade first, and for image and custom runtimes the correct path.
5. Issues encountered: missing Support entitlement, runtimes with no published
   date, functions whose repository could not be located, and any custom runtimes
   requiring a manual path.

State clearly that this is a plan: AWS Transform jobs, code merges, and runtime
deploys are all started and approved by a human, and every function carries a
rollback.
