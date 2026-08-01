"""Tests for FastAPI Web Server REST endpoints."""

from fastapi.testclient import TestClient
from kcj_mustar.server import app

client = TestClient(app)

def test_fastapi_health():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"
    assert "KCJ-MuStar" in res.json()["system"]

def test_fastapi_cycle_run():
    res = client.post("/v1/cycle/run", json={"state": "fastapi_unit_test", "use_gemma": True})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "EXECUTED"
    assert len(data["receipt"]) == 64

def test_fastapi_mermaid_render():
    res = client.post("/v1/mermaid/render", json={"code": "graph TD\n  A[State] --> B[Plan]"})
    assert res.status_code == 200
    assert "image/svg+xml" in res.headers["content-type"]
    assert "<svg" in res.text

def test_fastapi_mermaid_instaui():
    res = client.post("/v1/mermaid/instaui", json={"code": "graph TD\n  A --> B", "theme": "canvas-dark"})
    assert res.status_code == 200
    assert res.json()["component"] == "InstaUIMermaidCard"

def test_fastapi_mermaid_ariel():
    res = client.post("/v1/mermaid/ariel", json={"code": "graph TD\n  A --> B", "accent_color": "#89b4fa"})
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "ariel-mermaid-container" in res.text
