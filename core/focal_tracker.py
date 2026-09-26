"""
Módulo de Rastreamento de Foco e Cálculo Matemático de Enquadramento (9:16 e 1:1).
Garante que qualquer vídeo (1920x800, 1920x816, 1920x1080, 1280x530, etc.) seja
recortado perfeitamente centralizado no elemento de interesse sem distorção e sem exceder limites.
"""

from typing import Literal

class FocalTracker:
    """
    Calcula a janela de recorte vertical (1080x1920) ou quadrada (1080x1080)
    centralizando rigorosamente o ponto target_x no espaço real do vídeo.
    """

    @staticmethod
    def get_crop_params(orig_w: int, orig_h: int, target_x: float, aspect_ratio: str = "1:1"):
        """
        Calcula largura, altura e deslocamento X do recorte no espaço original de pixels.
        """
        if aspect_ratio == "1:1":
            crop_h = orig_h
            crop_w = min(orig_w, orig_h)
        else:  # 9:16
            crop_h = orig_h
            crop_w = int(round(orig_h * 9.0 / 16.0))
            if crop_w > orig_w:
                crop_w = orig_w

        # Centraliza target_x dentro da janela crop_w
        window_x = int(round(target_x - (crop_w / 2.0)))
        # Garante limites estritos [0, orig_w - crop_w]
        window_x = max(0, min(window_x, orig_w - crop_w))

        return crop_w, crop_h, window_x

    @staticmethod
    def get_ffmpeg_crop_filter(
        orig_w: int, 
        orig_h: int, 
        target_x: float, 
        aspect_ratio: Literal["1:1", "9:16"] = "1:1"
    ) -> str:
        """
        Retorna a string do filtro FFmpeg (-vf):
        1. Recorta no espaço original de pixels usando os limites reais do vídeo.
        2. Escala com Lanczos para a resolução de saída (1080x1080 para 1:1 ou 1080x1920 para 9:16).
        """
        crop_w, crop_h, window_x = FocalTracker.get_crop_params(orig_w, orig_h, target_x, aspect_ratio)

        if aspect_ratio == "1:1":
            return f"crop={crop_w}:{crop_h}:{window_x}:0,scale=1080:1080:flags=lanczos,setsar=1"
        else:
            return f"crop={crop_w}:{crop_h}:{window_x}:0,scale=1080:1920:flags=lanczos,setsar=1"
