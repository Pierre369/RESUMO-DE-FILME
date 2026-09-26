"""
Serviço de Síntese e Clonagem de Voz via OpenRouter (Fish Audio S2.1 Pro) e Edge-TTS (Fallback).
Suporta clonagem instantânea (stateless voice cloning) usando o parâmetro input_references
com amostras de áudio dublado extraídas diretamente do filme.
"""

import os
import base64
import json
import asyncio
import httpx
import edge_tts
from typing import Optional, Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_FILE = os.path.join(BASE_DIR, "app", "data", "config.json")
CACHE_DIR = os.path.join(BASE_DIR, "app", "data", "voice_samples")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

class VoiceService:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.openrouter_url = "https://openrouter.ai/api/v1/audio/speech"

    def _load_api_key(self) -> Optional[str]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    key = cfg.get("openrouter_api_key", "").strip()
                    if key:
                        return key
            except Exception:
                pass
        return os.environ.get("OPENROUTER_API_KEY", "").strip() or None

    def save_api_key(self, key: str):
        self.api_key = key.strip()
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                pass
        cfg["openrouter_api_key"] = self.api_key
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

    def get_key_status(self) -> Dict[str, Any]:
        has_key = bool(self.api_key)
        masked = ""
        if has_key:
            if len(self.api_key) > 10:
                masked = self.api_key[:6] + "..." + self.api_key[-4:]
            else:
                masked = "******"
        return {
            "has_key": has_key,
            "masked_key": masked,
            "provider": "OpenRouter (Fish Audio S2.1 Pro)",
            "fallback": "Edge-TTS Neural (pt-BR)"
        }

    async def test_api_key(self, key: str) -> Dict[str, Any]:
        """Testa se a chave OpenRouter é válida."""
        headers = {
            "Authorization": f"Bearer {key.strip()}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "CineShorts Studio"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    return {
                        "valid": True,
                        "label": data.get("label", "OpenRouter Key"),
                        "limit": data.get("limit", None),
                        "usage": data.get("usage", 0)
                    }
                else:
                    return {"valid": False, "error": f"Status {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def extract_character_sample(self, movie_path: str, character_name: str) -> Optional[str]:
        """
        Extrai uma amostra limpa de 10 a 14 segundos da fala dublada do personagem no filme
        para servir de referência para a clonagem.
        """
        sample_path = os.path.join(CACHE_DIR, f"sample_{abs(hash(character_name + movie_path)) % 100000}.wav")
        if os.path.exists(sample_path) and os.path.getsize(sample_path) > 10000:
            return sample_path

        char_lower = character_name.lower()
        movie_lower = movie_path.lower()

        # Timestamps específicos com falas claras e isoladas dos dubladores
        if "menu" in movie_lower:
            if "margot" in char_lower or "erin" in char_lower:
                start_ts, dur = "01:29:05", "12"
            elif "slowik" in char_lower or "chef" in char_lower:
                start_ts, dur = "01:29:56", "11"
            else:
                start_ts, dur = "01:29:05", "12"
        elif "palmer" in movie_lower:
            if "palmer" in char_lower or "eddie" in char_lower:
                start_ts, dur = "01:13:32", "12"
            elif "sam" in char_lower:
                start_ts, dur = "01:13:58", "10"
            else:
                start_ts, dur = "01:13:32", "12"
        elif "wick" in movie_lower or "john" in movie_lower:
            if "iosef" in char_lower:
                start_ts, dur = "00:08:50", "10"
            elif "viggo" in char_lower:
                start_ts, dur = "00:25:20", "12"
            else:
                start_ts, dur = "00:31:30", "12"
        elif "aranha" in movie_lower or "spider" in movie_lower:
            start_ts, dur = "00:15:00", "12"
        else:
            start_ts, dur = "00:10:00", "12"

        from app.services.media_service import MediaService
        audio_map = MediaService.get_best_audio_stream_map(movie_path)

        import subprocess
        cmd = [
            "ffmpeg", "-y", "-ss", start_ts, "-t", dur,
            "-i", movie_path,
            "-map", audio_map,
            "-ac", "1", "-ar", "44100",
            "-c:a", "pcm_s16le",
            sample_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return sample_path
        except Exception as e:
            print(f"Erro ao extrair amostra de voz: {e}")
            return None

    async def generate_speech(
        self,
        text: str,
        character_name: str,
        movie_path: str,
        output_audio_path: str,
        speed_rate: str = "+16%"
    ) -> Dict[str, Any]:
        """
        Gera a fala clonada usando OpenRouter (Fish Audio) se a chave existir,
        ou Edge-TTS Neural acelerado como fallback de alta fidelidade.
        """
        # Tenta OpenRouter Fish Audio se a chave estiver configurada
        if not self.api_key:
            self.api_key = self._load_api_key()

        if self.api_key:
            sample_wav = self.extract_character_sample(movie_path, character_name)
            if sample_wav and os.path.exists(sample_wav):
                try:
                    with open(sample_wav, "rb") as f:
                        b64_audio = base64.b64encode(f.read()).decode("utf-8")

                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "CineShorts Studio"
                    }

                    # Payload conforme especificação oficial do OpenRouter para Fish Audio S2.1
                    payload = {
                        "model": "fish-audio/s2.1-pro",
                        "input": text,
                        "response_format": "mp3",
                        "input_references": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": f"data:audio/wav;base64,{b64_audio}"
                                }
                            }
                        ]
                    }

                    async with httpx.AsyncClient(timeout=45.0) as client:
                        resp = await client.post(self.openrouter_url, headers=headers, json=payload)
                        if resp.status_code == 200 and len(resp.content) > 1000:
                            with open(output_audio_path, "wb") as f:
                                f.write(resp.content)
                            return {
                                "success": True,
                                "engine": "OpenRouter (Fish Audio S2.1 Pro)",
                                "cloned_from": character_name,
                                "path": output_audio_path
                            }
                        else:
                            # Tenta modelo alternativo se s2.1-pro der 404/400
                            payload["model"] = "fish-audio/s2.1-pro-free"
                            resp2 = await client.post(self.openrouter_url, headers=headers, json=payload)
                            if resp2.status_code == 200 and len(resp2.content) > 1000:
                                with open(output_audio_path, "wb") as f:
                                    f.write(resp2.content)
                                return {
                                    "success": True,
                                    "engine": "OpenRouter (Fish Audio S2.1 Pro Free)",
                                    "cloned_from": character_name,
                                    "path": output_audio_path
                                }
                            print(f"OpenRouter Fish Audio status {resp.status_code}: {resp.text[:300]}")
                except Exception as e:
                    print(f"Erro na chamada OpenRouter Fish Audio: {e}")

        # Fallback de alta fidelidade Edge-TTS Neural
        char_lower = character_name.lower()
        if any(female in char_lower for female in ["margot", "maggie", "erin", "mulher", "menina", "garota"]):
            voice = "pt-BR-FranciscaNeural"
        else:
            voice = "pt-BR-AntonioNeural"

        comm = edge_tts.Communicate(text, voice, rate=speed_rate)
        await comm.save(output_audio_path)

        return {
            "success": True,
            "engine": "Edge-TTS Neural (Fallback)",
            "voice": voice,
            "path": output_audio_path
        }
