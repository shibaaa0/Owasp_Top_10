#cve-2020-14343
import os
import json
from flask import Flask, request, jsonify, render_template_string
import yaml

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<title>YAML2JSON</title>
<h1>YAML → JSON</h1>
<form action="/convert" method="post" enctype="application/x-www-form-urlencoded">
  <textarea name="yaml" rows="15" cols="80"># Paste YAML here</textarea><br>
  <button type="submit">Convert</button>
</form>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/convert", methods=["POST"])
def convert():
    yaml_text = request.form.get("yaml", "")
    if not yaml_text:
        return jsonify({"error": "no yaml provided"}), 400

    try:
        # ===== VULNERABLE: using FullLoader (PyYAML < 5.4 allows python object constructors) =====
        loaded = yaml.load(yaml_text, Loader=yaml.FullLoader)

        def safe_convert(obj):
            try:
                json.dumps(obj)
                return obj
            except Exception:
                return repr(obj)
        if isinstance(loaded, dict):
            safe = {k: safe_convert(v) for k, v in loaded.items()}
        else:
            safe = safe_convert(loaded)

        return jsonify({"ok": True, "result": safe})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
