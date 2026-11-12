@echo off
title Live Demo Pipeline Xu Ly Anh Serverless - De Tai 9 UTH
color 0b
echo ======================================================================
echo    KHOI DONG HE THONG DEMO PIPELINE XU LY ANH SERVERLESS - DE TAI 9
echo    Truong Dai hoc Giao thong Van tai TP.HCM (UTH)
echo    Giang vien huong dan: TS. Le Quoc Tuan
echo ======================================================================
echo.
echo [1/2] Dang khoi dong Web Server Flask tai cong 5000...
start "" http://localhost:5000
python demo_app.py
pause
