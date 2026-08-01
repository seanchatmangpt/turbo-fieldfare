"""Log-to-Video Engine: Converts Chicago TDD execution logs & OCEL event streams into MP4 videos."""

import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any


def convert_log_to_video(
    log_data: Dict[str, Any],
    output_path: Path,
    fps: int = 1,
    duration_per_step: float = 2.0
) -> Path:
    """Transform Chicago TDD log dictionary into an MP4 video visualization using PIL and ffmpeg."""
    from PIL import Image, ImageDraw, ImageFont

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    receipt = str(log_data.get("receipt", "N/A"))
    status = str(log_data.get("status", "EXECUTED"))
    ocel_eid = str(log_data.get("quality", {}).get("OCEL_Event", {}).get("ocel:eid", "evt-000"))
    dispatch_apm = log_data.get("dispatch", {}).get("APM", 100000)

    frame_texts = [
        f"CHICAGO TDD EXECUTION LOOP: {status}",
        "Phase 1 (Chinese Strategy): PDDL+/POWL Hyper-Graph Synthesized",
        f"Phase 2 (Japanese Genba Quality): OCEL Event {ocel_eid} PASSED",
        f"Phase 3 (Korean Dispatch): Executed at {dispatch_apm:,} APM",
        f"BLAKE3 Causal Receipt: {receipt[:32]}..."
    ]

    temp_dir = Path(tempfile.mkdtemp(prefix="chicago_video_"))
    try:
        width, height = 1280, 720
        font = ImageFont.load_default()

        for idx, text in enumerate(frame_texts):
            img_path = temp_dir / f"frame_{idx:03d}.png"
            
            img = Image.new("RGB", (width, height), color=(17, 17, 27))
            draw = ImageDraw.Draw(img)

            # Header
            draw.text((40, 40), "CHICAGO TDD AUTONOMIC LOG STREAM", fill=(137, 180, 250), font=font)
            draw.line([(40, 70), (1240, 70)], fill=(137, 180, 250), width=2)

            # Frame narrative step
            draw.text((40, 180), f"Step {idx+1} of {len(frame_texts)}:", fill=(249, 226, 175), font=font)
            draw.text((40, 220), text, fill=(205, 214, 244), font=font)

            # BLAKE3 hash footer
            draw.text((40, 620), f"BLAKE3 RECEIPT: {receipt}", fill=(166, 227, 161), font=font)

            img.save(img_path)

        # Concatenate frame images into H.264 MP4 video
        ffmpeg_concat_cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(fps),
            "-i", str(temp_dir / "frame_%03d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]
        res = subprocess.run(ffmpeg_concat_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg video concatenation failed: {res.stderr}")

        return output_path
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
