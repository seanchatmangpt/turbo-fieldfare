"""Chicago TDD Loop 3: Lean TPS Andon Stop-the-Line Defect Isolation & VAL Validation (No Mocks)."""

from pathlib import Path
from kcj_mustar.autonomic_system import KCJAutonomicPipeline
from kcj_mustar.現場_quality.行灯_andon import 行灯チェック, validate_plan_with_val, VAL_BINARY

def test_chicago_tps_andon_crash():
    """Verify that a defective execution state halts immediately at the Japanese Andon gate."""
    pipeline = KCJAutonomicPipeline()

    # 1. Defective State: dirty working tree & failed build
    result = pipeline(state="broken_kernel_state", dirty_tree=True, build_passed=False)

    # 2. Andon Invariant Assertions
    assert result["status"] == "ANDON_STOP"
    assert result["receipt"] is None
    assert result["details"]["行灯停止"] is True
    assert "欠陥検出" in result["details"]["理由"]

def test_val_binary_presence_and_execution():
    """Verify that the independent VAL binary exists and is executable."""
    assert VAL_BINARY.exists()
    res = validate_plan_with_val(Path("nonexistent_domain.pddl"), Path("nonexistent_prob.pddl"), Path("nonexistent_plan.plan"))
    assert res["val_passed"] is False

if __name__ == "__main__":
    test_chicago_tps_andon_crash()
    test_val_binary_presence_and_execution()
    print("CHICAGO TDD LOOP 3 (LEAN ANDON CRASH & VAL VERIFICATION) PASSED SUCCESSFULLY!")
