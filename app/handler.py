from socketserver import StreamRequestHandler
from typing import Optional, Tuple, Dict
from app.server import HTTPServer


class HTTPHandler(StreamRequestHandler):
    server: HTTPServer

    def receive(self) -> Tuple[str, str, str, Dict]:
        start_line = self.read_line()

        if not start_line:
            return

        method, target, version = start_line.split(' ')

        if not method or not target or not version:
            return

        headers = {}

        while True:
            header_line = self.read_line()

            if not header_line:
                break

            key, value = header_line.split(':', maxsplit=1)

            headers[key.strip()] = value.strip()

        return method, target, version, headers

    def send(self, status_code: int = 200, status_text: str = 'OK') -> None:
        self.write_line(f'HTTP/1.1 {status_code} {status_text}')
        self.write_line('')

    def handle(self) -> None:
        method, target, version, headers = self.receive()

        print(method, target, version, headers)

        if target == '/':
            self.send()
        else:
            self.send(404, 'Not found')

    def read_line(self) -> Optional[str]:
        line = self.rfile.readline().decode('utf-8')

        return line.strip() if line else None

    def write_line(self, line: str) -> None:
        self.wfile.write(f'{line}\r\n'.encode())
