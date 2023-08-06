import pykka
from mopidy import backend
from .library import Library
from .playback import Playback
from .httpclient import HttpClientConfig
from .uri_parser import root_uri

def load_http_client_config(provider):
    provider=provider.split(":")
    name=provider[0]
    protocol=provider[1]
    url=provider[2]
    username=provider[3]
    password=provider[4]

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

class SubsonicBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(SubsonicBackend, self).__init__()
        self.config = config["multisonic"]
        self.audio = audio
        self.http_client_configs = load_http_client_configs(self.config)

        self.library = Library(self)
        self.playback = Playback(audio, self)
        self.uri_schemes = [root_uri]


