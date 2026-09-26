"""
Serviço de gerenciamento de Projetos do CineShorts Studio.
Permite salvar histórico, listar projetos no Dashboard/Aba Projetos,
atualizar status e armazenar metadados dos vídeos gerados.
"""

import os
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "app", "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")

INITIAL_PROJECTS = [
    {
        "id": "proj_palmer_master",
        "title": "Palmer: O Acerto de Contas no Bar",
        "movie_title": "Palmer (2021) Dublado.mp4",
        "character": "Eddie Palmer (Protagonista)",
        "scene_name": "Confronto no Bar em Defesa de Sam",
        "style_id": "confronto_vinganca",
        "style_name": "Confronto & Vingança",
        "aspect_ratio": "1:1",
        "duration_sec": 98.2,
        "cuts_count": 19,
        "status": "completed",
        "output_filename": "palmer_1x1_resumo.mp4",
        "output_url": "/static/output/palmer_1x1_resumo.mp4",
        "thumbnail_url": "/static/thumbs/thumb_24195.jpg",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "mode": "Diretor Guiado"
    }
]

class ProjectService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(PROJECTS_FILE):
            self._save_projects(INITIAL_PROJECTS)

    def _load_projects(self) -> List[Dict[str, Any]]:
        try:
            with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return INITIAL_PROJECTS

    def _save_projects(self, projects: List[Dict[str, Any]]):
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)

    def list_projects(self) -> List[Dict[str, Any]]:
        projects = self._load_projects()
        # Sort by creation / update descending
        return list(reversed(projects))

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        projects = self._load_projects()
        for p in projects:
            if p["id"] == project_id:
                return p
        return None

    def create_project(
        self,
        title: str,
        movie_title: str,
        character: str,
        scene_name: str,
        style_id: str,
        style_name: str,
        aspect_ratio: str = "1:1",
        mode: str = "Automático",
        output_filename: Optional[str] = None,
        thumbnail_url: Optional[str] = None
    ) -> Dict[str, Any]:
        projects = self._load_projects()
        proj_id = f"proj_{str(uuid.uuid4())[:8]}"
        new_project = {
            "id": proj_id,
            "title": title or f"Resumo: {movie_title}",
            "movie_title": movie_title,
            "character": character,
            "scene_name": scene_name,
            "style_id": style_id,
            "style_name": style_name,
            "aspect_ratio": aspect_ratio,
            "duration_sec": 90.0,
            "cuts_count": 18,
            "status": "processing",
            "output_filename": output_filename or f"{proj_id}.mp4",
            "output_url": f"/static/output/{output_filename or f'{proj_id}.mp4'}",
            "thumbnail_url": thumbnail_url or "/static/thumbs/thumb_24195.jpg",
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "mode": mode
        }
        projects.append(new_project)
        self._save_projects(projects)
        return new_project

    def update_project_status(self, project_id: str, status: str, output_url: Optional[str] = None):
        projects = self._load_projects()
        for p in projects:
            if p["id"] == project_id:
                p["status"] = status
                if output_url:
                    p["output_url"] = output_url
                break
        self._save_projects(projects)

    def delete_project(self, project_id: str) -> bool:
        projects = self._load_projects()
        initial_len = len(projects)
        projects = [p for p in projects if p["id"] != project_id]
        if len(projects) < initial_len:
            self._save_projects(projects)
            return True
        return False
