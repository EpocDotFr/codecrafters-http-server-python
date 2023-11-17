from socketserver import StreamRequestHandler
from typing import Optional, Tuple, Dict
from collections import namedtuple
from app.server import HTTPServer
import re

HTTPRequest = namedtuple('HTTPRequest', [
    'method',
    'url',
    'version',
    'headers',
])

HTTPResponse = namedtuple('HTTPResponse', [
    'status_code',
    'status_text',
])

URL = namedtuple('URL', [
    'scheme',
    'domain',
    'port',
    'path',
    'query',
    'fragment',
])

URL_REGEX = re.compile(r'(?:(?P<scheme>[a-z0-9.]+)(?:://)?)?(?P<domain>[a-z.-]+)?(?::(?P<port>[0-9]+))?(?P<path>.[^?#\s]*)(?:\?(?P<query>.[^#\s]*))?(?:#(?P<fragment>.+))?')


class HTTPHandler(StreamRequestHandler):
    server: HTTPServer

    def receive(self) -> HTTPRequest:
        start_line = self.receive_start_line()

        if not start_line:
            return

        method, url, version = start_line

        headers = self.receive_headers()

        return HTTPRequest(method, url, version, headers)

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

    def send(self, response: HTTPResponse) -> None:
        print(f'< {response.status_code} {response.status_text}\n')

        self.write_line(f'HTTP/1.1 {response.status_code} {response.status_text}')
        self.write_line('')

    def handle(self) -> None:
        request = self.receive()

        print(f'> {request.version} {request.method} {request.url} {request.headers}')

        if request.url.path == '/':
            self.send(HTTPResponse(200, 'OK'))
        else:
            self.send(HTTPResponse(404, 'Not found'))

    def read_line(self) -> Optional[str]:
        line = self.rfile.readline().decode('utf-8')

        return line.strip() if line else None

    def write_line(self, line: str) -> None:
        self.wfile.write(f'{line}\r\n'.encode())
