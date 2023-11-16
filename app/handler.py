from socketserver import StreamRequestHandler
from app.server import HTTPServer


class HTTPHandler(StreamRequestHandler):
    server: HTTPServer

    def receive(self):
        lines = self.rfile.readline()

    def send(self):
        self.wfile.write()

    def handle(self) -> None:
        request = self.receive()

        self.send()
