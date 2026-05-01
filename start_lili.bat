@echo off
title Lili AI Startup

echo Starting Ollama server...
start /min cmd /c "ollama serve"

echo Waiting 5 seconds...
timeout /t 5 >nul

echo Loading Lili model (llama3.1:8b)...
start /min cmd /c "ollama run llama3.1:8b"

echo Waiting 10 seconds for model to load...
timeout /t 10 >nul

echo Starting Lili Backend server...
cd /d D:\lpu\sem 04\lili\backend
start cmd /k "python -m uvicorn app:app --reload --port 8000"

echo.
echo =======================================
echo DONE! Ab browser khol lo
echo http://127.0.0.1:8000/ ya http://localhost:8000/
echo =======================================
echo.
pause