from collections import namedtuple

HTTPRequest = namedtuple('HTTPRequest', [
    'method',
    'url',
    'version',
    'body',
    'headers',
])

HTTPResponse = namedtuple('HTTPResponse', [
    'status_code',
    'status_text',
    'body',
    'headers',
])

URL = namedtuple('URL', [
    'scheme',
    'domain',
    'port',
    'path',
    'query',
    'fragment',
])
