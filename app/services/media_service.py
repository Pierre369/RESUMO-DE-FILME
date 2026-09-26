"""
Serviço de gerenciamento de mídias: filmes, vídeos de referência e extração de metadados.
"""

import os
import subprocess
import json
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILME_DIR = os.path.join(BASE_DIR, "FILME")
EXEMPLO_DIR = os.path.join(FILME_DIR, "exemplo")
THUMBNAIL_DIR = os.path.join(BASE_DIR, "app", "static", "thumbs")
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

class MediaService:
    @staticmethod
    def probe_file(file_path: str) -> Dict[str, Any]:
        """Extrai resolução, duração, codec e aspect ratio de qualquer arquivo de vídeo via ffprobe."""
        if not os.path.exists(file_path):
            return {}

        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=width,height,r_frame_rate,duration,codec_name:format=duration,size",
            "-of", "json", file_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            video_stream = next((s for s in data.get("streams", []) if "width" in s), {})
            fmt = data.get("format", {})
            
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            dur = float(fmt.get("duration", video_stream.get("duration", 0.0)))
            size_mb = round(float(fmt.get("size", 0)) / (1024 * 1024), 1)

            aspect = "16:9"
            if width > 0 and height > 0:
                ratio = width / height
                if 0.95 <= ratio <= 1.05:
                    aspect = "1:1"
                elif ratio < 0.6:
                    aspect = "9:16"
                elif ratio > 2.2:
                    aspect = "2.39:1"

            return {
                "width": width,
                "height": height,
                "duration": dur,
                "duration_formatted": f"{int(dur // 60):02d}:{int(dur % 60):02d}",
                "size_mb": size_mb,
                "aspect_ratio": aspect,
                "codec": video_stream.get("codec_name", "h264")
            }
        except Exception as e:
            print(f"Erro ao extrair metadados de {file_path}: {e}")
            return {}

    @staticmethod
    def list_movies() -> List[Dict[str, Any]]:
        """Lista todos os filmes disponíveis na pasta FILME/."""
        movies = []
        if not os.path.exists(FILME_DIR):
            return movies

        for f in os.listdir(FILME_DIR):
            if f.lower().endswith((".mp4", ".mkv", ".mov", ".avi")):
                full_path = os.path.join(FILME_DIR, f)
                info = MediaService.probe_file(full_path)
                thumb_name = f"thumb_{abs(hash(f)) % 100000}.jpg"
                thumb_path = os.path.join(THUMBNAIL_DIR, thumb_name)
                
                # Gera miniatura se não existir
                if not os.path.exists(thumb_path) and info.get("duration", 0) > 10:
                    capture_sec = min(60, int(info["duration"] / 4))
                    subprocess.run([
                        "ffmpeg", "-y", "-ss", str(capture_sec), "-i", full_path,
                        "-vframes", "1", "-vf", "scale=320:-1", "-q:v", "3", thumb_path
                    ], capture_output=True)

                movies.append({
                    "filename": f,
                    "path": full_path,
                    "thumbnail_url": f"/static/thumbs/{thumb_name}" if os.path.exists(thumb_path) else "",
                    **info
                })
        return movies

    @staticmethod
    def list_references() -> List[Dict[str, Any]]:
        """Lista os vídeos de referência de exemplo."""
        refs = []
        if not os.path.exists(EXEMPLO_DIR):
            return refs

        for f in os.listdir(EXEMPLO_DIR):
            if f.lower().endswith((".mp4", ".mov", ".mkv")):
                full_path = os.path.join(EXEMPLO_DIR, f)
                info = MediaService.probe_file(full_path)
                refs.append({
                    "filename": f,
                    "path": full_path,
                    **info
                })
        return refs
