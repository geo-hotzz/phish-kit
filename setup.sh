#!/bin/bash

# PhishLab - Automated deployment

echo "[*] Checking for virtual environment..."
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[*] Activating venv and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt -q

echo "[*] Starting PhishLab..."
python3 phishkit.py "$@"