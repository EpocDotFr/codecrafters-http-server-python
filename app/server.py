from socketserver import ThreadingTCPServer


class HTTPServer(ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
