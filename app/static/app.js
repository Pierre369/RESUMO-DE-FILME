document.addEventListener("DOMContentLoaded", () => {
  const movieSelect = document.getElementById("movie-select");
  const btnRender = document.getElementById("btn-render");
  const btnAiScript = document.getElementById("btn-ai-script");
  const scriptInput = document.getElementById("script-input");
  const progressBar = document.getElementById("progress-bar");
  const progressPercent = document.getElementById("progress-percent");
  const progressStepText = document.getElementById("progress-step-text");
  const masterVideo = document.getElementById("master-video");
  const playerFormatTag = document.getElementById("player-format-tag");
  const aspectRadios = document.querySelectorAll('input[name="aspect-ratio"]');

  // Load Initial Status
  fetch("/api/status")
    .then(res => res.json())
    .then(data => {
      if (data.antigravity && data.antigravity.connected) {
        document.getElementById("ag-status-text").innerText = `Antigravity CLI: Conectado (${data.antigravity.user})`;
      }
    })
    .catch(err => console.error("Erro ao verificar status do sistema:", err));

  // Load Movies
  fetch("/api/movies")
    .then(res => res.json())
    .then(data => {
      movieSelect.innerHTML = "";
      if (data.movies && data.movies.length > 0) {
        data.movies.forEach(m => {
          const opt = document.createElement("option");
          opt.value = m.path;
          opt.innerText = `${m.filename} (${m.duration_formatted} | ${m.size_mb} MB)`;
          movieSelect.appendChild(opt);
        });
      } else {
        movieSelect.innerHTML = '<option value="">Nenhum filme encontrado na pasta FILME/</option>';
      }
    })
    .catch(err => {
      console.error("Erro ao listar filmes:", err);
      movieSelect.innerHTML = '<option value="">Erro ao carregar filmes</option>';
    });

  // Aspect Ratio change
  aspectRadios.forEach(radio => {
    radio.addEventListener("change", (e) => {
      const val = e.target.value;
      playerFormatTag.innerText = val === "1:1" ? "1:1 Quadrado" : "9:16 Vertical";
      const container = masterVideo.parentElement;
      if (val === "1:1") {
        container.style.aspectRatio = "1 / 1";
      } else {
        container.style.aspectRatio = "9 / 16";
      }
    });
  });

  // Antigravity AI Script button
  btnAiScript.addEventListener("click", async () => {
    btnAiScript.disabled = true;
    btnAiScript.innerHTML = '<span class="animate-spin mr-1">⏳</span> Conectando ao Antigravity...';

    const moviePath = movieSelect.value || "Palmer";
    const aspect = document.querySelector('input[name="aspect-ratio"]:checked').value;

    try {
      const res = await fetch("/api/antigravity/generate-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_title: moviePath,
          character: "Eddie Palmer",
          scene_description: "Confronto no bar em defesa do Sam",
          aspect_ratio: aspect,
          target_duration: 90
        })
      });
      const data = await res.json();
      btnAiScript.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i> Roteiro Atualizado';
      setTimeout(() => {
        btnAiScript.disabled = false;
        btnAiScript.innerHTML = '<i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-400"></i> Gerar com Antigravity';
        if (window.lucide) lucide.createIcons();
      }, 2000);
    } catch (err) {
      console.error(err);
      btnAiScript.disabled = false;
      btnAiScript.innerHTML = 'Erro na geração';
    }
  });

  // Render Trigger
  btnRender.addEventListener("click", async () => {
    const moviePath = movieSelect.value;
    const aspect = document.querySelector('input[name="aspect-ratio"]:checked').value;

    btnRender.disabled = true;
    btnRender.classList.add("opacity-50", "cursor-not-allowed");
    progressBar.style.width = "10%";
    progressPercent.innerText = "10%";
    progressStepText.innerText = "Disparando renderizador no background...";

    try {
      const res = await fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_path: moviePath,
          aspect_ratio: aspect,
          narrator_voice: "Eddie Palmer (Clonada)",
          screenplay_text: scriptInput.value
        })
      });
      const data = await res.json();
      const jobId = data.job_id;

      // Poll status
      const interval = setInterval(async () => {
        try {
          const sRes = await fetch(`/api/render/status/${jobId}`);
          const sData = await sRes.json();

          progressBar.style.width = `${sData.progress}%`;
          progressPercent.innerText = `${sData.progress}%`;
          progressStepText.innerText = sData.step;

          if (sData.status === "completed") {
            clearInterval(interval);
            btnRender.disabled = false;
            btnRender.classList.remove("opacity-50", "cursor-not-allowed");
            progressStepText.innerText = "Vídeo final renderizado e pronto para download/reprodução!";
            
            // Reload video player
            masterVideo.src = sData.output_url || "/static/output/palmer_1x1_resumo.mp4";
            masterVideo.load();
            masterVideo.play().catch(() => {});
          } else if (sData.status === "error") {
            clearInterval(interval);
            btnRender.disabled = false;
            btnRender.classList.remove("opacity-50", "cursor-not-allowed");
            progressStepText.innerText = sData.step;
          }
        } catch (e) {
          console.error("Erro no polling:", e);
        }
      }, 800);

    } catch (err) {
      console.error(err);
      btnRender.disabled = false;
      btnRender.classList.remove("opacity-50", "cursor-not-allowed");
      progressStepText.innerText = "Erro ao iniciar renderização.";
    }
  });
});
