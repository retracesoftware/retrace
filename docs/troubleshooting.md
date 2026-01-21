# Troubleshooting

## Quick diagnosis

**Start here:** What's your symptom?

→ [Recording doesn't start](#recording-doesnt-start)  
→ [Recording incomplete or corrupted](#recording-incomplete-or-corrupted)  
→ [Replay diverges from original execution](#replay-diverges)  
→ [Replay crashes differently than recording](#replay-crashes-differently)  
→ [VS Code integration not working](#vs-code-integration-issues)  
→ [Performance issues](#performance-issues)  

---

## Recording doesn't start

### Symptom
- Set `RETRACE=1` but no recording directory created
- Application runs normally, no `trace.bin` generated

### Diagnosis

**1. Verify Retrace is installed:**
```bash
python -c "import retracesoftware.proxy; print('OK')"
```

If this fails:
```bash
python -m pip install --upgrade retracesoftware.proxy
python -m retracesoftware.autoenable
```

**2. Check environment variables:**
```bash
echo $RETRACE
echo $RETRACE_RECORDING_PATH
```

Both must be set before running your application.

**3. Verify Python version:**
```bash
python --version  # Must be 3.11
```

**4. Check for import errors:**
Run your app and look for import warnings:
```bash
RETRACE=1 RETRACE_RECORDING_PATH=test python your_app.py 2>&1 | grep -i retrace
```

### Solutions

**If import fails:**
- Reinstall: `pip install --upgrade retracesoftware.proxy`
- Check virtual environment is activated
- Verify pip installed to correct Python: `pip --version`

**If env vars not set:**
- Use full syntax: `RETRACE=1 RETRACE_RECORDING_PATH=./recording python app.py`
- In containers, verify env vars persist: `docker exec <container> env | grep RETRACE`

**If Python version wrong:**
- Install Python 3.11: see [Installation](installation.md)
- Use explicit version: `python3.11 app.py`

---

## Recording incomplete or corrupted

### Symptom
- Recording directory created but `trace.bin` missing or very small
- Replay fails with "unexpected end of file"

### Diagnosis

**1. Check disk space:**
```bash
df -h /path/to/recordings
```

**2. Check permissions:**
```bash
ls -ld /path/to/recordings
```

**3. Check if application crashed during recording:**
- Look for error messages in application logs
- Check `trace.bin` size: `ls -lh recording/trace.bin`

### Solutions

**If disk full:**
- Free up space
- Move recordings to larger volume
- Implement [retention policy](guides/record-in-production.md#retention-policy)

**If permission denied:**
```bash
chmod 755 /path/to/recordings
```

**If application crashed:**
- Recording may be partial but still usable
- Try replaying anyway: `cd recording/run && python -m retracesoftware --recording ..`
- If replay fails, recording is corrupted; discard and re-record

---

## Replay diverges

### Symptom
- Replay produces different output than recording
- Replay takes different code path
- Replay doesn't crash where original execution crashed

### Diagnosis: Divergence flowchart

```
Replay diverges?
│
├─> Check: Are you using threading/async?
│   └─> YES: Known edge case
│       - See "Threading divergence" below
│
├─> Check: Does code use randomness/time?
│   └─> YES: Ensure these cross external boundaries
│       - random.random() → should be wrapped
│       - time.time() → should be wrapped
│       - See "Non-determinism not captured" below
│
├─> Check: Did you modify code after recording?
│   └─> YES: Replay uses code from recording/run/
│       - Don't edit recording/run/
│       - See "Code mismatch" below
│
└─> Check: Different Python version or OS?
    └─> YES: May not be portable
        - Verify both use Python 3.11
        - Linux→macOS usually works, reverse may not
```

### Common causes

#### 1. Non-determinism not captured

**Symptom:** Replay behavior differs because random/time values aren't recorded.

**Solution:** Ensure non-deterministic operations cross external boundaries:

```python
# Bad: Direct use won't be captured
import random
x = random.random()  # Not captured

# Good: Route through external boundary
import requests
response = requests.get("https://api.example.com/random")  # Captured
```

Currently, built-in `random` and `time` modules should be automatically intercepted. If not:
- File an issue with reproduction case

#### 2. Threading divergence

**Symptom:** Replay thread ordering differs from recording.

**Known issue:** Complex threading patterns with shared state can diverge.

**Workaround:**
- Simplify threading (fewer threads, clearer synchronization)
- Record single-threaded execution if possible
- File an issue with reproduction case

#### 3. Code mismatch

**Symptom:** Replay uses different code than recording.

**Cause:** Replay executes from `recording/run/`, not your current working directory.

**Solution:**
- Don't modify files in `recording/run/`
- To debug different code, record again with updated code

#### 4. Iteration order

**Symptom:** Dictionary/set iteration order differs.

**Solution:**
- Python 3.11 guarantees dict order, but sets are not ordered
- If sets are causing divergence, convert to sorted lists at boundaries

---

## Replay crashes differently

### Symptom
- Recording crashed at line X
- Replay crashes at different line Y (or doesn't crash)

### Diagnosis

**1. Check for observer effect:**
- Breakpoints can change execution (especially in multi-threaded code)
- Replay without breakpoints first: `python -m retracesoftware --recording ..`

**2. Verify code hasn't changed:**
- Compare `recording/run/` with your current code
- Replay always uses `recording/run/` version

**3. Check external state dependencies:**
- Does crash depend on external state (DB, filesystem)?
- External state should be captured, but may have edge cases

### Solutions

**If observer effect:**
- Remove all breakpoints
- Run replay via CLI first
- Add breakpoints incrementally

**If code changed:**
- Record again with current code

**If external state issue:**
- File an issue with reproduction case

---

## VS Code integration issues

### Symptom: Can't open workspace

**Error:** "Unable to resolve workspace file"

**Solution:**
```bash
# Ensure workspace file exists
ls recording/replay.code-workspace

# Open from command line
code recording/replay.code-workspace
```

### Symptom: Breakpoints not hit

**Cause:** Debugging not configured correctly.

**Solution:**
1. Open `recording/replay.code-workspace`
2. Verify `run/` directory is in explorer
3. Open file from `run/` directory (not from filesystem)
4. Set breakpoint
5. Press F5

**Still not working?**
- Check VS Code's Python extension is installed
- Verify `.vscode/launch.json` exists in `recording/`
- Try replay via CLI first to confirm recording is valid

### Symptom: "Module not found" in VS Code

**Cause:** VS Code using wrong Python interpreter.

**Solution:**
1. Cmd/Ctrl+Shift+P → "Python: Select Interpreter"
2. Choose Python 3.11 with retracesoftware.proxy installed
3. Restart VS Code

---

## Performance issues

### Symptom: Recording too slow (>50% overhead)

**Diagnosis:**
```bash
# Profile without recording
time python app.py

# Profile with recording
time RETRACE=1 RETRACE_RECORDING_PATH=test python app.py

# Calculate overhead: (recorded - baseline) / baseline
```

**Solutions:**

**If overhead >50%:**
- Reduce code crossing external boundaries (many small DB queries → batch)
- Use sampling: record 10% of requests
- Profile which calls are slowest (future feature)

See [Record in Production](guides/record-in-production.md#performance-overhead).

### Symptom: Recording too large (>100MB)

**Diagnosis:**
```bash
du -sh recording/
du -sh recording/trace.bin
```

**Solutions:**
- Large `trace.bin` means many external calls or large data
- Review what data crosses boundaries
- Implement filtering (coming soon)
- Use shorter recording windows

### Symptom: Replay too slow

**Expected:** Replay should be ~same speed as original execution.

**If much slower:**
- Check disk I/O (reading large `trace.bin`)
- Verify no debugger overhead (run CLI replay first)
- File an issue if consistently slow

---

## Compatibility issues

### Library not working

**Symptom:** Library X causes recording/replay to fail.

**Diagnosis:**
```bash
# Try minimal reproduction
RETRACE=1 RETRACE_RECORDING_PATH=test python -c "import library_x; library_x.function()"
```

**Solution:**
- Check [Supported Environments](supported-environments.md)
- File an issue with reproduction case
- Include library name, version, and error message

### Platform-specific issues

**Linux → macOS:**
- Usually works

**macOS → Linux:**
- May fail due to OS differences

**Windows:**
- Not supported yet

---

## Getting help

### Before filing an issue

**Collect this information:**

1. **Environment:**
   ```bash
   python --version
   pip show retracesoftware.proxy
   uname -a  # OS version
   ```

2. **Minimal reproduction case:**
   - Smallest code that reproduces the issue
   - Include all dependencies

3. **Actual vs expected:**
   - What happened
   - What you expected

4. **Logs:**
   - Recording output
   - Replay output
   - Error messages

### File an issue

[GitHub Issues](https://github.com/retracesoftware/retrace/issues)

**Include:**
- Environment info (above)
- Minimal reproduction case
- Can you share the recording? (if not sensitive)

### Emergency support

**For customers with support contracts:**
- Email: support@retracesoftware.com
- Include recording if possible (see [Sharing recordings](guides/share-recording.md))

---

## Known limitations

See [Supported Environments](supported-environments.md#known-edge-cases) for current limitations.

**Not supported yet:**
- Windows
- Python < 3.11
- GPU operations
- Some multiprocessing spawn patterns

---

## Next steps

- [FAQ](faq.md) for quick answers
- [Architecture](architecture.md) to understand how it works
- [File an issue](https://github.com/retracesoftware/retrace/issues)
```
