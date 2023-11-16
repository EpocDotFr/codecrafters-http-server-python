from socketserver import StreamRequestHandler
from app.server import HTTPServer


class HTTPHandler(StreamRequestHandler):
    server: HTTPServer
