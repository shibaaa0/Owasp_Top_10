from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        os.system(f"ping -c 4 {user_input}")
        return "Ping Ping Ping"
    return '''
        <form method="POST">
            <input type="text" name="user_input" placeholder="Enter IP or host">
            <input type="submit" value="Ping">
        </form>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
