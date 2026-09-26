"""
Interface de Linha de Comando (CLI) para o Motor de Resumo de Filmes.
"""

import os
import sys
import json
import argparse
from core.screenplay import ScreenplayManager
from core.tts_engine import TTSEngine
from core.focal_tracker import FocalTracker
from core.pipeline import MovieSummaryPipeline

def main():
    parser = argparse.ArgumentParser(
        description="RESUMO-DE-FILME: Motor de Criação de Vídeos Verticais Cinematográficos (9:16)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: script-check
    p_script = subparsers.add_parser("script-check", help="Analisa a contagem de palavras e ritmo do roteiro")
    p_script.add_argument("file", help="Caminho para o arquivo roteiro.txt")

    # Comando: tts
    p_tts = subparsers.add_parser("tts", help="Gera voz neural com Edge-TTS a partir de um roteiro")
    p_tts.add_argument("file", help="Caminho para o roteiro em texto")
    p_tts.add_argument("--out-dir", default="./output", help="Diretório de saída")
    p_tts.add_argument("--voice", default="pt-BR-AntonioNeural", help="Voz neural da Microsoft")
    p_tts.add_argument("--rate", default="-9%", help="Ajuste de velocidade (ex: -9%% para tom dramático)")

    # Comando: crop-calc
    p_crop = subparsers.add_parser("crop-calc", help="Calcula as coordenadas de recorte 9:16 para um foco")
    p_crop.add_argument("--orig-w", type=int, default=1280, help="Largura original do filme")
    p_crop.add_argument("--orig-h", type=int, default=530, help="Altura original do filme")
    p_crop.add_argument("--target-x", type=float, required=True, help="Coordenada X do elemento focal")

    # Comando: render
    p_render = subparsers.add_parser("render", help="Renderiza a montagem de vídeo vertical 9:16")
    p_render.add_argument("--movie", required=True, help="Caminho do arquivo do filme")
    p_render.add_argument("--shots", required=True, help="Arquivo JSON com o mapa de cortes")
    p_render.add_argument("--voice", required=True, help="Arquivo WAV com a narração")
    p_render.add_argument("--out", default="video_final_vertical.mp4", help="Arquivo final de saída")
    p_render.add_argument("--temp", default="./temp_render", help="Diretório temporário de subcortes")

    args = parser.parse_args()

    if args.command == "script-check":
        if not os.path.exists(args.file):
            print(f"Erro: Arquivo '{args.file}' não encontrado.")
            sys.exit(1)
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        analysis = ScreenplayManager.validate_script(content)
        print("--- Análise de Roteiro ---")
        print(f"Palavras: {analysis['word_count']}")
        print(f"Duração estimada: {analysis['estimated_duration_sec']}s (~{analysis['estimated_duration_sec']/60:.1f} min)")
        print(f"Status: {analysis['status']}")
        print(f"Dica: {analysis['advice']}")

    elif args.command == "tts":
        if not os.path.exists(args.file):
            print(f"Erro: Arquivo '{args.file}' não encontrado.")
            sys.exit(1)
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        tts = TTSEngine(voice=args.voice, rate=args.rate)
        mp3 = os.path.join(args.out_dir, "narracao.mp3")
        wav = os.path.join(args.out_dir, "narracao.wav")
        print("Gerando narração com Edge-TTS...")
        tts.generate_speech(content, output_mp3=mp3, output_wav=wav)
        dur = tts.get_audio_duration(wav)
        print(f"Sucesso! Narração gerada: {wav} (Duração: {dur:.2f}s)")

    elif args.command == "crop-calc":
        crop_x = FocalTracker.compute_crop_x(args.orig_w, args.orig_h, args.target_x)
        filt = FocalTracker.get_ffmpeg_crop_filter(args.orig_w, args.orig_h, args.target_x)
        print(f"Crop X calculado: {crop_x}")
        print(f"Filtro FFmpeg correspondente:\n{filt}")

    elif args.command == "render":
        pipeline = MovieSummaryPipeline()
        print("Iniciando renderização de vídeo vertical...")
        out = pipeline.run_render(args.movie, args.shots, args.voice, args.out, args.temp)
        print(f"Vídeo renderizado com sucesso: {out}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
