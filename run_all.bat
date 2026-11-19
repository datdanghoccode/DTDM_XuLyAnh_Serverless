@echo off
chcp 65001 > nul
title SERVERLESS IMAGE PROCESSING LAB - DE TAI 9 (UTH)

echo ===============================================================================
echo          SERVERLESS IMAGE PROCESSING LAB - HOC PHAN DIEN TOAN DAM MAY
echo                     DE TAI 9: EVENT-DRIVEN & COLD START
echo                       GVHD: TS. LE QUOC TUAN - UTH
echo ===============================================================================
echo.
echo [1/3] Kiem tra moi truong Python tren he thong...
python --version > nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python! Vui long cai dat Python 3.10+ va them vao PATH.
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] Kiem tra cac thu vien phu thuoc (Flask, Pillow)...
python -c "import flask, PIL" > nul 2>&1
if errorlevel 1 (
    echo [THONG BAO] Dang tu dong cai dat flask va pillow...
    pip install flask pillow
    if errorlevel 1 (
        echo [LOI] Khong the cai dat cac goi thu vien can thiet!
        pause
        exit /b 1
    )
) else (
    echo [OK] Cac thu vien Flask va Pillow da duoc cai dat day du!
)

echo.
echo [3/3] Khoi chay he thong 2 Web dong thoi (Web 1: 5001, Web 2: 5002)...
python run_project.py

pause
