from . import uri_parser
from . import httpclient
from mopidy import models
import json

top_root_dir = models.Ref.directory(
    name="Multisonic",
    uri=uri_parser.root_uri + ":" + uri_parser.build_top()
)

def is_http_client_config_uri(http_client_config, uri):
    provider_name = uri_parser.get_provider_name(uri)
    return http_client_config.name == provider_name

def get_http_client_config(http_client_configs, uri):
    for http_client_config in http_client_configs:
        if is_http_client_config_uri(http_client_config, uri):
            return http_client_config

def browse_root_top(http_client_configs):
    return list(map(
        lambda http_client_config: models.Ref.directory(
            name=http_client_config.name,
            uri=uri_parser.build_top(http_client_config.name)
        ),
        http_client_configs
    ))

def browse_top(http_client_config):
    return [
        models.Ref.directory(
            name="Artists",
            uri=uri_parser.build_artists(http_client_config.name)
        )
        #models.Ref.directory(
        #    name="Playlist",
        #    uri=uri_parser.build_playlists(http_client_config.name)
        #),
    ]

def browse_artists(http_client_config, uri):
    artists = []

    data = json.loads(httpclient.get_artists(http_client_config).text)
    for index in data["subsonic-response"]["artists"]["index"]:
        for artist in index["artist"]:
            artists.append(
                models.Ref.artist(
                    name=artist["name"],
                    uri=uri_parser.build_artist(
                        str(artist["id"]),
                        http_client_config.name
                    ),
                )
            )
    return artists

def browse_artist(http_client_config, uri):
    albums = []
    id = uri_parser.get_id(uri)
    data = json.loads(httpclient.get_artist(http_client_config, id).text)
    for album in data["subsonic-response"]["artist"]["album"]:
        albums.append(
            models.Ref.album(
                name=album["name"],
                uri=uri_parser.build_album(
                    str(album["id"]),
                    http_client_config.name
                )
            )
        )

    return albums

def browse_album(http_client_config, uri):
    tracks = []
    id = uri_parser.get_id(uri)
    data = json.loads(httpclient.get_album(http_client_config, id).text)
    for song in data["subsonic-response"]["album"]["song"]:
        tracks.append(
            models.Ref.track(
                name=song["title"],
                uri=uri_parser.build_track(
                    str(song["id"]),
                    http_client_config.name
                )
            )
        )

    return tracks

def browse(http_client_configs, uri):
    if uri_parser.is_root_top(uri):
        return browse_root_top(http_client_configs)

    http_client_config = get_http_client_config(http_client_configs, uri)

    if uri_parser.is_top(uri):
        return browse_top(http_client_config)
    if uri_parser.is_artists(uri):
        return browse_artists(http_client_config, uri)
    if uri_parser.is_artist(uri):
        return browse_artist(http_client_config, uri)
    if uri_parser.is_album(uri):
        return browse_album(http_client_config, uri)
