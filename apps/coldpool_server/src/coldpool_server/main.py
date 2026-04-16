from coldpool_server.flask_server.flask_server import FlaskServer


def main() -> None:
    server = FlaskServer()
    server.run(host="0.0.0.0", port=5000, debug=False)
