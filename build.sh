#!/bin/bash
echo "Installing Playwright browser dependencies..."
pip install -r requirements.txt
playwright install chromium
