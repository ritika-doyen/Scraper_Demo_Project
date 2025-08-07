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

def run_scraper(query, output_file=None, limit=None):
    logger.info(f"Running IndiaMART scraper for: {query}")
    logger.info(f"Received limit: {limit}")

    search_url = build_search_url(query)
    logger.info(f"Opening URL: {search_url}")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ))
        page = context.new_page()
        page.goto(search_url, timeout=60000)

        try:
            logger.info("Waiting for cards to load...")
            page.wait_for_selector("div.card", timeout=30000)
            time.sleep(5)

            logger.info("Scrolling...")
            for _ in range(8):
                page.mouse.wheel(0, 2000)
                time.sleep(2)

            time.sleep(5)  # Allow JavaScript to finish

            # DEBUG: Save screenshot + HTML on server
            page.screenshot(path="static/debug_indiamart.png", full_page=True)
            with open("static/debug_indiamart.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.card")

            for card in cards:
                if limit and len(results) >= int(limit):
                    break

                name_tag = card.select_one("div.companyname a.cardlinks")
                address_tag = card.select_one("p.tac.wpw")
                phone_tag = card.select_one("span.pns_h")

                name = name_tag.get_text(strip=True) if name_tag else ""
                address = address_tag.get_text(strip=True) if address_tag else ""
                phone = phone_tag.get_text(strip=True) if phone_tag else ""

                if name or address or phone:
                    results.append({
                        "Name": name,
                        "Address": address,
                        "Phone": phone,
                    })

            logger.info(f"FOUND_COUNT: {len(results)}")
            browser.close()
            save_results(results, query, output_file)
            return len(results)

        except PlaywrightTimeoutError:
            logger.error("Timeout: No results found.")
            browser.close()
            save_results([], query, output_file)
            return 0


















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
