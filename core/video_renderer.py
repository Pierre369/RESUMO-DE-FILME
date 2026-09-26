"""
Módulo de Renderização e Montagem Final com FFmpeg.
"""

import os
import sys
import json
import csv
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional
from core.config import PipelineConfig

class VideoRenderer:
    """
    Renderiza sub-cortes em paralelo, concatena a sequência e faz o mix do áudio
    (voz principal + ambiência do filme atenuada/ducked).
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()

    def render_subclip(self, movie_file: str, shot: Dict[str, Any], output_path: str, orig_w: int, orig_h: int) -> bool:
        """Renderiza um único corte recortado para 9:16."""
        m_start = shot['m_start']
        dur = shot['dur']
        crop_x = shot['crop_x']
        
        vf = f"scale=-1:{self.config.video.target_height}:flags={self.config.video.scale_flags}," \
             f"crop={self.config.video.target_width}:{self.config.video.target_height}:{crop_x}:0,setsar=1"
        
        cmd = [
            'ffmpeg', '-y',
            '-ss', f"{m_start:.3f}",
            '-i', movie_file,
            '-t', f"{dur:.3f}",
            '-vf', vf,
            '-r', str(self.config.video.fps),
            '-c:v', 'libx264', '-preset', self.config.video.preset, '-crf', str(self.config.video.crf),
            '-pix_fmt', self.config.video.pix_fmt,
            '-af', f"volume={self.config.audio.ambient_duck_volume}",
            '-c:a', 'aac', '-b:a', '128k', '-ar', str(self.config.audio.sample_rate), '-ac', str(self.config.audio.channels),
            output_path
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0

    def render_all_shots(self, movie_file: str, shots: List[Dict[str, Any]], temp_dir: str, orig_w: int = 1280, orig_h: int = 530) -> List[str]:
        """Renderiza todos os cortes em paralelo utilizando ThreadPoolExecutor."""
        os.makedirs(temp_dir, exist_ok=True)
        clip_paths = []

        def worker(item):
            s_idx, s = item
            out_p = os.path.join(temp_dir, f"sub_{s_idx:03d}.mp4")
            ok = self.render_subclip(movie_file, s, out_p, orig_w, orig_h)
            if not ok:
                raise RuntimeError(f"Falha ao renderizar corte #{s_idx}")
            return out_p

        items = list(enumerate(shots, start=1))
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            clip_paths = list(executor.map(worker, items))

        return clip_paths

    def assemble_final_video(self, clip_paths: List[str], voice_audio: str, output_final: str, temp_dir: str) -> str:
        """
        Concatena os cortes e combina a narração com o áudio ambiente do filme.
        """
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, 'w', encoding='utf-8') as f:
            for p in clip_paths:
                f.write(f"file '{p.replace('\\', '/')}'\n")

        raw_video = os.path.join(temp_dir, "raw_assembled.mp4")
        cmd_concat = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', raw_video]
        subprocess.run(cmd_concat, check=True, capture_output=True)

        filter_complex = f"[0:a]volume={self.config.audio.ambient_mix_volume}[bg];" \
                         f"[1:a]volume={self.config.audio.voice_volume}[voice];" \
                         f"[bg][voice]amix=inputs=2:duration=first:dropout_transition=2[a_out]"

        cmd_final = [
            'ffmpeg', '-y',
            '-i', raw_video,
            '-i', voice_audio,
            '-filter_complex', filter_complex,
            '-map', '0:v',
            '-map', '[a_out]',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', self.config.audio.bitrate, '-ar', str(self.config.audio.sample_rate),
            '-shortest',
            output_final
        ]

        subprocess.run(cmd_final, check=True, capture_output=True)
        return output_final
