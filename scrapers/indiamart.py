## indiamart.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import os
import time
from urllib.parse import quote_plus
from utils.logger import get_logger

logger = get_logger("indiamart")

def build_search_url(query):
    return f"https://dir.indiamart.com/search.mp?ss={quote_plus(query)}"

def scroll_until_end(page, expected_cards=None, max_scrolls=50):
    logger.info("Starting auto-scroll to load all results...")
    last_height = 0
    total_cards_loaded = 0

    for i in range(max_scrolls):
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(1)  # Reduced from 2s to 1s

        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            logger.info(f"No more content loaded after {i+1} scrolls.")
            break
        last_height = new_height

        total_cards_loaded = len(page.query_selector_all(".supplierInfoDiv"))
        if expected_cards and total_cards_loaded >= expected_cards:
            logger.info(f"Loaded enough cards ({total_cards_loaded}) early at scroll {i+1}")
            break
        elif not expected_cards and total_cards_loaded >= 100:
            logger.info(f"Auto-scroll exited early at {total_cards_loaded} cards (default max reached).")
            break

    logger.info("Auto-scroll completed.")

def extract_data_from_page(page):
    try:
        cards = page.query_selector_all(".supplierInfoDiv")
        logger.info(f"Found {len(cards)} cards on current scroll.")

        companies = page.locator(".supplierInfoDiv .companyname a").all_inner_texts()
        locations = page.locator(".supplierInfoDiv .newLocationUi span.highlight").all_inner_texts()
        phones = page.locator(".supplierInfoDiv .pns_h, .supplierInfoDiv .contactnumber .duet").all_inner_texts()
        urls = page.locator(".supplierInfoDiv .companyname a").evaluate_all("els => els.map(el => el.href)")

        max_len = max(len(companies), len(locations), len(phones), len(urls))
        data = []

        for i in range(max_len):
            data.append({
                "Company Name": companies[i] if i < len(companies) else "",
                "Location": locations[i] if i < len(locations) else "",
                "Phone": phones[i] if i < len(phones) else "",
                "URL": urls[i] if i < len(urls) else ""
            })

        return data
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        return []

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
    url = build_search_url(query)
    logger.info(f"Opening URL: {url}")

    all_data = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_selector(".supplierInfoDiv", timeout=15000)

            scroll_until_end(page, expected_cards=int(limit) if limit else None)
            all_data = extract_data_from_page(page)

            if limit:
                all_data = all_data[:int(limit)]

            if output_file:
                save_to_csv(all_data, output_file)

            browser.close()
            logger.info(f"Scraping completed with {len(all_data)} results.")
            print(f"FOUND_COUNT: {len(all_data)}")
            return len(all_data)

        except PlaywrightTimeoutError:
            logger.error("Timeout while loading IndiaMART.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        return 0









"""
# indiamart.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import os
import time
from urllib.parse import quote_plus
from utils.logger import get_logger

logger = get_logger("indiamart")

def build_search_url(query):
    return f"https://dir.indiamart.com/search.mp?ss={quote_plus(query)}"

def scroll_until_end(page, max_scrolls=50):
    logger.info("Starting auto-scroll to load all results...")
    last_height = 0
    for i in range(max_scrolls):
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(2)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            logger.info(f"No more content loaded after {i+1} scrolls.")
            break
        last_height = new_height
    logger.info("Auto-scroll completed.")

def extract_data_from_page(page):
    data = []
    try:
        cards = page.query_selector_all(".supplierInfoDiv")
        logger.info(f"Found {len(cards)} cards on current scroll.")

        for card in cards:
            company_name = card.query_selector(".companyname a")
            location = card.query_selector(".newLocationUi span.highlight")
            phone_elem = card.query_selector(".pns_h, .contactnumber .duet")
            link = card.query_selector(".companyname a")

            company = company_name.inner_text().strip() if company_name else ""
            city = location.inner_text().strip() if location else ""
            phone = phone_elem.inner_text().strip() if phone_elem else ""
            url = link.get_attribute("href") if link else ""

            data.append({
                "Company Name": company,
                "Location": city,
                "Phone": phone,
                "URL": url
            })

    except Exception as e:
        logger.error(f"Error extracting data: {e}")
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
    url = build_search_url(query)
    logger.info(f"Opening URL: {url}")

    all_data = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_selector(".supplierInfoDiv", timeout=15000)

            scroll_until_end(page)

            all_data = extract_data_from_page(page)

            if limit:
                all_data = all_data[:int(limit)]

            if output_file:
                absolute_path = os.path.abspath(output_file)
                logger.info(f"Saving output to absolute path: {absolute_path}")
                save_to_csv(all_data, absolute_path)


            browser.close()
            logger.info(f"Scraping completed with {len(all_data)} results.")
            print(f"FOUND_COUNT: {len(all_data)}")
            return len(all_data)

        except PlaywrightTimeoutError:
            logger.error("Timeout while loading IndiaMART.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        return 0


"""
