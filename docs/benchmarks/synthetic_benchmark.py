"""
Synthetic worst-case benchmark for Retrace overhead.

Measures pure proxy interception cost by calling external functions
in a tight loop with minimal actual work.
"""

import time
from datetime import datetime

def tight_loop_time_calls(iterations=10000):
    """Worst case: Call time.time() repeatedly"""
    start = time.perf_counter()
    
    for _ in range(iterations):
        t = time.time()
    
    elapsed = time.perf_counter() - start
    return elapsed

def tight_loop_datetime_calls(iterations=10000):
    """Worst case: Call datetime.now() repeatedly"""
    start = time.perf_counter()
    
    for _ in range(iterations):
        dt = datetime.now()
    
    elapsed = time.perf_counter() - start
    return elapsed

def run_benchmarks():
    """Run all synthetic benchmarks"""
    print("="*70)
    print("RETRACE SYNTHETIC WORST-CASE BENCHMARKS")
    print("="*70)
    print("These measure pure proxy interception overhead in tight loops.")
    print("Real applications will see much lower overhead.")
    print("="*70)
    
    # Warmup
    tight_loop_time_calls(100)
    tight_loop_datetime_calls(100)
    
    print("\n## Test 1: time.time() calls (10,000 iterations)")
    print("Measures: Cost of intercepting time module calls")
    
    runs = []
    for i in range(5):
        elapsed = tight_loop_time_calls(10000)
        runs.append(elapsed)
        print(f"  Run {i+1}: {elapsed*1000:.2f}ms ({10000/elapsed:.0f} calls/sec)")
    
    avg = sum(runs) / len(runs)
    print(f"  Average: {avg*1000:.2f}ms ({10000/avg:.0f} calls/sec)")
    print(f"  Per-call overhead: {(avg/10000)*1000000:.2f}µs")
    
    print("\n## Test 2: datetime.now() calls (10,000 iterations)")
    print("Measures: Cost of intercepting datetime module calls")
    
    runs = []
    for i in range(5):
        elapsed = tight_loop_datetime_calls(10000)
        runs.append(elapsed)
        print(f"  Run {i+1}: {elapsed*1000:.2f}ms ({10000/elapsed:.0f} calls/sec)")
    
    avg = sum(runs) / len(runs)
    print(f"  Average: {avg*1000:.2f}ms ({10000/avg:.0f} calls/sec)")
    print(f"  Per-call overhead: {(avg/10000)*1000000:.2f}µs")
    
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)
    print("This represents WORST CASE overhead:")
    print("- Tight loops calling external functions")
    print("- Zero actual business logic")
    print("- Maximum proxy interception density")
    print()
    print("Real applications will see much lower overhead because:")
    print("- Most code is internal (not intercepted)")
    print("- External calls do actual work (network, DB)")
    print("- Business logic dominates execution time")
    print("="*70)

if __name__ == '__main__':
    run_benchmarks()
