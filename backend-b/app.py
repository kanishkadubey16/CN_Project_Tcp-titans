from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    response = jsonify({
        "backend": "B",
        "status": "ok"
    })
    response.headers["X-Backend"] = "B"
    return response


@app.route("/api/status", methods=["GET"])
def status():
    response = jsonify({
        "backend": "B",
        "status": "ok"
    })
    response.headers["X-Backend"] = "B"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002)


