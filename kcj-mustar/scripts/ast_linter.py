"""AST Quality & Construct Scanner for kcj-mustar.

Scans Python source trees for forbidden constructs:
- Forbidden `print()` calls (must use structured logging or explicit streams).
- Hardcoded literal strings and numbers inside functions (must be defined in Enum, Pydantic BaseSettings, or module-level constants).
"""

import ast
import sys
from pathlib import Path


class ConstructLinter(ast.NodeVisitor):
    def __init__(self, filename: Path):
        self.filename = filename
        self.violations: list[str] = []
        self.inside_function = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_inside = self.inside_function
        self.inside_function = True
        
        # Docstrings are valid first statements in functions
        body_start = 0
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            body_start = 1

        for stmt in node.body[body_start:]:
            self.visit(stmt)

        self.inside_function = old_inside

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        old_inside = self.inside_function
        self.inside_function = True

        body_start = 0
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            body_start = 1

        for stmt in node.body[body_start:]:
            self.visit(stmt)

        self.inside_function = old_inside

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.violations.append(
                f"{self.filename}:{node.lineno}:{node.col_offset}: "
                f"FORBIDDEN_CONSTRUCT: 'print()' calls are forbidden (use structured logging)"
            )
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        if self.inside_function:
            if isinstance(node.value, str):
                # Ignore trivial formatters, single char strings, empty strings, and dunder names
                val = node.value.strip()
                if len(val) > 2 and not val.startswith("__") and not val.startswith("%%") and not val.startswith("\n"):
                    self.violations.append(
                        f"{self.filename}:{node.lineno}:{node.col_offset}: "
                        f"HARDCODED_LITERAL_STRING: Hardcoded string literal '{node.value[:30]}...' found in function. Use Enum, Pydantic, or module Constant."
                    )
            elif isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                # Allow trivial numbers 0, 1, -1
                if node.value not in (0, 1, -1):
                    self.violations.append(
                        f"{self.filename}:{node.lineno}:{node.col_offset}: "
                        f"HARDCODED_LITERAL_NUMBER: Hardcoded numeric literal '{node.value}' found in function. Use Enum, Pydantic, or module Constant."
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
        sys.stderr.write("ERROR: src directory not found\n")
        return 1

    violations: list[str] = []
    for py_file in sorted(src_dir.rglob("*.py")):
        violations.extend(scan_file(py_file))

    if violations:
        sys.stderr.write("=== BUILD_BROKEN: AST CONSTRUCT & HARDCODED LITERAL VIOLATIONS FOUND ===\n")
        for v in violations[:30]:
            sys.stderr.write(f"  {v}\n")
        sys.stderr.write(f"\nTotal Violations: {len(violations)}\n")
        return 1

    sys.stdout.write("ALIVE: AST construct & literal scanner passed cleanly (no hardcoded literals found in functions)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
