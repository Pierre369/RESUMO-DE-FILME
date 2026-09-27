"""
Módulo de Rastreamento de Foco e Cálculo Matemático de Enquadramento (1:1 e 9:16).
Utiliza Rede Neural Profunda (OpenCV YuNet ONNX) e Visão Computacional de ponta
para garantir que o rosto dos atores e o centro dramático da cena estejam SEMPRE
perfeitamente enquadrados, sem cortar queixos, olhos ou ações, reproduzindo
o corte milimétrico dos vídeos de referência do TikTok.
"""

import os
import subprocess
from typing import Literal, Optional, List, Tuple
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
YUNET_MODEL_PATH = os.path.join(CURRENT_DIR, "face_detection_yunet_2023mar.onnx")

class FocalTracker:
    """
    Rastreia o ponto de atenção do vídeo e calcula a janela de recorte quadrada (1080x1080)
    ou vertical (1080x1920) centralizando os atores no espaço real do vídeo.
    """

    _yunet_detector = None

    @classmethod
    def get_yunet_detector(cls):
        if not HAS_CV2 or not os.path.exists(YUNET_MODEL_PATH):
            return None
        if cls._yunet_detector is None:
            try:
                cls._yunet_detector = cv2.FaceDetectorYN.create(
                    model=YUNET_MODEL_PATH,
                    config="",
                    input_size=(640, 360),
                    score_threshold=0.3,
                    nms_threshold=0.3,
                    top_k=5000
                )
            except Exception:
                cls._yunet_detector = None
        return cls._yunet_detector

    @staticmethod
    def detect_optimal_target_x(
        movie_path: str,
        start_ts: str,
        orig_w: int = 1920,
        orig_h: int = 1080,
        fallback_x: Optional[float] = None
    ) -> float:
        """
        Analisa o frame do vídeo na posição do take usando Visão Computacional Neural (YuNet).
        Varre múltiplos offsets temporais (0.0s, 0.5s, 1.0s, 1.5s) para capturar o enquadramento
        dos personagens mesmo em cenas de corte rápido ou iluminação desafiadora.
        """
        default_x = fallback_x if fallback_x is not None else (orig_w / 2.0)

        if not HAS_CV2:
            return default_x

        detector = FocalTracker.get_yunet_detector()
        cascade_front = None
        cascade_prof = None

        for offset in [0.0, 0.5, 1.0, 1.5]:
            try:
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

                ih, iw = img.shape[:2]

                # 1. Tentativa com Rede Neural YuNet (Extremamente Precisa)
                if detector is not None:
                    detector.setInputSize((iw, ih))
                    _, faces = detector.detect(img)
                    if faces is not None and len(faces) > 0:
                        detected_centers = []
                        for f in faces:
                            fx, fy, fw, fh = f[:4]
                            conf = f[-1]
                            if fw >= 30 and fh >= 30:  # Ignora ruídos minúsculos
                                detected_centers.append((fx + (fw / 2.0), fw * fh, conf))

                        if detected_centers:
                            # Se há múltiplos atores em cena (ex: diálogo/embate),
                            # enquadra de forma a englobar os dois principais
                            if len(detected_centers) >= 2:
                                # Ordena pelos maiores rostos (primeiro plano)
                                detected_centers.sort(key=lambda item: item[1], reverse=True)
                                c1 = detected_centers[0][0]
                                c2 = detected_centers[1][0]
                                # Se a distância entre eles couber no crop
                                crop_limit = min(orig_w, orig_h) * 0.85
                                if abs(c1 - c2) <= crop_limit:
                                    return (c1 + c2) / 2.0

                            if fallback_x is not None:
                                best = min(detected_centers, key=lambda item: abs(item[0] - fallback_x))
                                return best[0]
                            else:
                                best = max(detected_centers, key=lambda item: item[1])
                                return best[0]

                # 2. Fallback Haar Cascades (se YuNet não detectar)
                if cascade_front is None:
                    cascade_front = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    cascade_prof = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                haar_faces = cascade_front.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(40, 40))
                if len(haar_faces) == 0:
                    haar_faces = cascade_prof.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(40, 40))

                if len(haar_faces) > 0:
                    centers = [f[0] + (f[2] / 2.0) for f in haar_faces if f[2] >= 40]
                    if centers:
                        if fallback_x is not None:
                            best = min(centers, key=lambda c: abs(c - fallback_x))
                            return best
                        else:
                            return centers[0]

            except Exception:
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
