---
name: mediapackage-origin-and-packaging-health
agent_type: "Incident RCA"
description: Diagnoses AWS Elemental MediaPackage origin and packaging problems
  by analyzing origin endpoint 4xx and 5xx egress errors, egress response time
  latency, ingress health, packaging and endpoint configuration, and input
  switching between redundant ingest sources. Use this skill when playback
  fails or stalls, the CDN reports errors from the MediaPackage origin, egress
  latency spikes, or ingest from the upstream encoder is failing.
version: "1.0.0"
last_updated: "2026-08-14"
---

# MediaPackage Origin and Packaging Health

Use this skill to systematically diagnose why AWS Elemental MediaPackage is
serving errors or high-latency responses, separate ingest problems from
packaging and egress problems, correlate with the upstream MediaLive channel,
and recommend targeted remediation. Posture is read-only: inspect metrics and
configuration first, then propose specific fixes.

## When to Activate

- The CDN or players report 4xx or 5xx errors coming from the MediaPackage
  origin endpoint.
- CloudWatch AWS/MediaPackage EgressResponseTime rises above its baseline.
- Manifest or segment requests fail intermittently during a live event.
- IngressBytes drops toward 0, indicating the encoder stopped delivering.
- Input switching occurred between two ingest endpoints on a channel.
- Playback stalls or rebuffers while the upstream encoder appears healthy.

## Step 1: Measure Egress Error Rate and Response Time

Start at the endpoint that the CDN pulls from.

1. In CloudWatch AWS/MediaPackage, evaluate per OriginEndpoint (and per Channel
   where dimensioned) over the incident window:
   - EgressRequestCount (SUM, 1-minute): total requests the origin served.
   - Origin 4xx count and 5xx count (SUM): client-side versus server-side
     errors. Compute error ratio as errors / EgressRequestCount.
   - EgressResponseTime (Average and p90): time to serve manifest and segment
     requests. Rising latency points at origin load, ingest gaps, or packaging
     work per request.
2. Split 4xx from 5xx; they mean different things.

| Error Class | Typical Cause | Where to Look |
|-------------|---------------|---------------|
| 404 Not Found | Segment or manifest not yet available or aged out | Ingest gap, startover/DVR window, timing skew |
| 403 Forbidden | Request lacks required auth or signature | CDN auth, endpoint whitelist/CDN identifier |
| 400 Bad Request | Malformed manifest or segment request | Endpoint packaging config, player request |
| 5xx | Origin cannot produce a response | Ingest loss, packaging error, origin overload |

3. A rising 404 rate on a live endpoint almost always means the origin has no
   fresh segments to serve, which redirects the investigation to ingest
   (Step 2) and the upstream encoder (Step 4).

## Step 2: Check Ingress Health

Confirm that content is actually arriving at MediaPackage.

1. In CloudWatch AWS/MediaPackage, evaluate per Channel:
   - IngressBytes (SUM, 1-minute): bytes received from the upstream encoder. A
     drop toward 0 means ingest has stopped.
   - IngressResponseTime where available: latency of accepting ingest.
2. List channels and endpoints with use_aws (mediapackage ListChannels, then
   ListOriginEndpoints for the channel). Capture:
   - The two ingest endpoints on the channel (MediaPackage provides redundant
     ingest URLs) and their HlsIngest or ingest settings.
   - Whether both ingest paths or only one is receiving data.
3. Correlate IngressBytes timing with the egress errors from Step 1. If
   IngressBytes fell just before egress 404/5xx rose, the root cause is
   upstream, not in MediaPackage packaging.

## Step 3: Validate Endpoint and Packaging Configuration

Rule out packaging or endpoint misconfiguration as the fault.

1. From ListOriginEndpoints and the endpoint detail, review the active
   packaging type and its settings:
   - HLS (HlsPackage): SegmentDurationSeconds, PlaylistWindowSeconds,
     PlaylistType, ad markers.
   - DASH (DashPackage): SegmentDurationSeconds, ManifestWindowSeconds,
     MinBufferTimeSeconds, profile.
   - CMAF or Microsoft Smooth settings where used.
2. Check the window and segment settings against the symptom:
   - A PlaylistWindowSeconds or ManifestWindowSeconds shorter than the CDN
     cache or player buffer can cause 404s on segments that aged out.
   - StartoverWindowSeconds governs DVR/startover availability; requests
     outside the window return 404 by design.
3. Confirm access controls without weakening them:
   - CDN authorization (for example, a CDN identifier secret) must match
     between the CDN and the endpoint; a mismatch yields 403. Fix by aligning
     the shared secret, not by removing authorization.
   - Do not open the endpoint publicly or remove CDN authorization to clear
     403s.

## Step 4: Correlate With Upstream MediaLive

Trace the fault to its true origin when ingest is the problem.

1. If IngressBytes dropped, inspect the feeding MediaLive channel: confirm it is
   RUNNING, check ActiveAlerts, InputLossSeconds, and whether a pipeline failed
   over (see the MediaLive channel and input health skill).
2. MediaLive STANDARD channels feed both MediaPackage ingest endpoints (one per
   pipeline). If only one ingest path lost data, the corresponding MediaLive
   pipeline is the suspect while the other keeps the stream alive.
3. Align timestamps across the chain: source loss at the contribution encoder
   propagates to MediaLive InputLossSeconds, then to MediaPackage IngressBytes,
   then to egress 404/5xx. Establishing this timeline confirms the root cause
   is upstream of MediaPackage.

## Step 5: Assess Input Switching

Understand redundancy behavior on the channel.

1. MediaPackage accepts two redundant ingest inputs and switches to the healthy
   one when a source degrades. Determine whether a switch occurred during the
   incident window.
2. If input switching happened cleanly, egress should have stayed healthy on
   the surviving input; a brief blip is expected at the switch point.
3. If both ingest inputs degraded at once, no switch can help; the fault is a
   shared upstream cause (single MediaLive source, contribution network).

## Step 6: Remediate

Match the fix to the confirmed root cause. Keep changes specific.

- Ingest stopped (IngressBytes at 0): repair the upstream MediaLive channel or
  contribution source; MediaPackage recovers egress once fresh segments arrive.
- One ingest path lost on a redundant channel: repair the corresponding
  MediaLive pipeline; leave the surviving path serving traffic.
- 404 from short windows: increase PlaylistWindowSeconds or ManifestWindowSeconds
  and StartoverWindowSeconds to cover the CDN cache and player buffer needs.
- 403 from auth mismatch: realign the CDN authorization secret between the CDN
  and the endpoint; do not disable authorization.
- Elevated EgressResponseTime from origin load: front the origin with a CDN and
  confirm cache hit ratio so repeat requests are served from edge, not origin.
- Packaging misconfiguration (400): correct the specific HLS or DASH setting
  identified in Step 3 and validate with a test player.

## Output

Provide a diagnosis summary:
1. Root cause category: ingest loss (upstream), packaging or window
   misconfiguration, CDN authorization mismatch, origin overload, or clean
   input-switch blip.
2. Supporting evidence: egress 4xx and 5xx ratio against EgressRequestCount,
   EgressResponseTime trend, IngressBytes trend, and the correlated timeline
   with the upstream MediaLive channel.
3. Which channel and origin endpoint were affected and whether input switching
   occurred.
4. Specific remediation steps tied to the confirmed cause.
5. Preventive measures: CloudWatch alarms on IngressBytes drop, egress 5xx
   rate, and EgressResponseTime, plus CDN caching and redundant ingest
   validation.
