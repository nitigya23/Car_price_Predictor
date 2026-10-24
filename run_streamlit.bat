@echo off
title Ford Car Valuation AI - Streamlit
echo =======================================================
echo        FORD CAR VALUATION AI - STREAMLIT APP
echo =======================================================
echo Starting Streamlit on http://localhost:8501 ...
cd /d "%~dp0"
python -m streamlit run streamlit_app.py
pause

