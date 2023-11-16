from app.handler import HTTPHandler
from app.server import HTTPServer


def main() -> None:
    with HTTPServer(('127.0.0.1', 4221), HTTPHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
