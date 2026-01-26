"""
Benchmark actual external boundary crossings that Retrace intercepts.
"""

import time
import os

def test_environment_variable_access(iterations=10000):
    """Environment variables are external state"""
    start = time.perf_counter()
    
    for _ in range(iterations):
        val = os.environ.get('HOME', '')
    
    elapsed = time.perf_counter() - start
    return elapsed

def test_file_operations(iterations=1000):
    """File I/O is an external boundary"""
    import tempfile
    
    # Create temp file
    tf = tempfile.NamedTemporaryFile(mode='w', delete=False)
    filename = tf.name
    tf.write("test data")
    tf.close()
    
    start = time.perf_counter()
    
    for _ in range(iterations):
        with open(filename, 'r') as f:
            data = f.read()
    
    elapsed = time.perf_counter() - start
    
    # Cleanup
    os.unlink(filename)
    
    return elapsed

def run_benchmarks():
    print("="*70)
    print("EXTERNAL BOUNDARY CROSSING BENCHMARKS")
    print("="*70)
    print("These test actual boundaries that Retrace intercepts.")
    print("="*70)
    
    # Warmup
    test_environment_variable_access(100)
    test_file_operations(10)
    
    print("\n## Test 1: Environment variable access (10,000 iterations)")
    runs = []
    for i in range(5):
        elapsed = test_environment_variable_access(10000)
        runs.append(elapsed)
        print(f"  Run {i+1}: {elapsed*1000:.2f}ms ({10000/elapsed:.0f} calls/sec)")
    
    avg = sum(runs) / len(runs)
    print(f"  Average: {avg*1000:.2f}ms ({10000/avg:.0f} calls/sec)")
    print(f"  Per-call: {(avg/10000)*1000000:.2f}µs")
    
    print("\n## Test 2: File read operations (1,000 iterations)")
    runs = []
    for i in range(5):
        elapsed = test_file_operations(1000)
        runs.append(elapsed)
        print(f"  Run {i+1}: {elapsed*1000:.2f}ms ({1000/elapsed:.0f} ops/sec)")
    
    avg = sum(runs) / len(runs)
    print(f"  Average: {avg*1000:.2f}ms ({1000/avg:.0f} ops/sec)")
    print(f"  Per-operation: {(avg/1000)*1000:.2f}ms")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    run_benchmarks()
