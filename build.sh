#!/usr/bin/env bash
echo "Installing Playwright browser dependencies..."
pip install -r requirements.txt
playwright install chromium

echo "Installing Playwright browsers..."
playwright install --with-deps

