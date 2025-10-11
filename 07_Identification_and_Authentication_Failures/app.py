from flask import Flask, request, redirect, session, send_file, render_template_string
import json
import os

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret"

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_users(u):
    with open(USERS_FILE, "w") as f:
        json.dump(u, f, indent=2)

users = load_users()

# ---------- Vulnerable logic intentionally ----------
# register_user: DOES NOT normalize/strip username (vulnerable)
def register_user(username, password):
    if username in users:
        return False
    users[username] = {"password": password}
    save_users(users)
    return True

# login_user: checks username exactly, but stores stripped username into session (vulnerable)
def login_user(username, password):
    if username in users and users[username]["password"] == password:
        # critical bug: we strip username when saving to session
        session["username"] = username.strip()
        return True
    return False

INDEX_HTML = """
<!doctype html>
<title>Auth Lab - Vulnerable (with superuser)</title>
<h2>Login / Register (VULNERABLE)</h2>
{% if error %}<p style="color:red">{{error}}</p>{% endif %}
<form method="post">
  <label>Username: <input name="username"></label><br>
  <label>Password: <input name="password"></label><br>
  <button name="register" type="submit">Register</button>
  <button name="login" type="submit">Login</button>
</form>
<p>
- Demo vuln: register a username with leading/trailing spaces (e.g. "<code> superuser </code>"), then login with the same spaced username and password. After login the session username is trimmed to "superuser".
</p>
<p><a href="/database.json">Download users.json</a></p>
"""

DASH_HTML = """
<!doctype html>
<title>Dashboard</title>
<p>{{ content }}</p>
<form method="post" action="/logout"><button type="submit">Logout</button></form>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if "register" in request.form:
            ok = register_user(username, password)
            if ok:
                # do NOT auto-login after register in this minimal demo
                return redirect("/")
            else:
                error = "Username already exists!"
        elif "login" in request.form:
            if login_user(username, password):
                return redirect("/dashboard")
            else:
                error = "Invalid username or password!"
    return render_template_string(INDEX_HTML, error=error)

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/")
    username = session["username"]
    if username == "superuser":
        content = "open(/flag.txt)"
    else:
        content = "Is that all you can do? Try to login as superuser"
    return render_template_string(DASH_HTML, content=content)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/database.json")
def download_db():
    if os.path.exists(USERS_FILE):
        return send_file(USERS_FILE, as_attachment=True)
    return "No users.json", 404

if __name__ == "__main__":
    app.run(debug=True)
