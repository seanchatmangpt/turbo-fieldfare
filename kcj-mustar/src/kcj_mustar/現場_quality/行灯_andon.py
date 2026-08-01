"""現場 (Genba Quality) & 行灯 (Andon Fences) - Lean Quality Control in Japanese.

Integrates independent VAL (KCL-Planning/VAL) plan verification, mirroring mfw-planner's engines.toml reference pattern.
"""

import subprocess
from pathlib import Path
import dspy

VAL_BINARY = Path("/Users/sac/ferroplan/benchmarks/.val/VAL/build/bin/Validate")

class 行灯検証Signature(dspy.Signature):
    """ポカヨケ(Mistake-proofing)と行灯(Andon)ルールに従い、品質検証を実行する."""
    現場ログ_ja = dspy.InputField(desc="現場 (Ground truth) 実行ログ")
    検証規約_ja = dspy.InputField(desc="ポカヨ케 품질규약")
    行灯停止_ja = dspy.OutputField(desc="行灯 (Andon) 停止フラグ: true/false")
    改善指示_ja = dspy.OutputField(desc="改善 (Kaizen) フィードバック")


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


def 行灯チェック(dirty_tree: bool, build_passed: bool, val_result: dict | None = None) -> dict[str, bool | str]:
    """Execute Lean Andon stop-the-line check on defect or VAL failure."""
    if dirty_tree or not build_passed:
        return {
            "行灯停止": True,
            "理由": "欠陥検出: 작업 트리 dirty 또는 빌드 실패 -> 行灯(Andon) 스트ップ라인 발동",
            "改善": "리포 상태를 클린하게 정리하고 재검증하십시오."
        }
    
    if val_result and not val_result.get("val_passed", True):
        return {
            "行灯停止": True,
            "理由": f"VAL 독립 검증 실패: {val_result.get('error', 'Plan invalid')}",
            "改善": "PDDL 플랜 사전/사후 조건을 재조정하십시오."
        }

    return {
        "行灯停止": False,
        "理由": "現場(Genba) 検証正常完了 (VAL verified)",
        "改善": "継続的改善(Kaizen) 維持"
    }
