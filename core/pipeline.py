"""
Módulo Orquestrador do Pipeline de Resumo de Filmes.
"""

import os
import json
from typing import Dict, Any, List, Optional
from core.config import PipelineConfig
from core.screenplay import ScreenplayManager
from core.tts_engine import TTSEngine
from core.subtitle_sync import SubtitleSync
from core.focal_tracker import FocalTracker
from core.video_renderer import VideoRenderer

class MovieSummaryPipeline:
    """
    Controlador mestre que coordena todas as etapas do resumo de filme:
    1. Roteirização em 1ª pessoa (~3min)
    2. Síntese de voz com cadência cinematográfica (Edge-TTS)
    3. Sincronização de legendas (Whisper)
    4. Cálculo de enquadramento 9:16 (Focal Tracker)
    5. Renderização e mixagem de áudio com FFmpeg
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.tts = TTSEngine(
            voice=self.config.tts.voice,
            rate=self.config.tts.rate,
            pitch=self.config.tts.pitch
        )
        self.renderer = VideoRenderer(self.config)

    def run_voiceover(self, script_text: str, output_dir: str) -> Dict[str, str]:
        """Gera os arquivos de narração em MP3 e WAV."""
        os.makedirs(output_dir, exist_ok=True)
        mp3_path = os.path.join(output_dir, "narracao.mp3")
        wav_path = os.path.join(output_dir, "narracao.wav")

        self.tts.generate_speech(script_text, output_mp3=mp3_path, output_wav=wav_path)
        duration = self.tts.get_audio_duration(wav_path)

        return {
            "mp3": mp3_path,
            "wav": wav_path,
            "duration": str(round(duration, 2))
        }

    def run_subtitles(self, audio_path: str, output_srt: str) -> str:
        """Gera legendas sincronizadas utilizando Whisper."""
        return SubtitleSync.generate_srt_with_whisper(audio_path, output_srt)

    def run_render(self, movie_path: str, shots_json: str, voice_audio: str, output_video: str, temp_dir: str) -> str:
        """Renderiza o vídeo vertical com todos os cortes centralizados."""
        with open(shots_json, 'r', encoding='utf-8') as f:
            shots = json.load(f)

        clip_paths = self.renderer.render_all_shots(movie_path, shots, temp_dir)
        final_video = self.renderer.assemble_final_video(clip_paths, voice_audio, output_video, temp_dir)
        return final_video
