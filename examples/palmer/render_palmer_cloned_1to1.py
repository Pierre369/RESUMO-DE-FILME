import os
import subprocess

movie = r'D:\Downloads\RESUMO DE FILME\FILME\Palmer (2021) Dublado.mp4'
work_dir = r'D:\Downloads\RESUMO DE FILME\palmer_work_v3'
os.makedirs(work_dir, exist_ok=True)
os.makedirs(os.path.join(work_dir, 'segments'), exist_ok=True)

segments = [
    # --- BLOCO 1: A Descoberta (cloned_narr_1: 15.36s) ---
    ("01_palmer_chega_sala", 4376.0, 5.00, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_1.wav", 0.0, 5.00)),
    ("02_palmer_abre_porta", 4384.0, 5.00, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_1.wav", 5.00, 5.00)),
    ("03_sam_rosto_borrado", 4392.0, 5.36, 560, "narration_slice", ("palmer_narration_cloned/cloned_narr_1.wav", 10.00, 5.36)),
    
    # --- DIÁLOGO DO FILME 1: Palmer dá o conselho (5.5s) ---
    ("04_dialogo_conselho", 4412.0, 5.50, 680, "movie_dialogue", None),
    
    # --- DIÁLOGO DO FILME 2: Sam revela que foi o Daryl (9.5s) ---
    ("05_dialogo_revelacao", 4438.0, 9.50, 650, "movie_dialogue", None),
    
    # --- BLOCO 2: A Fúria de Palmer (cloned_narr_2: 11.00s) ---
    ("06_palmer_choque_face", 4448.0, 3.50, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_2.wav", 0.0, 3.50)),
    ("07_palmer_levanta_cama", 4452.5, 3.50, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_2.wav", 3.50, 3.50)),
    ("08_palmer_passos_porta", 4456.5, 4.00, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_2.wav", 7.00, 4.00)),
    
    # --- DIÁLOGO DO FILME 3: Maggie tenta segurar na porta (4.5s) ---
    ("09_maggie_porta_impede", 4458.5, 4.50, 800, "movie_dialogue", None),
    
    # --- BLOCO 3: A Estrada e a Chegada no Bar (cloned_narr_3: 12.72s) ---
    ("10_caminhonete_partida", 4464.0, 4.20, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_3.wav", 0.0, 4.20)),
    ("11_caminhonete_estrada", 4471.0, 4.50, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_3.wav", 4.20, 4.50)),
    ("12_daryl_amigos_rindo", 4478.5, 4.02, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_3.wav", 8.70, 4.02)),
    
    # --- DIÁLOGO DO FILME 4: Palmer prensa Daryl na parede (8.0s) ---
    ("13_dialogo_confronto", 4496.0, 8.00, 756, "movie_dialogue", None),
    
    # --- AÇÃO DO FILME: A Porrada e o Bar em Silêncio (9.0s) ---
    ("14_acao_porrada_queda", 4516.0, 4.50, 756, "movie_dialogue", None),
    ("15_amigos_bar_choque", 4534.5, 4.50, 650, "movie_dialogue", None),
    
    # --- BLOCO 4: A Saída do Bar (cloned_narr_4: 8.96s) ---
    ("16_palmer_sai_noite", 4539.5, 4.40, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_4.wav", 0.0, 4.40)),
    ("17_palmer_fuma_varanda", 4548.0, 4.56, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_4.wav", 4.40, 4.56)),
    
    # --- DIÁLOGO DO FILME 5: "Só em quem tem mais de trinta" (7.5s) ---
    ("18_dialogo_30anos", 4554.0, 7.50, 880, "movie_dialogue", None),
    
    # --- BLOCO 5: Fechamento de Moral (cloned_narr_5: 5.65s) ---
    ("19_palmer_olhar_final", 4562.0, 5.65, 756, "narration_slice", ("palmer_narration_cloned/cloned_narr_5.wav", 0.0, 5.65))
]

print(f"Total de segmentos únicos a renderizar: {len(segments)}")
segment_files = []

for idx, (name, v_start, v_dur, crop_x, a_type, a_info) in enumerate(segments):
    out_seg = os.path.join(work_dir, 'segments', f"{idx:02d}_{name}.mp4")
    segment_files.append(out_seg)
    
    if a_type == "movie_dialogue":
        cmd = (
            f'ffmpeg -y -ss {v_start} -t {v_dur} -i "{movie}" '
            f'-vf "scale=-1:1080,crop=1080:1080:{crop_x}:0,setsar=1" '
            f'-c:v libx264 -preset fast -crf 18 -r 24 -pix_fmt yuv420p '
            f'-af "volume=1.0" -c:a aac -b:a 192k -ar 48000 "{out_seg}"'
        )
    else:
        narr_file, narr_offset, narr_len = a_info
        tmp_narr = os.path.join(work_dir, f"tmp_cloned_narr_{idx}.wav")
        subprocess.run(f'ffmpeg -y -ss {narr_offset} -t {narr_len} -i "{narr_file}" -ar 48000 -ac 2 "{tmp_narr}"', shell=True, capture_output=True)
        
        cmd = (
            f'ffmpeg -y -ss {v_start} -t {v_dur} -i "{movie}" -i "{tmp_narr}" '
            f'-filter_complex "[0:v]scale=-1:1080,crop=1080:1080:{crop_x}:0,setsar=1[v];'
            f'[0:a]volume=0.08[a_film];[1:a]volume=1.25[a_voice];'
            f'[a_film][a_voice]amix=inputs=2:duration=first:dropout_transition=1[a]" '
            f'-map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 18 -r 24 -pix_fmt yuv420p '
            f'-c:a aac -b:a 192k -ar 48000 "{out_seg}"'
        )
        
    print(f"Renderizando segmento {idx+1}/{len(segments)}: {name} ({v_dur:.2f}s)...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Erro em {name}: {res.stderr[:300]}")

concat_list = os.path.join(work_dir, "concat_list.txt")
with open(concat_list, "w", encoding="utf-8") as f:
    for s_file in segment_files:
        f.write(f"file '{s_file.replace(os.sep, '/')}'\n")

output_final = r'D:\Downloads\RESUMO DE FILME\palmer_1x1_resumo.mp4'
concat_cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_list}" -c copy -movflags +faststart "{output_final}"'
print("Concatenando versão master final com multi-sample voice cloning...")
res_concat = subprocess.run(concat_cmd, shell=True, capture_output=True, text=True)

if res_concat.returncode == 0:
    print(f"VÍDEO MASTER FINAL CONCLUÍDO: {output_final}")
    p = subprocess.run(f'ffprobe -v error -show_entries format=duration,size -of json "{output_final}"', shell=True, capture_output=True, text=True)
    print(p.stdout)
else:
    print(f"Erro na concatenacao: {res_concat.stderr[:300]}")
