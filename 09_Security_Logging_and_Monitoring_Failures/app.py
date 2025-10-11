# app.py
from flask import Flask, request, render_template_string, redirect, url_for, send_file, abort, Response
import difflib
import datetime
import os
import threading
import json

app = Flask(__name__)

TEST_FILE = "test.txt"
LOG_FILE = "logs.txt"
LOCK = threading.Lock()

# Ensure files exist
if not os.path.exists(TEST_FILE):
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write("")  # empty by default

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")  # create empty logs file

HTML_TEMPLATE = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Edit test.txt</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    textarea { width: 100%; height: 60vh; font-family: monospace; font-size: 14px; }
    .info { margin-bottom: 1rem; color: #444; }
    .btn { padding: 0.5rem 1rem; font-size: 1rem; }
    .loglink { margin-left: 1rem; }
  </style>
</head>
<body>
  <h1>Chỉnh sửa test.txt</h1>
  <p class="info">IP của bạn: {{ ip }}</p>
  <form method="post" action="{{ url_for('index') }}">
    <textarea name="content" spellcheck="false">{{ content }}</textarea>
    <div style="margin-top:0.5rem;">
      <button class="btn" type="submit">Lưu thay đổi</button>
      <a class="btn loglink" href="/logs.txt" download> Tải logs.txt </a>
      <a class="btn loglink" href="/robos.txt" download> Tải robos.txt </a>
    </div>
  </form>
  {% if message %}
    <p><strong>{{ message }}</strong></p>
  {% endif %}
  <hr>
  <h3>Ghi chú</h3>
  <ul>
    <li>Các thay đổi sẽ được ghi vào <code>logs.txt</code> dưới dạng bản ghi có thời gian, IP và mô tả thao tác (thêm/sửa/xóa tại vị trí ký tự).</li>
    <li>Vị trí ký tự là chỉ số (index) trong chuỗi trước/sau khi thay đổi — bắt đầu từ 0.</li>
  </ul>
</body>
</html>
"""

def client_ip():
    # get real client ip if behind proxy (X-Forwarded-For), fallback to remote_addr
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        # X-Forwarded-For có thể chứa nhiều ip, lấy ip đầu tiên
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"

def diff_ops(old: str, new: str):
    """
    Compute character-level diffs using SequenceMatcher and return a list of ops.
    Each op is dict: {tag, i1, i2, j1, j2, text}
    tag: replace/insert/delete/equal
    i1,i2: old string indices
    j1,j2: new string indices
    text: inserted/replaced text (for insert/replace), or deleted text (for delete)
    """
    s = difflib.SequenceMatcher(a=old, b=new)
    ops = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            ops.append({
                "tag": "replace",
                "old_pos": [i1, i2],
                "new_pos": [j1, j2],
                "old_text": old[i1:i2],
                "new_text": new[j1:j2]
            })
        elif tag == "delete":
            ops.append({
                "tag": "delete",
                "old_pos": [i1, i2],
                "deleted_text": old[i1:i2]
            })
        elif tag == "insert":
            ops.append({
                "tag": "insert",
                "new_pos": [j1, j2],
                "inserted_text": new[j1:j2]
            })
    return ops

def append_log_entry(ip: str, ops, old_preview: str, new_preview: str):
    """
    Append a structured, readable log entry to LOG_FILE.
    Uses a combined plain-text + JSON line for easier reading and parsing.
    """
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    entry = {
        "time": timestamp,
        "ip": ip,
        "ops": ops
    }
    # human readable summary
    lines = []
    lines.append(f"--- LOG ENTRY {timestamp} ---")
    lines.append(f"IP: {ip}")
    if not ops:
        lines.append("No changes detected.")
    else:
        lines.append("Operations:")
        for op in ops:
            tag = op.get("tag")
            if tag == "replace":
                lines.append(f"  - replace old[{op['old_pos'][0]}:{op['old_pos'][1]}] -> new[{op['new_pos'][0]}:{op['new_pos'][1]}], "
                             f"old_text={repr(op['old_text'])}, new_text={repr(op['new_text'])}")
            elif tag == "delete":
                lines.append(f"  - delete old[{op['old_pos'][0]}:{op['old_pos'][1]}], text={repr(op['deleted_text'])}")
            elif tag == "insert":
                lines.append(f"  - insert at new[{op['new_pos'][0]}:{op['new_pos'][1]}], text={repr(op['inserted_text'])}")
            else:
                lines.append(f"  - {op}")
    # optional small previews (first 200 chars)
    lines.append("Old preview (first 200 chars):")
    lines.append(old_preview[:200])
    lines.append("New preview (first 200 chars):")
    lines.append(new_preview[:200])
    lines.append("")  # blank line
    # Write atomically with lock
    with LOCK:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
            f.write("\n")
            # Also append machine-readable JSON line for parsers
            f.write(json.dumps(entry, ensure_ascii=False))
            f.write("\n\n")

@app.route("/", methods=["GET", "POST"])
def index():
    ip = client_ip()
    message = None
    if request.method == "POST":
        new_content = request.form.get("content", "")
        # read old
        with LOCK:
            with open(TEST_FILE, "r", encoding="utf-8") as f:
                old_content = f.read()
        # compute ops
        ops = diff_ops(old_content, new_content)
        # if changed, overwrite test.txt and log
        if ops:
            with LOCK:
                # write new content
                with open(TEST_FILE, "w", encoding="utf-8") as f:
                    f.write(new_content)
            append_log_entry(ip, ops, old_content, new_content)
            message = f"Đã lưu. Ghi nhận {len(ops)} thao tác vào logs."
        else:
            message = "Không có thay đổi."
    # always show current content
    with LOCK:
        with open(TEST_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    return render_template_string(HTML_TEMPLATE, content=content, ip=ip, message=message)

@app.route("/robos.txt", methods=["GET"])
def robos():
    # user asked /robos.txt (mình giữ chính xác), trả nội dung tương tự robots.txt
    content = "User-agent: *\nDisallow:\n"
    return Response(content, mimetype="text/plain; charset=utf-8")

@app.route("/logs.txt", methods=["GET"])
def get_logs():
    # allow downloading logs file
    if not os.path.exists(LOG_FILE):
        abort(404)
    # send as attachment so browser will download
    return send_file(LOG_FILE, as_attachment=True, download_name="logs.txt", mimetype="text/plain; charset=utf-8")

if __name__ == "__main__":
    # For development only. In production, dùng WSGI server như gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=True)
