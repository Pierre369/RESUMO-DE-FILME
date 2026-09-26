# Arquitetura e Roadmap do Aplicativo: CineShorts Engine

Este documento serve como a **planta de engenharia (blueprint)** para transformar este pipeline de scripts em uma aplicação completa (SaaS Web ou Desktop App via Electron/Tauri), projetada para automatizar a produção de vídeos verticais (9:16) a partir de longas-metragens.

---

## 1. Visão Geral do Produto

O objetivo do aplicativo é permitir que criadores de conteúdo, canais de resumo e produtoras gerem vídeos cinematográficos em formato 9:16 com retenção máxima, utilizando inteligência artificial para roteirização em 1ª pessoa, síntese de voz dramática, decupagem automática e enquadramento dinâmico dos sujeitos.

---

## 2. Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                 FRONTEND (Next.js / Tauri)                  │
│  - Editor de Roteiro (WPM & Previews de Áudio)              │
│  - Timeline de Cortes & Marcadores de Cena                  │
│  - Player Interativo com Bounding Box 9:16 Ajustável        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / WebSocket (Progresso)
┌──────────────────────────────▼──────────────────────────────┐
│                    BACKEND (FastAPI Core)                   │
│  - Orquestrador de Jobs (Celery / Redis Queue)              │
│  - API de Projetos, Mídias e Configurações                  │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐
│  MOTOR IA   │         │  VISÃO COMP │         │ MOTOR MÍDIA │
│  - LLM Roteiro│       │  - PySceneDetect│     │  - FFmpeg   │
│  - Edge/Eleven│       │  - YOLOv8 /   │       │    (NVENC)  │
│  - Whisper  │         │    MediaPipe  │       │  - Concat   │
└─────────────┘         └─────────────┘         └─────────────┘
```

---

## 3. Componentes e Módulos do Sistema

### 3.1 Módulo 1: Roteirista de IA (Screenplay Engine)
- **Função:** Ler o arquivo de legendas original do filme (`.srt` de 2 horas) ou transcrição completa.
- **Prompt Estruturado:**
  - Identificar o personagem selecionado pelo usuário.
  - Selecionar os 8 a 12 eventos cruciais da jornada daquele personagem.
  - Escrever a narração em 1ª pessoa respeitando a métrica de 350-420 palavras (~3 minutos).
  - Inserir marcas de direção dramática `[...]` para respiração da voz.

### 3.2 Módulo 2: Motor de Voz e Sincronia Temporal (TTS & Align)
- **Síntese de Voz:**
  - Integração com `edge-tts` (gratuito) e provedores premium (`ElevenLabs`, `Kokoro-82M`).
  - Aplicação automática de taxa de velocidade cinemática (-9% a -12%).
- **Sincronia Palavra por Palavra:**
  - `faster-whisper` para gerar timestamps exatos de cada palavra.
  - Permite gerar legendas animadas no estilo "Hormozi / TikTok" no frontend.

### 3.3 Módulo 3: Visão Computacional e Auto-Framing (Focal AI)
- **Detecção de Cortes (Scene Splitter):**
  - Utiliza `PySceneDetect` (AdaptiveDetector) para segmentar o filme em tomadas puras, evitando que o corte 9:16 atravesse duas tomadas com enquadramentos opostos.
- **Rastreamento de Sujeito (Auto-Centering):**
  - Modelo `YOLOv8-pose` ou `MediaPipe Face/Body Detection`.
  - Para cada sub-corte, o modelo identifica as pessoas na tela, calcula quem está falando ou em primeiro plano e define o centro horizontal ideal:
    $$X_{target} = \frac{x_{min} + x_{max}}{2}$$
  - O backend converte automaticamente esse centro para o parâmetro FFmpeg:
    $$X_{crop} = \text{clamp}(X'_{target} - 540, 0, W_{scaled} - 1080)$$

### 3.4 Módulo 4: Editor Visual Interativo (UI/UX)
- **Timeline Interativa:** Exibe a trilha de áudio narrada em cima e a régua de takes do filme embaixo.
- **Janela de Ajuste 9:16:**
  - O usuário vê a tela original em 16:9 widescreen.
  - Uma máscara retangular vertical (9:16) é sobreposta. O usuário pode arrastar a máscara para a esquerda ou direita se desejar sobrescrever o foco automático da IA.

### 3.5 Módulo 5: Renderizador Distribuído (High Performance)
- **Aceleração por Hardware:** Uso de `h264_nvenc` (NVIDIA) ou `h264_amf` (AMD) para renderizar os 60+ sub-cortes em segundos em vez de minutos.
- **Pipeline em Lote:** Renderização simultânea de múltiplos trechos em threads isoladas, unificados via `FFmpeg concat demuxer`.
- **Ducking Automatizado:** Mixagem estéreo com curva de compressão sidechain ou ducking fixo de ambiência (-22 dB).

---

## 4. Estrutura do Banco de Dados / Projeto

```json
{
  "project_id": "proj_spiderman_001",
  "movie_file": "/storage/movies/homem_aranha.mp4",
  "character": "Peter Parker",
  "script": {
    "text": "Eu só queria ser normal de novo...",
    "duration_target_seconds": 180,
    "words_count": 395
  },
  "audio": {
    "tts_voice": "pt-BR-AntonioNeural",
    "rate": "-9%",
    "film_volume": 0.08,
    "voice_volume": 1.25
  },
  "cuts": [
    {
      "id": 1,
      "time_in": "00:00:15.500",
      "time_out": "00:00:18.000",
      "duration": 2.500,
      "focus_target": "face_peter",
      "target_x": 960,
      "crop_x": 1140,
      "locked_by_user": false
    }
  ]
}
```

---

## 5. Fases de Implementação Recomendadas

### Fase 1: API Core & Automação Local (Atual)
- [x] Motor de decupagem e cálculo 9:16 verificado e funcional (`core/`).
- [x] CLI para execução por linha de comando (`cli.py`).
- [x] Integração com Edge-TTS e mixagem com ducking.
- [x] Exemplos de projeto com dados reais validados.

### Fase 2: Backend REST & IA de Rastreamento (Próximo Passo)
- [ ] API FastAPI expondo endpoints `/api/project`, `/api/script/generate`, `/api/cuts/detect`, `/api/render`.
- [ ] Integração do detector de faces YOLOv8 para sugerir automaticamente `target_x` e `crop_x` de cada take.
- [ ] Suporte a aceleração GPU no FFmpeg (`h264_nvenc`).

### Fase 3: Interface Web / Desktop
- [ ] Criação do painel visual em Next.js / Tailwind.
- [ ] Player de vídeo com overlay interativo de enquadramento 9:16.
- [ ] Exportação direta com 1 clique para formatos de redes sociais.
