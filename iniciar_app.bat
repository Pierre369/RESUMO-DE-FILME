@echo off
title CineShorts Studio - Motor de Resumo de Filmes
cd /d "%~dp0"

echo =======================================================
echo         CineShorts Studio - Painel Minimalista
echo     Alimentado por Google Antigravity & NVIDIA CUDA
echo =======================================================
echo.
echo Iniciando servidor FastAPI local...
echo Abrindo o navegador em http://localhost:8000 ...

start http://localhost:8000

"D:\Downloads\ANTIGRAVITY\clonar_voz\.venv_clone\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
