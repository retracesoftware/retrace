# Installation

## Prerequisites

- Python 3.11
- Linux (Ubuntu 22.04+, Debian 11+) or macOS (13.0+)
- pip

## Install

**1. Install dependencies:**
```bash
python -m pip install --upgrade pip
python -m pip install --upgrade retracesoftware.proxy requests
```

**2. Enable Retrace** (one-time per environment):
```bash
python -m retracesoftware.autoenable
```

This configures Retrace for your Python environment.

**Using a virtual environment?** (recommended)
```bash
python3.11 -m venv retrace-env
source retrace-env/bin/activate  # On macOS/Linux
python -m pip install --upgrade pip
python -m pip install --upgrade retracesoftware.proxy requests
python -m retracesoftware.autoenable
```

## Verify installation

Create a test file `hello.py`:
```python
import requests

response = requests.get("https://httpbin.org/uuid")
print(response.json())
```

Record it:
```bash
RETRACE=1 RETRACE_RECORDING_PATH=test_recording python hello.py
```

You should see the JSON output, and a `test_recording/` directory should be created with `trace.bin` and other files.

Replay it:
```bash
cd test_recording/run
python -m retracesoftware --recording ..
```

You should see the same output (no network needed).

**Success!** You're ready to use Retrace.

Clean up:
```bash
rm -rf test_recording
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'retracesoftware'`**
- Run the install commands again
- Verify you're in the correct virtual environment

**`autoenable` fails**
- Check Python version: `python --version` (must be 3.11)
- Try with fresh virtual environment

**Recording directory not created**
- Verify RETRACE=1 is set
- Check for error messages during execution

**Replay hangs or fails**
- Ensure you're running from `recording/run/` directory
- Verify trace.bin was created during recording

**Still stuck?**
- [Troubleshooting guide](troubleshooting.md)
- [File an issue](https://github.com/retracesoftware/retrace/issues)

---

## Next steps

→ [Run the quickstart](quickstart.md) (10 minutes - Flask demo)  
→ [Try a domain demo](demos/ai-agent.md)  
→ [Check compatibility](supported-environments.md)
