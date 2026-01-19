# CLI reference

Retrace exposes a CLI via:

```bash
python -m retracesoftware --help
````

The two core subcommands are:

* `record` — run a program under Retrace and write a deterministic recording
* `replay` — replay a recording deterministically

> Keep this file in sync with your actual `--help` output as the CLI evolves.

---

## Quick examples

### Record a script

```bash
python -m retracesoftware record -- python your_script.py --arg value
```

### Record a module entrypoint

```bash
python -m retracesoftware record -- python -m yourservice
```

### Replay a recording

```bash
python -m retracesoftware replay path/to/recording
```

---

## `record`

### Synopsis

```bash
python -m retracesoftware record [options] -- <command...>
```

### Examples

```bash
# Script
python -m retracesoftware record -- python app.py

# Module
python -m retracesoftware record -- python -m yourservice

# Any command (if supported)
python -m retracesoftware record -- yourservice --flag value
```

### Options to document (fill in what you support)

These are common knobs teams expect; include only what’s real:

* `--output <dir>`
  Where recordings are written.

* `--name <label>`
  Optional label to help identify the recording.

* `--read-timeout <ms>`
  Tune timeouts for record-time reads (if applicable).

* `--include <module|path>` / `--exclude <module|path>`
  Control what gets instrumented/recorded (if supported).

* `--redact <rule>`
  Redact sensitive values at record time (if supported).

### Environment variables (if supported)

* `RETRACE_OUTPUT` — default output directory for recordings
* `RETRACE_LOG` — logging level/format
* `RETRACE_MODE` — used by `retracesoftware-autoenable` (see below)

---

## `replay`

### Synopsis

```bash
python -m retracesoftware replay [options] <recording_dir>
```

### Examples

```bash
python -m retracesoftware replay recordings/rec-YYYYMMDD-HHMMSS
```

### Options to document (fill in what you support)

* `--verbose`
  Print additional information useful for diagnosing divergence.

* `--check`
  Validate determinism invariants (if supported).

* `--breakpoint <file:line>`
  Start replay paused at a breakpoint (if supported).

* `--export <format>`
  Export trace/timeline to JSON or another format (if supported).

---

## Auto-enable (optional)

If you use `retracesoftware-autoenable`, you can enable record/replay automatically when an environment variable is set.

Typical pattern:

* `RETRACE_MODE=record` enables recording
* `RETRACE_MODE=replay` enables replaying (with a specified recording path)

> Document the exact values you support and how the recording path is specified.

---

## Exit codes (recommended convention)

Document your intended behavior. A common scheme is:

* `0` — success
* `1` — user/config error (bad args, missing recording)
* `2` — replay divergence / determinism violation
* `3` — internal error

---

## Diagnostics

Helpful commands to include in bug reports:

```bash
python -m retracesoftware --help
python -m retracesoftware record --help
python -m retracesoftware replay --help
python --version
pip show retracesoftware
```

See also: [Troubleshooting](troubleshooting.md)

