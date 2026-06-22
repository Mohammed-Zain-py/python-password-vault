@echo off
title Secure Password Vault

cd /d "C:\Users\mdzai\Desktop\My_projects\python-password-vault"

echo -----------------------------------
echo IGNITING SECURE VAULT ENVIRONMENT...
echo -----------------------------------

echo [1/2] Booting FastAPI Backend...
start /B "" "venv\Scripts\python.exe" -m uvicorn backend.main:app --port 8000

echo [2/2] Launching Streamlit Interface...
timeout /t 2 /nobreak > NUL
start "" "venv\Scripts\streamlit" run frontend\app.py

echo.
echo Vault is running! Keep this black window open while using the app.
echo To shut down the vault completely, just close this window.
pause > NUL