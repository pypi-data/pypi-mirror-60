import os
from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/")
    @app.route("/health")
    def serve():
        return "app online!"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
