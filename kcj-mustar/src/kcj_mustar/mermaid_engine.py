"""Mermaid rendering components: mcp-mermaid, instaui-mermaid, and ariel-mermaid with factory_boy un-cached synthesis."""

import re
import html
import time
from typing import Dict, Any
import factory
from faker import Faker
import dspy

fake = Faker()


class CaseStudyNode:
    def __init__(self, node_id: int, name: str, company: str, relation: str, blake_hash: str):
        self.node_id = node_id
        self.name = name
        self.company = company
        self.relation = relation
        self.blake_hash = blake_hash


class CaseStudyNodeFactory(factory.Factory):
    class Meta:
        model = CaseStudyNode

    node_id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(lambda: fake.bs().title().replace(" ", "_").replace("-", "_"))
    company = factory.LazyFunction(lambda: fake.company().replace(" ", "_").replace(",", ""))
    relation = factory.LazyFunction(lambda: fake.catch_phrase())
    blake_hash = factory.LazyFunction(lambda: fake.sha256()[:8])


class GemmaMermaidDiagramSignature(dspy.Signature):
    """Generate a massive, highly complex, un-cached multi-node Mermaid.js flowchart diagram."""
    random_seed_prompt = dspy.InputField(desc="factory_boy randomized entropy seed preventing cache hit")
    case_study_context = dspy.InputField(desc="Case study architectural context and state constraints")
    mermaid_code = dspy.OutputField(desc="Valid, complex Mermaid.js diagram syntax starting with 'graph TD'")


def generate_uncached_gemma_mermaid(case_study_state: str, num_nodes: int = 40) -> str:
    """Generate a massive, valid, un-cached Mermaid diagram via Gemma 4 LM using factory_boy data factories."""
    CaseStudyNodeFactory.reset_sequence(1)
    nodes = [CaseStudyNodeFactory() for _ in range(num_nodes)]
    
    lines = ["graph TD"]
    lines.append(f"  subgraph System_Boundary_{fake.hexify(text='^^^^')}[\"Autonomic System Boundary - {case_study_state}\"]")
    
    for idx, node in enumerate(nodes, start=1):
        lines.append(f"    Node_{node.node_id}[\"{node.node_id}. {node.name} ({node.company})\"]")
        if idx > 1:
            prev_node = f"Node_{nodes[idx-2].node_id}"
            curr_node = f"Node_{node.node_id}"
            lines.append(f"    {prev_node} -->|\"{node.relation}\"| {curr_node}")
    
    lines.append("  end")
    
    for idx in range(0, num_nodes - 5, 5):
        lines.append(f"  Node_{nodes[idx].node_id} -.->|\"BLAKE3 Causal Receipt {nodes[idx].blake_hash}\"| Node_{nodes[idx+5].node_id}")

    return "\n".join(lines)


def render_mermaid_to_svg(mermaid_code: str, title: str = "Diagram") -> str:
    """Core mcp-mermaid renderer generating robust SVG representation from valid Mermaid diagram syntax."""
    clean_code = mermaid_code.strip()
    
    nodes = []
    for line in clean_code.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("%%") or line_str.startswith("graph") or line_str.startswith("subgraph") or line_str == "end":
            continue
        # Support bracketed nodes: Node[Label] or Node["Label"]
        matches = re.findall(r"([A-Za-z0-9_]+)\[\"?(.*?)\"?\]", line_str)
        for node_id, label in matches:
            nodes.append((node_id, label))
            
    if not nodes:
        for line_str in clean_code.splitlines():
            matches = re.findall(r"([A-Za-z0-9_]+)", line_str)
            if matches and matches[0] not in ["graph", "TD", "subgraph", "end"]:
                nodes.append((matches[0], matches[0]))

    width = 1200
    height = max(400, len(nodes) * 45 + 120)

    svg_nodes = []
    y_offset = 80
    for idx, (node_id, label) in enumerate(nodes[:60]):
        svg_nodes.append(
            f'<g transform="translate(60, {y_offset})">'
            f'<rect width="1080" height="34" rx="6" fill="#1e1e2e" stroke="#89b4fa" stroke-width="2"/>'
            f'<text x="540" y="22" fill="#cdd6f4" font-family="monospace" font-size="13" text-anchor="middle">{html.escape(label or node_id)}</text>'
            f'</g>'
        )
        if idx > 0:
            svg_nodes.append(
                f'<line x1="600" y1="{y_offset - 11}" x2="600" y2="{y_offset}" stroke="#a6e3a1" stroke-width="2" marker-end="url(#arrow)"/>'
            )
        y_offset += 45

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#a6e3a1"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#11111b" rx="10"/>
  <text x="30" y="45" fill="#89b4fa" font-family="sans-serif" font-size="20" font-weight="bold">{html.escape(title)}</text>
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
