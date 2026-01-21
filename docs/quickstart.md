# Quickstart: Flask + Requests

**What you'll learn:** Record a Flask app crash, replay it deterministically, and inspect the exact state that caused it—all without network traffic.

**Time:** 10 minutes

**Prerequisites:** 
- Retrace installed ([installation guide](installation.md))
- Python 3.11

---

## The scenario

You have a Flask API that processes order data. In production, it sometimes crashes with a `ValueError` on certain inputs, but you can't reproduce it locally.

## Step 1: Create the demo app

Create a file `demo_app.py`:
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/process-order', methods=['POST'])
def process_order():
    """Process an order and validate with external service"""
    data = request.json
    
    # Call external validation service
    validation_response = requests.post(
        'https://httpbin.org/post',
        json={'order_id': data['order_id']}
    )
    
    # Extract priority (this is where it can crash)
    priority = data['metadata']['priority']
    priority_level = int(priority[0])  # Assumes format like "1-high"
    
    return jsonify({
        'status': 'processed',
        'priority_level': priority_level,
        'validated': validation_response.status_code == 200
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

Create a test client `test_client.py`:
```python
import requests
import json

# This will trigger the crash
bad_order = {
    'order_id': 'ORD-12345',
    'metadata': {
        'priority': 'urgent'  # Doesn't start with a number!
    }
}

response = requests.post(
    'http://localhost:5000/process-order',
    json=bad_order
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

## Step 2: Record the crash

**Terminal 1** - Start the Flask app with recording:
```bash
RETRACE=1 RETRACE_RECORDING_PATH=crash_recording \
python demo_app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Terminal 2** - Trigger the crash:
```bash
python test_client.py
```

**Terminal 1** will show the crash:
```
ValueError: invalid literal for int() with base 10: 'u'
```

The crash is recorded! Stop the Flask app (Ctrl+C).

You now have a `crash_recording/` directory:
```
crash_recording/
├── replay.code-workspace
├── run/
│   └── demo_app.py
├── settings.json
└── trace.bin
```

## Step 3: Replay via CLI

From `crash_recording/run`:
```bash
cd crash_recording/run
python -m retracesoftware --recording ..
```

You should see:
```
 * Running on http://127.0.0.1:5000
ValueError: invalid literal for int() with base 10: 'u'
```

**Same crash, but no network traffic.** The external API call to httpbin.org was not executed—it returned the recorded result.

## Step 4: Replay in VS Code (the "aha" moment)

1. **Open the workspace:**
   - VS Code → File → "Open Workspace from File…"
   - Select `crash_recording/replay.code-workspace`

2. **Set breakpoints** in `run/demo_app.py`:
   - Line 11: `validation_response = requests.post(...)`
   - Line 17: `priority = data['metadata']['priority']`
   - Line 18: `priority_level = int(priority[0])`

3. **Start debugging:**
   - Press **F5** (or Run → Start Debugging)
   - The replay starts and hits your first breakpoint

4. **Inspect at line 17** (after external call returns):
   - Hover over `data` → see the full request payload
   - Hover over `priority` → see `"urgent"`
   - **This is the smoking gun:** priority doesn't start with a number

5. **Continue to line 18:**
   - Hover over `priority[0]` → see `"u"`
   - **Now you know exactly why it crashes:** `int("u")` fails

## What you just did

✅ **Recorded** a production-like crash (with external API call)  
✅ **Replayed** it deterministically (no network, no re-execution)  
✅ **Inspected** the exact state that caused the crash  
✅ **Found the root cause** in minutes (not hours of log analysis)

## The fix

Now you know the issue: `priority` needs validation before parsing:
```python
# Fixed version
priority = data['metadata']['priority']
if not priority[0].isdigit():
    return jsonify({'error': 'Invalid priority format'}), 400
priority_level = int(priority[0])
```

## Clean up
```bash
rm -rf crash_recording
```

---

## Next steps

**Want more context?**
- [How it works: Architecture](architecture.md)
- [What data is captured?](security-model.md)

**Try domain-specific demos:**
- [AI Agent observability](demos/ai-agent.md)
- [Fintech: trace sensitive data](demos/fintech.md)

**Use in production:**
- [Record safely in production](guides/record-in-production.md)
- [Share recordings with your team](guides/share-recording.md)
