# Security Model

## What data is captured

Retrace records data at **external boundaries only** - when your application code calls into external systems.

### Captured

**Function arguments at boundaries:**
- Database query parameters
- HTTP request bodies, headers, URLs
- File paths and file contents (if read/written)
- Arguments to external library calls (psycopg2, requests, etc.)

**Return values from boundaries:**
- Database query results
- HTTP response bodies, headers, status codes
- File read results
- Values returned from external libraries

**Execution metadata:**
- Stack traces (file, line, function names)
- Exception details (type, message)
- Thread identifiers

**Source code:**
- Copy of all `.py` files in your application directory
- Saved to `recording/run/` at recording time

### NOT captured

**Pure internal computation:**
- Local variables that don't cross boundaries
- Intermediate calculation results
- Variables on stack frames (unless they cross boundaries)

**Example:**
```python
# Captured: the SQL query and results
rows = db.execute("SELECT * FROM users WHERE id = ?", [user_id])

# NOT captured: this local computation
processed = [process_row(r) for r in rows]
total = sum(r['amount'] for r in processed)

# Captured: the HTTP request body
requests.post("https://api.example.com/data", json={'total': total})
```

---

## Security considerations

### 1. Sensitive data exposure

**Risk:** Recordings may contain PII, credentials, or regulated data.

**What gets recorded:**

| Data Type | Captured? | Why |
|-----------|-----------|-----|
| Database query parameters | ✅ Yes | Arguments to DB calls |
| Database results | ✅ Yes | Return values |
| API request bodies | ✅ Yes | Arguments to HTTP calls |
| API response bodies | ✅ Yes | Return values |
| Passwords in DB queries | ✅ Yes | If passed as parameters |
| API tokens in headers | ✅ Yes | If included in headers |
| Local computation | ❌ No | Doesn't cross boundaries |
| Environment variables | ⚠️ Partial | Only if accessed via external calls |

**Implications:**

- **Database recordings contain query results** - if you query PII, it's in the recording
- **HTTP recordings contain full requests/responses** - including auth headers if present
- **File I/O recordings contain file contents** - if your app reads sensitive files

### 2. Credentials and secrets

**Risk:** Credentials passed to external systems are captured.

**Examples of what's recorded:**

```python
# Database connection - password is captured
psycopg2.connect("host=db user=admin password=secret123")

# API call with token - token is captured
requests.get("https://api.example.com", headers={"Authorization": "Bearer abc123"})

# File with secrets - contents are captured
with open("/etc/secrets.json") as f:
    config = json.load(f)
```

**Mitigation:**

**Option 1:** Don't record in environments with production credentials
- Record in staging with test credentials
- Record locally with sanitized data

**Option 2:** Review recordings before sharing
- Check `trace.bin` size (large = lots of data)
- Don't share recordings externally without review

**Option 3:** Use credential injection (doesn't help with recording)
- Credentials still captured if passed through code
- Better: use separate recording environment

⚠️ **Coming soon:** Automatic credential redaction.

### 3. Compliance (GDPR, HIPAA, etc.)

**Key question:** Does your compliance framework allow recording production data?

**GDPR considerations:**
- Recordings may contain personal data (names, emails, IDs)
- Treat recordings as containing personal data
- Apply same retention/access policies as production logs
- Consider data minimization (don't record everything)

**HIPAA considerations:**
- Recordings may contain PHI if your app processes health data
- Treat recordings as PHI
- Store recordings with same controls as PHI
- Encryption at rest required
- Access logging required

**PCI considerations:**
- **Do not record payment card data** (cardholder data, CVV, etc.)
- If your app processes payments, ensure recording happens after tokenization
- Review recordings do not contain full PAN

**Recommendation:** 
- Consult your compliance team before production recording
- Use non-production environments for recording when possible
- Implement retention policies (see below)

### 4. Source code exposure

**Risk:** Recordings contain a copy of your source code in `recording/run/`.

**What's included:**
- All `.py` files in your application directory
- Not: dependencies, virtual environment, compiled code

**Implications:**
- Sharing recordings externally = sharing source code
- Treat recordings as you would treat your codebase
- Don't share if your code is proprietary/confidential

**Mitigation:**
- Watermark or track recording distribution
- Use NDAs when sharing externally
- Consider what source code reveals about your systems

---

## Access control

### Storage recommendations

**Local recordings:**
```bash
# Set restrictive permissions
chmod 700 /var/retrace/recordings
```

**Shared storage:**
- Use same access controls as production logs
- Limit access to developers who need to debug
- Log access to recordings (if required by compliance)

**Cloud storage (S3, etc.):**
```bash
# Example: S3 bucket policy
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::ACCOUNT:role/developers"},
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::recordings/*"
}
```

### Sharing externally

**Before sharing recordings:**
- [ ] Review what data is in the recording
- [ ] Check for credentials/tokens in `trace.bin`
- [ ] Review source code in `recording/run/`
- [ ] Confirm recipient has NDA/data agreement
- [ ] Document who received the recording
- [ ] Set expiration date for external access

See [Share a Recording](guides/share-recording.md) for operational guidance.

---

## Retention policies

**Recommended retention:**

| Recording Type | Retention | Why |
|----------------|-----------|-----|
| Production errors | 30 days | Compliance, debugging |
| Sample recordings | 7 days | Space management |
| Development recordings | 1 day | Clean up immediately |
| Compliance-required | Per regulation | Legal hold |

**Implementation:**

```bash
#!/bin/bash
# Example: Delete recordings older than 30 days
find /var/retrace/recordings -type d -mtime +30 -exec rm -rf {} +
```

**Considerations:**
- Longer retention = more storage cost + compliance burden
- Shorter retention = less debugging capability
- Balance based on your needs

---

## Encryption

### At rest

**Recordings should be encrypted at rest** if they contain:
- PII/PHI
- Production credentials
- Regulated data

**Options:**

**Filesystem encryption:**
```bash
# Linux: use LUKS encrypted volume
cryptsetup luksFormat /dev/sdX
mount /dev/mapper/encrypted /var/retrace/recordings
```

**Cloud encryption:**
- S3: Enable server-side encryption (SSE-S3 or SSE-KMS)
- Azure: Enable storage encryption
- GCP: Enable default encryption

### In transit

**When uploading recordings:**
- Use HTTPS/TLS for all transfers
- Don't send recordings via unencrypted channels (email attachments, HTTP)
- Use secure file transfer (SFTP, S3, etc.)

---

## Security checklist

Before enabling recording in production:

- [ ] **Data assessment:**
  - [ ] Document what data crosses external boundaries
  - [ ] Identify PII/PHI/regulated data in scope
  - [ ] Review with compliance/legal team

- [ ] **Access control:**
  - [ ] Set restrictive permissions on recording storage
  - [ ] Document who can access recordings
  - [ ] Implement logging if required

- [ ] **Retention:**
  - [ ] Define retention policy
  - [ ] Implement automated deletion
  - [ ] Document exceptions (legal hold, etc.)

- [ ] **Encryption:**
  - [ ] Enable encryption at rest
  - [ ] Verify TLS for transfers
  - [ ] Test encryption recovery

- [ ] **Sharing:**
  - [ ] Define external sharing policy
  - [ ] Require review before external sharing
  - [ ] Document NDAs/data agreements

- [ ] **Testing:**
  - [ ] Test recording in staging first
  - [ ] Review sample recordings for sensitive data
  - [ ] Verify retention policy works

---

## Incident response

**If a recording with sensitive data is exposed:**

1. **Contain:**
   - Revoke access immediately
   - Delete copies if possible
   - Identify who accessed it

2. **Assess:**
   - What data was in the recording?
   - Who accessed it?
   - What's the compliance impact?

3. **Notify:**
   - Notify compliance/legal team
   - Follow breach notification requirements if applicable
   - Document incident

4. **Prevent:**
   - Review access controls
   - Update sharing policies
   - Re-train team on procedures

---

## Limitations and future work

**Current limitations:**
- ❌ No automatic credential redaction
- ❌ No built-in PII detection/masking
- ❌ No selective field recording (record everything or nothing at boundary)

**Coming soon:**
- ⏳ Automatic credential detection and redaction
- ⏳ PII masking for common fields (email, phone, SSN)
- ⏳ Configurable filtering (exclude specific fields/calls)

---

## Next steps

- [Record in production](guides/record-in-production.md) - operational safety
- [Share recordings](guides/share-recording.md) - collaboration guidelines
- [Troubleshooting](troubleshooting.md)

---

**Questions?** [File an issue](https://github.com/retracesoftware/retrace/issues) or [contact security@retracesoftware.com](mailto:security@retracesoftware.com)
```
