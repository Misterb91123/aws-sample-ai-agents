---
name: iot-fleetwise-ingestion-health
agent_type: "Generic"
description: Provides investigation procedures for AWS IoT FleetWise data
  collection health, including campaign status, vehicles not reporting,
  ingestion and signal decode errors, and signal catalog, model manifest, or
  decoder manifest issues. Use this skill when FleetWise campaigns stop delivering
  data, when a subset of vehicles goes silent, when decoded signals are missing or
  malformed, or when a manifest change correlates with an ingestion drop.
version: "1.0.0"
last_updated: "2026-08-14"
---

# IoT FleetWise Ingestion Health

Use this skill to diagnose and resolve AWS IoT FleetWise data collection and
ingestion problems across campaigns and vehicles. Posture is read-only
investigation; recommend specific, least-change fixes only.

## When to Activate

- A FleetWise campaign delivers no data or a reduced volume to its destination.
- A subset of vehicles stops reporting while others continue.
- Decoded signals are missing, malformed, or arrive with unexpected values.
- A signal catalog, model manifest, or decoder manifest change precedes a drop.
- Destination (Timestream or S3) shows a gap in FleetWise-delivered records.

## Step 1: List Campaigns and Status

1. Call iotfleetwise ListCampaigns via `use_aws` to enumerate campaigns with name,
   status, and the associated signalCatalogArn and targetArn (fleet or vehicle).
2. For each suspect campaign call iotfleetwise GetCampaign to read the full spec:
   collection scheme (time-based or condition-based), signalsToCollect, the
   dataDestinationConfigs (Timestream or S3), and compression/priority settings.
3. Interpret campaign status:

| Status | Meaning | Action |
|--------|---------|--------|
| RUNNING | Active and deployed | Expect data; if none, go to Step 2/3 |
| SUSPENDED | Paused | No data by design; confirm intent |
| WAITING_FOR_APPROVAL | Not yet approved | Approve to start collection |
| CREATING / DELETING | Transitional | Wait or confirm lifecycle intent |

4. Confirm the campaign is actually deployed to the intended fleet/vehicles and
   that the destination config points at the expected Timestream table or S3 path.

## Step 2: Check Vehicle Reporting Coverage

1. Enumerate the vehicles in the campaign target (the associated fleet) and call
   iotfleetwise GetVehicleStatus for each to read per-campaign status such as
   HEALTHY, SUSPENDED, DELETING, or READY, and the deployment/collection state.
2. Compute coverage = reporting vehicles / expected vehicles. A partial drop
   (some vehicles silent) points at those vehicles or their edge agent, not the
   campaign definition.
3. For silent vehicles, check whether the Edge Agent (running on the vehicle
   gateway) is connected to AWS IoT: verify the underlying thing certificate is
   ACTIVE and attached and the IoT policy permits the required publish topics.
4. Cluster silent vehicles by model manifest or decoder manifest to see if the
   gap aligns with a specific vehicle build.

## Step 3: Check Ingestion and Decode Error Signals

1. Review the campaign destination for arrival gaps: for Timestream, query the
   target table for the most recent ingestion timestamp per vehicle; for S3,
   check for the expected object partitions and their record counts.
2. FleetWise Edge Agent logs (on the vehicle gateway) record decode failures where
   a signal defined in the decoder manifest cannot be extracted from the network
   frame (for example a CAN signal whose message ID or bit layout does not match
   the actual bus). Missing or malformed signals with healthy connectivity point
   at decode, not transport.
3. Distinguish transport gaps (no records at all for a vehicle) from decode gaps
   (records arrive but specific signals are null or out of range). Transport gaps
   go to Step 2 connectivity; decode gaps go to Step 4.

## Step 4: Validate the Decoder and Model Manifest

1. Confirm the signal catalog, model manifest, and decoder manifest are ACTIVE and
   consistent. A campaign references signals by fully qualified name; if the model
   manifest omits a signal or the decoder manifest lacks a decoder for it, that
   signal will not be collected.
2. For decode gaps, verify the decoder manifest network interface and signal
   decoders match the vehicle bus reality: CAN message ID, start bit, length,
   scaling factor, and offset. A recent decoder manifest change with wrong scaling
   commonly yields malformed values.
3. Verify that the signals listed in the campaign signalsToCollect all exist in the
   model manifest and have a corresponding decoder. A mismatch here means the
   campaign silently collects nothing for those signals.
4. If a manifest change precedes the drop, treat that revision as the prime suspect
   and compare it against the last known-good manifest.

## Step 5: Remediate

| Root Cause | Recommended Fix |
|------------|-----------------|
| Campaign SUSPENDED or WAITING_FOR_APPROVAL | Approve/resume the campaign after confirming intent |
| Wrong or empty destination config | Point dataDestinationConfigs at the correct Timestream table or S3 location |
| Vehicle Edge Agent disconnected | Reactivate/attach the correct ACTIVE certificate and scoped IoT policy for the affected vehicles |
| Signal missing from model/decoder manifest | Add the signal and its decoder, publish a corrected manifest revision |
| Decoder scaling/offset/bit layout wrong | Correct the CAN decoder parameters and redeploy the decoder manifest |
| Campaign references non-existent signal | Fix signalsToCollect to match the model manifest |

Prohibited: do not disable FleetWise logging or destination encryption, do not
grant wildcard IAM to the FleetWise service or destination role, and do not open
public access on the S3 destination.

## Output

Provide:
1. Campaign inventory with status, destination, and deployment target.
2. Vehicle reporting coverage (reporting vs expected, clustering of silent
   vehicles) and whether the gap is transport or decode.
3. Root cause with evidence (vehicle status, destination arrival timestamps, decode
   error findings, manifest revision correlation).
4. Specific least-change fix (manifest correction or campaign/destination fix) and
   prevention steps (manifest validation before deploy, coverage alarms, decode
   error monitoring).
