# Architecture

## Overview

Retrace is a deterministic record-replay system for Python that operates at **call boundaries** rather than system calls or bytecode. This design enables production-safe recording with minimal overhead while maintaining portability across environments.

**Two layers:**

1. **Record-Replay** (open preview): Captures external interactions, replays deterministically
2. **Provenance Engine** (commercial, coming soon): Tracks value origins via bytecode-level instrumentation

---

## Core concepts

### Internal vs External code

Retrace partitions your program into two domains:

**Internal code** (deterministic):
- Your application logic
- Pure Python computation
- Local variables and control flow

**External code** (non-deterministic):
- Network I/O (HTTP, sockets)
- Database calls
- Filesystem access
- Time, randomness, system calls
- Any library operation that produces different results on subsequent runs

**Key insight:** Only boundary crossings need to be recorded. Internal code is deterministic and will produce the same results when replayed.

### Boundaries

A **boundary** is where internal code calls external code:

```python
# Your app (internal)
def process_order(order_id):
    # Internal: deterministic
    validated = validate_order(order_id)
    
    # BOUNDARY: external call
    customer = db.query("SELECT * FROM customers WHERE id = ?", [order_id])
    
    # Internal: deterministic
    result = process(customer, validated)
    
    # BOUNDARY: external call
    requests.post("https://api.example.com/notify", json=result)
    
    return result
```

Retrace intercepts at the boundary markers, not inside `db.query()` or `requests.post()`.

---

## How recording works

### 1. Proxy system

**During recording**, Retrace wraps external functions with **bidirectional proxies**:

```
Your Code (Internal)
        ↓
    [Gateway: int_to_ext]  ← Intercepts call, records args
        ↓
   External Library
        ↓
    [Gateway: ext_to_int]  ← Intercepts return, records result
        ↓
   Your Code (Internal)
```

**What's recorded:**
- Function called
- Arguments (serialized)
- Return value (serialized) or exception
- Thread ID (for multi-threaded replay)

**Not recorded:**
- What happens inside the external library
- Internal computation between boundaries

### 2. Serialization

Recorded data is written to `trace.bin` in a binary format:

```
CALL → function_name → args → kwargs
RESULT → value
ERROR → exception_type → exception_value
```

### 3. Environment capture

The recording also preserves:
- Source code snapshot (`recording/run/`)
- Configuration files
- VS Code workspace setup

---

## How replay works

### 1. Stub system

**During replay**, external functions are replaced with **stubs** that return recorded values:

```
Your Code (Internal)
        ↓
    [Stub: read from trace.bin]  ← Returns recorded result
        ↓
   Your Code (Internal)
```

External libraries are **never executed**. No network, no DB, no filesystem.

### 2. Deterministic ordering

**For multi-threaded programs**, a **demultiplexer** (C++) ensures threads execute in recorded order:

- Each thread reads from its own logical stream in `trace.bin`
- Threads block until their recorded turn
- Reproduces original execution order exactly

### 3. Code execution

Replay executes code from `recording/run/`, not your current working directory. This ensures:
- Same source code as recording time
- No drift if code changed after recording
- Self-contained replays

---

## Provenance engine (coming soon)

The **provenance engine** adds a second layer: bytecode-level tracking of value origins.

### How it works

**Custom Python interpreter** (C++) replaces CPython's eval loop:

1. **Instruction counter**: Global per-thread counter increments on each bytecode
2. **Stack provenance**: Every value on the stack is tagged with:
   - When it was created (instruction counter)
   - How it arrived on the stack (function return, argument, attribute load)

**Example:**

```python
# Line 10
x = get_value()  # instruction counter: 1000

# Line 11
y = x + 5        # instruction counter: 1001

# Line 12
z = process(y)   # instruction counter: 1002
```

At line 12:
- `z` tagged with counter 1002 (when it was created)
- Click `z` → jump to instruction 1002 → see `process(y)` call
- Click `y` → jump to instruction 1001 → see `x + 5`
- Click `x` → jump to instruction 1000 → see `get_value()` call

This enables **value-level provenance**: "Where did this value come from?"

---

## Component architecture

### Record-Replay components

```
┌─────────────────────────────────────────┐
│  Your Application                       │
├─────────────────────────────────────────┤
│  retracesoftware.proxy                  │
│  ├─ RecordProxySystem (recording)       │
│  ├─ ReplayProxySystem (replay)          │
│  └─ Gateway (boundary interception)     │
├─────────────────────────────────────────┤
│  retracesoftware.utils (C++)            │
│  └─ Fast proxy/unwrap, vectorcall       │
├─────────────────────────────────────────┤
│  retracesoftware.stream (C++)           │
│  ├─ Binary serialization                │
│  └─ Thread demultiplexer                │
└─────────────────────────────────────────┘
```

### Provenance engine components (coming soon)

```
┌─────────────────────────────────────────┐
│  retracesoftware.interpreter (C++)      │
│  ├─ Custom eval loop                    │
│  ├─ Instruction counter                 │
│  ├─ Stack provenance tracking           │
│  └─ ~100 bytecode handlers              │
└─────────────────────────────────────────┘
```

The interpreter runs **on top of replay**, so:
1. Replay eliminates non-determinism
2. Interpreter tracks provenance deterministically

---

## Design principles

### 1. Python-level boundaries, not system calls

**Why:** System call interception (like rr) requires:
- Running in the recording environment
- Root/ptrace permissions
- Platform-specific syscall knowledge

Retrace operates at Python call boundaries:
- Portable across machines
- No special permissions
- Works with Python libraries, not syscalls

### 2. Record only boundaries, not everything

**Why:** Recording all bytecode or all syscalls is expensive and produces huge traces.

Recording only boundary crossings:
- Low overhead (10-30%)
- Small recordings (MB, not GB)
- Fast replay

### 3. Determinism via data playback, not re-execution

**Why:** Re-executing external calls (even with same inputs) can diverge:
- Databases change
- APIs update
- Time passes

Replay returns **recorded data**, not re-executing anything external. This guarantees determinism.

### 4. C++ for performance-critical paths

**Why:** Python is slow for proxy/serialization/demux operations.

C++ extensions (retracesoftware.utils, retracesoftware.stream) handle:
- Object wrapping/unwrapping
- Vectorcall-based dispatch
- Binary serialization
- Thread demultiplexing

Keeps overhead acceptable for production.

---

## Why this works

### For most libraries

**C extensions work** because:
- Retrace intercepts at Python-visible function boundaries
- Doesn't matter what happens inside the extension
- Only the inputs/outputs are recorded

Example: `psycopg2.execute()`:
- Retrace records: SQL query (input) + rows (output)
- Doesn't record: internal PostgreSQL protocol, C libpq calls
- Replay returns: recorded rows, no database needed

### For complex programs

**Multi-threaded programs work** because:
- Each thread has its own logical stream in `trace.bin`
- Demultiplexer ensures replay thread ordering matches recording
- No race conditions because external calls are stubbed

**Async/await works** because:
- Async is just cooperative multithreading at Python level
- Same boundary interception works
- Event loop scheduling is deterministic in replay

---

## Limitations

### What doesn't work well

**1. Tight integration with C internals:**
- Libraries that require exact native types (not proxies)
- Extensions that inspect type layout or slots
- Direct memory manipulation

**2. Opaque native resources:**
- GPU handles, raw file descriptors
- Resources that can't be serialized
- Require live objects, not recorded data

**3. Work entirely in C:**
- No Python-visible boundaries to intercept
- Example: numpy operations that never call back to Python

**4. Platform-specific behavior:**
- Some recordings may not be portable (Linux → macOS usually OK, reverse may not)

**5. Spawn/exec patterns:**
- `multiprocessing` with spawn mode
- Launching subprocesses via shell

See [Supported Environments](supported-environments.md#known-edge-cases) for details.

---

## Performance characteristics

### Recording overhead

**Typical:** 1-5% slowdown

**Factors:**
- How often code crosses boundaries (more = higher overhead)
- Size of data at boundaries (large payloads = more serialization)
- Number of threads (more threads = more demux overhead)

### Replay speed

**Typical:** Same speed as original execution (sometimes faster)

**Why:**
- No actual external execution (no network latency, DB queries)
- Reading from `trace.bin` is fast
- Internal computation is unchanged

### Storage

**Typical:** 1-100MB per recording

**Factors:**
- Execution length (longer = more calls)
- Data size at boundaries (large responses = larger trace)
- Number of external calls

---

## Comparison to other approaches

### vs Traditional debuggers (pdb, gdb)

| Feature | Traditional | Retrace |
|---------|-------------|---------|
| Production use | No | Yes |
| Reproducible | No | Yes |
| Time-travel | No | Yes |
| Performance | N/A | 10-30% overhead |

### vs Time-travel debuggers (rr, Mozilla rr)

| Feature | rr | Retrace |
|---------|-----|---------|
| Level | System calls | Python boundaries |
| Portability | Recording environment only | Any Python 3.11 environment |
| Overhead | 2-10x slowdown | 10-30% |
| Language | Any | Python only |

### vs APM/logging (Datadog, New Relic)

| Feature | APM/Logging | Retrace |
|---------|-------------|---------|
| Visibility | Metrics + logs | Full execution state |
| Reproducibility | No | Yes |
| Inspection | Pre-defined logs | Any variable |
| Overhead | Low | 10-30% |

---

## Further reading

**Implementation details:**
- [Patent document](../Retrace_patent__1_.docx) - Technical specification
- [MCP server design](../MCP_server_design___1_.docx) - API layer architecture

**Operational:**
- [Record in production](guides/record-in-production.md)
- [Deployment topologies](deployment-topologies.md)
- [Troubleshooting](troubleshooting.md)
```

