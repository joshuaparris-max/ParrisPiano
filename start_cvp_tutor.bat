@echo off
setlocal
set ROOT=%~dp0
cd /d "%ROOT%"
echo [CVP Tutor] Preparing environment...

if exist ".venv\Scripts\python.exe" (
  set PY=".venv\Scripts\python.exe"
) else (
  echo [CVP Tutor] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo [CVP Tutor] Could not create venv. Make sure Python 3.11+ is on PATH.
    exit /b 1
  )
  set PY=".venv\Scripts\python.exe"
)

echo [CVP Tutor] Installing requirements (first run may take a minute)...
%PY% -m pip install --upgrade pip >nul
%PY% -m pip install -r cvp_tutor\requirements.txt >nul
if errorlevel 1 (
  echo [CVP Tutor] Failed to install dependencies.
  exit /b 1
)

echo [CVP Tutor] Launching app...
%PY% -m cvp_tutor.app
