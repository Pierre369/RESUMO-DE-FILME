"""
Módulo de Rastreamento de Foco e Cálculo Matemático de Enquadramento 9:16.
"""

from typing import Tuple

class FocalTracker:
    """
    Calcula a janela de recorte vertical (1080x1920) para manter o elemento focal
    (rosto, personagem ou objeto de ação) rigorosamente centralizado sem barras pretas.
    """

    @staticmethod
    def compute_crop_x(orig_w: int, orig_h: int, target_x: float, target_w: int = 1080, target_h: int = 1920) -> int:
        """
        Calcula o deslocamento X (crop_x) para um vídeo anamórfico/widescreen
        escalado para altura target_h (1920px), centralizando o ponto target_x.

        Fórmula:
            scale_factor = target_h / orig_h
            scaled_w = orig_w * scale_factor
            scaled_target_x = target_x * scale_factor
            crop_x = round(scaled_target_x - (target_w / 2))
            clamp(crop_x, 0, scaled_w - target_w)
        """
        scale_factor = target_h / float(orig_h)
        scaled_w = orig_w * scale_factor
        scaled_target_x = target_x * scale_factor
        
        ideal_crop_x = int(round(scaled_target_x - (target_w / 2.0)))
        max_crop_x = max(0, int(round(scaled_w - target_w)))

        # Garante que a janela de 1080px fique 100% dentro dos limites do vídeo escalado
        return max(0, min(ideal_crop_x, max_crop_x))

    @staticmethod
    def get_ffmpeg_crop_filter(orig_w: int, orig_h: int, target_x: float, target_w: int = 1080, target_h: int = 1920) -> str:
        """
        Retorna a string completa do filtro de vídeo FFmpeg (-vf)
        com escala Lanczos de alta nitidez e recorte centralizado.
        """
        crop_x = FocalTracker.compute_crop_x(orig_w, orig_h, target_x, target_w, target_h)
        return f"scale=-1:{target_h}:flags=lanczos,crop={target_w}:{target_h}:{crop_x}:0,setsar=1"
