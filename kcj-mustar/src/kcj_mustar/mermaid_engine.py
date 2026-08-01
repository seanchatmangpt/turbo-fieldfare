"""Mermaid rendering components: mcp-mermaid, instaui-mermaid, and ariel-mermaid."""

import re
import html
from typing import Dict, Any


def render_mermaid_to_svg(mermaid_code: str, title: str = "Diagram") -> str:
    """Core mcp-mermaid renderer generating clean SVG representation from Mermaid diagram syntax."""
    clean_code = mermaid_code.strip()
    escaped_code = html.escape(clean_code)
    
    # Extract nodes for diagram layout
    lines = [line.strip() for line in clean_code.splitlines() if line.strip() and not line.startswith("%%")]
    nodes = []
    for line in lines:
        match = re.findall(r"([A-Za-z0-9_]+)\[(.*?)\]", line)
        for node_id, label in match:
            nodes.append((node_id, label))
            
    height = max(200, len(nodes) * 50 + 100)
    width = 600

    svg_nodes = []
    y_offset = 60
    for idx, (node_id, label) in enumerate(nodes):
        svg_nodes.append(
            f'<g transform="translate(50, {y_offset})">'
            f'<rect width="500" height="36" rx="6" fill="#1e1e2e" stroke="#89b4fa" stroke-width="2"/>'
            f'<text x="250" y="22" fill="#cdd6f4" font-family="sans-serif" font-size="14" text-anchor="middle">{html.escape(label or node_id)}</text>'
            f'</g>'
        )
        y_offset += 50

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <rect width="100%" height="100%" fill="#11111b" rx="8"/>
  <text x="20" y="35" fill="#89b4fa" font-family="sans-serif" font-size="18" font-weight="bold">{html.escape(title)}</text>
  {"".join(svg_nodes)}
</svg>"""
    return svg_content


def instaui_mermaid_component(mermaid_code: str, theme: str = "canvas-dark") -> Dict[str, Any]:
    """InstaUI component wrapper for responsive web app layout rendering of Mermaid diagrams."""
    svg = render_mermaid_to_svg(mermaid_code, title=f"InstaUI Mermaid ({theme})")
    return {
        "component": "InstaUIMermaidCard",
        "props": {
            "theme": theme,
            "code": mermaid_code,
            "svg": svg,
            "responsive": True,
            "interactive": True
        }
    }


def ariel_mermaid_style(mermaid_code: str, accent_color: str = "#89b4fa") -> str:
    """Ariel design system CSS & SVG wrapper styling Mermaid diagram components."""
    svg = render_mermaid_to_svg(mermaid_code, title="Ariel Styled Diagram")
    return f"""<div class="ariel-mermaid-container" style="border: 1px solid {accent_color}; padding: 16px; border-radius: 12px; background: #181825;">
  <style>
    .ariel-mermaid-container rect {{ transition: all 0.3s ease; }}
    .ariel-mermaid-container rect:hover {{ stroke: #f5e0dc; cursor: pointer; }}
  </style>
  {svg}
</div>"""
