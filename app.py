# app.py

from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import os
import csv
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

def get_available_plugins():
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    return [f[:-3] for f in os.listdir(plugin_dir) if f.endswith(".py") and f != "__init__.py"]

def generate_filename(query, site):
    filename_safe = query.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
    return f"{filename_safe}_{site}_{timestamp}.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    available_plugins = get_available_plugins()

    if request.method == "POST":
        site = request.form.get("site")
        query = request.form.get("query")
        limit = request.form.get("limit")

        if site and query:
            filename = generate_filename(query, site)
            output_rel_path = os.path.join("static", filename)
            output_abs_path = os.path.abspath(output_rel_path)

            os.makedirs("static", exist_ok=True)

            command = [
                "python", "runner.py",
                "--mode", "modular",
                "--site", site,
                "--query", query,
                "--output", output_abs_path
            ]
            if limit:
                command.extend(["--limit", limit])

            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                message = f"Scraping completed. Output saved to static/{filename}"

                if os.path.exists(output_abs_path):
                    with open(output_abs_path, newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) > 1:
                            session["headers"] = rows[0]
                            session["table_data"] = rows[1:]
                            session["output_file"] = filename
                        else:
                            message += "<br>⚠️ Output file is empty."
                    session["message"] = message
                else:
                    session["message"] = message + "<br>⚠️ Output file not found."
            except subprocess.CalledProcessError as e:
                session["message"] = f"❌ Scraper failed. Error: {e.stderr or e.stdout or 'Check logs.'}"
        else:
            session["message"] = "⚠️ Please fill all fields."

        return redirect(url_for("index"))

    return render_template(
        "index.html",
        message=session.pop("message", None),
        output_file=session.pop("output_file", None),
        headers=session.pop("headers", None),
        table_data=session.pop("table_data", None),
        available_plugins=available_plugins,
        timestamp=int(time.time())
    )

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)














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





