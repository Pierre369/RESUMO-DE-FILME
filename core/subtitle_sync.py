"""
Módulo de Sincronização e Geração de Legendas (.SRT) com Whisper.
"""

import os
import subprocess
from typing import List, Dict, Any

class SubtitleSync:
    """
    Gera arquivos .srt com precisão de timestamp para legendagem dinâmica.
    """

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Converte segundos para o formato padrão SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def generate_srt_with_whisper(audio_path: str, output_srt: str, model_size: str = "base") -> str:
        """
        Executa transcrição e alinhamento temporal usando OpenAI Whisper.
        """
        try:
            import whisper
            model = whisper.load_model(model_size)
            result = model.transcribe(audio_path, language="pt", task="transcribe")
            
            with open(output_srt, 'w', encoding='utf-8') as f:
                for idx, segment in enumerate(result['segments'], start=1):
                    start_str = SubtitleSync.format_timestamp(segment['start'])
                    end_str = SubtitleSync.format_timestamp(segment['end'])
                    text = segment['text'].strip()
                    f.write(f"{idx}\n{start_str} --> {end_str}\n{text}\n\n")

            return output_srt
        except ImportError:
            # Fallback se whisper não estiver instalado no ambiente
            print("Aviso: 'openai-whisper' não instalado diretamente. Utilizando fallback via CLI do whisper.")
            cmd = ['whisper', audio_path, '--model', model_size, '--language', 'pt', '--output_format', 'srt', '--output_dir', os.path.dirname(output_srt)]
            subprocess.run(cmd, check=True)
            return output_srt
