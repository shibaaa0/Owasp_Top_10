# vulnerable_app.py
from flask import Flask, request, session, redirect, url_for, render_template_string, send_file
import os
import pickle
import uuid
import subprocess

app = Flask(__name__)
app.secret_key = "REPLACE_WITH_RANDOM_SECRET"  # đổi thật khi test
USERDATA_DIR = "./user_data"
os.makedirs(USERDATA_DIR, exist_ok=True)

# ---------- Classes (mô phỏng như PHP) ----------
class Gun:
    def __init__(self, name, type_):
        self.name = name
        self.type = type_

    def getgun(self):
        return self.name

    def gettype(self):
        return self.type

class Resource:
    def __init__(self, link):
        self.link = link

    # <-- DANGER: ví dụ này thực thi lệnh hệ thống!
    def getgun(self):
        # MẪU NGUY HIỂM: tải nội dung từ link (chỉ ví dụ)
        # Trong mô phỏng thực tế, một payload pickle có thể khiến hàm này được gọi
        # và thực thi lệnh tùy ý. Chỉ chạy trong môi trường lab cô lập.
        try:
            # dùng curl để minh họa; trong lab có thể đổi thành command khác
            output = subprocess.check_output(["curl", "-s", self.link], stderr=subprocess.DEVNULL, timeout=5)
            return output.decode(errors="ignore")[:100]  # trả về 100 ký tự đầu
        except Exception as e:
            return f"Error fetching: {e}"

# ---------- Helpers ----------
def userdata_path(sessid):
    return os.path.join(USERDATA_DIR, sessid)

def append_pickled_object(sessid, obj):
    path = userdata_path(sessid)
    with open(path, "ab") as f:
        # lưu object dạng pickle + phân tách bằng một byte delimiter
        # (Ở ví dụ này dùng b"|\n" làm delimiter)
        f.write(pickle.dumps(obj))
        f.write(b"|\n")

def read_pickled_objects(sessid):
    path = userdata_path(sessid)
    if not os.path.exists(path):
        return []
    data = open(path, "rb").read()
    parts = data.split(b"|\n")
    objs = []
    for p in parts:
        if not p:
            continue
        try:
            objs.append(pickle.loads(p))
        except Exception as e:
            # lỗi unpickle -> bỏ qua hoặc log
            objs.append(f"<<unpickle error: {e}>>")
    return objs

# ---------- Routes ----------
INDEX_HTML = """
<!doctype html>
<title>Gun Catalogue (Flask Demo)</title>
<h1>Gun Catalogue (Insecure Deserialization Demo)</h1>
<form action="{{ url_for('add') }}" method="post">
  <input name="name" placeholder="Gun name">
  <input name="type" placeholder="Gun type">
  <button type="submit">Add Gun</button>
</form>
<br>
<form action="{{ url_for('add_resource') }}" method="post">
  <input name="link" placeholder="Resource link (for Resource object)">
  <button type="submit">Add Resource (dangerous)</button>
</form>
<br>
<a href="{{ url_for('show') }}">Show Guns</a>
"""

@app.before_request
def assign_session():
    if "sessid" not in session:
        session["sessid"] = str(uuid.uuid4())

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "unknown")
    type_ = request.form.get("type", "unknown")
    g = Gun(name, type_)
    append_pickled_object(session["sessid"], g)
    return redirect(url_for("index"))

@app.route("/add_resource", methods=["POST"])
def add_resource():
    # TÍNH NĂNG NGUY HIỂM: cho phép lưu một object Resource (mô phỏng attacker)
    link = request.form.get("link", "")
    r = Resource(link)
    append_pickled_object(session["sessid"], r)
    return redirect(url_for("index"))

@app.route("/show")
def show():
    items = read_pickled_objects(session["sessid"])
    out = []
    for it in items:
        if isinstance(it, str) and it.startswith("<<unpickle error"):
            out.append(it)
            continue
        # Ở đây code gọi method getgun() trên object đã unpickle
        # => nếu object là Resource và thực thi subprocess, sẽ chạy lệnh.
        try:
            name = getattr(it, "getgun", lambda: "N/A")()
            type_ = getattr(it, "gettype", lambda: "N/A")()
            out.append(f"Name: {name}, Type: {type_}")
        except Exception as e:
            out.append(f"Error calling methods: {e}")
    return "<br>".join(["<h2>Stored objects:</h2>"] + out)

@app.route("/download_db")
def download_db():
    # cho phép tải file session (mô phỏng route /database.db trong PHP)
    path = userdata_path(session["sessid"])
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "No data", 404

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
