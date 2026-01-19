# FAQ

## What is Retrace?
Retrace records a real Python execution and lets you replay it deterministically later. It’s designed for “can’t reproduce” bugs, incident debugging, and deep execution insight (including the foundation for data lineage).

---

## Is Retrace an APM / observability tool?
Not in the traditional sense. APMs and logs help you *detect* and *triage* issues at scale; Retrace helps you *reproduce and understand* a specific execution with full context.

They work well together: use logs/APM to identify the failing request or time window, then capture a Retrace recording to debug locally.

---

## What do you mean by “deterministic replay”?
It means the same recorded execution can be replayed repeatedly with identical behavior:
- same control flow / branching
- same outputs
- same key intermediate values

Replay is not “rerun and hope”; it’s reconstructing behavior from what was recorded.

---

## Can I replay offline?
That’s the goal. A good test is:
1) record with network on
2) turn off Wi-Fi
3) replay — it should still behave the same

If replay still needs live dependencies, that usually means a nondeterministic interaction wasn’t captured (please report it with a minimal repro).

---

## Does Retrace work with C extensions?
Retrace is built for real Python applications, which often include C extensions. Coverage depends on what interactions are captured and proxied. If you hit a case that fails record/replay, please file an issue with a minimal reproducible example.

---

## What gets recorded?
At a high level, Retrace records enough execution events and external interactions to reproduce the original run deterministically (calls, values, identities, and the results of nondeterministic operations).

Because recordings can include sensitive data, treat them like production data.
See: [Security model](security-model.md)

---

## Is it safe to use in production?
It can be, but production use requires operational controls:
- strict access control to recordings
- encryption at rest/in transit
- retention & deletion policies
- redaction/sanitization where needed
- a “break-glass” capture workflow

See: [Deployment topologies](deployment-topologies.md) and [Security model](security-model.md)

---

## How big are recordings?
It depends on:
- how long the run is
- how much data flows through the program
- what you choose to capture

Start with short recordings and minimal repros. For production use, define retention and storage policies.

---

## Can Retrace help with flaky dependencies (timeouts, transient APIs, etc.)?
Yes — this is a core use case. Record once when the flaky behavior occurs, then replay repeatedly to understand exactly what happened without relying on the dependency being flaky again.

---

## Can Retrace replace logs?
Usually no. Logs are still useful to:
- find which executions to record
- correlate incidents (request IDs, trace IDs)
- monitor and alert at scale

Retrace reduces the need for “log everything” by allowing you to reproduce and inspect the execution directly.

---

## How do I report a bug effectively?
The fastest path to a fix is:
- OS + Python version
- Retrace version (`pip show retracesoftware`)
- whether it fails on **record**, **replay**, or **diverges**
- exact record/replay commands
- minimal repro script (best)
- relevant logs/stack trace

See: [Troubleshooting](troubleshooting.md)

---

## What’s the difference between this repo and the component repos?
This repo (`retracesoftware/retrace`) is the umbrella front door:
- docs, onboarding, demos, and community entry points

Core components live in separate repos:
- `retracesoftware-proxy`
- `retracesoftware-stream`
- `retracesoftware-utils`
- `retracesoftware-functional`
- `retracesoftware-autoenable`

---

## Where should I ask questions?
Use **GitHub Discussions** for “how do I…?” and general Q&A.
Use **GitHub Issues** for bugs and feature requests.
