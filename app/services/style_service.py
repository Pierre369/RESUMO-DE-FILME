"""
Serviço de gerenciamento de Modelos de Estilo Narrativo.
Define com clareza a mecânica exata (1ª pessoa intercalada, 3ª pessoa, duelo de diálogos)
e especifica para que cada modelo serve.
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
        "id": "narracao_hibrida_1p",
        "name": "Narração Híbrida em 1ª Pessoa (O Modelo Viral TikTok)",
        "category": "1ª Pessoa Intercalada com Filme Dublado",
        "badge": "Mais Usado • 99% Retenção",
        "description": "O protagonista narra em 1ª pessoa ('Eu tava lá, fiz isso...') com ritmo frenético (+16%), alternando sem pausas mortas com os diálogos originais dublados do filme a 100% de volume sob ducking inteligente (-22dB).",
        "use_case": "Micro-cenas de alto impacto, vingança, quebra de expectativas, confrontos diretos e clímax onde o espectador vive a cena na pele do personagem.",
        "pacing": "Frenético e contínuo (corte seco imediato quando a fala termina)",
        "hook_style": "Choque imediato nos primeiros 3s em 1ª pessoa",
        "retention_score": "99%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    },
    {
        "id": "duelo_dialogos_filme",
        "name": "Duelo de Diálogos & Embate (80% Foco no Filme Dublado)",
        "category": "Foco nos Diálogos Originais",
        "badge": "Ação & Discussão",
        "description": "Narração ultracurta de gancho inicial (4s) e transições pontuais, dando protagonismo quase total para os atores do filme dublado brigarem, discutirem ou negociarem a 100% de volume.",
        "use_case": "Cenas icônicas de tribunal, discussões tensas, interrogatórios, ameaças cara a cara e embates verbais dramáticos.",
        "pacing": "Tenso e dramático, guiado pelas pausas e reações dos atores",
        "hook_style": "Apresentação rápida da ameaça antes do embate",
        "retention_score": "96%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    },
    {
        "id": "narrador_onisciente_3p",
        "name": "Narrador Onisciente & Reações (3ª Pessoa Dinâmica)",
        "category": "3ª Pessoa Externa com Cortes de Reação",
        "badge": "Mistério & Conspiração",
        "description": "Voz externa enérgica contando os fatos em 3ª pessoa ('Esse homem achou que ia enganar todo mundo...'), com perguntas instigantes que cortam imediatamente para a reação dublada do filme.",
        "use_case": "Histórias de crimes, golpes, filmes com múltiplos personagens, mistérios não resolvidos e conspirações.",
        "pacing": "Investigativo e ágil",
        "hook_style": "Pergunta retórica intrigante ou segredo exposto",
        "retention_score": "95%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    },
    {
        "id": "storytelling_emocional_1p",
        "name": "Storytelling Íntimo & Redenção (1ª Pessoa Emocional)",
        "category": "1ª Pessoa Profunda",
        "badge": "Drama & Conexão",
        "description": "O personagem desabafa em 1ª pessoa de forma sincera e vulnerável, intercalando com os diálogos mais comoventes e close-ups expressivos do filme dublado.",
        "use_case": "Filmes de drama, histórias de pais e filhos, superação de traumas, amizades improváveis e despedidas.",
        "pacing": "Emotivo e contínuo, valorizando expressões e redenção",
        "hook_style": "Confissão sincera de um erro ou sacrifício",
        "retention_score": "94%",
        "recommended_aspect": "1:1 ou 9:16",
        "is_default": True
    }
]

class StyleService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        # Sempre salva a versão mais recente e clara
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
        use_case: str = "Resumos personalizados",
        reference_video_path: Optional[str] = None
    ) -> Dict[str, Any]:
        styles = self._load_styles()
        new_style = {
            "id": f"custom_{str(uuid.uuid4())[:8]}",
            "name": name,
            "category": category,
            "badge": "Personalizado",
            "description": description,
            "use_case": use_case,
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
