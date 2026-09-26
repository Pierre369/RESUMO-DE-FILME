# Especificação Técnica de Arquitetura (Engine Internals)

Este documento descreve detalhadamente a matemática, os algoritmos e a arquitetura de processamento de mídia empregados no motor de resumos cinematográficos verticais.

---

## 1. Transformação Geométrica de Aspect Ratio (16:9 / 2.39:1 $\rightarrow$ 9:16)

A maioria dos filmes é masterizada em proporções horizontais (ex.: $1920 \times 1080$, $3840 \times 2160$ ou anamórfico $1920 \times 800$). O objetivo do motor é converter esse conteúdo para o padrão vertical estrito de redes sociais: **$1080 \times 1920$ (9:16)** sem letterboxing (barras pretas), preenchendo 100% da tela e mantendo o ponto focal no centro absoluto.

### 1.1 Dedução Matemática do Crop Dinâmico

Seja o vídeo de entrada com resolução:
- Largura nativa: $W_{in}$
- Altura nativa: $H_{in}$

A resolução de saída vertical é:
- $W_{out} = 1080$
- $H_{out} = 1920$

#### Passo 1: Fator de Escala Vertical
Para preencher a altura completa sem distorcer o aspecto original dos atores:
$$S = \frac{H_{out}}{H_{in}} = \frac{1920}{H_{in}}$$

#### Passo 2: Dimensões Escaladas
A largura do vídeo após o redimensionamento vertical uniforme é:
$$W_{scaled} = \text{round}(W_{in} \cdot S)$$
$$H_{scaled} = 1920$$

*Exemplo:* Para um vídeo $1920 \times 1080$:
$$S = \frac{1920}{1080} \approx 1.7778$$
$$W_{scaled} = \text{round}(1920 \cdot 1.7778) = 3413 \text{ pixels}$$

#### Passo 3: Mapeamento de Ponto de Foco e Origem de Janela
Seja $(X_{target}, Y_{target})$ o ponto focal do objeto ou rosto de interesse nas coordenadas originais do filme ($0 \le X_{target} \le W_{in}$).

Ao redimensionar a imagem, a nova coordenada horizontal do ponto focal torna-se:
$$X'_{target} = X_{target} \cdot S$$

Para posicionar esse ponto exatamente no centro horizontal do quadro de 1080 pixels ($X_{center} = 540$), a coordenada de corte inicial $X_{crop}$ deve ser:
$$X_{crop} = \text{round}(X'_{target} - 540)$$

#### Passo 4: Algoritmo de Clamping de Fronteira
Para evitar amostragem fora dos limites válidos do frame (o que causaria erro no FFmpeg ou bordas pretas indesejadas):
$$X_{crop\_final} = \max\left(0, \; \min\left(X_{crop}, \; W_{scaled} - 1080\right)\right)$$

### 1.2 Expressão FFmpeg Resultante
```bash
-vf "scale=-1:1920,crop=1080:1920:{X_crop_final}:0"
```

---

## 2. Decupagem de Cortes e Lógica Multi-Câmera

### 2.1 O Problema da Troca de Ângulo
Em uma conversa dramática, a câmera corta entre o Ator A (à esquerda) e a Atriz B (à direita). Se esse take for tratado como um único recorte estático, quando a câmera cortar para o segundo ator, ele ficará fora de quadro ou cortado pela metade.

### 2.2 Estratégia de Sub-Cortes
O motor adota o particionamento em **sub-cortes independentes**:
```
Take Original (00:01:10 a 00:01:16 - 6s)
 ├── Sub-corte 1: 00:01:10 - 00:01:12.8 (2.8s) -> Foco: Ator A  -> X_crop = 1140
 └── Sub-corte 2: 00:01:12.8 - 00:01:16.0 (3.2s) -> Foco: Atriz B -> X_crop = 1850
```

Cada sub-corte possui seus próprios metadados no arquivo de decupagem (`mapa_de_cortes.json`):
```json
{
  "id": 14,
  "start": "00:35:12.400",
  "end": "00:35:15.200",
  "target_x": 1280,
  "crop_x": 1735,
  "description": "Zendaya na cafeteria - foco rosto"
}
```

---

## 3. Arquitetura de Áudio e Ducking Dinâmico

O pipeline constrói uma paisagem sonora cinematográfica em duas camadas:

```
[Trilha do Filme Original]  ──> Volume Ducking (0.08 / -22dB) ──┐
                                                                ├──> [amix] ──> [Áudio Final 48kHz]
[Narração Neural TTS]       ──> Normalização / Ganho (1.25)    ──┘
```

### 3.1 Vantagens Deste Método
1. **Imersão Total:** O espectador ouve as explosões, passos, vento e a trilha orquestral do filme original sincronizados com os cortes visuais.
2. **Inteligibilidade Vocal:** Ao atenuar o áudio do filme em 22 dB e elevar a narração, a voz humana corta a mixagem com total clareza em alto-falantes de smartphones.

---

## 4. Pipeline de Processamento Paralelo e Concat

Para renderizar 60 a 80 cortes de um longa de 2 horas em alta resolução sem sobrecarregar a memória RAM:

1. **Extração e Processamento Concorrente:**
   - O orquestrador divide os cortes entre $N$ threads de CPU usando `ThreadPoolExecutor`.
   - Cada thread executa uma instância isolada do FFmpeg com seek rápido (`-ss` antes de `-i`):
     ```bash
     ffmpeg -y -ss {start} -to {end} -i "{input_movie}" -vf "scale=-1:1920,crop=1080:1920:{crop_x}:0" -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -an "subcuts/subcut_{id:03d}.mp4"
     ```
2. **Concatenação Sem Perdas (Concat Demuxer):**
   - Cria-se um arquivo de manifesto `filelist.txt`:
     ```
     file 'subcuts/subcut_001.mp4'
     file 'subcuts/subcut_002.mp4'
     ...
     ```
   - O FFmpeg realiza a junção dos fluxos de vídeo em velocidade ultra rápida:
     ```bash
     ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy raw_video_concat.mp4
     ```
3. **Muxing com a Trilha Sonora:**
   - O áudio original extraído dos trechos e o áudio da narração são combinados em uma única passagem final com o container MP4 otimizado para streaming (`movflags +faststart`).
