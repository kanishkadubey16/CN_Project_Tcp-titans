from flask import Flask, jsonify, request, make_response

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    response = jsonify({
        "backend": "A",
        "status": "ok"
    })
    response.headers["X-Backend"] = "A"
    return response


@app.route("/api/status", methods=["GET"])
def status():
    etag = '"backend-a-v1"'

    # Conditional request
    if request.headers.get("If-None-Match") == etag:
        response = make_response("", 304)
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "max-age=60"
        response.headers["X-Backend"] = "A"
        return response

    response = jsonify({
        "backend": "A",
        "status": "ok"
    })

    response.headers["X-Backend"] = "A"
    response.headers["Cache-Control"] = "max-age=60"
    response.headers["ETag"] = etag

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)