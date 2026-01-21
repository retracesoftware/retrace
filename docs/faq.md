# FAQ

## General

### What is Retrace?

Retrace records Python program executions in production and replays them deterministically in your local environment. You can then inspect the exact state that caused bugs using VS Code's debugger.

### How is this different from logging?

Logging captures what you predicted you'd need. Retrace captures the entire execution, so you can inspect *any* variable at *any* point, even ones you didn't know to log.

### How is this different from APM tools (Datadog, New Relic)?

APM tools show aggregated metrics and traces. Retrace gives you the actual execution—you can set breakpoints and step through the code that crashed in production.

### How is this different from time-travel debuggers (rr, Mozilla rr)?

rr works at the system call level and requires running in the recording environment. Retrace works at Python boundaries and produces portable recordings you can replay anywhere.

---

## Recording

### Does recording require code changes?

No. Set environment variables and run your app:
```bash
RETRACE=1 RETRACE_RECORDING_PATH=recording python app.py
```

### What's the performance overhead?

Typically 10-30% depending on how much code crosses external boundaries (network, DB, filesystem). See [Production recording guide](guides/record-in-production.md#performance-overhead).

### Can I record in production?

Yes. Retrace is designed for production recording with safety controls:
- Configurable sampling rates
- Minimal overhead
- No code changes required

See [Record safely in production](guides/record-in-production.md).

### What data gets recorded?

Data at external boundaries:
- Database queries and results
- HTTP requests and responses  
- File I/O
- Function arguments/returns for external libraries

**Not recorded:** pure internal computation, local variables.

See [Security Model](security-model.md#what-data-is-captured) for details.

### How big are recordings?

Typically 1MB - 100MB depending on:
- Execution length
- Number of external calls
- Size of data crossing boundaries

A short Flask request might be 5-10MB. A long-running job might be 100MB+.

### How long can I record?

No hard limit, but larger recordings:
- Take more disk space
- Slower to replay
- Harder to debug (too much to inspect)

Recommended: record individual requests/tasks (seconds to minutes), not entire server lifetimes.

---

## Replay

### Can I replay anywhere?

Requirements:
- Python 3.11
- Retrace installed
- Linux or macOS

Then yes—replay doesn't need access to production databases, networks, or credentials. It's completely self-contained.

### Does replay hit external systems?

No. External calls return recorded results. No network traffic, no database queries, no filesystem access (except reading the recording).

### Can I modify code during replay?

No. Replay executes the code from `recording/run/` (the code at recording time). To debug different code, record again.

### Why does replay diverge from recording?

Common causes:
- Threading/async edge cases
- Non-determinism not captured
- Code modified after recording

See [Troubleshooting: Replay diverges](troubleshooting.md#replay-diverges) for diagnosis.

### Can I replay the same recording multiple times?

Yes. Recordings are immutable—replay them as many times as needed.

---

## Compatibility

### What Python versions are supported?

Python 3.11 only (currently).

Python 3.12 support coming soon.

### What operating systems?

- ✅ Linux (Ubuntu 22.04+, Debian 11+)
- ✅ macOS (13.0+)
- ❌ Windows (not yet supported)

### Do I need to list my dependencies?

No. Most Python libraries work automatically because Retrace operates at Python call boundaries, not inside library code.

See [Supported Environments](supported-environments.md#library-compatibility).

### Does it work with Flask/Django/FastAPI?

Yes. Web frameworks are supported.

### Does it work with async/await?

Yes.

### Does it work with threading?

Yes, but complex threading patterns may have edge cases. File an issue if you encounter problems.

### Does it work with multiprocessing?

Partially. Basic patterns work, but `spawn` mode has known issues.

### Does it work with Celery/background jobs?

Yes, if the job framework is compatible. Record the worker process.

### Does it work with Docker/Kubernetes?

Yes. Set environment variables in your container config. See [Record in production](guides/record-in-production.md#deployment-patterns).

---

## VS Code Integration

### Do I need VS Code?

No. You can replay via CLI:
```bash
cd recording/run
python -m retracesoftware --recording ..
```

But VS Code provides the best debugging experience (breakpoints, inspect variables).

### How do I open a recording in VS Code?

```bash
code recording/replay.code-workspace
```

Or: File → Open Workspace from File → select `replay.code-workspace`.

### Can I use other IDEs?

VS Code is officially supported. Other IDEs might work with CLI replay, but no specific integration yet.

---

## Security & Privacy

### Is it safe to share recordings?

Recordings may contain:
- Database query results (PII, sensitive data)
- API credentials (if passed in code)
- Source code

Review before sharing externally. See [Security Model](security-model.md).

### Can I redact sensitive data?

Not yet. Coming soon.

Currently: don't record in production if you can't share the data, or record in staging with sanitized data.

### Are recordings encrypted?

Recordings are plain files. Encrypt the storage volume if needed. See [Security Model: Encryption](security-model.md#encryption).

### What about compliance (GDPR, HIPAA)?

Recordings may contain regulated data. Treat them like production logs:
- Apply same retention policies
- Same access controls
- Same encryption requirements

Consult your compliance team before production recording. See [Security Model: Compliance](security-model.md#compliance-gdpr-hipaa-etc).

---

## Troubleshooting

### Recording doesn't start—why?

Check:
1. `RETRACE=1` is set
2. `RETRACE_RECORDING_PATH` is set
3. Retrace is installed: `python -c "import retracesoftware.proxy"`
4. Python 3.11: `python --version`

See [Troubleshooting: Recording doesn't start](troubleshooting.md#recording-doesnt-start).

### Replay fails—what do I do?

Start here: [Troubleshooting guide](troubleshooting.md).

Common fixes:
- Verify you're in `recording/run/` directory
- Check `--recording ..` points to recording root
- Ensure `trace.bin` exists

### Can I get help?

Yes:
- [File an issue](https://github.com/retracesoftware/retrace/issues)
- [Community discussions](https://github.com/retracesoftware/retrace/discussions)
- Email: support@retracesoftware.com

---

## Use Cases

### Can I use this for debugging?

Yes—that's the primary use case. Record production bugs, replay locally, inspect state.

### Can I use this for testing?

Yes. Record test executions to create reproducible test cases.

### Can I use this for compliance/auditing?

Potentially. Recordings capture exact execution flow and data. Consult your compliance team about requirements.

### Can I use this for training AI models?

Interesting use case. Recordings contain execution traces that could be used for training, but no official support yet.

---

## Licensing & Cost

### Is Retrace free?

The record-replay foundation is open source (preview release).

The provenance engine (value-level lineage) will be a paid product.

### What's the difference between free and paid?

**Free (record-replay):**
- Record executions
- Replay deterministically
- Debug in VS Code

**Paid (provenance engine - coming soon):**
- Trace any value back to its origin
- Data lineage queries
- API for automated analysis

### Can I use it commercially?

Yes. Check the license file for terms.

---

## Roadmap

### What's coming next?

**Short term:**
- Python 3.12 support
- Windows support
- Performance improvements

**Medium term:**
- Automatic credential redaction
- PII masking
- Provenance engine (paid)

**Long term:**
- More language support (Node.js, Go)
- AI-powered debugging assistants

### Can I request features?

Yes! [File an issue](https://github.com/retracesoftware/retrace/issues) with your use case.

### How can I contribute?

Coming soon: contribution guidelines.

For now: file issues, share feedback, spread the word.

---

## Still have questions?

- [Documentation home](index.md)
- [File an issue](https://github.com/retracesoftware/retrace/issues)
- [Community discussions](https://github.com/retracesoftware/retrace/discussions)
- [Email us](mailto:support@retracesoftware.com)
```

