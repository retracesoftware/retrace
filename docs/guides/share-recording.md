# Share a Recording

## Why share recordings

Share recordings to:
- **Collaborate on bugs** - teammates can replay your exact execution
- **Get support** - send recordings instead of trying to describe the issue
- **Document incidents** - preserve production state for post-mortems
- **Reproduce locally** - developers replay production issues in VS Code

---

## What's in a recording

A recording directory contains:

```
my_recording/
├── trace.bin              # Captured execution data
├── run/                   # Copy of source files at recording time
│   └── your_app.py
├── replay.code-workspace  # VS Code workspace config
└── settings.json          # Replay settings
```

**Size:** Typically 1MB - 100MB depending on execution length and data.

**Important:** The recording is self-contained. The recipient doesn't need access to your production environment, databases, or network.

---

## Package the recording

### Option 1: Zip it

```bash
cd /path/to/recordings
tar -czf bug-12345.tar.gz my_recording/
```

Or:
```bash
zip -r bug-12345.zip my_recording/
```

### Option 2: Share the directory directly

If you have shared storage (NFS, S3):

```bash
# Upload to S3
aws s3 cp my_recording/ s3://team-recordings/bug-12345/ --recursive

# Or copy to shared drive
cp -r my_recording/ /mnt/shared/team-recordings/bug-12345/
```

---

## Sharing methods

### Internal team

**Via Slack/Teams:**
- Zip the recording
- Upload to your chat tool
- Share link with context: "Recording of bug-12345, crashes at line 42"

**Via shared storage:**
- Upload to team S3 bucket, NFS, or network drive
- Share path: `/mnt/recordings/bug-12345/`

**Via Git (for small recordings):**
```bash
# Only if recording is small (<10MB) and contains no sensitive data
git add recordings/bug-12345/
git commit -m "Add recording for bug-12345"
git push
```

⚠️ **Don't commit large recordings** (>10MB) to Git.

### External support

**To Retrace support:**
1. Zip the recording
2. Upload to file sharing (Dropbox, Google Drive, WeTransfer)
3. Email link to support@retracesoftware.com with:
   - Brief description of the issue
   - Expected vs actual behavior
   - Recording filename

**To third-party vendors:**
- **Review security policy first** (see below)
- Strip sensitive data if needed
- Use secure file transfer

---

## Using a shared recording

### Recipient: Unpack and replay

**1. Unpack:**
```bash
tar -xzf bug-12345.tar.gz
# Or: unzip bug-12345.zip
```

**2. Replay via CLI:**
```bash
cd bug-12345/run
python -m retracesoftware --recording ..
```

**3. Or replay in VS Code:**
- Open `bug-12345/replay.code-workspace`
- Set breakpoints
- Press F5 to start debugging

**That's it.** No setup, no environment variables, no production access needed.

### What the recipient sees

- **Exact same execution** as the original recording
- **Same crash/error** (if there was one)
- **Same variable values** at every breakpoint
- **No network traffic** - all external calls return recorded results

---

## Security considerations

### What's captured

Recordings contain:
- Arguments passed to external calls (DB queries, API requests)
- Return values from external calls
- Source code from `run/` directory
- Exception details

### What's NOT captured

- Local variables that don't cross boundaries
- Pure internal computation
- Credentials (unless explicitly passed through intercepted calls)

### Before sharing externally

**Review the recording:**
1. Check `trace.bin` size - large files may contain unexpected data
2. Review `run/` directory - ensure no secrets in source code
3. Consider what external calls were made:
   - Database queries with PII?
   - API requests with tokens?
   - Filesystem access with sensitive paths?

**Strip sensitive data** (if needed):

Currently there's no built-in redaction tool. If the recording contains sensitive data:
- Don't share it externally
- Or work with recipient under NDA/data agreement

⚠️ **Coming soon:** Recording redaction tools.

### Internal sharing policy

Recommended policy:
- ✅ Share recordings freely within team
- ⚠️ Review before sharing with other teams
- ❌ Don't share externally without security review

See [Security Model](../security-model.md) for full details.

---

## Troubleshooting

**Recipient can't replay: "file not found" or "module not found"**
- Ensure they have Retrace installed (same version as recorder)
- Check they're in `recording/run/` directory when replaying
- Verify `trace.bin` exists in recording directory

**Replay diverges or fails**
- Recordings are tied to Python 3.11 - verify recipient's version
- Some recordings may not be portable across OS (Linux → macOS usually works, reverse may not)
- See [Troubleshooting guide](../troubleshooting.md)

**Recording too large to share**
- Compress with `tar -czf` (often reduces size 50-80%)
- Split large files: `split -b 100M recording.tar.gz recording.tar.gz.part`
- Upload to cloud storage instead of email/Slack

**Need to share many recordings**
- Set up team S3 bucket or shared storage
- Automate uploads from production
- Use consistent naming: `{service}-{date}-{issue-id}/`

---

## Best practices

**For recorders:**
- Name recordings meaningfully: `auth-service-2026-01-21-login-failure/`
- Add context in commit message or Slack thread
- Include issue tracker link when sharing
- Clean up old recordings regularly

**For recipients:**
- Confirm you can replay before debugging (save time)
- Document findings back to the team
- Delete recordings after debugging (don't hoard)

---

## Next steps

- [Record in production](record-in-production.md)
- [Security model](../security-model.md)
- [Troubleshooting guide](../troubleshooting.md)
```
