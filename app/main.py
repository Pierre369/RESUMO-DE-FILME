"""
Servidor FastAPI Core do CineShorts Studio v2.0.
Arquitetura completa de estúdio com navegação por abas (Dashboard, Projetos, Modelos de Estilo),
upload direto de arquivos, seleção de personagens para ponto de vista, sugestão de cenas de impacto,
modo inteligente 100% automático e modo diretor guiado.
"""

import os
import uuid
import shutil
import asyncio
from typing import Optional, List
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.antigravity_bridge import AntigravityBridge
from app.services.media_service import MediaService
from app.services.render_service import RenderService
from app.services.project_service import ProjectService
from app.services.style_service import StyleService

app = FastAPI(title="CineShorts Studio", version="2.0.0")

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
FILME_DIR = os.path.join(BASE_DIR, "FILME")
EXEMPLO_DIR = os.path.join(FILME_DIR, "exemplo")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FILME_DIR, exist_ok=True)
os.makedirs(EXEMPLO_DIR, exist_ok=True)

# Mount statics
app.mount("/static/output", StaticFiles(directory=OUTPUT_DIR), name="output")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

antigravity_bridge = AntigravityBridge()
media_service = MediaService()
render_service = RenderService()
project_service = ProjectService()
style_service = StyleService()

# --- Modelos Pydantic ---

class ScreenplayRequest(BaseModel):
    movie_title: str
    character: str
    scene_description: str
    aspect_ratio: str = "1:1"
    target_duration: int = 90
    style_id: str = "confronto_vinganca"

class RenderRequest(BaseModel):
    movie_path: str
    movie_title: str
    character: str
    scene_id: Optional[str] = None
    scene_name: str
    style_id: str
    style_name: str
    aspect_ratio: str = "1:1"
    narrator_voice: str = "Eddie Palmer (Clonada)"
    screenplay_text: Optional[str] = None
    project_id: Optional[str] = None
    mode: str = "Diretor Guiado"

class SmartAutoRequest(BaseModel):
    movie_path: str
    movie_title: str
    style_id: str
    aspect_ratio: str = "1:1"
    target_duration: int = 90

class AnalyzeMovieRequest(BaseModel):
    movie_title: str

class ImpactScenesRequest(BaseModel):
    movie_title: str
    character_name: str
    style_id: str = "confronto_vinganca"

class CreateStyleRequest(BaseModel):
    name: str
    category: str
    description: str
    pacing: str = "Dinâmico"
    hook_style: str = "Gancho de impacto"

class SaveKeyRequest(BaseModel):
    openrouter_api_key: str

# --- Rotas da Aplicação ---

@app.get("/")
async def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CineShorts Studio API is running. UI not found."}

@app.get("/api/settings/keys")
async def get_key_settings():
    return render_service.voice_service.get_key_status()

@app.post("/api/settings/keys")
async def save_key_settings(req: SaveKeyRequest):
    render_service.voice_service.save_api_key(req.openrouter_api_key)
    return {"success": True, **render_service.voice_service.get_key_status()}

@app.post("/api/settings/test-key")
async def test_key_settings(req: SaveKeyRequest):
    result = await render_service.voice_service.test_api_key(req.openrouter_api_key)
    return result

@app.get("/api/status")
async def get_system_status():
    ag_info = antigravity_bridge.check_connection()
    projects = project_service.list_projects()
    completed_count = sum(1 for p in projects if p.get("status") == "completed")
    voice_info = render_service.voice_service.get_key_status()
    return {
        "antigravity": ag_info,
        "gpu": {
            "name": "NVIDIA GeForce RTX 4060",
            "vram": "8 GB GDDR6",
            "cuda": "12.x / 13.x",
            "status": "Ativo & Acelerado"
        },
        "voice": voice_info,
        "stats": {
            "total_projects": len(projects),
            "completed_projects": completed_count,
            "total_minutes_generated": round(completed_count * 1.6, 1),
            "preferred_format": "1:1 (Quadrado)"
        },
        "engine_version": "2.0.0"
    }

# --- Filmes & Upload ---

@app.get("/api/movies")
async def list_movies():
    movies = media_service.list_movies()
    return {"movies": movies}

@app.post("/api/upload/movie")
async def upload_movie(file: UploadFile = File(...)):
    """Permite fazer upload de arquivos de filme diretamente pela interface."""
    try:
        clean_filename = os.path.basename(file.filename)
        save_path = os.path.join(FILME_DIR, clean_filename)
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        info = media_service.probe_file(save_path)
        return {
            "success": True,
            "message": f"Filme '{clean_filename}' carregado com sucesso.",
            "path": save_path,
            "filename": clean_filename,
            **info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar filme: {str(e)}")

# --- Modelos de Estilo ---

@app.get("/api/styles")
async def list_styles():
    styles = style_service.list_styles()
    return {"styles": styles}

@app.post("/api/styles")
async def create_style(req: CreateStyleRequest):
    new_style = style_service.create_custom_style(
        name=req.name,
        category=req.category,
        description=req.description,
        pacing=req.pacing,
        hook_style=req.hook_style
    )
    return {"success": True, "style": new_style}

@app.post("/api/upload/reference")
async def upload_reference_video(
    file: UploadFile = File(...),
    style_name: str = Form(...),
    category: str = Form("Personalizado"),
    description: str = Form("Modelo de estilo extraído de vídeo de referência")
):
    """Permite fazer upload de um vídeo de referência para criar um novo modelo de estilo."""
    try:
        clean_name = os.path.basename(file.filename)
        save_path = os.path.join(EXEMPLO_DIR, clean_name)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        new_style = style_service.create_custom_style(
            name=style_name,
            category=category,
            description=description,
            pacing="Ritmo adaptado da referência",
            hook_style="Gancho baseado no vídeo de referência",
            reference_video_path=save_path
        )
        return {"success": True, "style": new_style}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar referência: {str(e)}")

# --- Projetos ---

@app.get("/api/projects")
async def list_projects():
    projects = project_service.list_projects()
    return {"projects": projects}

@app.post("/api/projects")
async def create_project(req: RenderRequest):
    project = project_service.create_project(
        title=f"{req.movie_title.replace('.mp4', '')}: {req.scene_name}",
        movie_title=req.movie_title,
        character=req.character,
        scene_name=req.scene_name,
        style_id=req.style_id,
        style_name=req.style_name,
        aspect_ratio=req.aspect_ratio,
        mode=req.mode
    )
    return {"project": project}

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    deleted = project_service.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    return {"success": True, "message": "Projeto excluído com sucesso."}

# --- Inteligência Antigravity ---

@app.post("/api/antigravity/analyze-movie")
async def analyze_movie(req: AnalyzeMovieRequest):
    """Identifica os personagens centrais para a escolha do ponto de vista."""
    result = antigravity_bridge.analyze_movie(req.movie_title)
    return result

@app.post("/api/antigravity/impact-scenes")
async def get_impact_scenes(req: ImpactScenesRequest):
    """Gera 3 opções de cenas de alto impacto com badges de retenção."""
    scenes = antigravity_bridge.get_impact_scenes(
        movie_title=req.movie_title,
        character_name=req.character_name,
        style_id=req.style_id
    )
    return {"scenes": scenes}

@app.post("/api/antigravity/generate-script")
async def generate_script(req: ScreenplayRequest):
    """Gera o roteiro completo intercalado em 1ª pessoa com diálogos do filme."""
    result = antigravity_bridge.generate_screenplay(
        movie_title=req.movie_title,
        character=req.character,
        scene_description=req.scene_description,
        aspect_ratio=req.aspect_ratio,
        target_duration=req.target_duration,
        style_id=req.style_id
    )
    return result

@app.post("/api/antigravity/smart-auto")
async def smart_auto_generate(req: SmartAutoRequest, bg_tasks: BackgroundTasks):
    """
    Modo Inteligente 100% Automático:
    O Antigravity escolhe a melhor cena de impacto, o personagem ideal,
    gera o roteiro e dispara o motor de renderização automaticamente.
    """
    analysis = antigravity_bridge.analyze_movie(req.movie_title)
    main_char = next((c for c in analysis["characters"] if c.get("recommended")), analysis["characters"][0])
    
    scenes = antigravity_bridge.get_impact_scenes(req.movie_title, main_char["name"], req.style_id)
    top_scene = scenes[0]

    screenplay = antigravity_bridge.generate_screenplay(
        movie_title=req.movie_title,
        character=main_char["name"],
        scene_description=top_scene["summary"],
        aspect_ratio=req.aspect_ratio,
        target_duration=req.target_duration,
        style_id=req.style_id
    )

    job_id = str(uuid.uuid4())[:8]
    output_filename = f"cineshort_auto_{job_id}_{req.aspect_ratio.replace(':', 'x')}.mp4"

    # Salva projeto
    style = style_service.get_style(req.style_id) or {"name": "Confronto & Vingança"}
    clean_title = req.movie_title.replace('.mkv', '').replace('.mp4', '').strip()
    thumb_url = "/static/thumbs/thumb_61769.jpg" if "menu" in req.movie_title.lower() else "/static/thumbs/thumb_24195.jpg"

    project = project_service.create_project(
        title=f"{clean_title}: {top_scene['title']}",
        movie_title=req.movie_title,
        character=main_char["name"],
        scene_name=top_scene["title"],
        style_id=req.style_id,
        style_name=style.get("name", "Estilo Padrão"),
        aspect_ratio=req.aspect_ratio,
        mode="Inteligente (Automático)",
        output_filename=output_filename,
        thumbnail_url=thumb_url
    )

    # Inicia render assíncrono
    bg_tasks.add_task(
        render_service.render_scene_async,
        job_id=job_id,
        movie_path=req.movie_path,
        aspect_ratio=req.aspect_ratio,
        narrator_voice=f"{main_char['name']}",
        scene_id=top_scene.get("id"),
        scene_name=top_scene.get("title"),
        screenplay_text=screenplay.get("screenplay_text"),
        output_filename=output_filename,
        project_id=project["id"]
    )

    return {
        "success": True,
        "job_id": job_id,
        "project": project,
        "character": main_char,
        "scene": top_scene,
        "screenplay": screenplay["screenplay_text"],
        "output_filename": output_filename
    }

# --- Renderização ---

@app.post("/api/render")
async def start_render(req: RenderRequest, bg_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    output_filename = f"cineshort_{job_id}_{req.aspect_ratio.replace(':', 'x')}.mp4"
    clean_title = req.movie_title.replace('.mkv', '').replace('.mp4', '').strip()
    thumb_url = "/static/thumbs/thumb_61769.jpg" if "menu" in req.movie_title.lower() else "/static/thumbs/thumb_24195.jpg"

    # Cria ou vincula projeto
    project = project_service.create_project(
        title=f"{clean_title}: {req.scene_name}",
        movie_title=req.movie_title,
        character=req.character,
        scene_name=req.scene_name,
        style_id=req.style_id,
        style_name=req.style_name,
        aspect_ratio=req.aspect_ratio,
        mode=req.mode,
        output_filename=output_filename,
        thumbnail_url=thumb_url
    )

    bg_tasks.add_task(
        render_service.render_scene_async,
        job_id=job_id,
        movie_path=req.movie_path,
        aspect_ratio=req.aspect_ratio,
        narrator_voice=req.narrator_voice,
        scene_id=req.scene_id,
        scene_name=req.scene_name,
        screenplay_text=req.screenplay_text,
        output_filename=output_filename,
        project_id=project["id"]
    )
    return {"job_id": job_id, "project_id": project["id"], "status": "started", "output_filename": output_filename}

@app.get("/api/render/status/{job_id}")
async def get_render_status(job_id: str):
    return render_service.get_job_status(job_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
