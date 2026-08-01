"""FastAPI Server exposing KCJ Autonomic Cycle execution, Mermaid rendering, and Log Video generation endpoints."""

from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from kcj_mustar import __version__
from kcj_mustar.autonomic_system import run_autonomic_cycle
from kcj_mustar.mermaid_engine import render_mermaid_to_svg, instaui_mermaid_component, ariel_mermaid_style
from kcj_mustar.video_engine import convert_log_to_video

app = FastAPI(
    title="KCJ-MuStar Autonomic & Visualization Server",
    description="FastAPI Web Server exposing KCJ multi-lingual cycles, PDDL synthesis, Mermaid diagram rendering, and Log-to-Video generation",
    version=__version__
)


class CycleRequest(BaseModel):
    state: str = "unibit_l1_execution_wip"
    use_gemma: bool = True


class MermaidRequest(BaseModel):
    code: str = "graph TD\n  A[State] --> B[PDDL_Plan]\n  B --> C[OCEL_Check]\n  C --> D[BLAKE3_Dispatch]"
    theme: Optional[str] = "canvas-dark"
    accent_color: Optional[str] = "#89b4fa"


@app.get("/")
def health_check():
    """Server health check endpoint."""
    return {
        "status": "ONLINE",
        "system": "KCJ-MuStar Autonomic Server",
        "version": __version__
    }


@app.post("/v1/cycle/run")
def execute_autonomic_cycle(req: CycleRequest) -> Dict[str, Any]:
    """Execute one full KCJ Autonomic cycle (Chinese strategy, Japanese quality, Korean dispatch)."""
    try:
        res = run_autonomic_cycle(state=req.state, use_gemma=req.use_gemma)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/mermaid/render")
def render_mcp_mermaid(req: MermaidRequest):
    """Render Mermaid code to mcp-mermaid SVG format."""
    svg_content = render_mermaid_to_svg(req.code)
    return Response(content=svg_content, media_type="image/svg+xml")


@app.post("/v1/mermaid/instaui")
def render_instaui_mermaid(req: MermaidRequest):
    """Render InstaUI Mermaid component JSON payload."""
    return instaui_mermaid_component(req.code, theme=req.theme or "canvas-dark")


@app.post("/v1/mermaid/ariel")
def render_ariel_mermaid(req: MermaidRequest):
    """Render Ariel design system styled Mermaid HTML container."""
    html_out = ariel_mermaid_style(req.code, accent_color=req.accent_color or "#89b4fa")
    return Response(content=html_out, media_type="text/html")


@app.post("/v1/video/generate")
def generate_log_video_endpoint(state: str = Query("chicago_tdd_api_video", description="State name for cycle")):
    """Run Chicago TDD cycle and return generated MP4 video file."""
    output_path = Path("scratch/chicago_tdd_api_execution.mp4")
    log_data = run_autonomic_cycle(state=state, use_gemma=True)
    video_path = convert_log_to_video(log_data=log_data, output_path=output_path, fps=1)
    
    if not video_path.exists():
        raise HTTPException(status_code=500, detail="Failed to generate MP4 video file")
    
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename="chicago_tdd_execution.mp4"
    )
