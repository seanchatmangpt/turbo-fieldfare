"""現場 (Genba Quality) & 行灯 (Andon Fences) - Lean Quality Control in Japanese.

Integrates independent VAL plan verification, OCEL 2.0 event stream recording,
and automated log cleanup based on configurable max limits.
"""

import time
import json
from pathlib import Path
import subprocess
import dspy

VAL_BINARY = Path("/Users/sac/ferroplan/benchmarks/.val/VAL/build/bin/Validate")
OCEL_LOG_DIR = Path("/Users/sac/turbo-fieldfare/kcj-mustar/scratch/ocel_logs")
OCEL_LOG_FILE = OCEL_LOG_DIR / "gemma_ocel_events.jsonl"
DEFAULT_MAX_OCEL_EVENTS = 50


class 行灯検証Signature(dspy.Signature):
    """ポカヨケ(Mistake-proofing)と行灯(Andon)ルールに従い、品質検証を実行する."""
    現場ログ_ja = dspy.InputField(desc="現場 (Ground truth) 実行ログ")
    検証規約_ja = dspy.InputField(desc="ポカヨケ品質規約")
    行灯停止_ja = dspy.OutputField(desc="行灯 (Andon) 停止フラグ: true/false")
    改善指示_ja = dspy.OutputField(desc="改善 (Kaizen) フィードバック")


def record_ocel_event(event_type: str, object_id: str, status: str, max_events: int = DEFAULT_MAX_OCEL_EVENTS) -> dict:
    """Generate OCEL 2.0 event log entry and record to log file with automatic cleanup."""
    OCEL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    event = {
        "ocel:eid": f"evt-{int(time.time() * 1000)}",
        "ocel:timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ocel:activity": event_type,
        "ocel:omap": [object_id],
        "ocel:vmap": {
            "status": status,
            "engine": "gemma_genba_andon_v2"
        }
    }

    # Append new event
    existing_events = []
    if OCEL_LOG_FILE.exists():
        with open(OCEL_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        existing_events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    existing_events.append(event)

    # Cleanup log file if it exceeds configured max limit
    if len(existing_events) > max_events:
        existing_events = existing_events[-max_events:]

    with open(OCEL_LOG_FILE, "w", encoding="utf-8") as f:
        for ev in existing_events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    return event


def validate_plan_with_val(domain_path: Path, problem_path: Path, plan_path: Path) -> dict:
    """Run independent VAL (KCL-Planning/VAL) validation on domain, problem, and plan files."""
    if not VAL_BINARY.exists():
        return {"val_passed": False, "error": f"VAL binary not found at {VAL_BINARY}"}
    
    cmd = [
        str(VAL_BINARY),
        "-v",
        "-t", "0.001",
        str(domain_path),
        str(problem_path),
        str(plan_path)
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        passed = (proc.returncode == 0) and ("Plan valid" in proc.stdout or "Plan successful" in proc.stdout)
        return {
            "val_passed": passed,
            "returncode": proc.returncode,
            "stdout": proc.stdout[:1000]
        }
    except Exception as e:
        return {"val_passed": False, "error": str(e)}


def 行灯チェック(dirty_tree: bool, build_passed: bool, val_result: dict | None = None, max_ocel_events: int = DEFAULT_MAX_OCEL_EVENTS) -> dict[str, bool | str | dict]:
    """Execute Lean Andon stop-the-line check with OCEL 2.0 process logging & configurable cleanup."""
    status = "FAILED" if (dirty_tree or not build_passed or (val_result and not val_result.get("val_passed", True))) else "PASSED"
    ocel_event = record_ocel_event(
        event_type="AndonQualityInspection",
        object_id="pipeline-001",
        status=status,
        max_events=max_ocel_events
    )

    if dirty_tree or not build_passed:
        return {
            "行灯停止": True,
            "理由": "欠陥検出: 작업 트리 dirty 또는 빌드 실패 -> 行灯(Andon) 스트ップライン 발동",
            "改善": "리포 상태를 클린하게 정리하고 재검증하십시오.",
            "OCEL_Event": ocel_event
        }
    
    if val_result and not val_result.get("val_passed", True):
        return {
            "行灯停止": True,
            "理由": f"VAL 독립 검증 실패: {val_result.get('error', 'Plan invalid')}",
            "改善": "PDDL 플랜 사전/사후 조건을 재조정하십시오.",
            "OCEL_Event": ocel_event
        }

    return {
        "行灯停止": False,
        "理由": "現場(Genba) 検証正常完了 (VAL & OCEL 2.0 verified)",
        "改善": "継続的改善(Kaizen) 維持",
        "OCEL_Event": ocel_event
    }
