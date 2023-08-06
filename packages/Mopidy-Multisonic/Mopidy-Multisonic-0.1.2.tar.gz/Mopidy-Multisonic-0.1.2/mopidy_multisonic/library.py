
from mopidy import backend
from mopidy import models
from . import browser
from . import lookup
from . import uri_parser

class Library(backend.LibraryProvider):
    def __init__(self, backend):
        self.backend = backend
        self.root_directory = browser.top_root_dir

    def get_http_client_configs(self):
        return self.backend.http_client_configs

    def browse(self, uri):
        return browser.browse(self.get_http_client_configs(), uri)

    def get_distinct(self, field, query=None):
        return set()


    def get_images(self, uris):
        return {}


    def lookup(self, uri):
        return lookup.lookup(self.get_http_client_configs(), uri)


    def refresh(self, uri=None):
        pass


    def search(self, query=None, uris=None, exact=False):
        pass
