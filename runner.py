
"""

# runner.py

import argparse
import importlib
import sys

def run_scraper(site, query, output_file):
    print(f"Running: {site} for '{query}' -> {output_file}")
    try:
        scraper = importlib.import_module(f"scrapers.{site}")
        scraper.run_scraper(query, output_file)
        print("✅ Scraper finished.")
    except Exception as e:
        print(f"Scraper failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="modular")
    parser.add_argument("--site", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run_scraper(args.site, args.query, args.output)

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
