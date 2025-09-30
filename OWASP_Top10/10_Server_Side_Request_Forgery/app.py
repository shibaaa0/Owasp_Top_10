from flask import Flask, request, render_template_string
from markupsafe import escape
import urllib.request

app = Flask(__name__)
MAX = 100 * 1024  # max bytes to read
TIMEOUT = 5

INDEX_HTML = """
<!doctype html>
<title>URL2HTML</title>
<h1>URL → HTML</h1>
<form action="/fetch" method="post">
<input type="text" name="url" size="80" value="# Paste URL here"><br>
  <button type="submit">Fetch</button>
</form>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/fetch", methods=["POST"])
def fetch():
    url = request.form.get("url", "").strip()
    if not url:
        return "No URL", 400

    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            data = r.read(MAX + 1)
    except Exception as e:
        return f"Fetch error: {escape(str(e))}", 502

    if len(data) > MAX:
        data = data[:MAX]

    try:
        text = data.decode("utf-8")
    except Exception:
        text = data.decode("latin-1", errors="replace")

    safe_text = escape(text)

    return render_template_string("<!doctype html><title>Result</title><pre>{{content}}</pre>",
                                  content=safe_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
