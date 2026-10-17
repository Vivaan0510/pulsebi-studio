@echo off
title PulseBI Studio - Local Engine
cd /d "C:\Users\Vivaan Kesarwani\pulsebi-studio"
call "C:\Users\Vivaan Kesarwani\pulsebi-studio\.venv\Scripts\activate.bat"
echo Starting PulseBI Studio...
streamlit run app.py
pause
