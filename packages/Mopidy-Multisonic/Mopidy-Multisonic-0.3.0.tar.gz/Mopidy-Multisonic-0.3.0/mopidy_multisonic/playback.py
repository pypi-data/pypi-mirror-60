from mopidy import backend
from . import uri_parser
from .httpclient import get_stream
from .browser import get_http_client_config

class Playback(backend.PlaybackProvider):
    def __init__(self, audio, backend):
        self.audio = audio
        self.backend = backend

    def get_http_client_configs(self):
        return self.backend.http_client_configs

    def translate_uri(self, uri):
        http_client_config = get_http_client_config(self.get_http_client_configs(), uri)
        id = uri_parser.get_id(uri)
        return get_stream(http_client_config, str(id)).url

