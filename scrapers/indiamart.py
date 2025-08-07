# indiamart.py

# indiamart.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import time
from datetime import datetime
from urllib.parse import quote_plus
from utils.logger import get_logger

logger = get_logger("indiamart")

logger.info("🛠 Custom indiamart.py loaded with enhanced stealth and scraping logic.")

def build_search_url(query):
    return f"https://dir.indiamart.com/search.mp?ss={quote_plus(query)}"

def extract_data(page, limit=None):
    cards = page.locator(".supplierInfoDiv").all()
    logger.info(f"Found {len(cards)} supplier cards")
    
    if limit:
        cards = cards[:limit]

    data = []
    for i, card in enumerate(cards):
        try:
            name = card.locator(".companyname a").inner_text().strip()
            location = card.locator(".newLocationUi span").inner_text().strip()
            phone = card.locator(".contactnumber span.pns_h").inner_text().strip()
            url = card.locator(".companyname a").get_attribute("href")
            data.append({
                "Name": name,
                "Location": location,
                "Phone": phone,
                "URL": url
            })
        except Exception as e:
            logger.warning(f"Error parsing card {i}: {e}")
            continue

    return data

def save_to_csv(data, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Location", "Phone", "URL"])
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Results saved to {file_path}")

def run_scraper(query, output_file=None, limit=None):
    logger.info(f"Running IndiaMART scraper for: {query}")
    logger.info(f"Received limit: {limit}")

    search_url = build_search_url(query)

    if not output_file:
        date_str = datetime.now().strftime("%d%m%y")
        output_file = f"{query.replace(' ', '_')}_indiamart_{date_str}.csv"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        logger.info(f"Opening URL: {search_url}")
        page.goto(search_url, timeout=60000)

        try:
            logger.info("Waiting for supplier cards to load...")
            page.wait_for_selector(".supplierInfoDiv", timeout=20000)
        except PlaywrightTimeoutError:
            logger.warning("Timeout: supplierInfoDiv not found.")
            save_to_csv([], output_file)
            return 0

        # Give extra time for JS to load more cards
        time.sleep(3)

        results = extract_data(page, limit=limit)
        if not results:
            logger.warning("No data scraped from IndiaMART.")

        save_to_csv(results, output_file)
        browser.close()
        return len(results)



















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
