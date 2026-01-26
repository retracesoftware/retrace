# Retrace Benchmarks - Quick Reference

## TL;DR

**Internal code:** 0% overhead  
**External boundaries:** +15µs per operation  
**Real applications:** <1% overhead

---

## Running Benchmarks

```bash
# Quick run (all benchmarks)
./run_all_benchmarks.sh

# Individual tests
python synthetic_benchmark.py                # Internal (baseline)
RETRACE=1 python synthetic_benchmark.py      # Internal (retrace)

python external_boundary_benchmark.py        # External (baseline)
RETRACE=1 python external_boundary_benchmark.py  # External (retrace)

# Detailed analysis
python analyze_results.py
```

---

## Understanding Results

### Benchmark A: Internal Code

**What it tests:** Python operations that Retrace doesn't intercept
- `time.time()` calls
- `datetime.now()` calls
- Pure computation

**Expected:** 0% overhead

**Why:** Internal deterministic code runs at native speed

---

### Benchmark B: External Boundaries

**What it tests:** Operations that Retrace does intercept
- Environment variable access
- File I/O operations
- External state queries

**Expected:** +0.35-15µs per operation

**Why:** Retrace captures arguments, results, and writes to trace

---

## Real-World Translation

### Example: Web API Request

```
Total: 50ms
├── 40ms: Business logic (0% overhead)
├── 8ms: Database query
│   └── +0.015ms Retrace
└── 2ms: Cache lookup
    └── +0.015ms Retrace

Total overhead: 0.03ms / 50ms = 0.06%
```

### Key Insight

Retrace overhead (15µs) is invisible compared to real I/O latency (1-100ms).

---

## Files Generated

```
benchmarks/
├── results/
│   ├── internal_baseline.txt    # Full output
│   ├── internal_retrace.txt     # Full output
│   ├── external_baseline.txt    # Full output
│   └── external_retrace.txt     # Full output
├── synthetic_benchmark.py       # Internal code test
├── external_boundary_benchmark.py  # Boundary test
├── run_all_benchmarks.sh        # Runner script
└── analyze_results.py           # Analysis tool
```

---

## Comparing Versions

```bash
# Run benchmarks for current version
./run_all_benchmarks.sh

# Archive results
mkdir -p results/archive/v0.1.0
cp results/*.txt results/archive/v0.1.0/

# Checkout different version and re-run
git checkout v0.2.0
./run_all_benchmarks.sh

# Compare
diff results/archive/v0.1.0/ results/
```

---

## Production Benchmarking

### Using Apache Bench (ab)

```bash
# Baseline
ab -n 1000 -c 10 http://localhost:8000/api/endpoint

# With Retrace
RETRACE=1 python app.py
ab -n 1000 -c 10 http://localhost:8000/api/endpoint

# Compare throughput
```

### Using Your APM

1. Deploy with Retrace recording 1-10% of traffic
2. Check latency metrics (p50, p95, p99) in Datadog/New Relic
3. Expected: <1% latency increase

---

## Troubleshooting

### High Variance

**Symptom:** Results vary by >20% between runs

**Fix:**
- Close other apps
- Disable background services  
- Run multiple times
- Check CPU throttling

### Unexpected High Overhead

**Symptom:** >50µs per operation

**Check:**
- Large payloads being serialized?
- Disk I/O bottleneck?
- Correct Python version (3.11)?

**Fix:**
- Use sampling (1-10%)
- Faster storage for traces
- Profile with cProfile

---

## APM Comparison

| Tool | Overhead |
|------|----------|
| Datadog | 2-5% |
| New Relic | 3-7% |
| Dynatrace | 1-3% |
| **Retrace** | **<1%** |

---

## Quick Wins

**Best case for Retrace:**
- CPU-heavy internal logic
- Few external calls per request
- Low request volume (sampling not needed)

**Challenging case:**
- Tight loops with external calls
- High request volume
- Large payloads

**Solution for challenging cases:**
- Use sampling (1-10%)
- Error-triggered recording only
- Adjust trace buffer size

---

## Questions?

**"Why 0% for time.time()?"**  
Not an external boundary - internal deterministic code.

**"Why 46% for os.environ?"**  
Percentage is high but absolute (0.35µs) is tiny. Real I/O (5ms) makes it 0.007%.

**"Should I run these before deploying?"**  
Optional. They show theoretical max. Production benchmarking (APM) shows actual.

---

See **README.md** for full documentation  
See **docs/performance.md** for detailed analysis
