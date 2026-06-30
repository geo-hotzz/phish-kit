"""
PhishKit — Tunnel provider (ngrok / Cloudflare / LocalTunnel)
"""

import subprocess
import threading
import time
import requests
import json
import os
import re


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
        elif self.provider == "localtunnel":
            return self._start_localtunnel()
        return None

    def _start_ngrok(self):
        if self.auth_token:
            subprocess.run(["ngrok", "authtoken", self.auth_token], capture_output=True)
        
        # Start ngrok with host-header rewrite
        self.process = subprocess.Popen(
            ["ngrok", "http", str(self.local_port), "--host-header=rewrite", "--log=stdout"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        time.sleep(4)
        
        # Get public URL from ngrok API
        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            data = resp.json()
            tunnels = data.get("tunnels", [])
            if tunnels:
                self.public_url = tunnels[0]["public_url"]
        except Exception as e:
            print(f"[-] Failed to get ngrok URL: {e}")
        
        return self.public_url

    def _start_cloudflare(self):
        self.process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{self.local_port}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)
        # cloudflared prints URL to logs - we'll return a placeholder
        return f"http://localhost:{self.local_port} (via cloudflared)"

    def _start_localtunnel(self):
        self.process = subprocess.Popen(
            ["npx", "localtunnel", "--port", str(self.local_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(5)
        
        # LocalTunnel prints "your url is: https://xxxx.loca.lt" to stderr
        try:
            stdout_data = []
            stderr_data = []
            
            # Read available output
            for line in self.process.stderr:
                stderr_data.append(line)
                if "url is" in line.lower():
                    # Extract URL
                    match = re.search(r'https?://[^\s]+', line)
                    if match:
                        self.public_url = match.group(0)
                        break
                if len(stderr_data) > 20:
                    break
        except Exception as e:
            pass
        
        # If we didn't get it from stderr, try common localtunnel URL pattern
        if not self.public_url:
            # LocalTunnel typically uses a random subdomain on loca.lt
            # We can try to get it from the process output
            try:
                for line in self.process.stderr:
                    if "loca.lt" in line:
                        match = re.search(r'https?://[^\s]+loca\.lt[^\s]*', line)
                        if match:
                            self.public_url = match.group(0)
                            break
            except:
                pass
        
        if not self.public_url:
            self.public_url = f"http://localhost:{self.local_port} (via localtunnel - check terminal output)"
        
        return self.public_url

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except:
                self.process.kill()
            self.process = None

    def get_url(self):
        return self.public_url
