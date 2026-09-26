"""
Configurações globais e modelos de parâmetros para o motor de edição.
"""

from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class VideoConfig:
    target_width: int = 1080
    target_height: int = 1920
    fps: int = 24
    crf: int = 20
    preset: str = "veryfast"
    scale_flags: str = "lanczos"
    pix_fmt: str = "yuv420p"

@dataclass
class AudioConfig:
    sample_rate: int = 48000
    channels: int = 2
    bitrate: str = "256k"
    voice_volume: float = 1.0
    ambient_duck_volume: float = 0.03
    ambient_mix_volume: float = 0.3

@dataclass
class TTSConfig:
    voice: str = "pt-BR-AntonioNeural"
    rate: str = "-9%"
    pitch: str = "+0Hz"
    target_duration_sec: float = 180.0

@dataclass
class PipelineConfig:
    video: VideoConfig = field(default_factory=VideoConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    burn_subtitles: bool = False
    max_workers: int = 4
