from .backend import logger
from . import cache

def lookup(http_client_configs, uri):
    model = cache.fetch_model(uri)
    if None == model:
        logger.error("Can't lookup " + uri)
        return

    return [model]
