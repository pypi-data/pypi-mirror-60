from collections import namedtuple
import uuid
import requests
import hashlib

HttpClientConfig = namedtuple(
    'HttpClientConfig',
    [
        'name',
        'url',
        'username',
        'password',
    ]
)

def get_request(client_config, endpoint, params={}):
    return requests.get(
        client_config.url + endpoint,
        params=build_params(client_config, params)
    )

def build_login_params(client_config):
    salt = build_salt()
    return {
        "u": client_config.username,
        "t": build_token(client_config, salt),
        "s": salt
    }

def build_params(client_config, params):
    login_params = build_login_params(client_config)
    return {**params, **login_params}

def build_salt():
    return uuid.uuid4().hex

def build_token(client_config, salt):
    return hashlib.md5((client_config.password + salt).encode()).hexdigest()


def get_artists(client_config):
    params = {
        "f": "json",
    }
    return get_request(client_config, "/rest/getArtists", params)


def get_artist(client_config, id):
    params = {
        "id": id,
        "f": "json",
    }
    return get_request(client_config, "/rest/getArtist", params)

def get_album(client_config, id):
    params = {
        "id": id,
        "f": "json",
    }
    return get_request(client_config, "/rest/getAlbum", params)

def get_song(client_config, id):
    params = {
        "id": id,
        "f": "json",
    }
    return get_request(client_config, "/rest/getSong", params)

def get_stream(client_config, id):
    params = {
        "id": id,
    }
    return get_request(client_config, "/rest/stream", params)
