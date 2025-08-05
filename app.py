# app.py

from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
from datetime import datetime
import csv

app = Flask(__name__)

last_output_file = None
last_table_data = None
last_headers = None
last_message = None

@app.route("/", methods=["GET", "POST"])
def index():
    global last_output_file, last_table_data, last_headers, last_message

    if request.method == "POST":
        site = request.form.get("site")
        query = request.form.get("query")
        limit = request.form.get("limit")

        if site and query:
            filename_safe = query.lower().replace(" ", "_")
            date_str = datetime.now().strftime("%d%m%y")
            output_file = f"{filename_safe}_{site}_{date_str}.csv"
            output_path = os.path.join("static", output_file)

            command = ["python", "runner.py", "--mode", "modular", "--site", site, "--query", query, "--output", output_path]
            if limit:
                command.extend(["--limit", limit])

            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                last_message = f"Scraping completed. Output saved to static/{output_file}"

                # Extract FOUND_COUNT from stdout
                found_count = None
                if result.stdout:
                    for line in result.stdout.splitlines():
                        if "FOUND_COUNT:" in line:
                            try:
                                found_count = int(line.split("FOUND_COUNT:")[1].strip())
                            except ValueError:
                                pass

                # Compare with limit
                if limit:
                    try:
                        int_limit = int(limit)
                        if found_count is not None and found_count < int_limit:
                            last_message += f"<br>⚠️ Only {found_count} records found out of requested {int_limit}."
                    except ValueError:
                        last_message += "<br>⚠️ Invalid limit value."

                # Load results from CSV
                if os.path.exists(output_path):
                    with open(output_path, newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) > 1:
                            last_headers = rows[0]
                            last_table_data = rows[1:]
                            last_output_file = output_file
                        else:
                            last_message += "<br>⚠️ Output file is empty."
                            last_output_file = None
                            last_table_data = None
                else:
                    last_message += "<br>⚠️ Output file not found."
                    last_output_file = None
                    last_table_data = None

            except subprocess.CalledProcessError as e:
                last_message = f"Scraper failed. Error: {e.stderr or e.stdout or 'Check logs.'}"
        else:
            last_message = "⚠️ Please fill all fields."

        return redirect(url_for('index'))

    return render_template("index.html",
                           message=last_message,
                           output_file=last_output_file,
                           headers=last_headers,
                           table_data=last_table_data)

if __name__ == "__main__":
    app.run(debug=True)






"""
# app.py

from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
from datetime import datetime
import csv

app = Flask(__name__)

last_output_file = None
last_table_data = None
last_headers = None
last_message = None

@app.route("/", methods=["GET", "POST"])
def index():
    global last_output_file, last_table_data, last_headers, last_message

    if request.method == "POST":
        site = request.form.get("site")
        query = request.form.get("query")

        if site and query:
            filename_safe = query.lower().replace(" ", "_")
            date_str = datetime.now().strftime("%d%m%y")
            output_file = f"{filename_safe}_{site}_{date_str}.csv"
            output_path = os.path.join("static", output_file)

            command = ["python", "runner.py", "--mode", "modular", "--site", site, "--query", query, "--output", output_path]
            try:
                subprocess.run(command, check=True)
                last_message = f"✅ Scraping completed. Output saved to static/{output_file}"
                if os.path.exists(output_path):
                    with open(output_path, newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) > 1:
                            last_headers = rows[0]
                            last_table_data = rows[1:]
                            last_output_file = output_file
                        else:
                            last_message += "<br>⚠️ Output file is empty."
                            last_output_file = None
                            last_table_data = None
                else:
                    last_message += "<br>⚠️ Output file not found."
                    last_output_file = None
                    last_table_data = None
            except subprocess.CalledProcessError:
                last_message = "Scraper failed. Please check logs."
        else:
            last_message = "⚠️ Please fill all fields."

        return redirect(url_for('index'))

    return render_template("index.html",
                           message=last_message,
                           output_file=last_output_file,
                           headers=last_headers,
                           table_data=last_table_data)

if __name__ == "__main__":
    app.run(debug=True)

"""





