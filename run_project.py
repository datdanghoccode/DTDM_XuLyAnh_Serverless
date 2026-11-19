# -*- coding: utf-8 -*-
"""
run_project.py
Master Launcher and Multi-Process Supervisor for Dual-Web Serverless Architecture:
- Web 1: Knowledge & Learning Hub (http://localhost:5001)
- Web 2: Interactive Live Lab (http://localhost:5002)

Author: Đề tài 9 - Điện toán đám mây (UTH)
GVHD: TS. Lê Quốc Tuấn
"""

import os
import sys
import time
import socket
import threading
import webbrowser
import logging

# Set working directory to project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Suppress verbose Flask request logs to keep terminal clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def check_port_available(port, host="127.0.0.1"):
    """Returns True if the port is free to bind, False if already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

def get_web1_app():
    """Instantiate Web 1 Knowledge Hub Flask application."""
    from web1_learning_hub.app import create_app
    return create_app()

def get_web2_app():
    """Instantiate Web 2 Live Lab Flask application."""
    from web2_live_lab.app import create_app
    return create_app()

def run_web1(app, host="0.0.0.0", port=5001):
    app.run(host=host, port=port, debug=False, use_reloader=False)

def run_web2(app, host="0.0.0.0", port=5002):
    app.run(host=host, port=port, debug=False, use_reloader=False)

BANNER = """
================================================================================
          SERVERLESS IMAGE PROCESSING LAB - HOC PHAN DIEN TOAN DAM MAY
                     DE TAI 9: EVENT-DRIVEN & COLD START
                       GVHD: TS. LE QUOC TUAN - UTH
================================================================================

 [WEB 1] KNOWLEDGE & LEARNING HUB (PORT 5001)
 URL: http://localhost:5001
 -------------------------------------------------------------------------------
 - Co so ly thuyet: FaaS, Event Source, At-least-once delivery, Cold/Warm Start
 - Thuat toan Khoa luy dang nguyen tu DynamoDB (ConditionExpression)
 - Mo hinh an toan thong tin chuan OWASP Serverless Top 10 (SAS-01 -> SAS-05)
 - Bo trinh dien Code tuong tac (Interactive Code Walkthrough)
 - Phan tich Dinh luong 100 runs, Diem ngot 512MB RAM & Uoc tinh chi phi
 - So tay van hanh SRE Runbook xu ly su co SQS DLQ Redrive

 [WEB 2] INTERACTIVE LIVE LAB WORKBENCH (PORT 5002)
 URL: http://localhost:5002
 -------------------------------------------------------------------------------
 - Visual Pipeline Canvas (Client -> S3 -> SQS -> Lambda -> DynamoDB & S3 Thumb)
 - Standard Ingestion: Tao Thumbnail 300x300, giam 89% kich thuoc, trich metadata
 - Duplicate Ingestion: Kiem chung khoa luy dang tra ve ngay trong < 2.5 ms
 - Poison Pill Ingestion: Co lap tap tin hong vao SQS DLQ sau 3 lan retry
 - Benchmark 100 runs: Bieu do histogram phan phoi do tre (p50, p90, p95, p99)
 - Real-time Telemetry Log Console & Modal SRE DLQ Inspect / Redrive

================================================================================
 Nhan [Ctrl + C] de dung toan bo may chu bat cu luc nao.
================================================================================
"""

def start_servers(open_browser=True):
    # Port checking
    web1_available = check_port_available(5001)
    web2_available = check_port_available(5002)

    if not web1_available:
        print("[CANH BAO] Cong 5001 dang bi chiem dung boi tien trinh khac!")
    if not web2_available:
        print("[CANH BAO] Cong 5002 dang bi chiem dung boi tien trinh khac!")

    web1_app = get_web1_app()
    web2_app = get_web2_app()

    t1 = threading.Thread(target=run_web1, args=(web1_app, "0.0.0.0", 5001), daemon=True)
    t2 = threading.Thread(target=run_web2, args=(web2_app, "0.0.0.0", 5002), daemon=True)

    t1.start()
    t2.start()

    print(BANNER)

    if open_browser:
        time.sleep(1.2)
        try:
            print("[AUTO-BROWSER] Dang tu dong mo trinh duyet Web 1 va Web 2...")
            webbrowser.open("http://localhost:5001")
            time.sleep(0.3)
            webbrowser.open("http://localhost:5002")
        except Exception as e:
            print(f"[AUTO-BROWSER] Khong the tu dong mo trinh duyet: {e}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[DUNG HE THONG] Da nhan tin hieu ngat. Dang dong cac may chu Flask...")
        sys.exit(0)

if __name__ == "__main__":
    start_servers(open_browser=True)
