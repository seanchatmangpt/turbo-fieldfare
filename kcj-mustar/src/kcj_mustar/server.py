"""FastAPI Server exposing KCJ Autonomic Cycle execution, Mermaid rendering, and Log Video generation endpoints."""

from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from kcj_mustar import __version__
from kcj_mustar.autonomic_system import run_autonomic_cycle
from kcj_mustar.models import AutonomicCycleResult, ExecutionStatus, SystemConstants
from kcj_mustar.mermaid_engine import render_mermaid_to_svg, instaui_mermaid_component, ariel_mermaid_style
from kcj_mustar.video_engine import convert_log_to_video

app = FastAPI(
    title="KCJ-MuStar Autonomic & Visualization Server",
    description="FastAPI Web Server exposing KCJ multi-lingual cycles, PDDL synthesis, Mermaid diagram rendering, and Log-to-Video generation",
    version=__version__
)


class CycleRequest(BaseModel):
    state: str = Field(default="unibit_l1_execution_wip", description="Initial state tag")
    use_gemma: bool = Field(default=True, description="Local Gemma server connection flag")


class MermaidRequest(BaseModel):
    code: str = Field(default="graph TD\n  A[State] --> B[PDDL_Plan]\n  B --> C[OCEL_Check]\n  C --> D[BLAKE3_Dispatch]", description="Mermaid diagram code")
    theme: Optional[str] = Field(default="canvas-dark", description="InstaUI theme name")
    accent_color: Optional[str] = Field(default="#89b4fa", description="Ariel accent color hex")


class HealthResponse(BaseModel):
    status: ExecutionStatus = ExecutionStatus.PASSED
    system: str = "KCJ-MuStar Autonomic Server"
    version: str = __version__


@app.get("/")
def health_check() -> HealthResponse:
    """Server health check endpoint."""
    return HealthResponse()


@app.post("/v1/cycle/run")
def execute_autonomic_cycle(req: CycleRequest) -> AutonomicCycleResult:
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
    video_path = convert_log_to_video(log_data=log_data.model_dump(), output_path=output_path, fps=1)
    
    if not video_path.exists():
        raise HTTPException(status_code=500, detail="Failed to generate MP4 video file")
    
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename="chicago_tdd_execution.mp4"
    )
