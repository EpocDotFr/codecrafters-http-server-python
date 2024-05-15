from app.custom_types import URL, HTTPRequest, HTTPResponse
from socketserver import StreamRequestHandler
from typing import Optional, Tuple, Dict
from app.server import HTTPServer
import re
import os

URL_REGEX = re.compile(r'(?:(?P<scheme>[a-z0-9.]+)(?:://)?)?(?P<domain>[a-z.-]+)?(?::(?P<port>[0-9]+))?(?P<path>.[^?#\s]*)(?:\?(?P<query>.[^#\s]*))?(?:#(?P<fragment>.+))?')


class HTTPHandler(StreamRequestHandler):
    server: HTTPServer

    def receive(self) -> Optional[HTTPRequest]:
        start_line = self.receive_start_line()

        if not start_line:
            return None

        method, url, version = start_line

        headers = self.receive_headers()

        body = self.receive_body(headers)

        return HTTPRequest(method, url, version, body, headers)

    def receive_start_line(self) -> Optional[Tuple[str, URL, str]]:
        start_line = self.read_line()

        if not start_line:
            return None

        method, target, version = start_line.split(' ')

        if not method or not target or not version:
            return None

        return method, self.parse_target(target), version

    def parse_target(self, target: str) -> URL:
        scheme = domain = port = path = query = fragment = None

        match = URL_REGEX.fullmatch(target)

        if match:
            match = match.groupdict()

            scheme = match.get('scheme', '') or ''
            domain = match.get('domain', '') or ''
            port = match.get('port', None) or None
            path = match.get('path', '') or ''
            query = self.parse_query(match.get('query', '') or '')
            fragment = match.get('fragment', '') or ''

        return URL(scheme, domain, port, path, query, fragment)

    def parse_query(self, query: str) -> Dict:
        ret = {}

        if not query:
            return ret

        for pair in query.split('&'):
            key, value = pair.split('=', maxsplit=1)

            ret[key] = value

        return ret

    def receive_headers(self) -> Dict:
        headers = {}

        while True:
            header_line = self.read_line()

            if not header_line:
                break

            key, value = header_line.split(':', maxsplit=1)

            headers[key.strip()] = value.strip()

        return headers

    def receive_body(self, headers: Dict) -> bytes:
        content_length = headers.get('Content-Length', 0)

        if not content_length:
            return b''

        return self.rfile.read(int(content_length))

    def send(self, response: HTTPResponse) -> None:
        print(f'< {response.status_code} {response.status_text}\n')

        self.write_line(f'HTTP/1.1 {response.status_code} {response.status_text}')

        response_headers = response.headers.copy()

        if response.body:
            response_headers['Content-Length'] = len(response.body)

        for key, value in response_headers.items():
            self.write_line(f'{key}: {value}')

        self.write_line('')

        self.write_body(response.body)

    def handle(self) -> None:
        request = self.receive()

        if not request:
            return

        print(f'> {request.version} {request.method} {request.url} {request.headers}')

        response_headers = {
            'Connection': 'Close'
        }

        if request.url.path == '/' and request.method == 'GET':
            self.send(HTTPResponse(200, 'OK', b'', response_headers))
        if request.url.path == '/user-agent' and request.method == 'GET':
            response_headers['Content-Type'] = 'text/plain'

            self.send(HTTPResponse(200, 'OK', request.headers.get('User-Agent').encode(), response_headers))
        elif request.url.path.startswith('/echo/') and request.method == 'GET':
            response_headers['Content-Type'] = 'text/plain'

            if request.headers.get('Accept-Encoding') == 'gzip':
                response_headers['Content-Encoding'] = 'gzip'

            self.send(HTTPResponse(200, 'OK', request.url.path[6:].encode(), response_headers))
        elif request.url.path.startswith('/files/'):
            directory = self.server.config.get('directory')

            if directory:
                if request.method == 'GET':
                    filename = os.path.join(directory, request.url.path[7:])

                    if os.path.isfile(filename):
                        response_headers['Content-Type'] = 'application/octet-stream'

                        with open(filename, 'rb') as f:
                            body = f.read()

                        self.send(HTTPResponse(200, 'OK', body, response_headers))

                        return
                elif request.method == 'POST':
                    filename = os.path.join(directory, request.url.path[7:])

                    with open(filename, 'wb') as f:
                        f.write(request.body)

                    self.send(HTTPResponse(201, 'Created', b'', response_headers))

                    return

            self.send(HTTPResponse(404, 'Not found', b'', response_headers))
        else:
            self.send(HTTPResponse(404, 'Not found', b'', response_headers))

    def read_line(self) -> Optional[str]:
        line = self.rfile.readline().decode()

        return line.rstrip('\r\n') if line else None

    def write_line(self, line: str) -> None:
        self.wfile.write(f'{line}\r\n'.encode())

    def write_body(self, body: bytes = b'') -> None:
        self.wfile.write(body)
