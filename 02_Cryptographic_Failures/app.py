from flask import Flask, request, redirect, url_for, g, send_file
import sqlite3
import os

app = Flask(__name__)
DATABASE = "database.db"
app.secret_key = "supersecret"  # cần cho việc redirect an toàn

# ==========================
# 🔹 HÀM LẤY DATABASE
# ==========================
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# ==========================
# 🔹 ROUTE LOGIN (/)
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        cur = db.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        if user:
            # chuyển hướng sang trang welcome
            return redirect(url_for("welcome", username=user["username"]))
        else:
            return """
                <h3>Login failed! Try again.</h3>
                <a href='/'>Back to login</a>
            """

    return """
        <h2>Login</h2>
        <form method="post">
            Username: <input name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    """

# ==========================
# 🔹 ROUTE WELCOME
# ==========================
@app.route("/welcome")
def welcome():
    username = request.args.get("username")
    if not username:
        return redirect("/")
    return f"<h2>Welcome, {username}!</h2>"

# ==========================
# 🔹 ROUTE ROBOTS.TXT
# ==========================
@app.route("/robots.txt")
def robots():
    content = """User-agent: *
Disallow: /database.db
Allow: /
"""
    return content, 200, {"Content-Type": "text/plain"}

# ==========================
# 🔹 ROUTE DOWNLOAD DATABASE
# ==========================
@app.route("/database.db")
def download_db():
    if not os.path.exists(DATABASE):
        return "Database not found!", 404
    return send_file(DATABASE, as_attachment=True)

# ==========================
# 🔹 CHẠY ỨNG DỤNG
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
