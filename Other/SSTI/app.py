from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def home():    
    try:
        text = request.headers.get("User-Agent")
    except:
        text = None  
    return render_template_string(text)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)