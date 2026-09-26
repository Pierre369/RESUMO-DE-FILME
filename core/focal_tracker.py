"""
Módulo de Rastreamento de Foco e Cálculo Matemático de Enquadramento (9:16 e 1:1).
Combina Visão Computacional (Detecção Facial com OpenCV) e cálculo geométrico estrito
para garantir que o rosto e a ação do personagem estejam SEMPRE perfeitamente centralizados,
sem cortar queixos, olhos ou laterais, e sem distorção anamórfica.
"""

import subprocess
from typing import Literal, Optional
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class FocalTracker:
    """
    Rastreia o ponto de atenção do vídeo e calcula a janela de recorte vertical (1080x1920) 
    ou quadrada (1080x1080) centralizando rigorosamente o personagem no espaço real do vídeo.
    """

    @staticmethod
    def detect_optimal_target_x(
        movie_path: str,
        start_ts: str,
        orig_w: int = 1920,
        orig_h: int = 1080,
        fallback_x: Optional[float] = None
    ) -> float:
        """
        Analisa o frame do vídeo na posição do take usando Visão Computacional (OpenCV).
        Testa múltiplos offsets temporais (0.0s, 0.5s, 1.0s) para garantir detecção facial precisa
        mesmo em cenas em movimento ou cortes de câmera.
        Se encontrar o rosto do personagem, retorna o centro X exato do rosto.
        Se for plano geral de objeto ou paisagem, usa o fallback_x calibrado ou o centro do filme.
        """
        default_x = fallback_x if fallback_x is not None else (orig_w / 2.0)

        if not HAS_CV2:
            return default_x

        try:
            cascade_front = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            cascade_prof = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

            # Varre 3 micro-pontos no início da cena (0.0s, 0.5s, 1.0s) para capturar o rosto
            for offset in [0.0, 0.5, 1.0]:
                cmd = [
                    "ffmpeg", "-ss", str(start_ts), "-i", movie_path,
                    "-ss", str(offset), "-vframes", "1",
                    "-f", "image2pipe", "-vcodec", "png", "-"
                ]
                p = subprocess.run(cmd, capture_output=True, timeout=5)
                if not p.stdout:
                    continue

                arr = np.frombuffer(p.stdout, np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if img is None:
                    continue

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # 1. Detector Frontal
                faces = cascade_front.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 50))

                # 2. Detector de Perfil (se frontal não achar)
                if len(faces) == 0:
                    faces = cascade_prof.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 50))

                if len(faces) > 0:
                    if fallback_x is not None:
                        # Filtra apenas faces próximas do personagem de interesse (<= 250px do fallback)
                        # e com dimensões de primeiro plano (evita ruídos no fundo do cenário)
                        valid_faces = [
                            f for f in faces
                            if abs((f[0] + (f[2] / 2.0)) - fallback_x) <= 250 and f[2] >= 60 and f[3] >= 60
                        ]
                        if valid_faces:
                            best_face = min(valid_faces, key=lambda f: abs((f[0] + (f[2] / 2.0)) - fallback_x))
                            fx, fy, fw, fh = best_face
                            return fx + (fw / 2.0)
                    else:
                        best_face = max(faces, key=lambda f: f[2] * f[3])
                        fx, fy, fw, fh = best_face
                        return fx + (fw / 2.0)

        except Exception as e:
            # Em caso de qualquer falha rápida, preserva o fallback
            pass

        return default_x

    @staticmethod
    def get_crop_params(orig_w: int, orig_h: int, target_x: float, aspect_ratio: str = "1:1"):
        """
        Calcula largura, altura e deslocamento X do recorte no espaço original de pixels.
        Garante que a janela nunca saia dos limites do filme.
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
        1. Recorta no espaço original de pixels usando os limites reais do vídeo e o foco ótimo.
        2. Escala com Lanczos para a resolução de saída (1080x1080 para 1:1 ou 1080x1920 para 9:16).
        """
        crop_w, crop_h, window_x = FocalTracker.get_crop_params(orig_w, orig_h, target_x, aspect_ratio)

        if aspect_ratio == "1:1":
            return f"crop={crop_w}:{crop_h}:{window_x}:0,scale=1080:1080:flags=lanczos,setsar=1"
        else:
            return f"crop={crop_w}:{crop_h}:{window_x}:0,scale=1080:1920:flags=lanczos,setsar=1"
