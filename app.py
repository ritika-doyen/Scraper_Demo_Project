"""

# app.py

from flask import Flask, render_template, request
import subprocess
import os
import csv
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    headers = []
    table_data = []
    filename = ""
    output_file_path = ""

    if request.method == "POST":
        site = request.form.get("site")
        query = request.form.get("query")

        if not site or not query:
            message = "⚠️ Please fill all fields."
        else:
            # create filename and path
            safe_query = query.lower().replace(" ", "_")
            date_str = datetime.now().strftime("%d%m%y")
            filename = f"{safe_query}_{site}_{date_str}.csv"
            output_file_path = f"static/{filename}"

            # run scraper via runner
            try:
                subprocess.run([
                    "python", "runner.py",
                    "--mode", "modular",
                    "--site", site,
                    "--query", query,
                    "--output", output_file_path
                ], check=True)

                message = f"✅ Scraping completed. Output saved to <b>{output_file_path}</b>"

                # read CSV file
                if os.path.exists(output_file_path):
                    with open(output_file_path, newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        headers = next(reader)
                        table_data = list(reader)
                else:
                    message += "<br>⚠️ CSV file not found."

            except subprocess.CalledProcessError:
                message = "Scraper failed. Check logs or internet connection."

    return render_template("index.html", message=message, headers=headers, table_data=table_data,
                           output_file=filename if table_data else None)

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
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

