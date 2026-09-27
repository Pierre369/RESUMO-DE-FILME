document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const tabBtnDashboard = document.getElementById("tab-btn-dashboard");
  const tabBtnProjects = document.getElementById("tab-btn-projects");
  const tabBtnStyles = document.getElementById("tab-btn-styles");
  const navBtnNewProject = document.getElementById("nav-btn-new-project");
  const headerPageTitle = document.getElementById("header-page-title");

  // Views
  const viewDashboard = document.getElementById("view-dashboard");
  const viewProjects = document.getElementById("view-projects");
  const viewStyles = document.getElementById("view-styles");
  const viewCreator = document.getElementById("view-creator");
  const btnCloseCreator = document.getElementById("btn-close-creator");

  // Dashboard elements
  const statTotalProjects = document.getElementById("stat-total-projects");
  const statCompletedProjects = document.getElementById("stat-completed-projects");
  const statTotalMinutes = document.getElementById("stat-total-minutes");
  const dashboardRecentProjects = document.getElementById("dashboard-recent-projects");
  const dashboardStylePreviews = document.getElementById("dashboard-style-previews");

  // Projects View elements
  const projectsGrid = document.getElementById("projects-grid");

  // Styles View elements
  const stylesGrid = document.getElementById("styles-grid");
  const btnOpenCreateStyleModal = document.getElementById("btn-open-create-style-modal");
  const createStyleModal = document.getElementById("create-style-modal");
  const btnCloseStyleModal = document.getElementById("btn-close-style-modal");
  const btnCancelCreateStyle = document.getElementById("btn-cancel-create-style");
  const btnSaveNewStyle = document.getElementById("btn-save-new-style");

  // Creator elements
  const creatorMovieSelect = document.getElementById("creator-movie-select");
  const creatorStyleSelect = document.getElementById("creator-style-select");
  const movieDropzone = document.getElementById("movie-dropzone");
  const movieFileInput = document.getElementById("movie-file-input");
  const movieUploadProgress = document.getElementById("movie-upload-progress");
  const uploadFilename = document.getElementById("upload-filename");
  const uploadPercent = document.getElementById("upload-percent");
  const uploadBar = document.getElementById("upload-bar");

  const btnTriggerSmartAuto = document.getElementById("btn-trigger-smart-auto");
  const btnTriggerGuidedMode = document.getElementById("btn-trigger-guided-mode");
  const guidedFlowContainer = document.getElementById("guided-flow-container");
  const charactersList = document.getElementById("characters-list");
  const impactScenesList = document.getElementById("impact-scenes-list");
  const customSceneInput = document.getElementById("custom-scene-input");
  const btnGenerateScreenplayGuided = document.getElementById("btn-generate-screenplay-guided");
  const screenplayReviewBox = document.getElementById("screenplay-review-box");
  const creatorScriptText = document.getElementById("creator-script-text");
  const btnRenderGuidedProject = document.getElementById("btn-render-guided-project");

  // Render Monitor elements
  const creatorRenderMonitor = document.getElementById("creator-render-monitor");
  const monitorProgressPercent = document.getElementById("monitor-progress-percent");
  const monitorProgressBar = document.getElementById("monitor-progress-bar");
  const monitorStepText = document.getElementById("monitor-step-text");
  const monitorPlayerBox = document.getElementById("monitor-player-box");
  const monitorFormatBadge = document.getElementById("monitor-format-badge");
  const monitorVideoContainer = document.getElementById("monitor-video-container");
  const monitorVideo = document.getElementById("monitor-video");
  const btnDownloadVideo = document.getElementById("btn-download-video");

  // Video Modal
  const videoModal = document.getElementById("video-modal");
  const btnCloseModal = document.getElementById("btn-close-modal");
  const modalVideoPlayer = document.getElementById("modal-video-player");
  const modalVideoTitle = document.getElementById("modal-video-title");
  const modalVideoInfo = document.getElementById("modal-video-info");
  const modalDownloadLink = document.getElementById("modal-download-link");
  const modalVideoBox = document.getElementById("modal-video-box");

  // Settings & Voice Cloning elements
  const btnOpenSettingsModal = document.getElementById("btn-open-settings-modal");
  const settingsModal = document.getElementById("settings-modal");
  const btnCloseSettingsModal = document.getElementById("btn-close-settings-modal");
  const inputOpenrouterKey = document.getElementById("input-openrouter-key");
  const btnTestOpenrouterKey = document.getElementById("btn-test-openrouter-key");
  const btnSaveOpenrouterKey = document.getElementById("btn-save-openrouter-key");
  const settingsKeyFeedback = document.getElementById("settings-key-feedback");
  const voiceStatusDot = document.getElementById("voice-status-dot");
  const voiceStatusText = document.getElementById("voice-status-text");

  // State
  let currentCharacters = [];
  let selectedCharacter = null;
  let currentImpactScenes = [];
  let selectedScene = null;
  let allMovies = [];
  let allStyles = [];

  // ========================================================
  // ROUTING & VIEW SWITCHING
  // ========================================================
  function switchView(viewName, title) {
    [viewDashboard, viewProjects, viewStyles, viewCreator].forEach(v => v.classList.remove("active"));
    [tabBtnDashboard, tabBtnProjects, tabBtnStyles].forEach(b => {
      b.classList.remove("active", "bg-matte-850", "border", "border-matte-800", "text-white", "font-semibold");
      b.classList.add("text-zinc-400");
    });

    headerPageTitle.innerText = title;

    if (viewName === "dashboard") {
      viewDashboard.classList.add("active");
      tabBtnDashboard.classList.add("active", "bg-matte-850", "border", "border-matte-800", "text-white", "font-semibold");
      tabBtnDashboard.classList.remove("text-zinc-400");
      loadDashboard();
    } else if (viewName === "projects") {
      viewProjects.classList.add("active");
      tabBtnProjects.classList.add("active", "bg-matte-850", "border", "border-matte-800", "text-white", "font-semibold");
      tabBtnProjects.classList.remove("text-zinc-400");
      loadProjects();
    } else if (viewName === "styles") {
      viewStyles.classList.add("active");
      tabBtnStyles.classList.add("active", "bg-matte-850", "border", "border-matte-800", "text-white", "font-semibold");
      tabBtnStyles.classList.remove("text-zinc-400");
      loadStyles();
    } else if (viewName === "creator") {
      viewCreator.classList.add("active");
      resetCreatorUI();
      loadCreatorDropdowns();
    }

    if (window.lucide) lucide.createIcons();
  }

  tabBtnDashboard.addEventListener("click", () => switchView("dashboard", "Dashboard"));
  tabBtnProjects.addEventListener("click", () => switchView("projects", "Biblioteca de Projetos"));
  tabBtnStyles.addEventListener("click", () => switchView("styles", "Modelos de Estilo"));
  navBtnNewProject.addEventListener("click", () => switchView("creator", "Novo Projeto"));
  btnCloseCreator.addEventListener("click", () => switchView("dashboard", "Dashboard"));

  document.querySelectorAll(".nav-goto-projects").forEach(b => b.addEventListener("click", () => switchView("projects", "Biblioteca de Projetos")));
  document.querySelectorAll(".nav-goto-styles").forEach(b => b.addEventListener("click", () => switchView("styles", "Modelos de Estilo")));
  document.querySelectorAll(".btn-open-creator-smart").forEach(b => {
    b.addEventListener("click", () => {
      switchView("creator", "Novo Projeto (Modo Inteligente)");
    });
  });
  document.querySelectorAll(".btn-open-creator-guided").forEach(b => {
    b.addEventListener("click", () => {
      switchView("creator", "Novo Projeto (Modo Diretor Guiado)");
      setTimeout(() => {
        btnTriggerGuidedMode.click();
      }, 200);
    });
  });

  // ========================================================
  // DASHBOARD DATA
  // ========================================================
  async function loadDashboard() {
    try {
      const sRes = await fetch("/api/status");
      const sData = await sRes.json();
      if (sData.stats) {
        statTotalProjects.innerText = sData.stats.total_projects;
        statCompletedProjects.innerText = sData.stats.completed_projects;
        statTotalMinutes.innerText = `${sData.stats.total_minutes_generated} min`;
      }
      if (sData.antigravity && sData.antigravity.user) {
        document.getElementById("sidebar-ag-user").innerText = sData.antigravity.user;
      }

      // Recent projects
      const pRes = await fetch("/api/projects");
      const pData = await pRes.json();
      renderRecentProjects(pData.projects.slice(0, 3));

      // Style previews
      const stRes = await fetch("/api/styles");
      const stData = await stRes.json();
      renderStylePreviews(stData.styles.slice(0, 4));

    } catch (e) {
      console.error("Erro ao carregar dashboard:", e);
    }
  }

  function renderRecentProjects(projects) {
    dashboardRecentProjects.innerHTML = "";
    if (!projects || projects.length === 0) {
      dashboardRecentProjects.innerHTML = `<div class="col-span-3 text-xs text-zinc-500 py-6 text-center">Nenhum projeto criado ainda.</div>`;
      return;
    }

    projects.forEach(p => {
      const card = document.createElement("div");
      card.className = "bg-matte-900 border border-matte-800 rounded-xl p-4 flex flex-col justify-between space-y-3 hover:border-zinc-700 transition";
      const aspectTag = p.aspect_ratio === "1:1" ? "1:1 (Quadrado)" : "9:16 (Vertical)";
      
      card.innerHTML = `
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono">${aspectTag}</span>
            <span class="text-[10px] text-zinc-500">${p.created_at}</span>
          </div>
          <h4 class="text-xs font-bold text-white leading-snug line-clamp-2">${p.title}</h4>
          <p class="text-[11px] text-zinc-400">Narrador: <span class="text-zinc-200">${p.character}</span></p>
        </div>
        <div class="pt-2 border-t border-matte-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[11px] text-emerald-400 flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Concluído (${p.cuts_count || 14} takes)
            </span>
            <button class="btn-play-project px-2.5 py-1 rounded bg-matte-850 hover:bg-zinc-800 text-xs font-medium text-white transition flex items-center gap-1.5"
              data-url="${p.output_url}" data-title="${p.title}" data-aspect="${p.aspect_ratio}">
              <i data-lucide="play" class="w-3 h-3 fill-white"></i> Assistir
            </button>
          </div>
          <button class="btn-reopen-project w-full py-1.5 px-2.5 rounded bg-matte-850 hover:bg-zinc-800 text-[10px] font-medium text-zinc-300 border border-matte-800 transition flex items-center justify-center gap-1"
            data-movie="${p.movie_title}" data-style="${p.style_id}" data-char="${p.character}" data-aspect="${p.aspect_ratio}" data-scene="${p.scene_name}">
            <i data-lucide="clapperboard" class="w-3 h-3 text-emerald-400"></i> Gerar Nova Cena no Estúdio
          </button>
        </div>
      `;
      dashboardRecentProjects.appendChild(card);
    });

    attachPlayEvents();
    attachReopenEvents();
    if (window.lucide) lucide.createIcons();
  }

  function renderStylePreviews(styles) {
    dashboardStylePreviews.innerHTML = "";
    styles.forEach(s => {
      const card = document.createElement("div");
      card.className = "bg-matte-900 border border-matte-800 rounded-xl p-4 flex flex-col justify-between space-y-2";
      card.innerHTML = `
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300 font-medium">${s.badge || 'Preset'}</span>
            <span class="text-[10px] font-mono text-emerald-400">${s.retention_score}</span>
          </div>
          <h4 class="text-xs font-bold text-white">${s.name}</h4>
          <p class="text-[11px] text-zinc-400 mt-1 line-clamp-2 leading-relaxed">${s.description}</p>
          <div class="mt-2 text-[10px] text-emerald-400 font-medium">🎯 Quando usar: <span class="text-zinc-300 font-normal">${s.use_case || 'Cenas de impacto'}</span></div>
        </div>
        <div class="pt-2 border-t border-matte-800 text-[10px] text-zinc-500">
          Cadência: <span class="text-zinc-300">${s.pacing}</span>
        </div>
      `;
      dashboardStylePreviews.appendChild(card);
    });
  }

  // ========================================================
  // PROJECTS LIBRARY
  // ========================================================
  async function loadProjects() {
    try {
      const res = await fetch("/api/projects");
      const data = await res.json();
      projectsGrid.innerHTML = "";

      if (!data.projects || data.projects.length === 0) {
        projectsGrid.innerHTML = `<div class="col-span-3 text-xs text-zinc-500 py-12 text-center">Nenhum projeto na biblioteca.</div>`;
        return;
      }

      data.projects.forEach(p => {
        const card = document.createElement("div");
        card.className = "bg-matte-900 border border-matte-800 rounded-xl overflow-hidden hover:border-zinc-700 transition flex flex-col justify-between";
        const aspectTag = p.aspect_ratio === "1:1" ? "1:1 Quadrado" : "9:16 Vertical";

        card.innerHTML = `
          <div class="p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono">${aspectTag}</span>
              <span class="text-[10px] text-zinc-500">${p.created_at}</span>
            </div>
            <div>
              <h3 class="text-xs font-bold text-white line-clamp-2">${p.title}</h3>
              <p class="text-[11px] text-zinc-400 mt-0.5">Filme: <span class="text-zinc-300">${p.movie_title}</span></p>
            </div>
            <div class="text-[11px] text-zinc-400 space-y-0.5 bg-matte-850 p-2.5 rounded-lg border border-matte-800">
              <div>Narrador: <span class="text-zinc-200 font-medium">${p.character}</span></div>
              <div>Estilo: <span class="text-zinc-200">${p.style_name || 'Confronto'}</span></div>
              <div>Modo: <span class="text-zinc-200">${p.mode || 'Diretor'}</span></div>
            </div>
          </div>
          <div class="px-4 pb-2">
            <button class="btn-reopen-project w-full py-2 px-3 rounded-lg bg-matte-850 hover:bg-zinc-800 border border-matte-800 hover:border-zinc-600 text-xs font-medium text-zinc-200 transition flex items-center justify-center gap-1.5"
              data-movie="${p.movie_title}" data-style="${p.style_id}" data-char="${p.character}" data-aspect="${p.aspect_ratio}" data-scene="${p.scene_name}">
              <i data-lucide="clapperboard" class="w-3.5 h-3.5 text-emerald-400"></i>
              <span>Gerar Nova Cena / Reabrir no Estúdio</span>
            </button>
          </div>
          <div class="p-4 pt-0 flex gap-2">
            <button class="btn-play-project flex-1 py-2 px-3 rounded-lg bg-white text-black font-semibold text-xs hover:bg-zinc-200 transition flex items-center justify-center gap-1.5"
              data-url="${p.output_url}" data-title="${p.title}" data-aspect="${p.aspect_ratio}">
              <i data-lucide="play" class="w-3 h-3 fill-black"></i> Assistir
            </button>
            <a href="${p.output_url}" download class="py-2 px-3 rounded-lg bg-matte-850 border border-matte-800 hover:border-zinc-600 text-xs text-white transition flex items-center justify-center">
              <i data-lucide="download" class="w-3.5 h-3.5"></i>
            </a>
            <button class="btn-delete-project py-2 px-3 rounded-lg bg-matte-850 border border-matte-800 hover:border-red-800 text-xs text-zinc-400 hover:text-red-400 transition"
              data-id="${p.id}">
              <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        `;
        projectsGrid.appendChild(card);
      });

      attachPlayEvents();
      attachDeleteEvents();
      attachReopenEvents();
      if (window.lucide) lucide.createIcons();
    } catch (e) {
      console.error(e);
    }
  }

  function attachPlayEvents() {
    document.querySelectorAll(".btn-play-project").forEach(b => {
      b.onclick = (e) => {
        const btn = e.currentTarget;
        const rawUrl = btn.getAttribute("data-url");
        const url = rawUrl ? (rawUrl.includes("?t=") ? rawUrl : `${rawUrl}?t=${Date.now()}`) : "";
        const title = btn.getAttribute("data-title");
        const aspect = btn.getAttribute("data-aspect") || "1:1";

        modalVideoTitle.innerText = title;
        modalVideoPlayer.src = url;
        modalDownloadLink.href = rawUrl;
        modalVideoInfo.innerText = aspect === "1:1" ? "1080x1080 (1:1 Quadrado) • Áudio Híbrido" : "1080x1920 (9:16 Vertical) • Áudio Híbrido";

        if (aspect === "1:1") {
          modalVideoBox.style.aspectRatio = "1 / 1";
          modalVideoBox.style.maxHeight = "500px";
        } else {
          modalVideoBox.style.aspectRatio = "9 / 16";
          modalVideoBox.style.maxHeight = "600px";
        }

        videoModal.classList.remove("hidden");
        modalVideoPlayer.play().catch(() => {});
        if (window.lucide) lucide.createIcons();
      };
    });
  }

  function attachDeleteEvents() {
    document.querySelectorAll(".btn-delete-project").forEach(b => {
      b.onclick = async (e) => {
        const id = e.currentTarget.getAttribute("data-id");
        if (confirm("Deseja realmente excluir este projeto?")) {
          try {
            await fetch(`/api/projects/${id}`, { method: "DELETE" });
            loadProjects();
          } catch (err) {
            console.error(err);
          }
        }
      };
    });
  }

  function attachReopenEvents() {
    document.querySelectorAll(".btn-reopen-project").forEach(b => {
      b.onclick = async (e) => {
        const btn = e.currentTarget;
        const movieTitle = btn.getAttribute("data-movie");
        const styleId = btn.getAttribute("data-style");
        const charName = btn.getAttribute("data-char");
        const aspect = btn.getAttribute("data-aspect") || "1:1";
        const sceneName = btn.getAttribute("data-scene");

        switchView("creator", `Estúdio: ${movieTitle}`);

        // 1. Seleciona o filme correspondente
        for (let i = 0; i < creatorMovieSelect.options.length; i++) {
          const opt = creatorMovieSelect.options[i];
          if (opt.dataset.filename === movieTitle || opt.value.includes(movieTitle)) {
            creatorMovieSelect.selectedIndex = i;
            break;
          }
        }

        // 2. Seleciona o modelo de estilo
        if (styleId) {
          creatorStyleSelect.value = styleId;
          const evt = new Event("change");
          creatorStyleSelect.dispatchEvent(evt);
        }

        // 3. Seleciona a proporção
        const radio = document.querySelector(`input[name="creator-aspect-ratio"][value="${aspect}"]`);
        if (radio) radio.checked = true;

        // 4. Carrega instantaneamente os personagens e cenas deste filme
        await autoLoadMovieScenes(movieTitle, charName, sceneName);
      };
    });
  }

  // Modal close
  btnCloseModal.onclick = () => {
    videoModal.classList.add("hidden");
    modalVideoPlayer.pause();
  };
  videoModal.onclick = (e) => {
    if (e.target === videoModal) {
      videoModal.classList.add("hidden");
      modalVideoPlayer.pause();
    }
  };

  // ========================================================
  // STYLES LIBRARY & CREATION
  // ========================================================
  async function loadStyles() {
    try {
      const res = await fetch("/api/styles");
      const data = await res.json();
      stylesGrid.innerHTML = "";
      allStyles = data.styles || [];

      allStyles.forEach(s => {
        const card = document.createElement("div");
        card.className = "bg-matte-900 border border-matte-800 rounded-xl p-5 space-y-3 flex flex-col justify-between";
        card.innerHTML = `
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-zinc-800 text-zinc-300 font-medium">${s.category}</span>
              <span class="text-xs font-mono text-emerald-400 font-semibold">${s.retention_score}</span>
            </div>
            <h3 class="text-sm font-bold text-white">${s.name}</h3>
            <p class="text-xs text-zinc-400 leading-relaxed">${s.description}</p>
            <div class="p-2.5 rounded-lg bg-matte-850/80 border border-matte-800 text-[11px] text-emerald-400 font-medium">
              🎯 <span class="text-zinc-200">Quando usar:</span> ${s.use_case || 'Cortes virais e micro-cenas'}
            </div>
          </div>
          <div class="pt-3 border-t border-matte-800 grid grid-cols-2 gap-2 text-[11px] text-zinc-400">
            <div>Cadência: <span class="text-zinc-200">${s.pacing}</span></div>
            <div>Gancho: <span class="text-zinc-200">${s.hook_style}</span></div>
          </div>
        `;
        stylesGrid.appendChild(card);
      });
      if (window.lucide) lucide.createIcons();
    } catch (e) {
      console.error(e);
    }
  }

  btnOpenCreateStyleModal.onclick = () => createStyleModal.classList.remove("hidden");
  btnCloseStyleModal.onclick = () => createStyleModal.classList.add("hidden");
  btnCancelCreateStyle.onclick = () => createStyleModal.classList.add("hidden");

  btnSaveNewStyle.onclick = async () => {
    const name = document.getElementById("new-style-name").value.trim();
    const cat = document.getElementById("new-style-cat").value.trim() || "Personalizado";
    const desc = document.getElementById("new-style-desc").value.trim();
    const file = document.getElementById("new-style-ref-file").files[0];

    if (!name || !desc) {
      alert("Por favor, preencha o nome e a descrição do modelo.");
      return;
    }

    try {
      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("style_name", name);
        formData.append("category", cat);
        formData.append("description", desc);
        await fetch("/api/upload/reference", { method: "POST", body: formData });
      } else {
        await fetch("/api/styles", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, category: cat, description: desc })
        });
      }
      createStyleModal.classList.add("hidden");
      document.getElementById("new-style-name").value = "";
      document.getElementById("new-style-desc").value = "";
      loadStyles();
    } catch (err) {
      console.error(err);
      alert("Erro ao salvar o modelo de estilo.");
    }
  };

  // ========================================================
  // CREATOR WORKFLOW (NOVO PROJETO)
  // ========================================================
  function resetCreatorUI() {
    screenplayReviewBox.classList.add("hidden");
    creatorRenderMonitor.classList.add("hidden");
    monitorPlayerBox.classList.add("hidden");
    customSceneInput.value = "";
  }

  async function loadCreatorDropdowns() {
    try {
      // Movies
      const mRes = await fetch("/api/movies");
      const mData = await mRes.json();
      allMovies = mData.movies || [];
      creatorMovieSelect.innerHTML = "";

      allMovies.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.path;
        opt.innerText = `${m.filename} (${m.duration_formatted} | ${m.size_mb} MB)`;
        opt.dataset.filename = m.filename;
        creatorMovieSelect.appendChild(opt);
      });

      // Styles
      const stRes = await fetch("/api/styles");
      const stData = await stRes.json();
      allStyles = stData.styles || [];
      creatorStyleSelect.innerHTML = "";

      allStyles.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.innerText = `${s.name} • [${s.category}]`;
        creatorStyleSelect.appendChild(opt);
      });

      function updateStyleInfoBox() {
        const selectedId = creatorStyleSelect.value;
        const curStyle = allStyles.find(s => s.id === selectedId) || allStyles[0];
        if (curStyle) {
          const nameEl = document.getElementById("infobox-style-name");
          const descEl = document.getElementById("infobox-style-desc");
          const useEl = document.getElementById("infobox-style-usecase");
          const paceEl = document.getElementById("infobox-style-pacing");
          if (nameEl) nameEl.innerText = curStyle.name;
          if (descEl) descEl.innerText = curStyle.description;
          if (useEl) useEl.innerText = curStyle.use_case || "Cortes dinâmicos de alta retenção";
          if (paceEl) paceEl.innerText = curStyle.pacing;
        }
      }

      creatorStyleSelect.onchange = updateStyleInfoBox;
      updateStyleInfoBox();

      // Carrega imediatamente as cenas e personagens do filme escolhido
      creatorMovieSelect.onchange = () => {
        const movieTitle = creatorMovieSelect.selectedOptions[0]?.dataset.filename || creatorMovieSelect.value;
        autoLoadMovieScenes(movieTitle);
      };

      const initialMovieTitle = creatorMovieSelect.selectedOptions[0]?.dataset.filename || allMovies[0]?.filename;
      if (initialMovieTitle) {
        autoLoadMovieScenes(initialMovieTitle);
      }

    } catch (e) {
      console.error(e);
    }
  }

  // Movie File Upload Handler
  movieFileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    movieUploadProgress.classList.remove("hidden");
    uploadFilename.innerText = `Enviando: ${file.name}`;
    uploadPercent.innerText = "0%";
    uploadBar.style.width = "0%";

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/upload/movie", true);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        uploadBar.style.width = `${percent}%`;
        uploadPercent.innerText = `${percent}%`;
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        const res = JSON.parse(xhr.responseText);
        uploadFilename.innerText = `Pronto: ${res.filename}`;
        uploadPercent.innerText = "100%";
        // Add to dropdown and select it
        const opt = document.createElement("option");
        opt.value = res.path;
        opt.innerText = `${res.filename} (${res.duration_formatted} | ${res.size_mb} MB)`;
        opt.dataset.filename = res.filename;
        opt.selected = true;
        creatorMovieSelect.appendChild(opt);
        setTimeout(() => movieUploadProgress.classList.add("hidden"), 3000);
        autoLoadMovieScenes(res.filename);
      } else {
        uploadFilename.innerText = "Erro ao enviar arquivo.";
      }
    };

    xhr.onerror = () => {
      uploadFilename.innerText = "Falha no envio.";
    };

    xhr.send(formData);
  });

  // --------------------------------------------------------
  // MODO INTELIGENTE (100% AUTOMÁTICO)
  // --------------------------------------------------------
  btnTriggerSmartAuto.addEventListener("click", async () => {
    const moviePath = creatorMovieSelect.value;
    const movieTitle = creatorMovieSelect.selectedOptions[0]?.dataset.filename || "Palmer";
    const styleId = creatorStyleSelect.value || "confronto_vinganca";
    const aspect = document.querySelector('input[name="creator-aspect-ratio"]:checked').value;

    btnTriggerSmartAuto.disabled = true;
    btnTriggerSmartAuto.innerHTML = `<span class="animate-spin mr-1">⏳</span> O Antigravity está analisando e gerando o projeto...`;

    try {
      const res = await fetch("/api/antigravity/smart-auto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_path: moviePath,
          movie_title: movieTitle,
          style_id: styleId,
          aspect_ratio: aspect,
          target_duration: 150,
          scene_id: selectedScene?.id || null,
          character: selectedCharacter || null
        })
      });

      const data = await res.json();
      btnTriggerSmartAuto.disabled = false;
      btnTriggerSmartAuto.innerHTML = `<i data-lucide="play" class="w-3.5 h-3.5 fill-black"></i> GERAR NO AUTOMÁTICO (2 A 3 MIN)`;
      if (window.lucide) lucide.createIcons();

      // Show Render Monitor
      startMonitoringRender(data.job_id, aspect, data.output_filename);

    } catch (err) {
      console.error(err);
      btnTriggerSmartAuto.disabled = false;
      btnTriggerSmartAuto.innerHTML = `Erro ao gerar`;
    }
  });

  // --------------------------------------------------------
  // MODO DIRETOR GUIADO
  // --------------------------------------------------------
  async function autoLoadMovieScenes(movieTitle, preselectedChar = null, preselectedSceneNameOrId = null) {
    try {
      // 1. Analisa filme e personagens
      const res = await fetch("/api/antigravity/analyze-movie", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ movie_title: movieTitle })
      });
      const data = await res.json();
      currentCharacters = data.characters || [];
      renderCharactersList(currentCharacters);

      if (preselectedChar) {
        selectedCharacter = preselectedChar;
      } else {
        const defaultChar = currentCharacters.find(c => c.recommended) || currentCharacters[0];
        selectedCharacter = defaultChar?.name || "Protagonista";
      }

      // Marca o radio do personagem selecionado
      document.querySelectorAll('input[name="guided-character"]').forEach(rad => {
        if (rad.value.toLowerCase().includes(selectedCharacter.toLowerCase()) || selectedCharacter.toLowerCase().includes(rad.value.toLowerCase())) {
          rad.checked = true;
        }
      });

      // 2. Busca cenas de impacto para esse personagem
      await fetchImpactScenes(movieTitle, selectedCharacter, preselectedSceneNameOrId);
      guidedFlowContainer.classList.remove("hidden");
    } catch (e) {
      console.error("Erro ao carregar cenas do filme:", e);
    }
  }

  btnTriggerGuidedMode.addEventListener("click", async () => {
    const movieTitle = creatorMovieSelect.selectedOptions[0]?.dataset.filename || "Palmer";
    btnTriggerGuidedMode.disabled = true;
    btnTriggerGuidedMode.innerHTML = `<span class="animate-spin mr-1">⏳</span> Antigravity analisando filme...`;

    try {
      await autoLoadMovieScenes(movieTitle);
      guidedFlowContainer.classList.remove("hidden");
      btnTriggerGuidedMode.disabled = false;
      btnTriggerGuidedMode.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i> Filme Analisado!`;
      setTimeout(() => {
        btnTriggerGuidedMode.innerHTML = `<i data-lucide="scan-search" class="w-3.5 h-3.5"></i> ANALISAR FILME & ESCOLHER CENA`;
        if (window.lucide) lucide.createIcons();
      }, 2500);

    } catch (err) {
      console.error(err);
      btnTriggerGuidedMode.disabled = false;
      btnTriggerGuidedMode.innerHTML = `Erro na análise`;
    }
  });

  function renderCharactersList(chars) {
    charactersList.innerHTML = "";
    chars.forEach((c, idx) => {
      const card = document.createElement("label");
      card.className = `p-3.5 border rounded-xl cursor-pointer transition flex items-start gap-3 bg-matte-850/60 hover:border-zinc-500 ${c.recommended ? 'border-white bg-matte-850' : 'border-matte-800'}`;
      card.innerHTML = `
        <input type="radio" name="guided-character" value="${c.name}" ${c.recommended ? 'checked' : ''} class="mt-1">
        <div class="space-y-1">
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-bold text-white">${c.name}</span>
            ${c.recommended ? '<span class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">Recomendado</span>' : ''}
          </div>
          <p class="text-[11px] text-zinc-400">${c.role}</p>
          <p class="text-[10px] text-zinc-500 italic">${c.tone}</p>
        </div>
      `;
      card.querySelector("input").addEventListener("change", () => {
        selectedCharacter = c.name;
        const movieTitle = creatorMovieSelect.selectedOptions[0]?.dataset.filename || "Palmer";
        fetchImpactScenes(movieTitle, selectedCharacter);
      });
      charactersList.appendChild(card);
    });
  }

  async function fetchImpactScenes(movieTitle, characterName, preselectedSceneNameOrId = null) {
    const styleId = creatorStyleSelect.value || "confronto_vinganca";
    try {
      const res = await fetch("/api/antigravity/impact-scenes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_title: movieTitle,
          character_name: characterName,
          style_id: styleId
        })
      });
      const data = await res.json();
      currentImpactScenes = data.scenes || [];
      renderImpactScenes(currentImpactScenes, preselectedSceneNameOrId);
    } catch (e) {
      console.error(e);
    }
  }

  function renderImpactScenes(scenes, preselectedSceneNameOrId = null) {
    impactScenesList.innerHTML = "";
    scenes.forEach((s, idx) => {
      let isChecked = false;
      if (preselectedSceneNameOrId) {
        const target = preselectedSceneNameOrId.toLowerCase();
        isChecked = s.id.toLowerCase() === target || s.title.toLowerCase().includes(target) || target.includes(s.title.toLowerCase());
      } else {
        isChecked = (idx === 0);
      }

      const card = document.createElement("label");
      card.className = `p-4 border rounded-xl cursor-pointer transition flex items-start gap-3 bg-matte-850/60 hover:border-zinc-500 ${isChecked ? 'border-white bg-matte-850' : 'border-matte-800'}`;
      card.innerHTML = `
        <input type="radio" name="guided-scene" value="${s.id}" ${isChecked ? 'checked' : ''} class="mt-1">
        <div class="space-y-1.5 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white">${s.title}</span>
            <span class="text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-emerald-400 font-mono">${s.badge}</span>
          </div>
          <p class="text-xs text-zinc-300 leading-relaxed">${s.summary}</p>
          <div class="text-[11px] text-zinc-400 flex items-center gap-1.5 pt-1">
            <i data-lucide="quote" class="w-3 h-3 text-zinc-500"></i>
            <span class="italic text-zinc-300">"${s.hook}"</span>
          </div>
        </div>
      `;
      if (isChecked) selectedScene = s;
      const selectThisScene = () => {
        selectedScene = s;
        const rad = card.querySelector("input");
        if (rad) rad.checked = true;
        document.querySelectorAll("#impact-scenes-list label").forEach(lbl => {
          lbl.classList.remove("border-white", "bg-matte-850");
          lbl.classList.add("border-matte-800");
        });
        card.classList.add("border-white", "bg-matte-850");
        card.classList.remove("border-matte-800");
      };
      card.addEventListener("click", selectThisScene);
      card.querySelector("input").addEventListener("change", selectThisScene);
      impactScenesList.appendChild(card);
    });
    if (window.lucide) lucide.createIcons();
  }

  // Generate Screenplay in Guided Mode
  btnGenerateScreenplayGuided.addEventListener("click", async () => {
    btnGenerateScreenplayGuided.disabled = true;
    btnGenerateScreenplayGuided.innerHTML = `<span class="animate-spin mr-1">⏳</span> O Antigravity está gerando o roteiro estruturado...`;

    const movieTitle = creatorMovieSelect.selectedOptions[0]?.dataset.filename || "Palmer";
    const customDesc = customSceneInput.value.trim();
    const sceneDesc = customDesc || selectedScene?.summary || selectedScene?.title || "Confronto de alto impacto";
    const styleId = creatorStyleSelect.value;
    const aspect = document.querySelector('input[name="creator-aspect-ratio"]:checked').value;

    try {
      const res = await fetch("/api/antigravity/generate-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_title: movieTitle,
          character: selectedCharacter || "Protagonista",
          scene_description: sceneDesc,
          aspect_ratio: aspect,
          target_duration: 150,
          style_id: styleId,
          scene_id: selectedScene?.id || null
        })
      });
      const data = await res.json();
      creatorScriptText.value = data.screenplay_text;
      screenplayReviewBox.classList.remove("hidden");

      btnGenerateScreenplayGuided.disabled = false;
      btnGenerateScreenplayGuided.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i> Roteiro Gerado com Sucesso!`;
      setTimeout(() => {
        btnGenerateScreenplayGuided.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-400"></i> Gerar Roteiro Estruturado com Antigravity`;
        if (window.lucide) lucide.createIcons();
      }, 2500);

    } catch (err) {
      console.error(err);
      btnGenerateScreenplayGuided.disabled = false;
      btnGenerateScreenplayGuided.innerHTML = `Erro ao gerar roteiro`;
    }
  });

  // Render Guided Project
  btnRenderGuidedProject.addEventListener("click", async () => {
    const moviePath = creatorMovieSelect.value;
    const movieTitle = creatorMovieSelect.selectedOptions[0]?.dataset.filename || "Palmer";
    const aspect = document.querySelector('input[name="creator-aspect-ratio"]:checked').value;
    const styleId = creatorStyleSelect.value;
    const styleName = creatorStyleSelect.selectedOptions[0]?.innerText.split(" (")[0] || "Confronto & Vingança";
    const sceneName = customSceneInput.value.trim() ? "Cena Personalizada" : (selectedScene?.title || "Confronto de Impacto");
    const sceneId = selectedScene?.id || "custom_scene";

    btnRenderGuidedProject.disabled = true;
    btnRenderGuidedProject.innerHTML = `<span class="animate-spin mr-1">⏳</span> Disparando renderizador...`;

    try {
      const res = await fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movie_path: moviePath,
          movie_title: movieTitle,
          character: selectedCharacter || "Protagonista",
          scene_id: sceneId,
          scene_name: sceneName,
          style_id: styleId,
          style_name: styleName,
          aspect_ratio: aspect,
          narrator_voice: `${selectedCharacter || 'Protagonista'} (Clonada)`,
          screenplay_text: creatorScriptText.value,
          mode: "Diretor Guiado"
        })
      });

      const data = await res.json();
      btnRenderGuidedProject.disabled = false;
      btnRenderGuidedProject.innerHTML = `<i data-lucide="play" class="w-4 h-4 fill-black"></i> RENDERIZAR VÍDEO MASTER COM ESSAS ESCOLHAS`;

      startMonitoringRender(data.job_id, aspect, data.output_filename);

    } catch (err) {
      console.error(err);
      btnRenderGuidedProject.disabled = false;
      btnRenderGuidedProject.innerHTML = `Erro ao disparar`;
    }
  });

  // --------------------------------------------------------
  // MONITORING & POLLING
  // --------------------------------------------------------
  function startMonitoringRender(jobId, aspect, outputFilename) {
    creatorRenderMonitor.classList.remove("hidden");
    creatorRenderMonitor.scrollIntoView({ behavior: "smooth" });

    monitorProgressBar.style.width = "5%";
    monitorProgressPercent.innerText = "5%";
    monitorStepText.innerText = "Iniciando motor de decupagem e renderização...";
    monitorPlayerBox.classList.add("hidden");

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/render/status/${jobId}`);
        const data = await res.json();

        monitorProgressBar.style.width = `${data.progress}%`;
        monitorProgressPercent.innerText = `${data.progress}%`;
        monitorStepText.innerText = data.step;

        if (data.status === "completed") {
          clearInterval(interval);
          monitorStepText.innerText = "Vídeo master gerado e finalizado com sucesso!";
          monitorPlayerBox.classList.remove("hidden");

          const rawUrl = data.output_url || (outputFilename ? `/static/output/${outputFilename}` : '');
          const videoUrl = rawUrl ? `${rawUrl}?t=${Date.now()}` : '';
          monitorVideo.src = videoUrl;
          btnDownloadVideo.href = rawUrl;

          monitorFormatBadge.innerText = aspect === "1:1" ? "1:1 Quadrado" : "9:16 Vertical";
          if (aspect === "1:1") {
            monitorVideoContainer.style.aspectRatio = "1 / 1";
          } else {
            monitorVideoContainer.style.aspectRatio = "9 / 16";
          }

          monitorVideo.load();
          monitorVideo.play().catch(() => {});
          loadProjects();
          loadDashboard();
        } else if (data.status === "error") {
          clearInterval(interval);
          monitorStepText.innerText = data.step;
        }
      } catch (e) {
        console.error("Erro no polling:", e);
      }
    }, 700);
  }

  // ========================================================
  // SETTINGS & OPENROUTER API KEY MANAGEMENT
  // ========================================================
  async function checkVoiceKeyStatus() {
    try {
      const res = await fetch("/api/settings/keys");
      const data = await res.json();
      if (data.has_key) {
        if (voiceStatusDot) {
          voiceStatusDot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
        }
        if (voiceStatusText) {
          voiceStatusText.innerText = `Ativo (${data.masked_key})`;
        }
      } else {
        if (voiceStatusDot) {
          voiceStatusDot.className = "w-2 h-2 rounded-full bg-amber-500";
        }
        if (voiceStatusText) {
          voiceStatusText.innerText = `Chave pendente (Edge Fallback)`;
        }
      }
    } catch (e) {
      console.error("Erro ao verificar status de voz:", e);
    }
  }

  if (btnOpenSettingsModal) {
    btnOpenSettingsModal.onclick = () => {
      settingsModal.classList.remove("hidden");
      settingsKeyFeedback.classList.add("hidden");
      if (window.lucide) lucide.createIcons();
    };
  }
  if (btnCloseSettingsModal) {
    btnCloseSettingsModal.onclick = () => {
      settingsModal.classList.add("hidden");
    };
  }
  if (settingsModal) {
    settingsModal.onclick = (e) => {
      if (e.target === settingsModal) settingsModal.classList.add("hidden");
    };
  }

  if (btnTestOpenrouterKey) {
    btnTestOpenrouterKey.onclick = async () => {
      const key = inputOpenrouterKey.value.trim();
      if (!key) {
        settingsKeyFeedback.className = "text-[11px] text-amber-400 p-2.5 rounded-lg bg-amber-950/40 border border-amber-800 leading-relaxed block";
        settingsKeyFeedback.innerText = "Por favor, digite a chave de API para testar.";
        return;
      }
      btnTestOpenrouterKey.disabled = true;
      btnTestOpenrouterKey.innerHTML = `<span class="animate-spin mr-1">⏳</span> Testando...`;
      try {
        const res = await fetch("/api/settings/test-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ openrouter_api_key: key })
        });
        const data = await res.json();
        btnTestOpenrouterKey.disabled = false;
        btnTestOpenrouterKey.innerHTML = `<i data-lucide="check-circle" class="w-3.5 h-3.5"></i> Testar Chave`;
        if (data.valid) {
          settingsKeyFeedback.className = "text-[11px] text-emerald-400 p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800 leading-relaxed block";
          settingsKeyFeedback.innerText = `✅ Chave Válida! Identificada como "${data.label}". Ativa para clonagem de voz sem delay via Fish Audio S2.1 Pro.`;
        } else {
          settingsKeyFeedback.className = "text-[11px] text-red-400 p-2.5 rounded-lg bg-red-950/40 border border-red-800 leading-relaxed block";
          settingsKeyFeedback.innerText = `❌ Falha ao validar chave: ${data.error || 'Não autorizada'}`;
        }
      } catch (e) {
        btnTestOpenrouterKey.disabled = false;
        btnTestOpenrouterKey.innerHTML = `<i data-lucide="check-circle" class="w-3.5 h-3.5"></i> Testar Chave`;
        settingsKeyFeedback.className = "text-[11px] text-red-400 p-2.5 rounded-lg bg-red-950/40 border border-red-800 leading-relaxed block";
        settingsKeyFeedback.innerText = `Erro de conexão: ${e.message}`;
      }
      if (window.lucide) lucide.createIcons();
    };
  }

  if (btnSaveOpenrouterKey) {
    btnSaveOpenrouterKey.onclick = async () => {
      const key = inputOpenrouterKey.value.trim();
      if (!key) {
        alert("Por favor, digite uma chave de API antes de salvar.");
        return;
      }
      btnSaveOpenrouterKey.disabled = true;
      btnSaveOpenrouterKey.innerHTML = `<span class="animate-spin mr-1">⏳</span> Salvando...`;
      try {
        const res = await fetch("/api/settings/keys", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ openrouter_api_key: key })
        });
        const data = await res.json();
        btnSaveOpenrouterKey.disabled = false;
        btnSaveOpenrouterKey.innerHTML = `<i data-lucide="save" class="w-3.5 h-3.5 fill-black"></i> Salvar Chave`;
        if (data.success) {
          settingsKeyFeedback.className = "text-[11px] text-emerald-400 p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800 leading-relaxed block";
          settingsKeyFeedback.innerText = `✅ Chave gravada com sucesso! Motor Fish Audio ativo (${data.masked_key}).`;
          checkVoiceKeyStatus();
          setTimeout(() => {
            settingsModal.classList.add("hidden");
          }, 1500);
        }
      } catch (e) {
        btnSaveOpenrouterKey.disabled = false;
        btnSaveOpenrouterKey.innerHTML = `<i data-lucide="save" class="w-3.5 h-3.5 fill-black"></i> Salvar Chave`;
        alert("Erro ao salvar chave: " + e.message);
      }
      if (window.lucide) lucide.createIcons();
    };
  }

  // Initial Load
  checkVoiceKeyStatus();
  switchView("dashboard", "Dashboard");
});
