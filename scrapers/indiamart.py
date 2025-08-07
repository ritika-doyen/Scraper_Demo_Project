## indiamart.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import os
import time
from datetime import datetime
from urllib.parse import quote_plus
from utils.logger import get_logger

logger = get_logger("indiamart")

def build_search_url(query, page=1):
    return f"https://dir.indiamart.com/search.mp?ss={quote_plus(query)}&page={page}"

def extract_data_from_page(page):
    data = []
    cards = page.query_selector_all(".supplierInfoDiv")
    logger.info(f"Found {len(cards)} cards on the current page.")
    for card in cards:
        try:
            company = card.query_selector(".companyname a")
            city = card.query_selector(".newLocationUi span.highlight")
            phone = card.query_selector(".pns_h, .contactnumber .duet")
            product = card.query_selector(".pnm, .prod_name, .product-name")
            supplier = card.query_selector(".cmp-contact span")

            data.append({
                "Company Name": company.inner_text().strip() if company else "",
                "Location": city.inner_text().strip() if city else "",
                "Phone": phone.inner_text().strip() if phone else "",
                "Product Name": product.inner_text().strip() if product else "",
                "Supplier": supplier.inner_text().strip() if supplier else "",
            })
        except Exception as e:
            logger.warning(f"Error extracting card: {e}")
    return data

def save_to_csv(data, file_path):
    if not data:
        logger.warning("No data to save.")
        return
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Saved {len(data)} records to {file_path}")

def run_scraper(query, output_file=None, limit=None):
    logger.info(f"Running IndiaMART scraper for: {query}")
    logger.info(f"Received limit: {limit}")
    total_data = []
    page_num = 1

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context()
            page = context.new_page()

            while True:
                url = build_search_url(query, page_num)
                logger.info(f"Opening URL: {url}")
                page.goto(url, timeout=60000)
                time.sleep(4)

                page_data = extract_data_from_page(page)
                if not page_data:
                    logger.info("No more data found on this page. Stopping.")
                    break

                total_data.extend(page_data)

                if limit and len(total_data) >= limit:
                    total_data = total_data[:limit]
                    break

                # IndiaMART usually limits results to 20 pages
                page_num += 1
                if page_num > 20:
                    logger.info("Reached maximum page limit.")
                    break

            if output_file:
                save_to_csv(total_data, output_file)

            browser.close()
            logger.info(f"Scraping completed with {len(total_data)} results.")
            print(f"FOUND_COUNT: {len(total_data)}")
            return len(total_data)

        except PlaywrightTimeoutError:
            logger.error("Timeout while loading IndiaMART.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

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
