"""
Configurações globais e modelos de parâmetros para o motor de edição.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal

@dataclass
class VideoConfig:
    aspect_ratio: Literal["9:16", "1:1"] = "1:1"
    target_width: int = 1080
    target_height: int = 1080
    fps: int = 24
    crf: int = 18
    preset: str = "fast"
    scale_flags: str = "lanczos"
    pix_fmt: str = "yuv420p"

    def set_aspect_ratio(self, ratio: Literal["9:16", "1:1"]):
        self.aspect_ratio = ratio
        if ratio == "1:1":
            self.target_width = 1080
            self.target_height = 1080
        elif ratio == "9:16":
            self.target_width = 1080
            self.target_height = 1920

@dataclass
class AudioConfig:
    sample_rate: int = 48000
    channels: int = 2
    bitrate: str = "192k"
    voice_volume: float = 1.25
    ambient_duck_volume: float = 0.08
    movie_dialogue_volume: float = 1.0

@dataclass
class VoiceCloneConfig:
    engine: Literal["xtts_v2", "edge_tts", "f5_tts"] = "xtts_v2"
    reference_wavs: List[str] = field(default_factory=list)
    language: str = "pt"
    device: str = "cuda"

@dataclass
class TTSConfig:
    voice: str = "pt-BR-AntonioNeural"
    rate: str = "-4%"
    pitch: str = "+0Hz"
    target_duration_sec: float = 90.0
    voice_clone: VoiceCloneConfig = field(default_factory=VoiceCloneConfig)

@dataclass
class PipelineConfig:
    video: VideoConfig = field(default_factory=VideoConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    burn_subtitles: bool = False
    max_workers: int = 4
