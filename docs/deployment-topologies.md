# Deployment topologies

This doc describes practical ways to run Retrace across dev/staging/prod, and tradeoffs around overhead, storage, and safety.

---

## Goals and constraints

Before choosing a topology, decide:
- Who triggers recordings? (developers, SRE, automated rules)
- Where are recordings stored? (local disk, object storage, secure vault)
- What’s the retention policy? (hours/days/weeks)
- What data may be captured? (PII/PHI/secrets considerations)
- What’s acceptable overhead? (CPU, memory, latency)

---

## Topology A: Developer local only (simplest)

**When:** early adoption, debugging locally.

- Developers run:
  - `record` locally while reproducing issues
  - `replay` locally

**Pros**
- zero production risk
- easiest to onboard

**Cons**
- doesn’t capture real production incidents

---

## Topology B: Staging capture

**When:** staging is realistic enough to capture “prod-like” incidents.

- Run service in staging with ability to enable recording (CLI flag, env var, admin endpoint)
- Store recordings in staging storage

**Pros**
- safer than prod
- close to real conditions

**Cons**
- staging rarely matches prod fully (traffic, timing, scale)

---

## Topology C: Production “break-glass” capture

**When:** you want to capture rare incidents directly in prod.

Patterns:
- feature flag enables recording for:
  - a single host/pod
  - a single request / correlation id
  - a short time window (e.g. 60 seconds)

**Pros**
- captures the real thing

**Cons**
- requires strong safety model (redaction, access control, retention)
- operational maturity needed

**Operational checklist**
- explicit allowlists of what to record
- storage encryption
- strict retention and deletion
- audit trail (who captured, who accessed)
- incident runbook

---

## Topology D: Sidecar/agent pattern (containerized environments)

**When:** Kubernetes / containers.

- App container runs under Retrace
- Sidecar handles:
  - exporting recordings
  - rotating/retaining files
  - uploading to object storage

**Pros**
- clean separation of concerns
- consistent ops across services

**Cons**
- more moving parts

---

## Recording storage options

- Local disk (short retention)
- Encrypted volume
- Object storage (S3/GCS/Azure) with strict IAM and bucket policies
- “Vault-like” storage for high sensitivity

See: [Security model](security-model.md)

---

## Recommended “starter” production approach

If you’re early:
1. Start with **local + staging**
2. Add **prod break-glass** only after:
   - you have redaction
   - you have clear access controls
   - you have retention automation

---

## Observability integration

Even if Retrace is not an APM, you’ll likely want:
- correlation ids (request id, trace id)
- service version/build id
- environment metadata (pod, node, region)
- links from incident tickets → recording ids

Document your metadata conventions here.
