@echo off
title PulseBI Studio ? Autonomous BI Engine (Offline & Online)
cd /d "%~dp0"
echo ===================================================
echo   Launching PulseBI Studio (Hybrid Offline/Online)
echo ===================================================
call .venv\Scripts\activate.bat
streamlit run app.py --browser.gatherUsageStats=false
pause
