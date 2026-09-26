"""
Serviço de gerenciamento de Modelos de Estilo Narrativo.
Permite listar presets pré-definidos (com nomes conceituais, sem nome de filmes)
e cadastrar novos modelos com ou sem upload de vídeos de referência.
"""

import os
import json
import uuid
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "app", "data")
STYLES_FILE = os.path.join(DATA_DIR, "styles.json")

DEFAULT_STYLES = [
    {
        "id": "confronto_vinganca",
        "name": "Confronto & Vingança",
        "category": "Ação Dinâmica & Alta Tensão",
        "badge": "Mais Usado",
        "description": "Ritmo acelerado focado em injustiça, gancho imediato nos primeiros 3 segundos, intercalação com os socos e falas mais marcantes do filme dublado e acerto de contas.",
        "pacing": "Rápido (cortes a cada 2.5s a 4s)",
        "hook_style": "Choque visual e moral imediato",
        "retention_score": "98%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    },
    {
        "id": "micro_historia_suspense",
        "name": "Micro-História Tensa (Suspense)",
        "category": "Mistério & Urgência",
        "badge": "Retenção Máxima",
        "description": "Foco em uma única micro-cena de alta pressão psicológica. O narrador em 1ª pessoa expõe a armadilha ou o perigo iminente enquanto o filme desenrola a tensão.",
        "pacing": "Cadenciado e tenso (cortes a cada 3s a 5s)",
        "hook_style": "Perigo silencioso ou contagem regressiva",
        "retention_score": "95%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    },
    {
        "id": "revelacao_virada",
        "name": "Revelação & Virada Inesperada",
        "category": "Quebra de Expectativa & Plot Twist",
        "badge": "Viral",
        "description": "História que parece seguir para um lado e tem uma quebra de expectativa total no meio. O narrador revela um segredo que muda o sentido da cena.",
        "pacing": "Crescente com aceleração no clímax",
        "hook_style": "Premissa enganosa e gancho surpresa",
        "retention_score": "96%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    },
    {
        "id": "drama_superacao",
        "name": "Drama & Conexão Emocional",
        "category": "Conexão Humana & Redenção",
        "badge": "Comovente",
        "description": "Foco na dor, proteção de vulneráveis e redenção moral do protagonista. Diálogos emotivos em 100% de volume com narração íntima e sincera.",
        "pacing": "Emotivo, valorizando close-ups e olhares",
        "hook_style": "Dilema moral comovente",
        "retention_score": "94%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    }
]

class StyleService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(STYLES_FILE):
            self._save_styles(DEFAULT_STYLES)

    def _load_styles(self) -> List[Dict[str, Any]]:
        try:
            with open(STYLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_STYLES

    def _save_styles(self, styles: List[Dict[str, Any]]):
        with open(STYLES_FILE, "w", encoding="utf-8") as f:
            json.dump(styles, f, indent=2, ensure_ascii=False)

    def list_styles(self) -> List[Dict[str, Any]]:
        return self._load_styles()

    def get_style(self, style_id: str) -> Optional[Dict[str, Any]]:
        styles = self._load_styles()
        for s in styles:
            if s["id"] == style_id:
                return s
        return None

    def create_custom_style(
        self,
        name: str,
        category: str,
        description: str,
        pacing: str = "Dinâmico",
        hook_style: str = "Gancho de impacto",
        reference_video_path: Optional[str] = None
    ) -> Dict[str, Any]:
        styles = self._load_styles()
        new_style = {
            "id": f"custom_{str(uuid.uuid4())[:8]}",
            "name": name,
            "category": category,
            "badge": "Personalizado",
            "description": description,
            "pacing": pacing,
            "hook_style": hook_style,
            "retention_score": "90%+",
            "recommended_aspect": "1:1 ou 9:16",
            "is_default": False,
            "reference_video_path": reference_video_path
        }
        styles.append(new_style)
        self._save_styles(styles)
        return new_style
