---
name: lift-and-shift-assessment
agent_type: "Generic"
description: Assesses on-premises or legacy workloads for lift-and-shift migration
  to AWS by evaluating compute requirements, storage dependencies, network patterns,
  and compatibility constraints. Use this skill when planning initial migration
  waves, sizing target infrastructure, or when identifying workloads that are
  good candidates for rehosting vs those that need refactoring.
version: "1.0.0"
last_updated: "2026-08-14"
---

# Lift-and-Shift Assessment

Use this skill to evaluate workloads for direct migration (rehosting) to AWS
and identify potential blockers, sizing requirements, and migration sequencing.

## When to Activate

- Planning a migration wave and need to assess workload readiness.
- Sizing target AWS infrastructure for migrating workloads.
- Identifying workloads suitable for lift-and-shift vs refactoring.
- Post-discovery phase: translating inventory data into migration plans.
- Estimating migration effort and timeline for stakeholder planning.

## Step 1: Gather Source Workload Profile

Collect key characteristics of the source workload:

**Compute:**
- CPU cores and utilization pattern (peak, average, burst)
- Memory (RAM) allocated and utilized
- Operating system and version
- Architecture (x86_64, ARM)
- Virtualization technology (VMware, Hyper-V, bare metal)

**Storage:**
- Disk count, size, type (SSD/HDD), and IOPS requirements
- Storage protocols (block, file/NFS, object)
- Data volume (total, growth rate)
- Backup and snapshot requirements

**Network:**
- Bandwidth requirements (inbound/outbound)
- Latency sensitivity (real-time, interactive, batch)
- Protocols used (TCP, UDP, multicast)
- Static IPs or DNS-dependent configurations
- Firewall rules and network segmentation

**Dependencies:**
- Other servers/services this workload communicates with
- Shared storage (NAS, SAN) dependencies
- License-bound software (tied to hardware MAC, CPU count)
- External integrations (on-prem databases, LDAP, file shares)

## Step 2: Assess Migration Compatibility

Evaluate blockers and compatibility:

| Factor | Compatible (Lift & Shift) | Requires Modification |
|--------|--------------------------|----------------------|
| OS | Standard Linux/Windows supported on EC2 | Proprietary UNIX (AIX, HP-UX), old EOL OS |
| Licensing | BYOL or included in EC2 | License tied to physical hardware/MAC address |
| Storage | Block storage translates to EBS | Shared multi-host SAN with active-active clustering |
| Network | Standard TCP/IP | Multicast-dependent (cluster heartbeats), Layer 2 adjacency |
| Architecture | Standard x86_64 | Custom hardware (GPU, FPGA not available in target region) |
| Data gravity | < 5TB manageable via network transfer | Petabyte-scale (requires physical transfer - Snowball) |
| Latency | Can tolerate 1-5ms additional network latency | Sub-millisecond latency requirement to another system |

**Hard blockers for lift-and-shift:**
- Mainframe workloads (need re-platform or specialized tooling)
- Software with hardware dongles
- Multicast-dependent clustering without cloud alternatives
- Licensing that explicitly prohibits cloud deployment

## Step 3: Size Target AWS Resources

Map source specs to AWS resources:

**EC2 Instance Sizing:**
1. Match CPU cores to vCPUs (note: 1 physical core ~ 2 vCPUs with hyperthreading).
2. Match memory requirements to instance family.
3. Select instance family based on workload type:
   - Compute-optimized (C-family): high CPU, low memory ratio
   - Memory-optimized (R/X-family): high memory, databases
   - General purpose (M-family): balanced workloads
   - Storage-optimized (I/D-family): high IOPS or throughput

4. Consider burstable instances (T-family) for low average, periodic peak workloads.
5. Factor in headroom: size for p95 utilization, not average.

**EBS Volume Sizing:**
- Match IOPS: gp3 (3,000-16,000 IOPS), io2 (up to 64,000 IOPS)
- Match throughput requirements
- Consider gp3 as default (configurable IOPS and throughput, cheaper than gp2)

**Network:**
- Most instance types provide adequate bandwidth for typical workloads
- For high-bandwidth: choose instances with enhanced networking
- Consider placement groups for low-latency inter-instance communication

## Step 4: Identify Migration Sequence

Order workloads for migration based on:

**Migrate first (low risk, high learning):**
- Stateless web servers
- Development/test environments
- Non-critical batch processing
- Standalone applications with few dependencies

**Migrate mid-wave (moderate complexity):**
- Application servers with database dependencies
- Services with many integrations (after dependencies are migrated)
- Clustered applications

**Migrate last (high complexity/risk):**
- Databases with strict consistency requirements
- Core authentication/directory services
- Applications requiring extended cutover windows
- Workloads with regulatory constraints

## Step 5: Estimate Migration Effort

For each workload, estimate:

| Phase | Activities | Typical Duration |
|-------|-----------|-----------------|
| Preparation | Agent install, discovery validation, network prep | 1-2 weeks |
| Testing | Pilot migration, validate in AWS, performance test | 1-2 weeks |
| Migration | Data replication, cutover, DNS switch | Hours to days (depends on data volume) |
| Validation | Smoke tests, performance comparison, monitoring setup | 2-3 days |
| Optimization | Right-sizing, cost tuning, modernization planning | Ongoing |

## Step 6: Risk Assessment

For each workload, document:
1. **Cutover window**: How long can the application be down during migration?
2. **Rollback plan**: Can we fail back to source if migration has issues?
3. **Data sync strategy**: How to keep source and target in sync during migration?
4. **Performance risk**: Will the workload perform differently on cloud infrastructure?
5. **Compliance**: Any regulatory constraints on data movement?

## Output

Produce a migration assessment:
1. **Workload Summary Table**: Workload, current specs, target AWS resources, estimated cost, complexity, migration strategy.
2. **Compatibility Assessment**: Blockers, modifications needed, and recommendations per workload.
3. **Target Sizing Table**: Source spec -> AWS resource mapping with cost estimate.
4. **Migration Sequence**: Recommended wave ordering with dependency mapping.
5. **Effort Estimate**: Per-workload and total migration effort in days/weeks.
6. **Risk Register**: Identified risks per workload with mitigations.
7. **Cost Comparison**: Current infrastructure cost vs projected AWS cost.