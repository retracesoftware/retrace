# Retrace

**Deterministic record/replay for Python services** — capture a production execution once, then replay it locally with the same code paths, inputs, and outcomes. Retrace gives you *debuggable replays* and a foundation for *execution insight + data lineage* across your application.

This repository is the **umbrella “front door”** for Retrace:
- ✅ Product overview + quickstart
- ✅ Record/Replay CLI entrypoint
- ✅ Docs (architecture, deployment, security model, troubleshooting)
- ✅ Demos (gifs/screenshots, minimal replay example, sample traces)
- ✅ Links to core component repositories
- ✅ Community (Issues + Discussions) and support channels

---

## 60-second path

### 1) Install
```bash
pip install retracesoftware
````

> If you prefer installing components explicitly, see **Components** below.

### 2) Record a run

Run your app under Retrace and produce a recording:

```bash
python -m retracesoftware record -- python your_script.py --arg value
```

### 3) Replay it locally

Replay the exact execution deterministically:

```bash
python -m retracesoftware replay path/to/recording
```

### 4) Inspect

During replay you can:

* step through code paths
* inspect values at key points
* understand “why did this happen?” without needing production logs

> Next: head to **docs/quickstart.md** for a minimal working example and common options.

---

## What Retrace is (and isn’t)

Retrace is built for:

* debugging “can’t reproduce” incidents
* understanding nondeterminism (timeouts, flaky dependencies, racey behavior)
* capturing complete execution context with minimal developer effort
* enabling higher-level use cases like data lineage and security analysis

Retrace is not:

* a traditional APM/logging system
* a profiling-only tool
* a “simulator” — replay is based on a real recorded execution

---

## CLI entrypoint

This repo documents the main CLI entrypoint:

```bash
python -m retracesoftware --help
python -m retracesoftware record --help
python -m retracesoftware replay --help
```

Typical patterns:

```bash
# Record a service startup (example)
python -m retracesoftware record -- python -m yourservice

# Replay a recording
python -m retracesoftware replay recordings/rec-YYYYMMDD-HHMMSS

# Replay with verbose output (example flag)
python -m retracesoftware replay recordings/rec-... --verbose
```

> Exact flags/options vary by version — see **docs/cli.md** for the definitive reference.

---

## Docs

Start here:

* **docs/quickstart.md** — the minimal working path
* **docs/architecture.md** — how record/replay works at a high level
* **docs/deployment-topologies.md** — running in dev/staging/prod (sidecar, agent, container, etc.)
* **docs/security-model.md** — what’s captured, how it’s stored, and how to operate safely
* **docs/troubleshooting.md** — common errors and how to file a great report

Suggested layout:

```
docs/
  quickstart.md
  cli.md
  architecture.md
  deployment-topologies.md
  security-model.md
  troubleshooting.md
  faq.md
```

---

## Demos

In **demos/** you’ll find:

* **demos/minimal-replay/** — smallest “record then replay” example
* **demos/gifs/** — short gifs/screenshots for the README and docs
* **demos/sample-traces/** — example recordings (or links/scripts to generate them)

Suggested layout:

```
demos/
  minimal-replay/
  gifs/
  screenshots/
  sample-traces/
```

---

## Components (core repos)

Retrace is composed of several repositories. If you’re contributing or want to understand internals, start here:

* **retracesoftware/retracesoftware-proxy**
  Runtime proxy layer that instruments Python behavior for recording and reconstructs behavior during replay.

* **retracesoftware/retracesoftware-stream**
  Binary object/type I/O used to persist events during record and retrieve them during replay.

* **retracesoftware/retracesoftware-utils**
  C++ utilities and types used by proxies (descriptor detection, wrapped objects, thread helpers, hashing controls, etc.).

* **retracesoftware/retracesoftware-functional**
  Functional combinators used to assemble gateway logic (efficient helpers, vectorcall-based primitives).

* **retracesoftware/retracesoftware-autoenable** (optional)
  `sitecustomize` hook to enable record/replay automatically when `RETRACE_MODE` is set.

---

## Community & support

This repo is the **community front door**.

* **Questions / “how do I…?”** → GitHub **Discussions**
* **Bugs / feature requests** → GitHub **Issues**

Other channels:

* Slack/Discord: **(add link here)**
* Email: **[support@retracesoftware.com](mailto:support@retracesoftware.com)** *(or replace with your preferred address)*

When reporting an issue, please include:

* OS + Python version
* Retrace version (`pip show retracesoftware`)
* Whether the problem occurs in **record**, **replay**, or both
* A minimal reproduction (or a safe-to-share recording, if possible)

---

## Security

Please don’t file sensitive security issues in public Issues.

See **SECURITY.md** for reporting guidelines.

---

## Contributing

Contributions are welcome! See **CONTRIBUTING.md** for:

* dev setup
* repo map
* testing
* release process (if applicable)

---

## License

See **LICENSE**.


