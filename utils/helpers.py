import os
import re

def sanitize_filename(name):
    return re.sub(r'\W+', '_', name.lower()) + ".csv"

def ensure_data_dir():
    os.makedirs("data", exist_ok=True)
