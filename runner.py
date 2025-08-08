# runner.py

import subprocess
subprocess.run(["playwright", "install", "chromium"], check=True)

import argparse
import importlib
import sys
import os
from datetime import datetime
import traceback

def generate_filename(query, site):
    filename_safe = query.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%d%m%y_%H%M%S")
    return os.path.join("static", f"{filename_safe}_{site}_{date_str}.csv")

def run_scraper(site, query, output_file, limit=None):
    try:
        scraper_module = importlib.import_module(f"plugins.{site}")
    except ModuleNotFoundError:
        print(f"[ERROR] Scraper module not found for site: {site}")
        sys.exit(1)

    try:
        os.makedirs("static", exist_ok=True)
        output_file = os.path.abspath(output_file)
        print(f"\n[INFO] Running: {site} for '{query}' -> {output_file}")
        count = scraper_module.run_scraper(query, output_file, limit=limit)
        print(f"FOUND_COUNT: {count}")
    except Exception as e:
        print(f"[ERROR] Scraper failed: {e}")
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Modular Web Scraper")
    parser.add_argument("--mode", default="modular")
    parser.add_argument("--site", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--output", required=False)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    output_file = args.output or generate_filename(args.query, args.site)
    run_scraper(args.site, args.query, output_file, args.limit)

if __name__ == "__main__":
    main()











"""

# runner.py

import argparse
import importlib
import sys
import os
from datetime import datetime

def generate_filename(query, site):
    filename_safe = query.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%d%m%y")
    return os.path.join("static", f"{filename_safe}_{site}_{date_str}.csv")

def run_scraper(site, query, output_file):
    try:
        scraper_module = importlib.import_module(f"scrapers.{site}")
    except ModuleNotFoundError:
        print(f"Scraper module not found for site: {site}")
        sys.exit(1)

    try:
        print(f"\n🟢 Running: {site} for '{query}' -> {output_file}")
        scraper_module.run_scraper(query, output_file)
    except Exception as e:
        print(f"❌ Scraper failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Modular Web Scraper")
    parser.add_argument("--mode", default="modular")
    parser.add_argument("--site", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--output", required=False, help="Output CSV file name")
    args = parser.parse_args()

    output_file = args.output or generate_filename(args.query, args.site)
    run_scraper(args.site, args.query, output_file)

if __name__ == "__main__":
    main()

    
"""