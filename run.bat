@echo off
title FashionPulse AI
echo.
echo ============================================================
echo   FASHIONPULSE AI ^| Women's Fashion Analytics
echo   Project by: S.K. Shrivastav ^| Sure Trust Data Analytics
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version

echo.
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt --quiet --no-warn-script-location
echo Dependencies ready!

echo.
echo [3/4] Checking ML models...
if not exist "models\sales_model.pkl" (
    echo.
    echo *** ML MODELS NOT FOUND ***
    echo To enable AI Prediction features, run in order:
    echo.
    echo   Step A: Copy women_clothing_50k.csv to the "data\" folder
    echo   Step B: python setup_database.py
    echo   Step C: python train_models.py
    echo.
    echo The dashboard will start without AI features for now.
) else (
    echo Models found! AI Prediction features enabled.
)

if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "outputs" mkdir outputs

echo.
echo [4/4] Launching FashionPulse AI...
echo.
echo ============================================================
echo   Open your browser:   http://localhost:5000
echo   Press Ctrl+C to stop the server
echo ============================================================
echo.

python app.py

pause
