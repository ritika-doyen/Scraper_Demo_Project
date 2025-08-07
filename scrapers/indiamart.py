# indiamart.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import os
from datetime import datetime

def scrape_indiamart_data(query, limit):
    url = f"https://dir.indiamart.com/search.mp?ss={query.replace(' ', '%20')}"

    output_folder = "static"
    os.makedirs(output_folder, exist_ok=True)

    date_str = datetime.now().strftime("%d%m%y")
    filename = f"speakers_indiamart_{date_str}.csv"
    filepath = os.path.join(output_folder, filename)

    scraped_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)  # wait for JavaScript to load results

            # Wait for the result cards to appear
            try:
                page.wait_for_selector(".card", timeout=10000)
            except PlaywrightTimeoutError:
                print("❌ .card selector not found. Possibly no results or bot-blocked.")

            # DEBUG: Save page HTML to inspect what's being loaded (especially on Render)
            with open(os.path.join(output_folder, "debug_rendered_page.html"), "w", encoding="utf-8") as f:
                f.write(page.content())

            cards = page.query_selector_all(".card")

            for card in cards:
                if len(scraped_data) >= limit:
                    break

                try:
                    name = card.query_selector("h2 a")
                    name_text = name.inner_text().strip() if name else ""

                    company = card.query_selector(".cmpny")
                    company_text = company.inner_text().strip() if company else ""

                    location = card.query_selector(".loc")
                    location_text = location.inner_text().strip() if location else ""

                    phone = card.query_selector(".contact-number")
                    phone_text = phone.inner_text().strip() if phone else ""

                    scraped_data.append({
                        "Name": name_text,
                        "Company": company_text,
                        "Location": location_text,
                        "Phone": phone_text,
                    })

                except Exception as e:
                    print("❌ Error parsing card:", e)

            browser.close()

        except Exception as e:
            print("❌ Error during scraping:", e)

    # Save to CSV
    if scraped_data:
        keys = scraped_data[0].keys()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(scraped_data)

    return {
        "filename": filename,
        "count": len(scraped_data),
        "limit": limit,
        "filepath": filepath
    }




















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
