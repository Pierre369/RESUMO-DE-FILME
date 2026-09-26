"""
Motor de Clonagem de Voz Neural (XTTS-v2 & Multi-Sample)
Capaz de sintetizar narrações em português brasileiro reproduzindo fielmente
o timbre do protagonista a partir de amostras de áudio limpas do filme.
"""

import os
import subprocess
from typing import List, Union

class VoiceCloneEngine:
    def __init__(self, device: str = "cuda"):
        os.environ["COQUI_TOS_AGREED"] = "1"
        self.device = device
        self._tts = None

    def _load_model(self):
        if self._tts is None:
            from TTS.api import TTS
            print(f"[VoiceCloneEngine] Carregando modelo XTTS-v2 no dispositivo: {self.device}...")
            self._tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)

    def clone_to_file(
        self,
        text: str,
        speaker_wavs: Union[str, List[str]],
        output_path: str,
        language: str = "pt"
    ) -> str:
        """
        Sintetiza texto em fala clonando o timbre do falante de referência.
        Suporta lista de múltiplos clipes (multi-sample) para capturar o timbre com máxima fidelidade.
        """
        self._load_model()
        
        raw_output = output_path + ".temp.wav"
        
        # Garante que o texto não vocalize pontuações indesejadas
        clean_text = text.replace(".", ",").replace("!", ",").replace("?", ",")
        clean_text = " ".join(clean_text.split())

        self._tts.tts_to_file(
            text=clean_text,
            speaker_wav=speaker_wavs,
            language=language,
            file_path=raw_output
        )

        # Normaliza para áudio padrão broadcast: 48kHz, 16-bit, estéreo
        cmd = f'ffmpeg -y -i "{raw_output}" -ar 48000 -ac 2 "{output_path}"'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        if os.path.exists(raw_output):
            try:
                os.remove(raw_output)
            except:
                pass

        return output_path
