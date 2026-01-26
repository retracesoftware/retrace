# Not Diamond Router: Audit Trail for LLM Routing Decisions

**What you'll learn:** Capture and replay LLM routing decisions to understand cost spikes, debug routing logic, and maintain compliance audit trails.

**Time:** 15 minutes

**Prerequisites:** 
- Retrace installed ([installation guide](../installation.md))
- Python 3.11
- Not Diamond API key ([get yours](https://notdiamond.ai))
- OpenAI API key

---

## The scenario

You're using Not Diamond to route queries between cheap models (GPT-4o-mini) and expensive models (GPT-4o) to optimize costs. Last month your AI bill spiked to $10K. You need to understand which queries triggered expensive models and why.

## Step 1: Set up API keys

```bash
export NOTDIAMOND_API_KEY="your_notdiamond_key_here"
export OPENAI_API_KEY="your_openai_key_here"
```

Verify Not Diamond is working:
```bash
pip install notdiamond
python -c "from notdiamond import NotDiamond; print('OK')"
```

## Step 2: Get the demo

Download the demo script:
```bash
curl -O https://raw.githubusercontent.com/retracesoftware/retrace/main/examples/notdiamond_audit_demo.py
```

Or if you cloned the repo:
```bash
cd retrace/examples
```

## Step 3: Run without recording

First, see how it works normally:
```bash
python notdiamond_audit_demo.py
```

You should see:
```
======================================================================
Not Diamond + Retrace: Router Audit Trail Demo
======================================================================
This demo shows how Retrace captures exact LLM routing decisions
for cost governance, debugging, and compliance.
======================================================================

======================================================================
[Query simple_1] What time is it?
======================================================================
[Router Decision] openai/gpt-4o-mini
[Session ID] chatcmpl-abc123...
[Response] The current time is...

...

======================================================================
SUMMARY
======================================================================
Total queries: 6

Model usage:
  openai/gpt-4o-mini: 3 queries
  openai/gpt-4o: 3 queries

Audit trail saved to: routing_audit.jsonl
======================================================================
```

Notice:
- Simple queries go to `gpt-4o-mini` (cheap)
- Complex queries go to `gpt-4o` (expensive)
- Audit trail is saved to `routing_audit.jsonl`

## Step 4: Record with Retrace

Now capture the routing decisions:
```bash
RETRACE=1 RETRACE_RECORDING_PATH=routing_audit python notdiamond_audit_demo.py
```

Same output, but now you have a recording in `routing_audit/`:
```
routing_audit/
├── replay.code-workspace
├── run/
│   └── notdiamond_audit_demo.py
├── settings.json
└── trace.bin
```

## Step 5: Replay via CLI

From `routing_audit/run`:
```bash
cd routing_audit/run
python -m retracesoftware --recording ..
```

You should see:
```
======================================================================
[Query simple_1] What time is it?
======================================================================
[Router Decision] openai/gpt-4o-mini
[Session ID] chatcmpl-abc123...
```

**Same routing decisions, but no API calls.** Not Diamond's router and OpenAI's models were not called—everything returned recorded results.

**Check determinism:**
```bash
# Original audit log
cat ../../routing_audit.jsonl

# Replayed audit log
cat routing_audit.jsonl

# Compare (should be identical)
diff ../../routing_audit.jsonl routing_audit.jsonl
```

## Step 6: Replay in VS Code (the "aha" moment)

1. **Open the workspace:**
   - VS Code → File → "Open Workspace from File…"
   - Select `routing_audit/replay.code-workspace`

2. **Set a breakpoint** in `run/notdiamond_audit_demo.py`:
   - Line 67: `result, session_id, provider = client.chat.completions.create(...)`
   - (Right after the Not Diamond routing decision)

3. **Start debugging:**
   - Press **F5** (or Run → Start Debugging)
   - The replay starts and hits your breakpoint

4. **Inspect at line 67** (after routing decision):
   - Hover over `user_query` → see the exact query
   - Hover over `chosen_model` → see which model was chosen
   - Hover over `session_id` → see Not Diamond's session ID
   - Hover over `candidate_models` → see which models were offered

5. **Press F5 to continue** to the next query

6. **Look for cost alerts:**
   - When you see a simple query routed to `gpt-4o`
   - Inspect why: check `candidate_models`, `user_query`

## What you just did

✅ **Captured** LLM routing decisions in production  
✅ **Replayed** them deterministically (no API calls)  
✅ **Inspected** exact routing choices for each query  
✅ **Found** which queries triggered expensive models

## The use cases

### 1. Cost governance

**CFO asks:** "Why did our AI costs spike 50% in Q4?"

With Retrace:
- Replay Q4 recordings
- See which queries triggered expensive models
- Prove it was legitimate complexity, not a bug

### 2. Debugging routing logic

**Bug:** Simple queries going to GPT-4 unnecessarily.

With Retrace:
- Replay and inspect `candidate_models`
- Find that your heuristic only offered GPT-4 (the bug)
- Fix: offer both models, let Not Diamond decide

### 3. Compliance & audit

**Requirement:** Prove which model processed customer data.

With Retrace:
- Recording shows: query → model → session_id
- Audit trail for SOC-2, HIPAA, data governance
- Can replay any disputed decision

### 4. Building evaluation datasets

**Goal:** Train a better custom router.

With Retrace:
- Capture real production queries
- See which models performed well
- Use as training data for Not Diamond custom router

## Demo: The bug scenario (optional)

Want to see debugging in action? Run with the buggy heuristic:

```bash
BUG_DEMO=1 RETRACE=1 RETRACE_RECORDING_PATH=routing_bug python notdiamond_audit_demo.py
```

The bug:
- Heuristic checks for keywords ("explain", "analyze", etc.)
- If found: only offers `gpt-4o` (expensive)
- If not found: only offers `gpt-4o-mini` (cheap)
- Problem: Forces specific model instead of letting router decide

With Retrace:
1. Open `routing_bug/replay.code-workspace`
2. Set breakpoint at line 55 (inside `get_candidate_models`)
3. Press F5 to debug
4. See the if/else logic forcing one model
5. Hover over `candidate_models` → see only one option
6. **Root cause found:** Buggy heuristic limits Not Diamond's choices

The fix: Remove the heuristic, always pass both models to Not Diamond.

## Clean up
```bash
rm -rf routing_audit routing_bug
rm -f routing_audit.jsonl
```

---

## Next steps

**More demos:**


**Production use:**
- [Record safely in production](../guides/record-in-production.md)
- [Security for AI applications](../security-model.md)

---

**Questions?** [File an issue](https://github.com/retracesoftware/retrace/issues)
