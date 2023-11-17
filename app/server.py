from socketserver import ThreadingTCPServer
from typing import Dict, Optional


class HTTPServer(ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    config: Dict

    def __init__(self, *args, config: Optional[Dict] = None, **kvargs):
        super().__init__(*args, **kvargs)

        self.config = {}

        if config:
            self.config.update(config)
