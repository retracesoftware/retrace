# Retrace Performance Benchmarks

This directory contains synthetic benchmarks for measuring Retrace's recording overhead.

---

## Quick Start

```bash
# Install dependencies
pip install retracesoftware

# Run all benchmarks
./run_all_benchmarks.sh

# View results
cat results/summary.txt
```

---

## Available Benchmarks

### 1. Internal Code Benchmark (`synthetic_benchmark.py`)

**Measures:** Operations that Retrace does NOT intercept (0% overhead)

**Tests:**
- `time.time()` calls in tight loop
- `datetime.now()` calls in tight loop

**Run:**
```bash
# Baseline
python synthetic_benchmark.py

# With Retrace
RETRACE=1 RETRACE_RECORDING_PATH=/tmp/recording \
python synthetic_benchmark.py
```

**Expected results:** 0% overhead (internal deterministic code runs at native speed)

---

### 2. External Boundary Benchmark (`external_boundary_benchmark.py`)

**Measures:** Operations that Retrace DOES intercept (actual overhead)

**Tests:**
- Environment variable access (`os.environ.get()`)
- File read operations (`open()` / `read()`)

**Run:**
```bash
# Baseline
python external_boundary_benchmark.py

# With Retrace
RETRACE=1 RETRACE_RECORDING_PATH=/tmp/recording \
python external_boundary_benchmark.py
```

**Expected results:** +0.35-15µs overhead per operation

---

## Understanding the Results

### Two Categories of Operations

**Category A: Internal Code (NOT intercepted)**
- Python stdlib functions
- Pure computation
- Object manipulation
- Control flow

**Result:** 0% overhead - runs at native speed

**Category B: External Boundaries (INTERCEPTED)**
- Network calls (HTTP, database)
- File I/O
- Environment variables
- System state queries

**Result:** +15µs average overhead per operation

### Why Overhead is Low in Real Applications

**Example: Web API Request**
```
Total request time: 50ms
├── 40ms: Internal business logic (0% overhead)
├── 8ms: Database query (actual work)
│   └── +0.015ms Retrace overhead
└── 2ms: Cache lookup (actual work)
    └── +0.015ms Retrace overhead

Total overhead: 0.03ms on 50ms = 0.06%
```

**Key insight:** External calls do real work (milliseconds) that dwarfs the recording overhead (microseconds).

---

## Benchmark Environment

All benchmarks are run with:
- Python 3.11
- Single-threaded execution
- 5 runs per test (averaged)
- Warmup runs (discarded)
- macOS (Apple Silicon) / Linux

### System Information

The benchmarks include system information in output:
- Python version
- OS/architecture
- CPU count
- Timestamp

---

## Interpreting Results

### Metrics Explained

**Throughput (ops/sec):**
- Higher is better
- Shows how many operations per second

**Per-operation time (µs or ms):**
- Lower is better
- More intuitive for understanding overhead

**Overhead calculation:**
```
Overhead = (With_Retrace - Baseline) / Baseline × 100%
```

### What "Good" Looks Like

**Internal code benchmark:**
- 0-5% overhead (within measurement noise)
- Per-call: <1µs difference

**External boundary benchmark:**
- 30-50% overhead in tight loops
- Per-call: +0.3-15µs absolute overhead
- Real apps: <1% because I/O latency >> recording overhead

### Red Flags

If you see:
- >100% overhead on internal code → measurement issue
- >50µs per boundary crossing → investigate
- High variance between runs → unstable environment

---

## Running Your Own Benchmarks

### Custom Benchmark Template

```python
"""
Custom benchmark for [your use case]
"""

import time

def baseline_operation():
    """Your operation without Retrace"""
    pass

def measure_operation(iterations=10000):
    start = time.perf_counter()
    
    for _ in range(iterations):
        baseline_operation()
    
    elapsed = time.perf_counter() - start
    return elapsed

def run_benchmark():
    # Warmup
    measure_operation(100)
    
    # Actual benchmark
    print(f"Running {10000} iterations...")
    runs = []
    for i in range(5):
        elapsed = measure_operation(10000)
        runs.append(elapsed)
        print(f"  Run {i+1}: {elapsed*1000:.2f}ms")
    
    avg = sum(runs) / len(runs)
    print(f"  Average: {avg*1000:.2f}ms")
    print(f"  Per-operation: {(avg/10000)*1000000:.2f}µs")

if __name__ == '__main__':
    run_benchmark()
```

**Usage:**
```bash
# Baseline
python your_benchmark.py

# With Retrace
RETRACE=1 RETRACE_RECORDING_PATH=/tmp/recording \
python your_benchmark.py
```

---

## Automated Benchmark Suite

### Run All Benchmarks

```bash
#!/bin/bash
# run_all_benchmarks.sh

set -e

mkdir -p results

echo "Running Retrace Performance Benchmarks"
echo "======================================="
echo ""

# Internal code benchmark
echo "1. Internal Code Benchmark (baseline)..."
python synthetic_benchmark.py > results/internal_baseline.txt

echo "2. Internal Code Benchmark (with Retrace)..."
RETRACE=1 RETRACE_RECORDING_PATH=/tmp/rec1 \
  python synthetic_benchmark.py > results/internal_retrace.txt

# External boundary benchmark
echo "3. External Boundary Benchmark (baseline)..."
python external_boundary_benchmark.py > results/external_baseline.txt

echo "4. External Boundary Benchmark (with Retrace)..."
RETRACE=1 RETRACE_RECORDING_PATH=/tmp/rec2 \
  python external_boundary_benchmark.py > results/external_retrace.txt

echo ""
echo "Benchmarks complete! Results in results/ directory"
echo ""

# Generate summary
python analyze_results.py
```

### Analysis Script

```python
# analyze_results.py
"""Analyze and summarize benchmark results"""

import re
import sys
from pathlib import Path

def parse_benchmark_file(filename):
    """Extract key metrics from benchmark output"""
    with open(filename) as f:
        content = f.read()
    
    results = {}
    
    # Extract test results (adjust regex to match your output format)
    for test_match in re.finditer(r'## Test \d+: (.+?)\n.*?Average: ([\d.]+)ms', content, re.DOTALL):
        test_name = test_match.group(1)
        avg_ms = float(test_match.group(2))
        results[test_name] = avg_ms
    
    return results

def main():
    results_dir = Path('results')
    
    print("="*70)
    print("RETRACE BENCHMARK SUMMARY")
    print("="*70)
    
    # Internal code tests
    print("\n## Internal Code (0% Expected Overhead)")
    internal_base = parse_benchmark_file(results_dir / 'internal_baseline.txt')
    internal_ret = parse_benchmark_file(results_dir / 'internal_retrace.txt')
    
    for test_name in internal_base:
        base = internal_base[test_name]
        ret = internal_ret.get(test_name, 0)
        overhead = ((ret - base) / base * 100) if base > 0 else 0
        print(f"  {test_name}:")
        print(f"    Baseline: {base:.2f}ms")
        print(f"    Retrace:  {ret:.2f}ms")
        print(f"    Overhead: {overhead:+.1f}%")
    
    # External boundary tests
    print("\n## External Boundaries (15µs Expected Overhead)")
    external_base = parse_benchmark_file(results_dir / 'external_baseline.txt')
    external_ret = parse_benchmark_file(results_dir / 'external_retrace.txt')
    
    for test_name in external_base:
        base = external_base[test_name]
        ret = external_ret.get(test_name, 0)
        diff_us = (ret - base) * 1000  # Convert ms to µs
        print(f"  {test_name}:")
        print(f"    Baseline: {base:.2f}ms")
        print(f"    Retrace:  {ret:.2f}ms")
        print(f"    Overhead: +{diff_us:.1f}µs per operation")
    
    print("\n" + "="*70)
    print("See results/ directory for detailed output")
    print("="*70)

if __name__ == '__main__':
    main()
```

---

## Comparing with APM Tools

For context, typical APM agent overhead:

| Tool | Reported Overhead |
|------|-------------------|
| Datadog APM | 2-5% |
| New Relic | 3-7% |
| Dynatrace | 1-3% |
| **Retrace** | **<1% (typical applications)** |

**Why Retrace is lower:**
- APM agents instrument everything
- Retrace only instruments external boundaries
- Internal code runs at 0% overhead

---

## Production Benchmarking

### Measuring Real Overhead

The synthetic benchmarks show theoretical overhead. To measure real overhead in your application:

**1. Baseline measurement**
```bash
# Measure without Retrace
ab -n 1000 -c 10 http://localhost:8000/api/endpoint
# Note: X requests/sec
```

**2. With Retrace recording**
```bash
# Start app with Retrace
RETRACE=1 RETRACE_RECORDING_PATH=/tmp/recording \
  python app.py

# Measure with Retrace
ab -n 1000 -c 10 http://localhost:8000/api/endpoint
# Note: Y requests/sec
```

**3. Calculate overhead**
```
Overhead = (X - Y) / X × 100%
```

### Using APM Tools

Your existing APM (Datadog, New Relic, etc.) will show:
- Request latency (p50, p95, p99)
- Throughput changes
- CPU/memory impact

**Expected:** <1% latency increase for most endpoints.

---

## Troubleshooting

### High Variance Between Runs

**Symptoms:** Results vary by >20% between runs

**Causes:**
- Background processes
- Thermal throttling
- Swap activity
- Network interference (for network benchmarks)

**Solutions:**
- Close other applications
- Disable background services
- Run benchmarks multiple times
- Use dedicated benchmark machine

### Unexpected High Overhead

**Symptoms:** >50µs per operation or >5% on real endpoints

**Causes:**
- Large payloads (megabytes being serialized)
- Complex object graphs (deep nesting)
- Disk I/O bottleneck (slow trace writes)

**Solutions:**
- Use sampling (record 1-10% of requests)
- Adjust trace buffer size
- Use faster storage for trace files
- Profile with Python profiler to identify bottleneck

### Lower Than Expected Overhead

**Symptoms:** 0% overhead on operations that should be intercepted

**Possible causes:**
- Operation not actually crossing boundary
- Retrace not intercepting this library/module
- Measurement error

**Verify:** Check trace file was created and contains recorded calls

---

## Contributing

### Adding New Benchmarks

1. Create `your_benchmark.py` in this directory
2. Follow template structure above
3. Document what you're measuring
4. Run baseline + Retrace comparison
5. Submit PR with results

### Benchmark Guidelines

**Do:**
- Measure single operations in isolation
- Run multiple iterations (1000+)
- Average across multiple runs (5+)
- Include warmup runs
- Document test environment

**Don't:**
- Mix multiple operations in one test
- Run too few iterations (<100)
- Cherry-pick best results
- Benchmark in unstable environment

---

## FAQ

**Q: Why do some tests show 0% overhead?**

A: Internal deterministic code isn't intercepted by Retrace. Only external boundary crossings (network, DB, file I/O) are recorded.

**Q: Why does the percentage overhead look high but absolute overhead is low?**

A: In tight loops, we're measuring pure proxy cost without real I/O latency. The 15µs overhead is 40% of a 40µs environment variable access, but only 0.3% of a 5ms database query.

**Q: Should I run these benchmarks before deploying Retrace?**

A: Optional but recommended. The synthetic benchmarks give you theoretical overhead. Real production benchmarking (using your APM) gives you actual overhead on your workload.

**Q: Can I use these benchmarks to compare Retrace versions?**

A: Yes! Run benchmarks on each version to track performance improvements or regressions.

---

## See Also

- [Performance Documentation](../docs/performance.md) - Detailed analysis
- [Record in Production](../docs/guides/record-in-production.md) - Deployment strategies
- [Architecture](../docs/architecture.md) - How Retrace works

---

## Results Archive

We maintain benchmark results across versions in `results/archive/`:

```
results/archive/
├── v0.1.0_2026-01-26/
│   ├── internal_baseline.txt
│   ├── internal_retrace.txt
│   ├── external_baseline.txt
│   └── external_retrace.txt
└── v0.2.0_2026-02-15/
    └── ...
```

This allows tracking performance over time and catching regressions.
