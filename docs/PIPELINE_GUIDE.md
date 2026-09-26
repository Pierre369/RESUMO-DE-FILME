# Guia Completo da Pipeline: Resumo Cinematográfico Vertical (9:16)

Este guia documenta o método exato de ponta a ponta para transformar qualquer longa-metragem em um resumo cinematográfico vertical dinâmico, focado em retenção para plataformas como TikTok, Instagram Reels e YouTube Shorts.

---

## 1. Fundamentos & Concepção de Roteiro

### 1.1 Perspectiva em Primeira Pessoa (1st Person POV)
Diferente de canais tradicionais de resumo que narram em terceira pessoa de forma impessoal ("Ele foi até a casa e descobriu..."), a abordagem deste projeto adota a **voz do próprio personagem**:
- O personagem narra suas dores, motivações ocultas, erros e dilemas morais.
- Cria conexão emocional instantânea com o público nos primeiros 3 segundos.
- O tom deve ser reflexivo, confessional e cinematográfico.

### 1.2 Estrutura Dramática em 3 Atos
Para um vídeo de aproximadamente 3 minutos (~180 segundos):

| Ato | Janela de Tempo | Objetivo Dramático | Ritmo Visual |
| :--- | :--- | :--- | :--- |
| **Ato 1: O Gancho e a Queda** | 0s - 45s | Apresentar o estado inicial e o erro fatal / catalisador. | Cortes de 2.0s a 3.5s. |
| **Ato 2: A Espiral de Consequências** | 45s - 130s | As perdas, confrontos, aprofundamento do conflito. | Cortes de 1.8s a 3.0s. |
| **Ato 3: O Clímax e a Resignação** | 130s - 180s | A escolha final, o sacrifício e a lição que ficou. | Cortes mais longos no clímax (2.5s - 4.5s) para peso dramático. |

### 1.3 Métrica de Fala e Pontuação Cinematográfica
- **Velocidade de Fala:** ~135 a 145 palavras por minuto (WPM).
- **Pontuação de Respiração:** O uso intencional de reticências (`...`) no texto força o motor de síntese de voz (TTS) a inserir micropausas de reflexão antes de revelações de impacto.

---

## 2. Geração e Tratamento de Voz (TTS)

Utiliza-se o motor neural de alta fidelidade da Microsoft (`edge-tts`).

### 2.1 Vozes Recomendadas
- **Masculina Dramática:** `pt-BR-AntonioNeural` (grave, reflexiva, autoritária).
- **Feminina Intensa:** `pt-BR-FranciscaNeural` (expressiva, profunda).

### 2.2 Parâmetros de Modulação
- **Taxa de Reprodução (`rate`):** `-9%` a `-10%`. A velocidade padrão do TTS soa robótica ou excessivamente rápida. Reduzir em 9% confere o peso e solenidade adequados a uma narração de cinema.
- **Pitch:** `+0Hz` (mantém o timbre original natural).

### 2.3 Pós-Processamento de Áudio
O arquivo gerado (`.mp3`) é convertido para áudio linear sem perdas (`WAV 48kHz, 16-bit, estéreo`) para garantir sincronia exata frame-a-frame durante o processo de mixagem do FFmpeg.

---

## 3. Decupagem e Detecção de Cenas (Shot Cutting)

### 3.1 Duração Ideal por Take
- **Máximo recomendado:** 4.5 segundos.
- **Média recomendada:** 2.0 a 3.0 segundos.
- Takes com mais de 5 segundos derrubam a métrica de retenção em feeds verticais.

### 3.2 O Princípio da Troca de Ângulo
Se uma tomada de 6 segundos possui uma virada de câmera ou troca de plano aos 3.2 segundos, ela **deve ser dividida em dois sub-cortes**:
- `Sub-corte A`: Centralizado no Sujeito A (ex: Peter Parker à esquerda).
- `Sub-corte B`: Recortado e centralizado no Sujeito B (ex: Zendaya à direita).

---

## 4. Enquadramento 9:16 Dinâmico (Dynamic Focal Tracking)

Longas-metragens são gravados em formatos widescreen (16:9, 1.85:1 ou 2.39:1 anamórfico). Ao recortar diretamente para vertical (9:16), 60% a 70% das bordas horizontais são descartadas.

### 4.1 A Fórmula do Crop Exato
Dado um vídeo original de dimensões $W_{orig} \times H_{orig}$ sendo escalado para uma altura de $1920$:

1. **Fator de Escala Vertical:**
   $$S = \frac{1920}{H_{orig}}$$

2. **Largura Escalada:**
   $$W_{scaled} = \text{round}(W_{orig} \times S)$$

3. **Posição X do Ponto Focal Escalado:**
   Dado o ponto de interesse horizontal $X_{target}$ na resolução original:
   $$X'_{target} = X_{target} \times S$$

4. **Cálculo da Origem do Crop ($X_{crop}$):**
   Para que $X'_{target}$ fique exatamente no centro ($X = 540$) do quadro de largura $1080$:
   $$X_{crop} = \text{round}(X'_{target} - 540)$$

5. **Limites de Borda (Clamping):**
   $$X_{crop} = \max(0, \min(X_{crop}, W_{scaled} - 1080))$$

### 4.2 Filtro FFmpeg Gerado
```bash
-vf "scale=-1:1920,crop=1080:1920:{X_crop}:0"
```

---

## 5. Mixagem e Ducking de Áudio

O vídeo final não é apenas narração seca. O som original do filme (explosões, passos, chuva, trilha sonora orquestral) é preservado no fundo para conferir imersão cinematográfica.

### 5.1 Parâmetros de Volume
- **Áudio Original do Filme (Ducking):** `volume=0.08` (redução de aproximadamente -22 dB).
- **Voz da Narração:** `volume=1.25` (ganho de +2 dB com normalização).

### 5.2 Filtro de Mixagem FFmpeg
```bash
-filter_complex "[0:a]volume=0.08[a_film];[1:a]volume=1.25[a_voice];[a_film][a_voice]amix=inputs=2:duration=first:dropout_transition=2[a_out]" -map 0:v -map "[a_out]"
```

---

## 6. Pipeline de Renderização em Alto Desempenho

1. **Geração dos Sub-cortes em Paralelo:**
   - O mapa de cortes (`mapa_de_cortes.json`) é processado com `ThreadPoolExecutor`.
   - Cada trecho é recortado, escalado e salvo temporariamente em `subcuts/subcut_XXX.mp4`.
2. **Concat Demuxer Sem Perdas:**
   - Todos os sub-cortes normalizados (1080x1920, 24fps) são concatenados via `-f concat -safe 0 -c copy`.
3. **Mixagem Final com Áudio:**
   - O arquivo de vídeo concatenado recebe o áudio do filme mixado com a narração TTS sincronizada.
   - O vídeo final é exportado com `libx264`, `preset fast`, `crf 18` e `movflags +faststart` para reprodução instantânea na web.
