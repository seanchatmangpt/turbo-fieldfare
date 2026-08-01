"""Chicago TDD Integration Test: Full Dogfooding Loop with Gemma 4 LM Inference, Combinatorial Maximalist PDDL+, & OCEL Event Log Verification."""

import urllib.request
import json
from pathlib import Path
from kcj_mustar.autonomic_system import configure_local_gemma_with_cache, KCJAutonomicPipeline, run_autonomic_cycle
from kcj_mustar.models import ExecutionStatus, AutonomicCycleResult
from kcj_mustar.現場_quality.行灯_andon import OCEL_LOG_FILE

def verify_gemma_server_online() -> bool:
    """Verify local Gemma 4 Apple Silicon Metal server on port 8080 is live and responding."""
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=3)
        data = json.loads(req.read().decode())
        models = [m["id"] for m in data.get("data", [])]
        assert "gemma-4-26b-a4b-it" in models
        print("✓ Gemma 4 Server Verified Live (gemma-4-26b-a4b-it)")
        return True
    except Exception as e:
        print(f"✗ Gemma 4 Server Reachability Check Failed: {e}")
        return False


def test_chicago_kcj_full_dogfood_loop():
    """Execute complete Chicago TDD dogfooding loop verifying Combinatorial Maximalist PDDL+ plan generation, Gemma 4 LM integration, and OCEL emission."""
    gemma_live = verify_gemma_server_online()
    assert gemma_live, "Gemma 4 server must be running on http://127.0.0.1:8080 for Chicago TDD dogfood loop"

    initial_state = "hyperdimensional_combinatorial_max_wip"
    
    # 1. Run full autonomic cycle through Gemma 4 LM + DSPy 2-Tier Cache
    result: AutonomicCycleResult = run_autonomic_cycle(state=initial_state, use_gemma=True)

    # 2. Verify Execution Status & BLAKE3 Receipt
    assert result.status == ExecutionStatus.EXECUTED
    assert result.receipt is not None
    assert len(result.receipt) == 64, f"Invalid BLAKE3 receipt length: {len(result.receipt)}"

    # 3. Verify Combinatorial Maximalist PDDL / POWL Plan Generation (100 Nodes, 64 Workers)
    strategy = result.strategy
    assert strategy is not None
    assert "PDDL" in strategy, "Strategy missing PDDL spec"
    assert "(define (domain agricola)" in strategy["PDDL"]["domain_pddl"]
    assert "Combinatorial-Maximal-KCJ-hyperdimensional_combinatorial_max_wip" in strategy["PDDL"]["problem_pddl"]
    assert "POWL_COMBINATORIAL_HYPERGRAPH_V4" in strategy["PDDL"]["powl_graph"]
    assert "LumenGrounding" in strategy, "Strategy missing Lumen vector database grounding"
    print(f"✓ Combinatorial Maximalist PDDL Domain ({len(strategy['PDDL']['domain_pddl'].splitlines())} lines) & Problem Specifications Verified!")

    # 4. Verify Japanese Genba Quality Gate & OCEL 2.0 Event Log Emission
    quality = result.quality
    assert quality is not None
    assert quality["行灯停止"] is False, "Quality check unexpectedly triggered Andon line-stop"
    assert "OCEL_Event" in quality, "Quality check missing OCEL event record"
    ocel_event = quality["OCEL_Event"]
    assert ocel_event["ocel:activity"] == "AndonQualityInspection"
    assert ocel_event["ocel:vmap"]["status"] == "PASSED"

    # Verify persistent OCEL log file write
    assert OCEL_LOG_FILE.exists(), f"OCEL log file missing at {OCEL_LOG_FILE}"
    with open(OCEL_LOG_FILE, "r", encoding="utf-8") as f:
        log_lines = [line.strip() for line in f if line.strip()]
        assert len(log_lines) > 0
    print(f"✓ OCEL 2.0 Event Log File Verified at {OCEL_LOG_FILE} ({len(log_lines)} events stored)")

    # 5. Verify Korean Real-Time Dispatch & APM Speed
    dispatch = result.dispatch
    assert dispatch is not None
    assert dispatch["성공"] is True
    assert dispatch["APM"] == 100000
    assert len(dispatch["영수증"]) == 64
    print("✓ High-APM Korean Real-Time Dispatch Verified!")


if __name__ == "__main__":
    test_chicago_kcj_full_dogfood_loop()
    print("\n=== ALL CHICAGO TDD DOGFOODING CHECKS PASSED WITH COMBINATORIAL MAXIMALIST PDDL+ & LIVE GEMMA 4 SERVER! ===")
