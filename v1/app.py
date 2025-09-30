from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/info")
def info():
    query_ip = request.args.get("ip")
    data = {
        "query_ip": query_ip,
        "remote_addr": request.remote_addr,
        "x_forwarded_for": request.headers.get("X-Forwarded-For"),
        "x_real_ip": request.headers.get("X-Real-IP"),
        "forwarded": request.headers.get("Forwarded"),
        "all_headers": {k: v for k, v in request.headers.items()},
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
