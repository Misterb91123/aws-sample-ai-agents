---
name: mediatailor-ad-insertion-health
agent_type: "Generic"
description: Evaluates AWS Elemental MediaTailor ad insertion and personalization
  health by analyzing ad decision server error and timeout rates, ad fill rate,
  avail duration mismatches, and personalized manifest generation errors. Use
  this skill when ad breaks show slates or blank avails, the ad decision server
  is slow or erroring, ad fill rate drops, or players report errors fetching
  personalized manifests from MediaTailor.
version: "1.0.0"
last_updated: "2026-08-14"
---

# MediaTailor Ad Insertion Health

Use this skill to systematically evaluate AWS Elemental MediaTailor ad
insertion and personalization, isolate whether the fault is in the ad decision
server (ADS), the avail signaling, or manifest generation, and recommend
targeted remediation. Posture is read-only: inspect metrics and playback
configuration first, then propose specific fixes.

## When to Activate

- Ad breaks play a slate or blank instead of ads (low or zero fill).
- CloudWatch AWS/MediaTailor AdDecisionServer.Errors or
  AdDecisionServer.Timeouts rise above baseline.
- The computed ad fill rate falls below its target.
- AvailDuration reported by MediaTailor does not match the ad content actually
  inserted (over-fill or under-fill of the avail).
- Players report errors fetching personalized manifests (GetManifest errors).
- Ad revenue or impression counts drop without a change in viewership.

## Step 1: Measure ADS Error and Timeout Rate

The ad decision server is the most common failure point.

1. In CloudWatch AWS/MediaTailor, evaluate per ConfigurationName over the
   incident window (SUM at 1-minute or 5-minute period):
   - AdDecisionServer.Ads: number of ads returned by the ADS.
   - AdDecisionServer.Errors: ADS responses that failed or were invalid.
   - AdDecisionServer.Timeouts: ADS calls that exceeded the configured timeout.
   - AdDecisionServer.Duration: latency of ADS responses.
2. Compute the ADS failure ratio as (Errors + Timeouts) divided by total ADS
   calls. A rising ratio directly reduces ad fill.
3. Distinguish the failure modes.

| ADS Signal | Reading | Likely Cause |
|------------|---------|--------------|
| High Timeouts, high Duration | ADS slow to respond | ADS overloaded or network latency to ADS |
| High Errors, low Duration | ADS returns fast failures | Bad VAST response, HTTP 4xx/5xx from ADS |
| Low Ads, no Errors | ADS returns empty | No campaign match, targeting or inventory gap |
| Normal Ads but low fill | Ads returned but not inserted | Avail or transcode mismatch (Step 3) |

## Step 2: Compute Ad Fill Rate

Quantify how much of the avail inventory is actually monetized.

1. Ad fill rate is the share of avail time (or avail slots) filled with real ads
   versus slate or blank. Approximate it from AdDecisionServer.Ads and
   AvailDuration against the ad content actually stitched in.
2. A low fill rate with a high ADS failure ratio (Step 1) means the ADS is the
   bottleneck: it is timing out or erroring before ads can be inserted.
3. A low fill rate with a healthy ADS means the ads were returned but could not
   be inserted, which redirects the investigation to avail signaling and
   transcode (Step 3).
4. Track fill rate over time and by ConfigurationName to see whether the drop is
   global or specific to one channel or content type.

## Step 3: Check Avail Signaling and Manifest Generation

Confirm that avails are signaled correctly and manifests build cleanly.

1. Compare AvailDuration (the duration MediaTailor was told the ad break is)
   against the duration of ads the ADS returned:
   - If returned ad duration is shorter than AvailDuration, the remainder shows
     slate (under-fill).
   - If longer, MediaTailor trims to fit the avail.
   A persistent mismatch means the SCTE-35 avail signaling or the ADS response
   duration is wrong.
2. Inspect manifest generation health:
   - GetManifest errors indicate players could not retrieve the personalized
     manifest. This is a delivery failure independent of ad availability.
   - Correlate GetManifest error timing with content origin health; MediaTailor
     proxies the origin manifest and personalizes it, so an origin problem
     surfaces here too.
3. Verify that ad creatives are transcoded to match the content stream
   (resolution, codec, segment structure). Ads that do not match the content
   profile cannot be stitched seamlessly and may be skipped, lowering fill even
   when the ADS returns valid ads.

## Step 4: Validate the Playback Configuration

Review the MediaTailor configuration that ties it all together.

1. Retrieve the configuration with use_aws (mediatailor ListPlaybackConfigurations,
   then GetPlaybackConfiguration for the ConfigurationName). Capture:
   - AdDecisionServerUrl: the ADS endpoint and its query template. Confirm the
     URL and required parameters (session, player, correlation macros) are
     present and correct.
   - VideoContentSourceUrl: the origin (for example, MediaPackage) MediaTailor
     personalizes from. Confirm it is reachable and healthy.
   - Timeout and retry behavior toward the ADS.
   - SlateAdUrl: the fallback slate shown when no ad fills the avail.
   - CDN configuration (content and ad segment prefixes) for delivery.
2. Check that the ADS URL template passes correct targeting macros; missing or
   malformed macros cause empty ADS responses (low Ads, no Errors from Step 1).
3. Confirm the VideoContentSourceUrl origin is the same one showing healthy
   egress; a degraded origin produces GetManifest errors regardless of ad
   health.

## Step 5: Remediate

Match the fix to the confirmed root cause. Keep changes specific.

- ADS timeouts: work with the ad server owner to reduce ADS response latency or
  scale the ADS; confirm network path latency to the ADS endpoint.
- ADS errors (bad VAST or HTTP failures): fix the ADS response format or the
  request template so the ADS returns valid ads.
- Empty ADS responses (low Ads): correct the targeting macros in the ADS URL
  template so campaigns match; confirm ad inventory exists.
- Avail duration mismatch: align SCTE-35 avail signaling with expected break
  duration, or ensure the ADS returns ads sized to the avail.
- Ad creative mismatch: transcode ad creatives to match the content profile so
  they stitch seamlessly.
- GetManifest errors: repair the VideoContentSourceUrl origin (for example, the
  MediaPackage endpoint) and confirm reachability.
- Frequent slate: use the ADS and avail findings above; the SlateAdUrl is a
  fallback, not a fix. Keep a valid slate configured so viewers never see a
  hard error during an unfilled avail.

## Output

Provide an evaluation summary:
1. Root cause category: ADS timeout, ADS error, empty ADS response, avail
   duration mismatch, ad creative mismatch, or manifest generation failure.
2. Supporting evidence: AdDecisionServer.Ads, AdDecisionServer.Errors,
   AdDecisionServer.Timeouts, AdDecisionServer.Duration, computed ad fill rate,
   AvailDuration versus inserted duration, and GetManifest error trend.
3. The affected playback configuration and its ADS and content source URLs.
4. Specific remediation steps tied to the confirmed cause.
5. Preventive measures: CloudWatch alarms on AdDecisionServer.Errors and
   Timeouts and on fill rate, ADS latency budgets, and a validated slate
   fallback so unfilled avails degrade gracefully.
