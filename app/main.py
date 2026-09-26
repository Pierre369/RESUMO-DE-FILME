"""
Servidor FastAPI Core do CineShorts Studio.
"""

import os
import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from app.services.antigravity_bridge import AntigravityBridge
from app.services.media_service import MediaService
from app.services.render_service import RenderService

app = FastAPI(title="CineShorts Studio", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount statics
app.mount("/static/output", StaticFiles(directory=OUTPUT_DIR), name="output")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

antigravity_bridge = AntigravityBridge()
media_service = MediaService()
render_service = RenderService()

class ScreenplayRequest(BaseModel):
    movie_title: str
    character: str
    scene_description: str
    aspect_ratio: str = "1:1"
    target_duration: int = 90

class RenderRequest(BaseModel):
    movie_path: str
    aspect_ratio: str = "1:1"
    narrator_voice: str = "pt-BR-AntonioNeural"
    screenplay_text: Optional[str] = None

@app.get("/")
async def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CineShorts Studio API is running. UI not found."}

@app.get("/api/status")
async def get_system_status():
    ag_info = antigravity_bridge.check_connection()
    return {
        "antigravity": ag_info,
        "gpu": {
            "name": "NVIDIA GeForce RTX 4060",
            "vram": "8 GB GDDR6",
            "cuda": "12.x / 13.x",
            "status": "Ready & Accelerated"
        },
        "engine_version": "1.0.0",
        "supported_aspect_ratios": ["1:1 (Quadrado)", "9:16 (Vertical)"]
    }

@app.get("/api/movies")
async def list_movies():
    movies = media_service.list_movies()
    return {"movies": movies}

@app.get("/api/references")
async def list_references():
    refs = media_service.list_references()
    return {"references": refs}

@app.post("/api/antigravity/generate-script")
async def generate_script(req: ScreenplayRequest):
    result = antigravity_bridge.generate_screenplay(
        movie_title=req.movie_title,
        character=req.character,
        scene_description=req.scene_description,
        aspect_ratio=req.aspect_ratio,
        target_duration=req.target_duration
    )
    return result

@app.post("/api/render")
async def start_render(req: RenderRequest, bg_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    output_filename = f"cineshort_{job_id}_{req.aspect_ratio.replace(':', 'x')}.mp4"
    
    bg_tasks.add_task(
        render_service.render_scene_async,
        job_id=job_id,
        movie_path=req.movie_path,
        aspect_ratio=req.aspect_ratio,
        narrator_voice=req.narrator_voice,
        output_filename=output_filename
    )
    return {"job_id": job_id, "status": "started", "output_filename": output_filename}

@app.get("/api/render/status/{job_id}")
async def get_render_status(job_id: str):
    return render_service.get_job_status(job_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
