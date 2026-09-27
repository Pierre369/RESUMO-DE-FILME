"""
Módulo de Geração e Renderização de Legendas Estilo TikTok / Reels Neon.
Produz legendas dinâmicas em caixa alta (UPPERCASE) com corte palavra por palavra
ou frases curtas (3-5 palavras), borda neon vermelha/branca e contraste absoluto,
idêntico aos vídeos de referência em FILME/exemplo.
"""

import os
import re
import math
from typing import List, Tuple

class SubtitleService:
    @staticmethod
    def chunk_text(text: str, max_words_per_chunk: int = 4) -> List[str]:
        """Divide o texto em blocos de 3 a 5 palavras para efeito dinâmico."""
        words = text.strip().split()
        if not words:
            return []
        chunks = []
        cur = []
        for w in words:
            cur.append(w)
            if len(cur) >= max_words_per_chunk or w.endswith((".", "!", "?", ",", ":")):
                chunks.append(" ".join(cur))
                cur = []
        if cur:
            chunks.append(" ".join(cur))
        return chunks

    @staticmethod
    def format_ass_time(seconds: float) -> str:
        """Formata segundos para H:MM:SS.cs (centésimos de segundo)."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        cs = int((s - int(s)) * 100)
        return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"

    @classmethod
    def generate_ass_file(
        cls,
        text: str,
        duration: float,
        output_ass_path: str,
        aspect_ratio: str = "1:1"
    ) -> str:
        """
        Cria arquivo .ass com estilo idêntico aos vídeos de referência:
        - Letras maiúsculas
        - Cor branca pura (&H00FFFFFF&)
        - Contorno vermelho neon marcante (&H001010E0&)
        - Posição centralizada no terço inferior (MarginV=280)
        """
        chunks = cls.chunk_text(text, max_words_per_chunk=4)
        if not chunks:
            chunks = [text.strip()]

        total_chunks = len(chunks)
        chunk_dur = duration / max(1, total_chunks)

        res_x = 1080
        res_y = 1080 if aspect_ratio == "1:1" else 1920
        font_size = 54 if aspect_ratio == "1:1" else 62
        margin_v = 300 if aspect_ratio == "1:1" else 550

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res_x}
PlayResY: {res_y}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTokNeon,Arial,{font_size},&H00FFFFFF,&H000000FF,&H001010E0,&H80000000,-1,0,0,0,100,100,1.5,0,1,5.5,2.0,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for i, chunk in enumerate(chunks):
            start_s = i * chunk_dur
            end_s = min(duration, (i + 1) * chunk_dur)
            # ligeiro ajuste de respiro
            if i == total_chunks - 1:
                end_s = duration
            
            clean_chunk = chunk.strip().upper()
            start_fmt = cls.format_ass_time(start_s)
            end_fmt = cls.format_ass_time(end_s)
            line = f"Dialogue: 0,{start_fmt},{end_fmt},TikTokNeon,,0,0,0,,{{\\c&H00FFFFFF&\\3c&H001010E0&}}{clean_chunk}"
            events.append(line)

        full_content = header + "\n".join(events) + "\n"
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        return output_ass_path
