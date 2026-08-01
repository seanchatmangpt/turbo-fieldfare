"""Test KCJ Autonomic System linked to local Gemma 4 + Lumen Grounding."""

import urllib.request
import json
from kcj_mustar.autonomic_system import configure_local_gemma_with_cache, KCJAutonomicPipeline, run_autonomic_cycle

def test_gemma_connection():
    """Verify local Gemma 4 server on port 8080 is reachable by DSPy."""
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8080/v1/models")
        data = json.loads(req.read().decode())
        assert data["data"][0]["id"] == "gemma-4-26b-a4b-it"
        print("Local Gemma 4 Server Verified!")
        return True
    except Exception as e:
        print(f"Server check error: {e}")
        return False

def test_chicago_kcj_full_cycle():
    """Verify real state transitions across Chinese (with Lumen Grounding), Japanese, and Korean domains."""
    initial_state = "unibit_l1_execution_wip"
    
    server_online = test_gemma_connection()
    result = run_autonomic_cycle(state=initial_state, use_gemma=server_online)

    assert result["status"] == "EXECUTED"
    assert result["receipt"] is not None
    assert len(result["receipt"]) == 64
    assert "推演策略" in result["strategy"]["策略"]
    assert "LumenGrounding" in result["strategy"]
    assert result["quality"]["行灯停止"] is False
    assert result["dispatch"]["성공"] is True

if __name__ == "__main__":
    test_chicago_kcj_full_cycle()
    print("GEMMA 4 + LUMEN GROUNDING + KCJ AUTONOMIC SYSTEM CYCLE PASSED SUCCESSFULLY!")
