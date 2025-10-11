from flask import Flask, request
import os
app = Flask(__name__)

@app.route("/")
def home():    
   return """
        <h1>MD5 Hash</h1>
        <form method='POST' action='/'>
        <input type='text' name='user_input'>
        <input type='submit' value='Hash'>
        </form>
        """

@app.route("/", methods=["POST"])
def hash_string():
    user_input = request.form.get("user_input", "")
    response = os.popen("echo -n " + user_input + " | md5sum").read()
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)