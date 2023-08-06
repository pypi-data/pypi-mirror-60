import logging
import pykka
import re
from mopidy import backend

logger = logging.getLogger(__name__)

from .library import Library
from .playback import Playback
from .httpclient import HttpClientConfig
from .uri_parser import root_uri


def load_http_client_config(provider):
    match = re.match(r'^([^:]+):(?: )?([^:]+)://([^:]+):([^@]+)@(.+)', provider)

    name=match.group(1)
    protocol=match.group(2)
    username=match.group(3)
    password=match.group(4)
    url=match.group(5)

    return HttpClientConfig(
        name=name,
        url=protocol + "://" + url,
        username=username,
        password=password
    )

def load_http_client_configs(config):
    return list(map(
        lambda provider: load_http_client_config(provider),
        config["providers"]
    ))

class MultisonicBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(MultisonicBackend, self).__init__()
        self.config = config["multisonic"]
        self.audio = audio
        self.http_client_configs = load_http_client_configs(self.config)

        self.library = Library(self)
        self.playback = Playback(audio, self)
        self.uri_schemes = [root_uri]
