"""Typer CLI interface for KCJ-MuStar, Autonomic Cycles, and Mermaid Rendering Engines."""

import sys
import json
import typer
from pathlib import Path

from kcj_mustar import __version__
from kcj_mustar.autonomic_system import run_autonomic_cycle
from kcj_mustar.mermaid_engine import render_mermaid_to_svg, instaui_mermaid_component, ariel_mermaid_style

app = typer.Typer(
    name="kcj",
    help="KCJ-MuStar CLI: Multi-Lingual Autonomic League, PDDL Synthesis & Mermaid Engines",
    add_completion=False
)

mermaid_app = typer.Typer(help="Mermaid Diagram Rendering (mcp-mermaid, instaui-mermaid, ariel-mermaid)")
app.add_typer(mermaid_app, name="mermaid")


@app.command()
def version():
    """Show current version of KCJ-MuStar."""
    typer.echo(f"KCJ-MuStar CLI version {__version__}")


@app.command()
def run(
    state: str = typer.Option("unibit_l1_execution_wip", "--state", "-s", help="Initial state string"),
    use_gemma: bool = typer.Option(True, "--gemma/--no-gemma", help="Connect to local Gemma 4 server on port 8080")
):
    """Run one full KCJ autonomic cycle across Chinese strategy, Japanese quality, and Korean dispatch."""
    typer.echo(f"=== Running KCJ Autonomic Cycle (State: {state}) ===")
    res = run_autonomic_cycle(state=state, use_gemma=use_gemma)
    typer.echo(json.dumps(res, indent=2, ensure_ascii=False))


@mermaid_app.command("render")
def render_mcp(
    code: str = typer.Argument("graph TD\n  A[State] --> B[Plan]\n  B --> C[Dispatch]", help="Mermaid diagram code"),
    output: Path = typer.Option(None, "--output", "-o", help="Optional output SVG file path")
):
    """Render Mermaid code using mcp-mermaid SVG renderer engine."""
    svg = render_mermaid_to_svg(code)
    if output:
        output.write_text(svg, encoding="utf-8")
        typer.echo(f"✓ Saved mcp-mermaid SVG to {output}")
    else:
        typer.echo(svg)


@mermaid_app.command("instaui")
def render_instaui(
    code: str = typer.Argument("graph TD\n  A[Init] --> B[InstaUI]", help="Mermaid diagram code"),
    theme: str = typer.Option("canvas-dark", "--theme", "-t", help="InstaUI theme name")
):
    """Render InstaUI Mermaid component wrapper."""
    comp = instaui_mermaid_component(code, theme=theme)
    typer.echo(json.dumps(comp, indent=2))


@mermaid_app.command("ariel")
def render_ariel(
    code: str = typer.Argument("graph TD\n  A[Init] --> B[ArielStyle]", help="Mermaid diagram code"),
    accent: str = typer.Option("#89b4fa", "--accent", "-a", help="Ariel accent color hex")
):
    """Render Ariel design system styled Mermaid HTML container."""
    html_out = ariel_mermaid_style(code, accent_color=accent)
    typer.echo(html_out)


def main():
    app()


if __name__ == "__main__":
    main()
