# Troubleshooting

This guide covers common failure modes for recording/replay and what to include when reporting problems.

If you don’t see your issue here, open a **Discussion** with your commands + a minimal repro. If it’s clearly a bug, we’ll convert it into an **Issue**.

---

## First checks (do these before anything else)

### 1) Confirm versions
```bash
python --version
pip show retracesoftware
python -m retracesoftware --help
````

### 2) Identify which phase fails

* **Record fails** (can’t create a recording)
* **Replay fails** (can’t replay a recording)
* **Replay diverges** (replay runs but behavior/output differs)

### 3) Reproduce with the smallest possible program

Try to reduce to:

* a single file
* one dependency (or none)
* no concurrency (threads/async) if you can avoid it
* no frameworks if possible (Flask/Django/etc.)

This makes it much faster to diagnose.

---

## Common issues

## A) Recording fails immediately

**Symptoms**

* the `record` command errors before your program really starts
* you see exceptions related to tracing/hooking

**Common causes**

* running under an IDE debugger or profiler (these often use `sys.settrace`)
* conflicting instrumentation (coverage tools, tracing, monkeypatching)
* unsupported runtime edge case

**Things to try**

1. Run outside your IDE debugger

   * VS Code / PyCharm debugging can conflict with tracing/hooking.
2. Disable other instrumentation temporarily

   * coverage, profiling, tracing libraries.
3. Try the smallest script possible:

```bash
python -c "print('hello')"
python -m retracesoftware record -- python -c "print('hello')"
```

**If it still fails**
Include in your report:

* the full stack trace
* whether an IDE debugger was active
* OS + Python version + Retrace version

---

## B) Replay fails immediately

**Symptoms**

* replay command errors before output appears
* missing files / unreadable recording / format errors

**Common causes**

* recording directory path is wrong or incomplete
* recording was created by a different version (potential compatibility issue)
* file permissions or incomplete upload/copy

**Things to try**

1. Confirm the recording path exists and has content:

```bash
ls -la path/to/recording
```

2. Try replaying on the same machine where it was recorded (to isolate copy issues)

3. Confirm versions:

```bash
pip show retracesoftware
```

**If it still fails**
Include:

* the replay command used
* directory listing of the recording root (filenames only is fine)
* full error output

---

## C) Replay diverges (output differs / different code path)

**Symptoms**

* replay completes but prints different output
* you observe different branching, different exception, or different timing behavior

**Common causes**

* an uncaptured source of nondeterminism (time, randomness, environment, filesystem, network)
* concurrency edge cases (thread scheduling / async timing)
* unsupported I/O path outside the capture boundary

**Things to try**

1. Replay multiple times — confirm it’s consistently diverging
2. Make nondeterminism obvious:

   * set a fixed seed (if relevant)
   * remove concurrency temporarily
   * reduce to a minimal reproducible script
3. If you have a verbose/diagnostic mode, enable it:

```bash
python -m retracesoftware replay path/to/recording --verbose
```

**What to include in a report**

* expected output vs actual output
* record command and replay command
* minimal code snippet that shows the divergence

---

## D) Replay still tries to access the network / external services

**Symptoms**

* replay hangs on a network call
* you see connection errors during replay

**What it usually means**

* the interaction wasn’t captured, or
* it is happening in a layer outside the capture boundary

**Things to try**

1. Confirm replay truly runs offline:

   * disable Wi-Fi and replay
   * or block outbound calls (e.g., firewall rule) and replay
2. Reduce the code to a single request:

   * one `requests.get(...)` call is a great reproducer

**If it still happens**
Include:

* the dependency used (`requests`, `httpx`, etc.)
* the minimal script
* the error output from replay

---

## E) Concurrency / async issues (threads, asyncio)

**Symptoms**

* replay nondeterminism appears only under load
* different ordering of events across runs
* occasional deadlocks or timeouts

**Things to try**

* reproduce with **one thread** / simplified async flow
* reduce work until it’s stable, then add complexity back step-by-step
* record a shorter window if you can (smaller reproducer)

**What to include**

* whether you use threads, multiprocessing, or asyncio
* a minimal repro focusing on scheduling/ordering

---

## What to include in an Issue (copy/paste template)

**Environment**

* OS:
* Python version:
* Retrace version (`pip show retracesoftware`):

**Phase**

* [ ] record fails
* [ ] replay fails
* [ ] replay diverges

**Commands**

```bash
# record
python -m retracesoftware record -- ...

# replay
python -m retracesoftware replay ...
```

**Expected**

* …

**Actual**

* …

**Minimal repro**

* code snippet or repo link

**Logs / stack trace**

```text
(paste here)
```

**Other notes**

* IDE debugger/profiler running? (yes/no)
* any unusual environment config?

---

## If you’re completely stuck

Open a **Discussion** with:

* what you’re trying to do
* the exact commands
* the smallest reproducer you can share
* full error output

We’ll help you narrow it down and convert to an Issue if needed.
