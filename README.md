# Retrace

**Record Python executions in production. Replay them deterministically anywhere.**

```bash
# Install
pip install retracesoftware.proxy requests
python -m retracesoftware.autoenable

# Record
RETRACE=1 RETRACE_RECORDING_PATH=recording python app.py

# Replay
cd recording/run
python -m retracesoftware --recording ..
```

**[Get started in 10 minutes →](docs/quickstart.md)**

---

## What is this?

When your Python app crashes in production with mysterious bugs:

**Without Retrace:**
- Reconstruct from incomplete logs
- Can't reproduce locally
- Guess what caused it

**With Retrace:**
- Record the exact execution
- Replay it in VS Code with breakpoints
- Inspect every variable at the crash point

No code changes. No guessing. Just deterministic replay.

---

## Quick example

```python
# Your app crashes in production
def process_order(data):
    priority = data['metadata']['priority']
    level = int(priority[0])  # ValueError: invalid literal for int()
```

**Record it:**
```bash
RETRACE=1 RETRACE_RECORDING_PATH=crash python app.py
```

**Replay in VS Code:**
```bash
code crash/replay.code-workspace
# Set breakpoint on line with crash
# Press F5
# Inspect: priority = "urgent" (doesn't start with a number!)
```

Root cause found in 60 seconds.

---

## Features

- ✅ **Production-safe recording** - 10-30% overhead, minimal instrumentation
- ✅ **Deterministic replay** - Exact same execution, every time
- ✅ **No external dependencies** - Replay without network, databases, or credentials
- ✅ **VS Code integration** - Debug with breakpoints, inspect any variable
- ✅ **Multi-threaded support** - Records and replays concurrent execution
- ✅ **Library compatible** - Works with Flask, Requests, psycopg2, SQLAlchemy, and most Python libraries

---

## Documentation

**Start here:**
- [Installation](docs/installation.md) (5 minutes)
- [Quickstart: Flask demo](docs/quickstart.md) (10 minutes)
- [Supported environments](docs/supported-environments.md) (Does it work for my stack?)

**Production use:**
- [Record safely in production](docs/guides/record-in-production.md)
- [Security model](docs/security-model.md) (What data is captured?)
- [Deployment topologies](docs/deployment-topologies.md) (Docker, K8s, CI/CD)

**When things break:**
- [Troubleshooting](docs/troubleshooting.md)
- [FAQ](docs/faq.md)

**[Full documentation →](docs/)**

---

## Requirements

- Python 3.11
- Linux (Ubuntu 22.04+, Debian 11+) or macOS (13.0+)
- Windows: not yet supported

---

## Status

**Preview release** - Production recording works. Provenance engine (value-level lineage) coming soon.

**What works:**
- Record/replay deterministically
- VS Code debugging integration
- Multi-threading and async/await
- Common libraries (Flask, Requests, PostgreSQL, SQLite)

**Known limitations:**
- Python 3.11 only (3.12 coming soon)
- Some multiprocessing patterns (spawn mode)
- Windows not supported yet

See [Supported Environments](docs/supported-environments.md) for details.

---

## Get help

- **Found a bug?** [File an issue](https://github.com/retracesoftware/retrace/issues)
- **Have questions?** [Start a discussion](https://github.com/retracesoftware/retrace/discussions)
- **Need support?** support@retracesoftware.com

---

## License

[Apache 2.0](LICENSE)

---

**Built by [Retrace Software](https://retracesoftware.com)**
```



