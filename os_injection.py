from flask import Flask, request, render_template_string
import os
import urllib.parse
app = Flask(__name__)

@app.route("/")
def home():    
   return """
        <form method='POST' action='/'>
        <select id='ping_type' name='ping_type'>
        <option value='ping'>Ping</option>
        <option value='blind_ping'>Blind Ping</option>
        </select>
        <input type='text' name='user_input'>
        <input type='submit' value='Send'>
        </form>
        """

@app.route("/", methods=["POST"])
def handle_ping():
    post_data = request.form  
    #post_data="ping_type=ping&user_input=8.8.8.8"

    ping_type = post_data.get("ping_type", "")
    user_input = post_data.get("user_input", "")

    print(ping_type)
    user_input = urllib.parse.unquote_plus(user_input)
    print(user_input)

    ping = "ping -c 4 " if os.name != "nt" else "ping "
    if ping_type == "ping":
        print(ping + user_input)
        response = os.popen(ping + user_input).read()
    else:
        os.system(ping + user_input)
        response = "Ping Ping Ping"
    return response

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)