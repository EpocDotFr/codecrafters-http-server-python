from app.handler import HTTPHandler
from app.server import HTTPServer
import argparse


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--directory')

    args = arg_parser.parse_args()

    config = {}

    if args.directory:
        config['directory'] = args.directory

    with HTTPServer(('127.0.0.1', 4221), HTTPHandler, config=config) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
