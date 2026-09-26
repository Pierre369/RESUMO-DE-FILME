"""
Módulo de Detecção de Cortes de Câmera e Transições de Cena.
"""

import cv2
from typing import List, Dict, Any

class SceneDetector:
    """
    Analisa variações bruscas de histograma/pixels entre quadros consecutivos
    para detectar cortes de câmera internos e permitir divisão inteligente de takes.
    """

    def __init__(self, threshold: float = 40.0):
        self.threshold = threshold

    def detect_cuts_in_range(self, movie_path: str, start_sec: float, duration_sec: float) -> List[float]:
        """
        Retorna a lista de timestamps absolutos (em segundos) onde ocorreram
        cortes de câmera dentro do intervalo especificado.
        """
        cap = cv2.VideoCapture(movie_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        start_frame = int(start_sec * fps)
        total_frames = int(duration_sec * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        prev_gray = None
        cuts = []

        for f in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_gray is not None and f > 2:  # Ignora primeiros 2 frames para estabilizar
                diff = cv2.absdiff(gray, prev_gray).mean()
                if diff > self.threshold:
                    cut_time = start_sec + (f / fps)
                    cuts.append(round(cut_time, 3))
            prev_gray = gray

        cap.release()
        return cuts
