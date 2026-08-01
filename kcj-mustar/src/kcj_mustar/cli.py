"""Typer CLI interface for KCJ-MuStar, Autonomic Cycles, FastAPI Server launch, Mermaid Rendering, and Log Video Engine."""

import sys
import json
import typer
import uvicorn
from pathlib import Path

from kcj_mustar import __version__
from kcj_mustar.autonomic_system import run_autonomic_cycle
from kcj_mustar.mermaid_engine import render_mermaid_to_svg, instaui_mermaid_component, ariel_mermaid_style
from kcj_mustar.video_engine import convert_log_to_video

app = typer.Typer(
    name="kcj",
    help="KCJ-MuStar CLI: Multi-Lingual Autonomic League, FastAPI Web Server, PDDL Synthesis, Mermaid & Log Video Engines",
    add_completion=False
)

mermaid_app = typer.Typer(help="Mermaid Diagram Rendering (mcp-mermaid, instaui-mermaid, ariel-mermaid)")
video_app = typer.Typer(help="Log-to-Video Engine (Chicago TDD & OCEL event log MP4 video renderer)")

app.add_typer(mermaid_app, name="mermaid")
app.add_typer(video_app, name="video")


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


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Loopback host address"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to listen on"),
    reload: bool = typer.Option(False, "--reload", help="Enable uvicorn auto-reload")
):
    """Launch FastAPI web server for KCJ autonomic cycles, REST endpoints, and video/mermaid APIs."""
    typer.echo(f"=== Launching KCJ-MuStar FastAPI Server on http://{host}:{port} ===")
    uvicorn.run("kcj_mustar.server:app", host=host, port=port, reload=reload)


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


@video_app.command("generate")
def generate_log_video(
    state: str = typer.Option("chicago_tdd_video_state", "--state", "-s", help="State for cycle run"),
    output: Path = typer.Option(Path("scratch/chicago_tdd_execution.mp4"), "--output", "-o", help="Output MP4 video file path"),
    fps: int = typer.Option(1, "--fps", help="Frames per second duration")
):
    """Execute Chicago TDD autonomic cycle and render execution logs into an MP4 video."""
    typer.echo(f"=== Running Chicago TDD Autonomic Cycle for Video Generation ===")
    log_data = run_autonomic_cycle(state=state, use_gemma=True)
    
    typer.echo(f"=== Rendering Log Video to {output} ===")
    video_file = convert_log_to_video(log_data=log_data, output_path=output, fps=fps)
    typer.echo(f"✓ Log MP4 Video successfully generated at {video_file.resolve()}")


def main():
    app()


if __name__ == "__main__":
    main()
