"""Test KCJ Autonomic System execution with vendored DSPy."""

from kcj_mustar.autonomic_system import KCJAutonomicPipeline, run_autonomic_cycle

def test_autonomic_system_cycle():
    # 1. Normal Clean Cycle (EXECUTED)
    res = run_autonomic_cycle(state="initial_verification")
    assert res["status"] == "EXECUTED"
    assert res["receipt"] is not None
    assert len(res["receipt"]) == 64  # BLAKE3 hash hex length

    # 2. Japanese Andon Stop-the-Line Gate Test (ANDON_STOP)
    pipeline = KCJAutonomicPipeline()
    res_andon = pipeline(state="initial_verification", dirty_tree=True, build_passed=False)
    assert res_andon["status"] == "ANDON_STOP"
    assert res_andon["details"]["行灯停止"] is True

if __name__ == "__main__":
    test_autonomic_system_cycle()
    print("ALL KCJ AUTONOMIC SYSTEM INTEGRATION TESTS PASSED SUCCESSFULLY!")
