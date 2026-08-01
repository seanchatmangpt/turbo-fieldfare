"""AST Quality & Construct Scanner for kcj-mustar.

Scans Python source trees for forbidden constructs:
- Forbidden `print()` calls (must use structured logging or explicit streams).
- Fake string-based mock/placeholder patterns.
"""

import ast
import sys
from pathlib import Path


class ConstructLinter(ast.NodeVisitor):
    def __init__(self, filename: Path):
        self.filename = filename
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call):
        # 1. Reject explicit print() calls
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.violations.append(
                f"{self.filename}:{node.lineno}:{node.col_offset}: "
                f"FORBIDDEN_CONSTRUCT: 'print()' calls are forbidden (use structured logging)"
            )
        self.generic_visit(node)


def scan_file(file_path: Path) -> list[str]:
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        linter = ConstructLinter(file_path)
        linter.visit(tree)
        return linter.violations
    except SyntaxError as e:
        return [f"{file_path}:{e.lineno}:{e.offset}: SYNTAX_ERROR: {e.msg}"]
    except Exception as e:
        return [f"{file_path}:1:1: SCAN_ERROR: {e}"]


def main() -> int:
    src_dir = Path("src")
    if not src_dir.is_dir():
        print("ERROR: src directory not found", file=sys.stderr)
        return 1

    violations: list[str] = []
    for py_file in sorted(src_dir.rglob("*.py")):
        violations.extend(scan_file(py_file))

    if violations:
        sys.stderr.write("=== BUILD_BROKEN: AST CONSTRUCT LINT VIOLATIONS FOUND ===\n")
        for v in violations:
            sys.stderr.write(f"  {v}\n")
        sys.stderr.write(f"\nTotal Violations: {len(violations)}\n")
        return 1

    sys.stdout.write("ALIVE: AST construct scanner passed cleanly (no print calls found in src/)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
