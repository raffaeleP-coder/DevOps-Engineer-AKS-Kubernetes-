from flask import Flask, jsonify, request, g, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging
import os
import time

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"]
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total number of HTTP 5xx responses",
    ["method", "path"]
)


@app.before_request
def start_timer():
    g.start_time = time.time()


@app.after_request
def record_metrics(response):
    duration = time.time() - g.start_time
    path = request.path

    if path != "/metrics":
        REQUEST_COUNT.labels(
            method=request.method,
            path=path,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            path=path
        ).observe(duration)

        if response.status_code >= 500:
            ERROR_COUNT.labels(
                method=request.method,
                path=path
            ).inc()

    app.logger.info(
        "%s %s %s %.2fms pod=%s env=%s",
        request.method,
        path,
        response.status_code,
        duration * 1000,
        os.getenv("HOSTNAME", "Unknown-Pod"),
        os.getenv("APP_ENV", "production"),
    )

    return response


@app.route("/")
def hello():
    return jsonify({
        "message": "DevOps Challenge Successful!",
        "status": "Running",
        "container_id": os.getenv("HOSTNAME", "Unknown-Pod"),
        "environment": os.getenv("APP_ENV", "production")
    })


@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)