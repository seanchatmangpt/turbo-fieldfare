"""구동 (Actuation) & 디스패치 (Dispatch) - High-Speed Action Execution & Causal Receipt Store in Korean."""

import json
from pathlib import Path
import blake3
import dspy

STORE_PATH = Path("/Users/sac/turbo-fieldfare/kcj-mustar/scratch/mu_star_store/receipts.jsonl")


class 실시간디스패치Signature(dspy.Signature):
    """검증된 계획을 바탕으로 초고속 구동 디스패치 명령을 생성함."""
    검증계획_ko = dspy.InputField(desc="검증 완료된 실행 계획")
    구동명령_ko = dspy.OutputField(desc="즉시 실행 가능한 디스패치 명령어")


def append_causal_receipt(plan_id: str, receipt_hash: str, status: str) -> None:
    """Store causal receipt into persistent mu_star_store JSONL log."""
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "plan_id": plan_id,
        "receipt": receipt_hash,
        "status": status
    }
    with open(STORE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def 디스패치실행(plan_id: str, verified: bool, apm_level: int = 100000) -> dict[str, str | bool | int]:
    """Execute high-speed action dispatch in Korean and append causal receipt."""
    if not verified:
        return {"성공": False, "메시지": "검증 실패: 디스패치거부", "APM": 0}
    
    hasher = blake3.blake3()
    hasher.update(f"DISPATCH:{plan_id}:{verified}:{apm_level}".encode("utf-8"))
    receipt_hash = hasher.hexdigest()

    append_causal_receipt(plan_id=plan_id, receipt_hash=receipt_hash, status="DISPATCHED")

    return {
        "성공": True,
        "디스패치ID": plan_id,
        "메시지": f"실시간 구동 명령 디스패치 완료: [{plan_id}]",
        "APM": apm_level,
        "영수증": receipt_hash
    }
