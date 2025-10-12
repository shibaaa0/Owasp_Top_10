from flask import Flask, request, redirect, g
import sqlite3

app = Flask(__name__)
DATABASE = "database.db"

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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "login" in request.form:
            username = request.form["username"]
            password = request.form["password"]
            db = get_db()
            cur = db.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
            user = cur.fetchone()
            if user:
                return redirect(f"/secret?id={user['id']}")
            else:
                return "Invalid username or password!"
        elif "register" in request.form:
            return redirect("/register")

    return """
    <h2>Login</h2>
    <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br><br>
        <button type="submit" name="login">Login</button>
        <button type="submit" name="register">Register</button>
    </form>
    """

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        secret = request.form["secret"]
        db = get_db()
        try:
            db.execute("INSERT INTO user (username, password, secret) VALUES (?, ?, ?)",
                       (username, password, secret))
            db.commit()
            return "Registration successful! <a href='/'>Go back to login</a>"
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return """
    <h2>Register</h2>
    <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        Secret: <input name="secret"><br>
        <input type="submit" value="Register">
    </form>
    """

@app.route("/secret")
def secret():
    user_id = request.args.get("id")
    if not user_id:
        return "Missing id!"
    db = get_db()
    cur = db.execute("SELECT * FROM user WHERE id=?", (user_id,))
    row = cur.fetchone()
    if row:
        return f"""
        <h2>Secret of {row['username']}:</h2>
        <p>{row['secret']}</p>
        """
    return "User not found!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
