"""Test KCJ multi-lingual imports and execution functions."""

from kcj_mustar.博弈_selfplay.推演_rollout import 执行推演
from kcj_mustar.現場_quality.行灯_andon import 行灯チェック
from kcj_mustar.구동_actuation.디스패치_dispatch import 디스패치실행

def test_kcj_pipeline():
    # 1. Chinese Strategy Rollout
    res_zh = 执行推演("initial_state")
    assert "推演策略" in res_zh["策略"]

    # 2. Japanese Andon Quality Check
    res_ja = 行灯チェック(dirty_tree=False, build_passed=True)
    assert res_ja["行灯停止"] is False

    # 3. Korean Real-Time Dispatch
    res_ko = 디스패치실행(plan_id="plan-001", verified=True)
    assert res_ko["성공"] is True

if __name__ == "__main__":
    test_kcj_pipeline()
    print("ALL KCJ MULTI-LINGUAL TESTS PASSED SUCCESSFULLY!")
