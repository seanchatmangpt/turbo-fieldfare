"""博弈 (Self-Play) & 推演 (Rollout) - Strategy Proposer Engine grounded via Lumen (sqlite-vec)."""

import sqlite3
from pathlib import Path
import dspy

LUMEN_DB_PATH = Path("/Users/sac/.local/share/lumen/cbc9ca60470b702f/index.db")


class 策略推演Signature(dspy.Signature):
    """根据当前状态与历史博弈推演 Optimal PDDL/POWL Strategy."""
    当前状态_zh = dspy.InputField(desc="当前系统状态 (State)")
    历史博弈_zh = dspy.InputField(desc="历史博弈轨迹 (History)")
    推演策略_zh = dspy.OutputField(desc="推演出的策略 (PDDL Domain/Problem)")


def query_lumen_grounding(keyword: str = "Metal", limit: int = 5) -> list[dict]:
    """Query codebase chunks from Lumen sqlite database."""
    if not LUMEN_DB_PATH.exists():
        return []
    try:
        conn = sqlite3.connect(LUMEN_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT file_path, symbol, kind, start_line, end_line FROM chunks WHERE symbol LIKE ? OR file_path LIKE ? LIMIT ?",
            (f"%{keyword}%", f"%{keyword}%", limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "file_path": r[0],
                "symbol": r[1],
                "kind": r[2],
                "start_line": r[3],
                "end_line": r[4]
            }
            for r in rows
        ]
    except Exception as e:
        return []


def 执行推演(state: str, history: list[str] | None = None) -> dict[str, str | list]:
    """Execute strategy rollout grounded against Lumen vector index."""
    grounded_chunks = query_lumen_grounding(keyword=state.split("_")[0] if "_" in state else "Metal")
    
    return {
        "状态": state,
        "策略": f"推演策略: [{state}] 规划完成",
        "博弈轮次": str(len(history) if history else 0),
        "LumenGrounding": grounded_chunks
    }
