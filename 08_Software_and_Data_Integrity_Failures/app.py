# app_vulnerable.py
from flask import Flask, request, redirect, url_for, render_template_string
import pickle, base64

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<title>Input</title>
<h2>Enter name and age</h2>
<form method="post">
  Name: <input name="user"><br>
  Age: <input name="age"><br>
  <button type="submit">Create Code</button>
</form>
"""

VIEW_HTML = """
<!doctype html>
<title>View</title>
<pre>{{ obj }}</pre>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user = request.form.get("user","")
        age = int(request.form.get("age",""))
        d = {"user": user, "age": age}
        pickled = pickle.dumps(d)
        b64 = base64.b64encode(pickled).decode()
        return redirect(url_for("view_code", code=b64))
    return render_template_string(INDEX_HTML)

@app.route("/view")
def view_code():
    code = request.args.get("code","")
    try:
        pickled = base64.b64decode(code)
        obj = pickle.loads(pickled)   # <<< vulnerable deserialization
    except Exception as e:
        obj = f"Error: {e}"
    return render_template_string(VIEW_HTML, code=code, obj=obj)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)
