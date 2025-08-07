# google_maps.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import csv
from datetime import datetime
from urllib.parse import quote_plus
from utils.logger import get_logger

logger = get_logger("google_maps")

logger.info("🚀 Optimized google_maps.py with performance improvements loaded.")

def build_search_url(query):
    return f"https://www.google.com/maps/search/{quote_plus(query)}"

def auto_scroll(page, scroll_container_selector, scroll_count=20, delay=1, limit=None):
    scroll_container = page.locator(scroll_container_selector).nth(1)
    logger.info("Starting scroll to load listings...")
    prev_count = 0

    for i in range(scroll_count):
        scroll_container.evaluate("el => el.scrollBy(0, el.scrollHeight)")
        time.sleep(delay)

        cards = page.locator("a.hfpxzc")
        current_count = cards.count()
        logger.info(f"Scroll {i+1}/{scroll_count} → {current_count} listings loaded.")

        # Early exit condition
        if limit and current_count >= limit:
            logger.info(f"Stopping scroll early at {current_count} listings.")
            break

        # Stop if no new listings loaded
        if current_count == prev_count:
            logger.info("No new listings loaded. Stopping scroll.")
            break
        prev_count = current_count

def extract_data(page, limit=None):
    cards = page.locator("a.hfpxzc")
    count = cards.count()
    logger.info(f"Total listings found: {count}")

    if limit:
        count = min(count, limit)

    names = cards.locator(":scope").evaluate_all("nodes => nodes.map(n => n.getAttribute('aria-label') || 'N/A')")
    urls = cards.locator(":scope").evaluate_all("nodes => nodes.map(n => n.getAttribute('href') || 'N/A')")

    data = [{"Name": names[i].strip(), "URL": urls[i].strip()} for i in range(count)]
    return data

def save_to_csv(data, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "URL"])
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Saved {len(data)} results to {file_path}")

def run_scraper(query, output_file=None, limit=None):
    logger.info(f"Running Google Maps scraper for: {query}")
    logger.info(f"Received limit: {limit}")

    search_url = build_search_url(query)

    if not output_file:
        date_str = datetime.now().strftime("%d%m%y")
        output_file = f"{query.replace(' ', '_')}_google_maps_{date_str}.csv"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        page.goto(search_url, timeout=60000)

        try:
            logger.info("Waiting for results to load...")
            page.locator("div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde").nth(1).wait_for(timeout=20000)
        except PlaywrightTimeoutError:
            logger.error("Timeout: Listing container not found.")
            save_to_csv([], output_file)
            return 0

        auto_scroll(page, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde", scroll_count=20, delay=1, limit=limit)
        results = extract_data(page, limit=limit)

        if not results:
            logger.warning("No data extracted.")

        save_to_csv(results, output_file)
        browser.close()

        print(f"FOUND_COUNT: {len(results)}")
        return len(results)











