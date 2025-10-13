from flask import Flask, request, render_template_string
import datetime

app = Flask(__name__)
FLAG_FILE = "test.txt"
LOG_FILE = "logs.txt"

def vigenere_encrypt(text, key):
    result = []
    key = key.upper()
    key_index = 0
    for char in text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
            key_index += 1
        else:
            result.append(char)
    return ''.join(result)

@app.route("/", methods=["GET", "POST"])
def index():
    with open(FLAG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if request.method == "POST":
        key = request.form.get("key", "")
        encrypted = vigenere_encrypt(content, key)
        with open(FLAG_FILE, "w", encoding="utf-8") as f:
            f.write(encrypted)

        # Ghi log
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.datetime.now()}] IP={request.remote_addr} | Vigenere key='{key}'\n")

        content = encrypted  # Hiển thị luôn nội dung sau khi mã hóa

    return render_template_string("""
    <html>
    <head>
        <title>Vigenère Cipher Tool</title>
        <style>
            body { font-family: Arial; background: #f4f4f4; padding: 30px; }
            textarea { width: 100%; height: 200px; font-family: monospace; padding: 10px; }
            input, button { padding: 8px 14px; margin-top: 10px; }
            .container { background: white; padding: 20px; border-radius: 10px; max-width: 700px; margin: auto; box-shadow: 0 0 10px #ccc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Mã hóa Vigenère</h2>
            <form method="POST">
                <label>Nhập khóa mã hóa:</label><br>
                <input type="text" name="key" required>
                <button type="submit">Mã hóa Vigenère</button>
            </form>
            <h3>Nội dung file:</h3>
            <textarea readonly>{{ content }}</textarea>
        </div>
    </body>
    </html>
    """, content=content)

@app.route("/logs.txt")
def logs():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.read()
    return f"<pre>{logs}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
