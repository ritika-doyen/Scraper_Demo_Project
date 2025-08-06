## Modular Web Scraper with Flask UI
This project provides a simple web interface to scrape business listings from platforms like Google Maps and IndiaMART, with support for custom queries, record limits, and CSV download.


## Features

1. Scrape business listings using keywords
2. Supports Google Maps and IndiaMART
3. Set custom record limit (e.g., "50 hospitals in Delhi")
4. UI to display and download scraped results
5. Auto-detects if fewer records are available than requested
6. Built using Playwright, BeautifulSoup, and Flask


## Tech Stack

Backend: Python, Playwright, BeautifulSoup
Frontend: HTML, Flask
Logging: Custom logger for debug visibility


## Installation

1. Clone the repo:
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
2. Install dependencies:
    pip install -r requirements.txt
3. Install Playwright browsers:
    playwright install


## Running the Project

1. Start the Flask app:
    python app.py
2. Open your browser:
    http://127.0.0.1:5000/


## Usage

1. Enter a search query like 10 hospitals in delhi
2. Choose a source (Google Maps or IndiaMART)
3. Enter a limit (e.g., 50)
4. Click Scrape
5. View results in table and download CSV


##  Project Structure

scraper_project/
├── app.py                 # Flask app (UI & logic)
├── runner.py              # CLI/bridge for modular scrapers
├── scrapers/
│   ├── google_maps.py     # Google Maps scraper
│   ├── indiamart.py       # IndiaMART scraper
│   └── utils/
│       └── logger.py      # Logger utility
├── templates/
│   └── index.html         # HTML UI
├── static/                # CSV output files
├── requirements.txt       # Dependencies
└── README.md              # Project docs


## Requirements

- requests
- beautifulsoup4
- pandas
- playwright
- pandas
- streamlit
- flask


## Notes

1. Google Maps results are limited by how many listings are actually shown (via scroll).
2. IndiaMART data may vary depending on suppliers’ visibility.
3. If fewer results are found than requested, the UI will notify you.




