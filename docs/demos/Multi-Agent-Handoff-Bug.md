# Multi-Agent Handoff Bug: Debug a Non-Reproducible Agent Workflow

**What you'll learn:** Record and replay a multi-agent workflow to find a subtle handoff-formatting bug that causes an incorrect decision (refund denied instead of approved).

**Time:** 10–15 minutes

**Prerequisites:**
- Retrace installed ([installation guide](../installation.md))
- Python 3.11
- VS Code (optional, for the “aha” replay debugging)

---

## The scenario

You have a two-agent customer refund workflow:

- **Agent A (Intake)** reads a complaint, looks up the order, and prepares a JSON handoff to Agent B.
- **Agent B (Resolution)** parses the handoff and decides whether to approve the refund.

A subtle formatting mismatch causes a bad decision:

- Agent A sends `refund_amount` as `"$150.00"`
- Agent B expects `"150.00"` and does `float(amount_str)`

When parsing fails, Agent B silently falls back to `0.0`, which fails the threshold check and denies the refund.

---

## Step 1: Get the demo

If you cloned the repo:
```bash
cd retrace/examples/multi_agent_handoff_bug
````

Demo files:

* `orchestrator.py` – runs the full workflow
* `agent_a_intake.py` – Agent A creates the handoff (bug is here)
* `agent_b_resolution.py` – Agent B parses and decides (bug surfaces here)
* `models.py`, `tools.py` – simple dataclasses + mock “external” actions

---

## Step 2: Run without recording

First, see the bug happen normally:

```bash
python orchestrator.py
```

You should see output like:

```
MULTI-AGENT REFUND WORKFLOW (BUG MODE)
...
refund_amount: $150.00
...
AGENT B (RESOLUTION):
WARNING: Could not parse '$150.00', using 0.0
Refund denied.
FINAL DECISION: DENIED
Amount: $0.00
```

Now run the fixed mode:

```bash
python orchestrator.py --fix
```

Expected:

```
MULTI-AGENT REFUND WORKFLOW (FIX MODE)
...
refund_amount: 150.00
...
Refund approved.
FINAL DECISION: APPROVED
Amount: $150.00
```

---

## Step 3: Record with Retrace

Now capture the workflow execution:

```bash
RETRACE=1 RETRACE_RECORDING_PATH=multi_agent_bug python orchestrator.py
```

This produces a recording folder (example):

```
multi_agent_bug/
├── replay.code-workspace
├── run/
│   ├── orchestrator.py
│   ├── agent_a_intake.py
│   ├── agent_b_resolution.py
│   ├── models.py
│   └── tools.py
├── settings.json
└── trace.bin
```

---

## Step 4: Replay via CLI

From the recording’s `run/` folder:

```bash
cd multi_agent_bug/run
python -m retracesoftware --recording ..
```

You should see the same workflow execute again.

> Note: this demo generates a `refund_id` with `random.randint()` in `tools.py`.
> If your replay produces a different refund ID in FIX MODE, that’s expected unless you make `issue_refund()` deterministic.
> The **handoff bug** and the **debugging path** remain identical.

---

## Step 5: Replay in VS Code (the “aha” moment)

1. **Open the workspace:**

   * VS Code → File → “Open Workspace from File…”
   * Select: `multi_agent_bug/replay.code-workspace`

2. **Set a breakpoint in Agent A (the bug source):**

   * File: `run/agent_a_intake.py`
   * Line **51**:

     * `return f"${amount:.2f}"  # ← THE BUG`

3. **Set a breakpoint in Agent B (where it manifests):**

   * File: `run/agent_b_resolution.py`
   * Line **52**:

     * `return float(amount_str)  # ← BUG TRIGGERS HERE`

4. **Start debugging:**

   * Press **F5** (Run → Start Debugging)
   * The replay starts and hits your breakpoint(s)

5. **Inspect the handoff (Agent A):**

   * Hover `amount` and the return value
   * Confirm the handoff contains a `$` prefix

6. **Continue to Agent B and inspect parsing:**

   * Hover `amount_str` → you’ll see `"$150.00"`
   * Step over the `float(amount_str)` call
   * Watch the `ValueError` path and fallback to `0.0`

7. **Continue (F5)**

   * See the threshold check deny the refund due to `amount < 10.00`

---

## What you just did

✅ Ran a multi-agent workflow that produced a wrong decision
✅ Recorded the execution once
✅ Replayed it deterministically for debugging
✅ Jumped straight to the root cause: a handoff formatting mismatch
✅ Confirmed the exact line in Agent A that introduced the bug

---

## The use cases

### 1. Agent handoff bugs (schema/format drift)

When agent teams evolve independently, you get “looks fine” JSON that subtly breaks downstream parsing.

### 2. Debugging non-reproducible production decisions

If the workflow only fails occasionally in production, you record the real execution once and debug locally.

### 3. AI-assisted support for platforms running customer code

Support can request a recording and reproduce + debug the exact customer failure without needing customer data.

### 4. Regression tests for agent workflows

Keep recordings as “known-bad” and “known-good” scenarios to prevent future reintroductions.

---

## Demo: Fix options

The simplest fix is to ensure Agent A always emits a numeric string:

* File: `agent_a_intake.py`
* Change BUG MODE formatting to match FIX MODE:

  * From: `"$150.00"`
  * To: `"150.00"`

Alternative: make Agent B more tolerant by stripping currency symbols before parsing (defensive parsing).

---

## Clean up

```bash
rm -rf multi_agent_bug
rm -f customer_notification.txt
```

---

## Next steps

**More demos:**

**Production use:**

* [Record safely in production](../guides/record-in-production.md)
* [Security model](../security-model.md)

---

**Questions?** [File an issue](https://github.com/retracesoftware/retrace/issues)

```
