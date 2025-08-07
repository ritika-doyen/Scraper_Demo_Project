# indiamart.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote_plus
from datetime import datetime
import time
import csv
import os
from utils.logger import get_logger

logger = get_logger("indiamart")

logger.info("🛠 Custom indiamart.py loaded.")

def build_search_url(query):
    return f"https://dir.indiamart.com/search.mp?ss={quote_plus(query)}"

def auto_scroll(page, scroll_pause=2, scroll_count=10, limit=None):
    logger.info("Scrolling through the page...")
    for i in range(scroll_count):
        logger.info(f"Scroll iteration: {i+1}")
        page.mouse.wheel(0, 10000)
        time.sleep(scroll_pause)

        current_cards = len(page.locator(".prd-listing").all())
        logger.info(f"Listings visible: {current_cards}")
        if limit and current_cards >= limit:
            logger.info(f"Stopping scroll early at {current_cards} listings.")
            break

def extract_data(page, limit=None):
    logger.info("Extracting data from IndiaMART cards...")
    cards = page.locator(".prd-listing").all()
    logger.info(f"Found {len(cards)} cards")

    if limit:
        cards = cards[:limit]

    data = []
    for i, card in enumerate(cards):
        try:
            name = card.locator("h2").inner_text().strip()
        except:
            name = "N/A"

        try:
            location = card.locator(".cmp-loc").inner_text().strip()
        except:
            location = "N/A"

        try:
            url = card.locator("a").first.get_attribute("href")
            if url and not url.startswith("http"):
                url = "https://indiamart.com" + url
        except:
            url = "N/A"

        data.append({
            "Name": name,
            "Location": location,
            "Profile URL": url or "N/A"
        })

    logger.info(f"Extracted {len(data)} records.")
    return data

def save_to_csv(data, output_file):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Location", "Profile URL"])
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"✅ Saved {len(data)} records to {output_file}")

def run_scraper(query, output_file=None, limit=None):
    logger.info(f"Running IndiaMART scraper for: {query}")
    logger.info(f"Received limit: {limit}")

    search_url = build_search_url(query)

    if not output_file:
        date_str = datetime.now().strftime("%d%m%y")
        filename_safe = query.lower().replace(" ", "_")
        output_file = f"static/{filename_safe}_indiamart_{date_str}.csv"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        logger.info(f"Opening URL: {search_url}")
        page.goto(search_url, timeout=60000)

        try:
            logger.info("Waiting for cards to appear...")
            page.wait_for_selector(".prd-listing", timeout=20000)
        except PlaywrightTimeoutError:
            logger.error("Timeout: Could not find listings.")
            save_to_csv([], output_file)
            print("FOUND_COUNT: 0")
            return 0

        auto_scroll(page, scroll_count=12, scroll_pause=2, limit=limit)
        data = extract_data(page, limit=limit)
        save_to_csv(data, output_file)
        print(f"FOUND_COUNT: {len(data)}")
        browser.close()
        return len(data)






















"""

# indiamart.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
from urllib.parse import quote_plus
from utils.logger import get_logger

logger = get_logger("indiamart")

def build_search_url(query):
    return f"https://dir.indiamart.com/search.mp?ss={quote_plus(query)}"

def save_results(results, query, output_file):
    if not output_file:
        date = datetime.now().strftime("%d%m%y")
        file_name = f"static/{query.replace(' ', '_')}_indiamart_{date}.csv"
    else:
        file_name = output_file

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(file_name, index=False)
    logger.info(f"IndiaMART results saved to {file_name}")

def run_scraper(query: str, output_file: str = None):
    logger.info(f"Running IndiaMART scraper for: {query}")
    search_url = build_search_url(query)
    logger.info(f"Opening URL: {search_url}")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # ✅ Headless for Flask UI
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ))

        page = context.new_page()
        page.goto(search_url, timeout=60000)

        try:
            logger.info("Waiting 5 seconds before checking for results...")
            time.sleep(5)

            # ✅ Try waiting for either of the known selectors
            page.wait_for_selector("div.prd-card, div.supplierInfoDiv", timeout=25000)
        except PlaywrightTimeoutError:
            logger.error("⏱ Timeout: No IndiaMART results.")
            browser.close()
            save_results([], query, output_file)
            return

        # ✅ Scroll to load more
        for _ in range(10):
            page.mouse.wheel(0, 2000)
            time.sleep(2)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.supplierInfoDiv")  # ✅ more consistent selector

        for card in cards:
            name = card.select_one("a.cardlinks")
            address = card.select_one("p.wpw")
            phone = card.select_one("span.pns_h")
            supplier = name
            price = card.select_one(".price")

            results.append({
                "Name": name.text.strip() if name else "",
                "Supplier": supplier.text.strip() if supplier else "",
                "Phone": phone.text.strip() if phone else "",
                "Address": address.text.strip() if address else "",
                "Price": price.text.strip() if price else "",
            })

        logger.info(f"✅ Scraped {len(results)} results.")
        browser.close()
        save_results(results, query, output_file)

"""
