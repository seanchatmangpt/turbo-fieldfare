"""Test 2-Tier Cache (LRU Memory + Disk FanoutCache) integration in DSPy."""

import time
import dspy
from kcj_mustar.autonomic_system import configure_local_gemma_with_cache, KCJAutonomicPipeline

def test_cache_hit_performance():
    """Verify that 2-tier caching works and returns cached outputs instantly."""
    configure_local_gemma_with_cache()
    
    pipeline = KCJAutonomicPipeline()

    # 1. First Run (Populates Cache)
    t0 = time.time()
    res1 = pipeline(state="cached_state_test", dirty_tree=False, build_passed=True)
    t1 = time.time()
    first_duration = t1 - t0

    # 2. Second Run (Cache Hit)
    t2 = time.time()
    res2 = pipeline(state="cached_state_test", dirty_tree=False, build_passed=True)
    t3 = time.time()
    second_duration = t3 - t2

    # Invariants
    assert res1["receipt"] == res2["receipt"]
    assert res1["status"] == res2["status"]
    assert second_duration < 0.05  # Cache hit must complete in < 50ms

    print(f"First run duration: {round(first_duration * 1000, 2)} ms")
    print(f"Second run (cache hit) duration: {round(second_duration * 1000, 2)} ms")
    print("DSPY 2-TIER CACHE VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_cache_hit_performance()
