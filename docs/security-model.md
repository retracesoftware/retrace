# Security model

Retrace records real execution behavior. That can include sensitive data.
This document describes how to operate Retrace safely and what controls you should put in place.

---

## Threat model (what could go wrong)

Recordings may contain:
- PII (names, emails)
- secrets (API keys, tokens)
- business-sensitive logic and data
- payloads that may be regulated

Risks:
- unauthorized access to recordings
- over-retention of sensitive recordings
- accidental sharing in bug reports
- using recordings outside their intended environment

---

## Core principles

1. **Least privilege**
   - only a small set of people/services can create, access, and export recordings

2. **Minimize capture**
   - record only what you need
   - prefer allowlists over “capture everything”

3. **Redaction**
   - redact at record time if possible
   - support post-processing redaction only as a fallback

4. **Encryption**
   - encrypt recordings at rest
   - encrypt in transit when uploading/exporting

5. **Retention & deletion**
   - recordings should expire automatically
   - provide secure deletion policies aligned to your infra

6. **Auditability**
   - log who captured, accessed, downloaded, and deleted recordings

---

## Data handling guidance

### In development
- treat recordings as sensitive by default
- avoid committing recordings to git
- use `.gitignore` for recording directories

### In staging/production
- store recordings in restricted locations
- apply environment-specific access controls
- ensure backups don’t silently keep recordings forever

---

## Recommended controls (baseline)

- Access control: “record” permission is separate from “read/export”
- Storage: encrypted bucket with strict IAM and short lifecycle rules
- Sharing: internal-only workflow for bug reproduction recordings
- Sanitization: explicit safe-sharing path for support

---

## Safe bug reports

If you need support from Retrace maintainers:
- Prefer a minimal code snippet + steps
- If you must share a recording:
  - sanitize/redact
  - share via a secure channel
  - time-limit access

---

## Open questions to document as you implement

Fill these in as your product stabilizes:
- What exact data categories may be captured by default?
- What redaction mechanisms exist? (rules, hooks, patterns)
- Can recording be restricted to a specific request/correlation id?
- How does replay prevent accidental outbound calls?
- What metadata is attached to recordings? (hostnames, env vars, etc.)

---

## Summary

Treat recordings like production data:
- protect access
- minimize capture
- expire quickly
- audit everything

