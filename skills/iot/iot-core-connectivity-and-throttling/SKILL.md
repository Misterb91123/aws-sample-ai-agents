---
name: iot-core-connectivity-and-throttling
agent_type: "Incident RCA"
description: Provides investigation procedures for AWS IoT Core device connectivity
  and message-broker throttling incidents, including MQTT connect failures, auth
  rejections, publish/subscribe throttling, and reconnect storms from duplicate
  client IDs. Use this skill when devices cannot connect or stay connected, when
  Connect.AuthError or Connect.Throttle rise, when Throttle.Exceeded or
  PublishIn.Throttle appear, or when the fleet enters a reconnect storm.
version: "1.0.0"
last_updated: "2026-08-14"
---

# IoT Core Connectivity and Throttling

Use this skill to diagnose and resolve AWS IoT Core connectivity failures and
message-broker throttling that prevent devices from connecting or exchanging
messages. Posture is read-only investigation; recommend specific, least-change
fixes only.

## When to Activate

- Devices fail to establish MQTT connections (CONNACK rejected or timeouts).
- CloudWatch AWS/IoT metric Connect.AuthError or Connect.ClientError is rising.
- Connect.Throttle, PublishIn.Throttle, Subscribe.Throttle, or Throttle.Exceeded
  are non-zero.
- Fleet-wide reconnect storm suspected (rapid connect/disconnect cycling).
- Devices connect but cannot publish or subscribe to expected topics.
- Sudden disconnects with DUPLICATE_CLIENTID or MQTT_KEEP_ALIVE_TIMEOUT reasons.

## Step 1: Classify the Failure Domain

Determine whether the problem is at connect, publish, or subscribe. Pull the
AWS/IoT namespace metrics in CloudWatch (Sum statistic, 1-minute period) and
compare success vs error/throttle counts.

| Symptom | Key Metrics | Likely Domain |
|---------|-------------|---------------|
| Cannot connect | Connect.Success down, Connect.AuthError / Connect.ClientError / Connect.Throttle up | Connection layer |
| Connects then drops | Disconnect reason codes (DUPLICATE_CLIENTID, MQTT_KEEP_ALIVE_TIMEOUT, CONNECTION_LOST) | Session stability |
| Connected, publish fails | PublishIn.Success down, PublishIn.AuthError / PublishIn.Throttle up | Publish path / policy |
| Connected, no messages received | Subscribe.Success down, Subscribe.AuthError / Subscribe.Throttle up | Subscription / policy |

Confirm the account data endpoint with `use_aws` calling iot DescribeEndpoint
(endpointType iot:Data-ATS) and verify devices target that ATS endpoint, not a
stale legacy endpoint.

## Step 2: Check Throttle Metrics Against Account Limits

IoT Core enforces per-account, per-region quotas. Map the elevated metric to the
relevant quota:

- Connect.Throttle / Throttle.Exceeded on connect: connections-per-second per
  account (default 500/s) and connect requests per second.
- PublishIn.Throttle: inbound publish requests per second (default 20000/s for
  the broker; message and per-connection limits also apply, e.g. per-connection
  publish 100 msg/s and inbound 512 KB max message).
- Subscribe.Throttle: subscriptions per second and subscriptions per connection
  (default 50 subscriptions per connection).

Procedure:
1. Graph the throttled metric (Sum) and overlay the matching success metric to
   compute a throttle ratio. A ratio above 1 percent sustained indicates a real
   quota pressure event.
2. Compare peak observed rate to the Service Quotas value for AWS IoT Core in the
   region. If observed peak approaches the quota, this is a capacity issue, not a
   defect.
3. Note whether throttling is broad (account-wide quota) or narrow (a single
   connection exceeding per-connection publish/subscribe rates), which points at
   one misbehaving device or firmware build.

## Step 3: Diagnose Authentication and Authorization Errors

Connect.AuthError, PublishIn.AuthError, and Subscribe.AuthError are distinct
signals. Auth errors are not throttling; do not treat them as capacity.

1. Enable or read IoT logging config with iot GetLoggingOptions (or v2 logging).
   Look in CloudWatch Logs group AWSIotLogsV2 for eventType CONNECT, PUBLISH, and
   SUBSCRIBE with status FAILURE and reason codes.
2. Connect.AuthError causes to distinguish:
   - Certificate INACTIVE, REVOKED, or not attached to a policy.
   - TLS failure (client did not present a cert, wrong CA, clock skew on device
     causing cert notBefore/notAfter validation failure).
   - Custom authorizer returned Deny or errored.
3. PublishIn.AuthError / Subscribe.AuthError causes: the attached IoT policy does
   not allow iot:Publish / iot:Subscribe / iot:Receive on the exact topic ARN, or
   policy variables (for example iot:Connection.Thing.ThingName) do not match.
4. Use iot ListCertificates and DescribeCertificate to confirm the device cert
   status is ACTIVE. Reference certificate IDs only; never read or echo private
   key material.

Recommended fix pattern: correct the IoT policy to grant the minimum required
topic-scoped permissions (specific topic and topicfilter ARNs). Do not grant
wildcard `iot:*` or `Resource: *`.

## Step 4: Detect Reconnect Storms and Duplicate Client IDs

A reconnect storm shows as high Connect.Success churn paired with disconnects
carrying DUPLICATE_CLIENTID. MQTT allows one active session per client ID; a
second device using the same client ID forcibly disconnects the first, which then
reconnects, repeating in a loop.

Procedure:
1. In AWSIotLogsV2, filter disconnectReason = DUPLICATE_CLIENTID and aggregate by
   clientId. A small set of client IDs with high disconnect counts confirms the
   collision.
2. Cross-check that firmware sets a unique client ID per device (commonly the
   thing name or serial). Shared or hardcoded client IDs across a build are the
   usual root cause.
3. Rule out keep-alive misconfiguration: MQTT_KEEP_ALIVE_TIMEOUT disconnects with
   coordinated reconnect can mimic a storm. Verify device keep-alive interval is
   within the negotiated range (IoT Core supports 30 to 1200 seconds).
4. Estimate blast radius: reconnect storms amplify Connect.Throttle because each
   loop consumes connect quota, so a storm can trigger Step 2 throttling as a
   secondary effect.

## Step 5: Remediate

Match the confirmed root cause to a specific, least-change action:

| Root Cause | Recommended Fix |
|------------|-----------------|
| Account connect/publish quota reached at legitimate load | Request a Service Quotas increase for the specific IoT Core limit; smooth device connect jitter/backoff |
| Single connection exceeding per-connection publish rate | Fix firmware to batch or rate-limit publishes below 100 msg/s per connection |
| Certificate INACTIVE / not attached | Reactivate or reprovision the correct ACTIVE certificate and attach the scoped policy |
| Policy too narrow / topic mismatch | Update IoT policy to allow the exact required topic and topicfilter ARNs, least privilege |
| Duplicate client IDs | Assign unique client IDs (thing name or serial) per device in firmware |
| Device clock skew failing TLS | Correct device time sync (NTP) so cert validity checks pass |

Prohibited: do not disable IoT logging, do not widen policies to wildcards, and
do not open connectivity by removing authentication.

## Output

Provide:
1. Failure classification (connect vs publish vs subscribe; auth vs throttle vs
   session stability) with the specific AWS/IoT metrics observed.
2. Root cause with evidence (metric ratios, AWSIotLogsV2 reason codes, certificate
   or policy findings, duplicate client ID aggregation).
3. Specific least-privilege fix mapped to the root cause.
4. Prevention steps (unique client IDs, connect backoff, quota headroom
   monitoring, alarms on Connect.AuthError and Throttle.Exceeded).
