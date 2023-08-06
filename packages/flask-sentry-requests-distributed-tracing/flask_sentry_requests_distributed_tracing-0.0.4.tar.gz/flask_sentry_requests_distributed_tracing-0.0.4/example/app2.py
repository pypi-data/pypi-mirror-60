from flask import Flask
import sentry_sdk

from flask_sentry_requests_distributed_tracing import (
    flask_sentry_requests_distributed_tracing,
)


def setup_sentry():
    sentry_sdk.init("https://733f871d2d0e4ac5981a62ac59133abe@sentry.io/2092136")


app = Flask(__name__)
flask_sentry_requests_distributed_tracing(app)
setup_sentry()


@app.route("/")
def hello():
    return "hello"


if __name__ == "__main__":
    app.run(port=5001)
