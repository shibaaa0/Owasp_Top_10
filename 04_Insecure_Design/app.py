# app.py
from flask import Flask, request, render_template_string, redirect, url_for, flash
import time
from collections import defaultdict, deque
import random

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# ======= CONFIG =======
REQUEST_LIMIT = 5        # max requests per window per IP
WINDOW_SECONDS = 60 * 60 # 1 hour
USE_HEADER_FOR_IP = True

# Generate a random 6-digit "OTP-like" secret at startup
REAL_CODE = f"{random.randint(0, 999999):06d}"  # e.g. "042719"
SECRET_TEXT = REAL_CODE

print("==== LAB START ====")
print("Secret (6-digit OTP) for this lab is:", REAL_CODE)
print("==== KEEP THIS FOR INSTRUCTOR/DEBUG ====")

# In-memory rate store: maps ip -> deque of timestamps
rate_store = defaultdict(deque)

TEMPLATE = """
<!doctype html>
<title>Enter Code</title>
<h2>Enter access code to view secret</h2>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul style="color: red;">
    {% for m in messages %}
      <li>{{ m }}</li>
    {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
<form method="POST">
  <label>Code (6 digits): <input name="code" autocomplete="off" maxlength="6"></label>
  <button type="submit">Submit</button>
</form>
{% if secret %}
  <h3>Secret (OTP):</h3>
  <pre>{{ secret }}</pre>
{% endif %}
<hr>
<p><strong>Note:</strong> Vulnerable demo: server rate-limits by IP but trusts headers like <code>X-Forwarded-For</code>. This allows spoofing to bypass limits.</p>
"""

def now_ts():
    return int(time.time())

def get_client_ip():
    """VULNERABLE: prefer header values, allowing spoofing"""
    header_names = ["Client-IP", "X-Forwarded-For", "X-Real-IP"]
    if USE_HEADER_FOR_IP:
        for h in header_names:
            val = request.headers.get(h)
            if val:
                ip = val.split(",")[0].strip()
                return ip
    return request.remote_addr or "unknown"

def prune_old_requests(deq):
    cutoff = now_ts() - WINDOW_SECONDS
    while deq and deq[0] < cutoff:
        deq.popleft()

def allowed_by_rate(ip):
    deq = rate_store[ip]
    prune_old_requests(deq)
    return len(deq) < REQUEST_LIMIT

def record_request(ip):
    rate_store[ip].append(now_ts())

@app.route("/", methods=["GET", "POST"])
def index():
    secret = None
    if request.method == "POST":
        client_ip = get_client_ip()
        if not allowed_by_rate(client_ip):
            flash(f"Rate limit exceeded for IP {client_ip}. Try again later.")
            return redirect(url_for("index"))

        record_request(client_ip)

        code = (request.form.get("code") or "").strip()
        if code == REAL_CODE:
            secret = SECRET_TEXT
        else:
            flash("Wrong code.")

    return render_template_string(TEMPLATE, secret=secret)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
