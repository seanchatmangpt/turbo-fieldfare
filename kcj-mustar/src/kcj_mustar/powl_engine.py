"""POWL (Partially Ordered Workflow Language) Diagram Renderer aligned with ~/POWL models & mfw-planner architecture."""

import html
from typing import Dict, Any, List


def generate_powl_mermaid_from_run(cycle_result: Dict[str, Any], entropy_seed: str = "") -> str:
    """Transform real Chicago TDD cycle output into a valid POWL (Partially Ordered Workflow Language) Mermaid diagram."""
    
    state = cycle_result.get("strategy", {}).get("状态", "cluster_idle")
    receipt = str(cycle_result.get("receipt", "0" * 64))
    ocel_eid = cycle_result.get("quality", {}).get("OCEL_Event", {}).get("ocel:eid", "evt-000")
    dispatch_apm = cycle_result.get("dispatch", {}).get("APM", 100000)

    lines = ["graph TD"]
    lines.append(f"  subgraph POWL_Root_Model[\"POWL Model: KCJ Autonomic Cycle ({state})\"]")
    
    # 1. Partial Order Node: Chinese Strategy Engine (博弈_selfplay)
    lines.append("    subgraph PO_Chinese_Strategy[\"Partial Order: 博弈_selfplay (Chinese Strategy Engine)\"]")
    lines.append("      T1[\"Transition: Query Lumen sqlite-vec Vector Index\"]")
    lines.append("      T2[\"Transition: Synthesize Agricola PDDL+ Domain (568 Lines)\"]")
    lines.append("      T3[\"Transition: Construct POWL Hyper-Graph (100 Nodes, 64 Workers)\"]")
    lines.append("      T1 --> T2 --> T3")
    lines.append("    end")

    # 2. Choice Gate & Partial Order Node: Japanese Quality Engine (現場_quality)
    lines.append("    subgraph Choice_Japanese_Quality[\"Choice Gate & Andon Fences: 現場_quality (Japanese Quality Control)\"]")
    lines.append("      Q1{\"Choice Gate: Val PDDL Verification & Tree Check\"}")
    lines.append("      Q_Pass[\"Transition: Emit OCEL 2.0 Event Log (" + ocel_eid + ")\"]")
    lines.append("      Q_Fail[\"Transition: Trigger Andon Cord Line-Stop (行灯停止)\"]")
    lines.append("      Q1 -->|\"Pass Invariants\"| Q_Pass")
    lines.append("      Q1 -->|\"Detect Defect\"| Q_Fail")
    lines.append("    end")

    # 3. Partial Order Node: Korean Actuation Engine (구동_actuation)
    lines.append("    subgraph PO_Korean_Actuation[\"Partial Order: 구동_actuation (Korean Real-Time Dispatch)\"]")
    lines.append(f"      D1[\"Transition: Execute High-Speed Dispatch ({dispatch_apm:,} APM)\"]")
    lines.append(f"      D2[\"Transition: Append Cryptographic BLAKE3 Receipt ({receipt[:16]}...)\"]")
    lines.append("      D1 --> D2")
    lines.append("    end")

    lines.append("  end")

    # Connect Partial Order & Choice Blocks via POWL Control Edge Dependencies
    lines.append("  PO_Chinese_Strategy --> Choice_Japanese_Quality")
    lines.append("  Q_Pass --> PO_Korean_Actuation")

    if entropy_seed:
        lines.append(f"  %% Entropy Seed: {entropy_seed}")

    return "\n".join(lines)


def render_powl_to_svg(powl_mermaid_code: str, title: str = "POWL Workflow Diagram") -> str:
    """Render POWL Mermaid workflow diagram into dark-mode SVG format."""
    clean_code = powl_mermaid_code.strip()
    
    # Parse subgraphs and transitions
    nodes = []
    for line in clean_code.splitlines():
        line_str = line.strip()
        if "[\"" in line_str and "\"]" in line_str:
            parts = line_str.split("[\"")
            node_id = parts[0].strip().replace("subgraph ", "")
            label = parts[1].split("\"]")[0]
            nodes.append((node_id, label))
        elif "{\"" in line_str and "\"}" in line_str:
            parts = line_str.split("{\"")
            node_id = parts[0].strip()
            label = parts[1].split("\"}")[0]
            nodes.append((node_id, label))

    width = 1100
    height = max(500, len(nodes) * 55 + 140)

    svg_nodes = []
    y_offset = 80
    for idx, (node_id, label) in enumerate(nodes):
        is_choice = "Choice Gate" in label
        box_color = "#f9e2af" if is_choice else ("#89b4fa" if "Partial Order" in label else "#1e1e2e")
        text_color = "#11111b" if is_choice or "Partial Order" in label else "#cdd6f4"
        
        svg_nodes.append(
            f'<g transform="translate(50, {y_offset})">'
            f'<rect width="1000" height="40" rx="8" fill="{box_color}" stroke="#a6e3a1" stroke-width="2"/>'
            f'<text x="500" y="25" fill="{text_color}" font-family="monospace" font-size="14" font-weight="bold" text-anchor="middle">{html.escape(label)}</text>'
            f'</g>'
        )
        if idx > 0:
            svg_nodes.append(
                f'<line x1="550" y1="{y_offset - 15}" x2="550" y2="{y_offset}" stroke="#a6e3a1" stroke-width="2" marker-end="url(#arrow)"/>'
            )
        y_offset += 55

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#a6e3a1"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#11111b" rx="10"/>
  <text x="30" y="45" fill="#89b4fa" font-family="sans-serif" font-size="22" font-weight="bold">{html.escape(title)}</text>
  {"".join(svg_nodes)}
</svg>"""
