# CLI Reference

## Recording

### Basic recording
```bash
RETRACE=1 RETRACE_RECORDING_PATH=<output_path> python your_app.py
```

**Parameters:**
- `RETRACE=1` - Enable recording
- `RETRACE_RECORDING_PATH=<path>` - Where to save the recording

**Example:**
```bash
RETRACE=1 RETRACE_RECORDING_PATH=recordings/crash-2026-01-21 python app.py
```

**Output:**
Creates directory at `<output_path>` containing:
- `trace.bin` - Captured execution data
- `run/` - Copy of source files
- `replay.code-workspace` - VS Code workspace
- `settings.json` - Replay configuration

---

## Replaying

### CLI replay

From the `<recording>/run/` directory:
```bash
cd <recording>/run
python -m retracesoftware --recording ..
```

**Example:**
```bash
cd recordings/crash-2026-01-21/run
python -m retracesoftware --recording ..
```

**Behavior:**
- Executes recorded program deterministically
- External calls return recorded results (no network/DB access)
- Crashes/exceptions reproduce exactly as recorded

### VS Code replay
```bash
code <recording>/replay.code-workspace
```

Or: File → Open Workspace from File → select `replay.code-workspace`

Then press **F5** to start debugging with breakpoints.

---

## Installation commands

### Install dependencies
```bash
python -m pip install --upgrade pip
python -m pip install --upgrade retracesoftware.proxy requests
```

### Enable Retrace

One-time per environment:
```bash
python -m retracesoftware.autoenable
```

### Verify installation
```bash
python -c "import retracesoftware.proxy; print('Retrace installed')"
```

---

## Environment variables

### Recording

| Variable | Required | Description |
|----------|----------|-------------|
| `RETRACE` | Yes | Set to `1` to enable recording |
| `RETRACE_RECORDING_PATH` | Yes | Output directory path |

**Example with Flask:**
```bash
RETRACE=1 RETRACE_RECORDING_PATH=recordings/test \
FLASK_APP=app.py \
flask run
```

**Example with Django:**
```bash
RETRACE=1 RETRACE_RECORDING_PATH=recordings/test \
python manage.py runserver
```

### Advanced (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `RETRACE_FILTER` | None | Filter which calls to record (future) |
| `RETRACE_MAX_SIZE` | None | Max trace.bin size (future) |

---

## Python module interface

### Recording programmatically
```python
import os

os.environ['RETRACE'] = '1'
os.environ['RETRACE_RECORDING_PATH'] = 'my_recording'

# Your application code
import myapp
myapp.run()
```

### Conditional recording
```python
import os

def enable_recording_if_error():
    try:
        run_application()
    except Exception as e:
        # Enable recording and retry
        os.environ['RETRACE'] = '1'
        os.environ['RETRACE_RECORDING_PATH'] = f'recordings/error-{id}'
        run_application()  # Re-run with recording
```

---

## Common patterns

### Record a Flask app
```bash
RETRACE=1 RETRACE_RECORDING_PATH=recordings/flask-test python app.py
```

### Record a script
```bash
RETRACE=1 RETRACE_RECORDING_PATH=recordings/script-test python myscript.py
```

### Record with arguments
```bash
RETRACE=1 RETRACE_RECORDING_PATH=recordings/with-args \
python myscript.py --arg1 value1 --arg2 value2
```

### Record in Docker
```bash
docker run -e RETRACE=1 \
  -e RETRACE_RECORDING_PATH=/recordings \
  -v ./recordings:/recordings \
  myapp:latest
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Application error (recorded) |
| Non-zero | Application exit code (preserved in replay) |

---

## Troubleshooting

**`RETRACE=1` has no effect**
- Verify `retracesoftware.proxy` is installed
- Check that `autoenable` was run
- Try `python -c "import retracesoftware.proxy"`

**Recording directory not created**
- Check write permissions on parent directory
- Verify `RETRACE_RECORDING_PATH` is set
- Look for error messages during startup

**Replay fails with "recording not found"**
- Ensure you're in `<recording>/run/` directory
- Verify `--recording ..` points to recording root
- Check that `trace.bin` exists

See [Troubleshooting](troubleshooting.md) for more.

---

## Next steps

- [Quickstart tutorial](quickstart.md)
- [Record in production](guides/record-in-production.md)
- [Architecture overview](architecture.md)

