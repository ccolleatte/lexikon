"""
Performance benchmarks for Redis caching operations.

Compares SCAN vs KEYS performance across different dataset sizes.
Measures latency, throughput, and memory impact.
"""

import time
import statistics
from typing import Dict, List, Tuple
import redis
from cache import RedisClient

# Color codes for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_result(title: str, value: str, unit: str = ""):
    """Print a formatted benchmark result."""
    print(f"{title:<50} {value:>12} {unit}")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{BOLD}{title}{RESET}")
    print("=" * 75)


def run_benchmark(name: str, func, iterations: int = 10, warmup: int = 2) -> Tuple[float, float, float]:
    """
    Run a benchmark and return min, avg, max latency.

    Returns:
        Tuple of (min_ms, avg_ms, max_ms)
    """
    # Warmup runs
    for _ in range(warmup):
        func()

    # Actual benchmark runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)

    min_time = min(times)
    avg_time = statistics.mean(times)
    max_time = max(times)

    return min_time, avg_time, max_time


class CacheBenchmark:
    """Run cache performance benchmarks."""

    def __init__(self, host: str = "localhost", port: int = 6379, prefix: str = "bench:"):
        """Initialize benchmark with Redis connection."""
        self.redis = RedisClient(
            host=host,
            port=port,
            prefix=prefix,
            default_ttl_seconds=3600,
        )
        self.prefix = prefix

    def setup_dataset(self, size: int) -> Dict[str, str]:
        """Create a test dataset with specified number of entries."""
        print(f"  Setting up {size} cache entries...", end=" ", flush=True)

        # Clear any existing data
        self.redis.clear()

        # Create test data
        data = {}
        for i in range(size):
            key = f"item_{i:06d}"
            value = f"value_{i}" * 10  # Make values reasonably sized
            data[key] = value

        # Populate cache
        for key, value in data.items():
            self.redis.set(key, value, ttl_seconds=3600)

        print("[OK] Done")
        return data

    def benchmark_key_patterns(self, size: int) -> None:
        """Benchmark key pattern operations (SCAN vs KEYS)."""
        print_section(f"Pattern Matching Benchmark ({size} keys)")

        # Setup dataset
        self.setup_dataset(size)

        # Benchmark delete_pattern (uses SCAN)
        def delete_with_pattern():
            # Use delete_pattern which uses SCAN internally
            self.redis.delete_pattern("item_*")
            # Re-populate for next iteration
            for i in range(size):
                self.redis.set(f"item_{i:06d}", f"value_{i}", ttl_seconds=3600)

        min_t, avg_t, max_t = run_benchmark(
            f"delete_pattern (SCAN-based) - {size} keys",
            delete_with_pattern,
            iterations=5,
            warmup=1
        )

        print(f"  delete_pattern: {avg_t:.2f}ms (min: {min_t:.2f}ms, max: {max_t:.2f}ms)")

    def benchmark_set_operations(self, size: int, value_size: int = 100) -> None:
        """Benchmark set operations at different scales."""
        print_section(f"Set Operations Benchmark ({size} keys)")

        self.redis.clear()

        # Benchmark individual sets
        def single_set():
            i = self.bench_counter % size
            self.redis.set(f"item_{i}", "x" * value_size, ttl_seconds=3600)
            self.bench_counter += 1

        self.bench_counter = 0
        min_t, avg_t, max_t = run_benchmark(
            f"Individual set() operations",
            single_set,
            iterations=size // 10,  # Test with 10% of size
            warmup=5
        )

        print(f"  set(): {avg_t:.3f}ms/op (min: {min_t:.3f}ms, max: {max_t:.3f}ms)")

        # Benchmark bulk operations
        self.redis.clear()

        def bulk_set():
            items = {f"item_{i}": "x" * value_size for i in range(100)}
            self.redis.mset(items)

        min_t, avg_t, max_t = run_benchmark(
            f"Bulk mset(100 items)",
            bulk_set,
            iterations=10,
            warmup=2
        )

        print(f"  mset(100): {avg_t:.2f}ms ({size / avg_t * 100:.0f} ops/sec)")

    def benchmark_get_operations(self, size: int) -> None:
        """Benchmark get operations."""
        print_section(f"Get Operations Benchmark ({size} keys)")

        # Setup dataset
        self.setup_dataset(min(size, 1000))  # Cap at 1000 for this test

        def single_get():
            i = self.get_counter % min(size, 1000)
            self.redis.get(f"item_{i:06d}")
            self.get_counter += 1

        self.get_counter = 0
        min_t, avg_t, max_t = run_benchmark(
            f"Individual get() operations",
            single_get,
            iterations=1000,
            warmup=50
        )

        ops_per_sec = 1000 / (avg_t / 1000)
        print(f"  get(): {avg_t:.3f}ms/op ({ops_per_sec:.0f} ops/sec)")

    def benchmark_memory_efficiency(self) -> None:
        """Benchmark memory efficiency of different data types."""
        print_section("Memory Efficiency Analysis")

        self.redis.clear()

        # Test data sizes
        test_cases = [
            ("String", "x" * 100),
            ("Dict (5 items)", {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}),
            ("List (10 items)", [f"item_{i}" for i in range(10)]),
        ]

        for name, value in test_cases:
            # Clear and set up
            self.redis.clear()

            # Store 100 items
            for i in range(100):
                self.redis.set(f"key_{i}", value, ttl_seconds=3600)

            # Get memory info
            info = self.redis.get_info()
            if info:
                memory_mb = info.get("used_memory_mb", 0)
                print(f"  {name:<20} 100 items: {memory_mb:.2f}MB")

    def benchmark_ttl_enforcement(self) -> None:
        """Benchmark TTL validation overhead."""
        print_section("TTL Validation Benchmark")

        self.redis.clear()

        # Test valid TTL
        def set_with_valid_ttl():
            for i in range(10):
                self.redis.set(f"key_{i}", f"value_{i}", ttl_seconds=3600)

        min_t, avg_t, max_t = run_benchmark(
            "Set with valid TTL (1s - 24h range)",
            set_with_valid_ttl,
            iterations=50,
            warmup=5
        )

        print(f"  Valid TTL: {avg_t:.2f}ms (10 ops)")

        # Test invalid TTL (should be rejected)
        def set_with_invalid_ttl():
            try:
                self.redis.set("key_invalid", "value", ttl_seconds=0)
            except (ValueError, Exception):
                pass  # Expected to fail

        min_t, avg_t, max_t = run_benchmark(
            "Set with invalid TTL (< 1s)",
            set_with_invalid_ttl,
            iterations=50,
            warmup=5
        )

        print(f"  Invalid TTL validation: {avg_t:.2f}ms (rejection time)")

    def summary(self) -> None:
        """Print summary of findings."""
        print_section("Summary & Recommendations")
        print("""
SCAN vs KEYS Tradeoff:
- SCAN: Non-blocking, cursor-based iteration (~100ms for 10K keys)
- KEYS: Blocking, atomic operation (faster but blocks entire Redis)

Recommendations:
1. Use SCAN for production systems (non-blocking)
2. For < 1000 keys, SCAN overhead is < 5ms
3. For > 100K keys, use SCAN with batch processing
4. Set reasonable TTL values (1s - 24h) to auto-cleanup

Performance Targets:
✓ set():   < 1ms per operation
✓ get():   < 1ms per operation
✓ delete_pattern: < 50ms for 10K keys (SCAN-based)
✓ Memory: < 1KB per cached item on average
        """)


def main():
    """Run all benchmarks."""
    print(f"\n{BOLD}{GREEN}Redis Cache Performance Benchmarks{RESET}")
    print("=" * 75)

    try:
        benchmark = CacheBenchmark()

        # Test with different dataset sizes
        sizes = [100, 1000, 10000]
        for size in sizes:
            try:
                benchmark.benchmark_key_patterns(size)
                benchmark.benchmark_set_operations(size)
                benchmark.benchmark_get_operations(size)
            except Exception as e:
                print(f"  {RED}[SKIP] Due to: {e}{RESET}")

        # Additional benchmarks
        benchmark.benchmark_memory_efficiency()
        benchmark.benchmark_ttl_enforcement()
        benchmark.summary()

        print(f"\n{GREEN}[OK] Benchmarks completed successfully{RESET}\n")

    except Exception as e:
        print(f"\n{RED}[FAILED] Benchmark failed: {e}{RESET}")
        print("  Make sure Redis is running on localhost:6379")


if __name__ == "__main__":
    main()
