# Arquitetura e Blueprint do Aplicativo: CineShorts Engine

Este documento define a especificação completa de engenharia, arquitetura de software e roadmap para transformar este ecossistema em um **aplicativo comercial de alta performance** (Desktop App via Electron/Tauri ou SaaS Web local).

---

## 1. Visão Geral do Produto

O **CineShorts Engine** é um estúdio automatizado para criadores de conteúdo que transforma longas-metragens em vídeos virais de alta retenção (formatos 1:1 e 9:16) através de:
1. **Engenharia Reversa de Vídeo de Referência:** O usuário faz upload de um vídeo de exemplo e o app replica seu estilo de ritmo, cortes e linguagem.
2. **Conexão Nativa ao Antigravity CLI / SDK:** O app utiliza o agente do próprio usuário em segundo plano (zero custo de API de LLM).
3. **Clonagem Neural de Voz do Protagonista:** Extração de dataset vocal multi-sample do próprio filme e síntese via XTTS-v2 na GPU local.
4. **Áudio Híbrido Intercalado:** Alternância inteligente entre narração em 1ª pessoa e falas dubladas icônicas do filme.
5. **Montagem de Zero Repetição:** Cada corte avança a ação sem reutilizar planos ou cansar a atenção do espectador.

---

## 2. Integração com o Antigravity (CLI & Python SDK)

O diferencial arquitetural do app é **não depender de chaves de API pagas pelo desenvolvedor**. O app detecta e utiliza o ambiente local do Antigravity do próprio usuário:

```
┌─────────────────────────────────────────────────────────────┐
│                    SEU APLICATIVO (UI/UX)                   │
│         Desktop (Tauri/Electron) ou Web Local (Next.js)     │
└──────────────────────────────┬──────────────────────────────┘
                               │ Chamada Assíncrona Local
┌──────────────────────────────▼──────────────────────────────┐
│           ANTIGRAVITY PYTHON SDK (google-antigravity)       │
│                               ou                            │
│           ANTIGRAVITY CLI (agy headless subprocess)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
    ┌───────────▼───────────┐     ┌───────────▼───────────┐
    │  Roteirista Autônomo   │     │ Decupador Cinemático  │
    │  (Análise de Legendas │     │ (Seleção de Cenas     │
    │   e Engenharia Reversa│     │  e Timestamps Chave)  │
    └───────────────────────┘     └───────────────────────┘
```

### Exemplo de Conexão no Backend do App:
```python
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

async def processar_filme_com_antigravity(filme_path, video_referencia_path):
    config = LocalAgentConfig(
        system_instructions="Você é o diretor de montagem especialista no estilo CineShorts...",
        capabilities=CapabilitiesConfig()
    )
    async with Agent(config) as agent:
        # O agente analisa o vídeo de referência e a cena do filme
        prompt = f"""
        Analise o vídeo de referência em {video_referencia_path}.
        Extraia o padrão de vocabulário, ritmo e intercalação.
        Gere o roteiro em 1ª pessoa e a lista de cortes para o filme {filme_path}.
        """
        response = await agent.chat(prompt)
        async for token in response:
            yield token  # Transmissão em tempo real para a barra de progresso do App
```

---

## 3. Funcionalidades Principais da Interface do App

### 3.1 Upload & Análise de Vídeo de Referência
- O usuário solta um vídeo do TikTok/Reels que viralizou.
- O motor de IA extrai automaticamente:
  - Duração ideal (ex: 75s a 110s).
  - Padrão de cortes (frequência de troca de plano a cada 2.5s a 4.5s).
  - Nível de gírias e coloquialismo brasileiro (ex: *"engoli seco com farinha"*).
  - Pontos de corte de áudio onde a cena original sobe a 100%.

### 3.2 Seletor de Aspect Ratio
- **Modo 1:1 Quadrado (1080×1080):** Ideal para manter dois atores em cena, expressões faciais completas e combates amplos sem cortes agressivos nas laterais.
- **Modo 9:16 Vertical (1080×1920):** Enquadramento total de tela vertical para imersão em smartphones.

### 3.3 Extrator Automático de Dataset Vocal (Voice Clone Studio)
- O app varre o filme dublado usando Whisper e encontra automaticamente 5 a 6 trechos de falas limpas do protagonista (sem trilha sonora de fundo).
- Constrói o **Dataset Multi-Sample** do ator (~30 segundos de fala).
- O motor XTTS-v2 processa na GPU local (RTX 4060) e gera a voz clonada com fidelidade máxima.

### 3.4 Sequenciador Visual com Regra de Zero Repetição
- Algoritmo que valida que **nenhum timestamp de corte visual se repete ou sobrepõe**.
- Toda vez que a narração corta para a fala do filme, a câmera muda de ângulo ou avança o tempo cronológico.

---

## 4. Estrutura de Pastas do Aplicativo

```text
app/
├── frontend/               # Interface do Usuário (Next.js + Tailwind + Lucide Icons)
│   ├── components/
│   │   ├── VideoUploader.tsx
│   │   ├── AspectRatioSelector.tsx
│   │   ├── TimelineEditor.tsx
│   │   └── VoiceCloneStudio.tsx
├── backend/                # Servidor de API (FastAPI + Python 3.11)
│   ├── api/
│   │   ├── routes_project.py
│   │   ├── routes_antigravity.py
│   │   └── routes_render.py
│   ├── engine/
│   │   ├── focal_tracker.py
│   │   ├── voice_clone.py
│   │   └── video_renderer.py
│   └── main.py
└── run_app.bat             # Inicializador em 1 clique
```

---

## 5. Próximos Passos de Desenvolvimento

1. **[Concluído]** Validação do motor de decupagem 1:1 e 9:16.
2. **[Concluído]** Clonagem de voz neural multi-sample na RTX 4060.
3. **[Concluído]** Áudio híbrido com intercalação de falas do filme.
4. **[Próximo]** Construção do backend FastAPI expondo os comandos para a interface gráfica.
5. **[Próximo]** Criação da interface desktop/web com seletor de vídeos e pré-visualização em tempo real.
