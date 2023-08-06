from . import uri_parser
from . import httpclient
from .browser import get_http_client_config
from mopidy import models
import json

def lookup_track(http_client_config, uri):
    id = uri_parser.get_id(uri)
    data = json.loads(httpclient.get_song(http_client_config, id).text)
    song = data["subsonic-response"]["song"]
    artists=[models.Artist(
        name=song["artist"],
        uri=uri_parser.build_artist(str(song["artistId"]), http_client_config.name)
    )]
    return [models.Track(
        uri=uri_parser.build_track(str(song["id"]), http_client_config.name),
        name=song["title"],
        artists=artists,
        album=models.Album(
            name=song["album"],
            uri=uri_parser.build_album(str(song["albumId"]), http_client_config.name),
            date=str(song["year"]),
            artists=artists
        ),
        date=str(song["year"]),
        length=song["duration"]*1000,
        disc_no=song["discNumber"],
        track_no=song["track"],
    )]

def lookup(http_client_configs, uri):
    http_client_config = get_http_client_config(http_client_configs, uri)
    if uri_parser.is_track(uri):
        return lookup_track(http_client_config, uri)
