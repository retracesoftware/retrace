# Supported Environments

## Python Versions

- ✅ **Python 3.11** (fully supported)
- ⏳ Python 3.12 (coming soon)
- ❌ Python 3.10 and earlier (not supported)

## Operating Systems

- ✅ **Linux** (Ubuntu 22.04+, Debian 11+, other distributions)
- ✅ **macOS** (13.0+, Apple Silicon and Intel)
- ❌ Windows (not yet supported)

## Library Compatibility

**Most Python libraries work without modification.** Retrace operates at Python call boundaries; it doesn't need to understand library internals.

**How:** During recording, external calls execute normally while Retrace captures inputs/outputs. During replay, external calls return recorded results instead of re-executing.

**Validated core:** Python 3.11 standard library (sockets, SSL, sqlite, threading, multiprocessing, subprocess), plus Flask, Requests, psycopg2, SQLAlchemy.

**Edge cases that can break:**
- C extensions requiring exact native types (not proxies)
- Opaque native resources (GPU handles, raw file descriptors)
- Work happening entirely in C without Python boundaries
- Complex `multiprocessing` spawn patterns

**To check your stack:** Record a realistic execution, then replay it. If replay completes without divergence, you're compatible.

See [Troubleshooting](troubleshooting.md) if you encounter issues.

## Known Limitations

**Concurrency:**
- ✅ Threading (fully supported)
- ✅ Async/await (supported)
- ⚠️ Multiprocessing (supported with caveats, see edge cases above)

**Execution environments:**
- ✅ Docker containers
- ✅ Kubernetes pods
- ✅ Standard servers/VMs
- ⚠️ Serverless (coming soon)

**Resource types:**
- ✅ Network I/O (HTTP, sockets, SSL)
- ✅ Database connections (PostgreSQL, SQLite)
- ✅ File I/O
- ❌ GPU operations
- ❌ Direct hardware access

---

*Last updated: January 2026*
