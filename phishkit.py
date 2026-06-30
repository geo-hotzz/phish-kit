#!/usr/bin/env python3
"""
PhishKit — Zphisher-style phishing simulation framework
Authorized pentesting use only.
"""

import os
import sys
import json
import signal
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

BANNER =rf"""
{Fore.RED}
  ____  _     _     _  _____ _ _ 
 |  _ \| |__ (_)___| |/ /_ _| | |
 | |_) | '_ \| / __| ' / | || | |
 |  __/| | | | \__ \ . \ | || | |
 |_|   |_| |_|_|___/_|\_\___|_|_|
{Fore.YELLOW}
  Phishing Simulation Framework v1.0
  Authorized Security Assessment Tool
{Style.RESET_ALL}
"""

TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"

def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def list_templates():
    templates = []
    if os.path.exists(TEMPLATES_DIR):
        templates = [d for d in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, d))]
    return templates

def print_templates(templates):
    print(f"\n{Fore.CYAN}Available templates:{Style.RESET_ALL}")
    for i, t in enumerate(templates, 1):
        print(f"  {Fore.GREEN}{i}.{Style.RESET_ALL} {t}")

def get_template_choice(templates):
    while True:
        try:
            choice = input(f"\n{Fore.YELLOW}Select template (1-{len(templates)}): {Style.RESET_ALL}").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(templates):
                return templates[int(choice) - 1]
            elif choice in templates:
                return choice
            else:
                print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")
        except (ValueError, IndexError):
            print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")

def print_campaign_info(template, port):
    print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Campaign started!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"  Template : {Fore.CYAN}{template}{Style.RESET_ALL}")
    print(f"  Local URL: {Fore.CYAN}http://0.0.0.0:{port}{Style.RESET_ALL}")
    print(f"  Capture  : {Fore.CYAN}{OUTPUT_DIR}/{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"  Press Ctrl+C to stop the server\n")

def signal_handler(sig, frame):
    print(f"\n{Fore.YELLOW}Shutting down PhishKit...{Style.RESET_ALL}")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="PhishKit - Phishing Simulation Framework")
    parser.add_argument("-c", "--config", default="config.json", help="Config file path")
    parser.add_argument("-t", "--template", help="Template name (skip menu)")
    parser.add_argument("-p", "--port", type=int, help="Port to run on")
    args = parser.parse_args()

    print(BANNER)

    # Load config
    config = load_config(args.config)
    port = args.port or config["server"]["port"]

    # Template selection
    templates = list_templates()
    if not templates:
        print(f"{Fore.RED}No templates found in '{TEMPLATES_DIR}/'.{Style.RESET_ALL}")
        sys.exit(1)

    if args.template:
        if args.template in templates:
            template = args.template
        else:
            print(f"{Fore.RED}Template '{args.template}' not found.{Style.RESET_ALL}")
            sys.exit(1)
    else:
        print_templates(templates)
        template = get_template_choice(templates)

    # Update config
    config["campaign"]["template"] = template
    config["server"]["port"] = port

    # Write back so server.py reads the right template
    with open(args.config, "w") as f:
        json.dump(config, f, indent=2)

    # Setup output
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Print campaign info
    print_campaign_info(template, port)

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Start server
    from modules.server import run_server
    run_server(config)

if __name__ == "__main__":
    main()
