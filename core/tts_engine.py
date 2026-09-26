"""
Módulo de Síntese de Voz (TTS) com Edge-TTS e Normalização de Áudio.
"""

import os
import subprocess
import asyncio
import edge_tts
from typing import Optional

class TTSEngine:
    """
    Gera narração vocalizada usando vozes neurais da Microsoft (Edge-TTS)
    com controle fino de cadência dramática e conversão para WAV 48kHz.
    """

    def __init__(self, voice: str = "pt-BR-AntonioNeural", rate: str = "-9%", pitch: str = "+0Hz"):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch

    async def generate_speech_async(self, text: str, output_mp3: str) -> str:
        """Gera áudio MP3 de forma assíncrona usando Edge-TTS."""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
        await communicate.save(output_mp3)
        return output_mp3

    def generate_speech(self, text: str, output_mp3: str, output_wav: Optional[str] = None) -> str:
        """Gera áudio MP3 e opcionalmente converte para WAV 48kHz PCM estéreo."""
        os.makedirs(os.path.dirname(os.path.abspath(output_mp3)), exist_ok=True)
        asyncio.run(self.generate_speech_async(text, output_mp3))

        if output_wav:
            cmd = [
                'ffmpeg', '-y',
                '-i', output_mp3,
                '-ar', '48000',
                '-ac', '2',
                '-c:a', 'pcm_s16le',
                output_wav
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_wav

        return output_mp3

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Retorna a duração exata do arquivo de áudio usando ffprobe."""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
