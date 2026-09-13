---
name: chime-sdk-media-session-quality
agent_type: "Incident RCA"
description: Provides investigation procedures for Amazon Chime SDK media session
  incidents including poor in-call quality from packet loss and jitter, WebRTC
  connection failures, attendee join errors, and meeting capacity limits. Use
  this skill when attendees cannot join meetings, when audio or video quality
  degrades mid-call, or when connection failures cluster during a session. All
  steps are read-only investigation and remediation targets network path,
  capacity sizing, and client configuration without disabling encryption or
  logging.

version: "1.0.0"
last_updated: "2026-08-14"
---

# Chime SDK Media Session Quality

Use this skill to diagnose Amazon Chime SDK meeting media quality problems and
join failures, then recommend safe remediation.

## When to Activate

- Attendees report choppy audio, frozen video, or robotic voice mid-call.
- Attendees fail to join meetings or drop shortly after joining.
- WebRTC connection setup fails or repeatedly renegotiates.
- A large meeting approaches or exceeds attendee capacity limits.
- Quality degrades for a subset of attendees on specific networks.

## Step 1: Classify Join Failure vs In-Call Quality

Separate connection establishment problems from media quality problems, since
they have different root causes.

| Symptom | Class | Direction |
|---------|-------|-----------|
| Cannot join, no media session starts | Join failure | Step 2 signaling and capacity |
| Joins then drops within seconds | Join failure | Step 3 WebRTC and network path |
| Joins fine, quality degrades over time | In-call quality | Step 3 packet loss and jitter |
| Only some attendees affected | Either | Correlate by network and client |

Read the meeting and attendee state via use_aws (read-only): Chime SDK Meetings
GetMeeting confirms the meeting exists and its MediaRegion; ListAttendees and
GetAttendee confirm whether the attendee was created and joined.

## Step 2: Check Capacity and Limits

Rule out capacity before deeper network analysis.

1. MediaRegion: confirm the meeting MediaRegion is close to the attendees. A
   distant MediaRegion increases round-trip time and packet loss.
2. Attendee capacity: standard meetings support up to 250 attendees; larger
   audiences require the appropriate meeting feature configuration. If join
   failures begin only past a threshold, capacity is the likely cause.
3. Account and API limits: creating meetings and attendees is subject to API
   rate limits. Throttling on CreateMeeting or CreateAttendee (visible as
   throttling errors in the application and correlated CloudWatch API metrics)
   causes join failures under burst load.

Decision:

| Finding | Cause |
|---------|-------|
| Failures start past attendee count limit | Capacity limit |
| CreateAttendee throttling under burst | API rate limit |
| MediaRegion far from attendees | Latency-driven quality and drops |

## Step 3: Check Media Metrics (Packet Loss and Jitter)

For in-call quality and post-join drops, examine WebRTC media statistics
collected from the client and any CloudWatch media metrics emitted for the
session.

Thresholds for interpretation:

| Metric | Good | Degraded | Poor |
|--------|------|----------|------|
| Packet loss | less than 1 percent | 1 to 5 percent | greater than 5 percent |
| Jitter | less than 30 ms | 30 to 50 ms | greater than 50 ms |
| Round-trip time | less than 100 ms | 100 to 250 ms | greater than 250 ms |

- Audio-specific symptoms (robotic voice, dropouts) usually track packet loss
  and jitter above the degraded band.
- Video freezes and resolution downgrades track sustained packet loss and
  constrained available bandwidth.
- WebRTC connection failures often show as ICE connection state failing before
  media flows, indicating the path could not be established.

## Step 4: Check the Network Path

Localize the impairment.

1. Determine whether affected attendees share a network, ISP, or geography. A
   cluster on one corporate network points to a local path issue.
2. Confirm the client can reach the Chime SDK media endpoints over the required
   UDP ports, with TCP fallback available. Blocked UDP forces TCP and raises
   latency and jitter.
3. Check for restrictive firewalls, VPNs, or proxies on affected clients that
   add hops and loss.
4. Compare MediaRegion to attendee location; a mismatch adds RTT that shows up
   as jitter and loss under load.

## Step 5: Remediate

Apply fixes to the localized cause. Never disable media encryption or session
logging.

Capacity and limits:
1. Select the correct meeting configuration for the audience size rather than
   forcing attendees past the standard limit.
2. Add retry with backoff on CreateMeeting and CreateAttendee, and request a
   targeted API rate increase if sustained burst demand is justified.

Network path and quality:
1. Set MediaRegion closest to the majority of attendees, or use the nearest
   region selection helper at join time.
2. Ensure the required UDP ports and endpoint ranges are allowed on affected
   networks so media does not fall back to TCP.
3. Advise affected clients to leave constrained VPNs or proxies for the session
   where policy allows.
4. Enable client-side adaptation (simulcast and bandwidth adaptation) so the
   client scales video down under loss rather than dropping.

Join failures:
1. For ICE failures, verify network reachability first, then confirm the
   attendee join token is fresh and used promptly after creation.

## Output

Provide:
1. Classification (join failure versus in-call quality) and the affected
   attendee scope.
2. Root cause with evidence (meeting and attendee state, capacity or API
   throttle findings, packet loss, jitter, and RTT values against thresholds,
   network path observations).
3. Specific remediation steps tied to the localized cause.
4. Prevention recommendations (MediaRegion selection, firewall and UDP port
   guidance, retry with backoff, monitoring on packet loss, jitter, and join
   failure rate).
