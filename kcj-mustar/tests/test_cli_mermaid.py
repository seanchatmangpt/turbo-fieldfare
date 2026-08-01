"""Tests for Typer CLI and Mermaid rendering engines (mcp-mermaid, instaui-mermaid, ariel-mermaid)."""

from typer.testing import CliRunner
from kcj_mustar.cli import app
from kcj_mustar.mermaid_engine import render_mermaid_to_svg, instaui_mermaid_component, ariel_mermaid_style

runner = CliRunner()

def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "KCJ-MuStar CLI version" in result.output

def test_mermaid_mcp_render():
    code = "graph TD\n  A[Node1] --> B[Node2]"
    svg = render_mermaid_to_svg(code, title="Test Diagram")
    assert "<svg" in svg
    assert "Node1" in svg
    assert "Node2" in svg

def test_mermaid_cli_mcp_command():
    result = runner.invoke(app, ["mermaid", "render", "graph TD\n  A[Start] --> B[End]"])
    assert result.exit_code == 0
    assert "<svg" in result.output

def test_mermaid_instaui_component():
    comp = instaui_mermaid_component("graph TD\n  A[App] --> B[Card]", theme="canvas-dark")
    assert comp["component"] == "InstaUIMermaidCard"
    assert comp["props"]["theme"] == "canvas-dark"

def test_mermaid_ariel_style():
    html_out = ariel_mermaid_style("graph TD\n  A[Init] --> B[Ariel]")
    assert 'class="ariel-mermaid-container"' in html_out
    assert "<svg" in html_out
