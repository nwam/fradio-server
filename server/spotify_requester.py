import urllib.request
import urllib.parse

import json
from base64 import b64encode
import logging
import sys
import time

CLIENT_ID_SECRET = b'5a87a7cf3de84cb4968337178a9bbdd8:984faa3ff5bd400da180d726924c3155'

URL_SPOTIFY_ACCONTS = 'https://accounts.spotify.com'
URL_ACCESS_TOKEN = URL_SPOTIFY_ACCONTS + '/api/token'
URL_GET_TRACK = 'https://api.spotify.com/v1/tracks/'
ENCODING = 'utf-8'

ART_THUMB_SIZE = 64

class SpotifyRequester:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, 
            filename="fradio-server-spotify.log", 
            format='%(asctime)s %(message)s')

        self.access_token_expiry = 0
        self.access_token_json = self._get_access_token(CLIENT_ID_SECRET)

#    def _init_urllib():
#        """Build an initilize URL opener"""
#        cookieProcessor = urllib.request.HTTPCookieProcessor()
#        opener = urllib.request.build_opener(cookieProcessor)
#        urllib.request.install_opener(opener)

    def _validate_access_token(self):
        if self.access_token_expiry > time.time():
            self._get_access_token(CLIENT_ID_SECRET)

    def _get_access_token(self, credentials):
        """Request Spotify's API for a token for performing non-user requests

        args:
            credentials (byte str): <spotify-client-id>:<spotify-client-secret>

        returns:
            json containing:
                'access_token': the access token
                'token_type': the type of access token, should be Bearer
                'expires_in: seconds until the token is invalid
        """

        access_token_data = urllib.parse.urlencode(
            {'grant_type':'client_credentials'}).encode(ENCODING)
        access_token_head = {'Authorization' : 'Basic {}'
            .format(b64encode(credentials).decode(ENCODING))}

        logging.info("Requesting Spotify for API-token")
        req = urllib.request.Request(   URL_ACCESS_TOKEN,
                                        data = access_token_data,
                                        headers = access_token_head)

        res = urllib.request.urlopen(req)
        access_token_json = json.loads(res.read().decode(ENCODING))
        logging.info("Received response: {}".format(access_token_json))

        self.access_token_expiry = time.time() + int(access_token_json['expires_in'])

        self.access_token_json = access_token_json

    def get_track_info(self, track_id):
        """Get and parse track info from Spotify

        Args:
            track_id (str): A Spotify track ID
                "4UoKkZIx4l2cMUoLUy5l5S", for example

        Returns:
            dictionary: Selected track information
        """
        self._validate_access_token()

        # Request Spotify for track info
        logging.info("Geting spotify track {}".format(track_id))
        track_head = {'Authorization' : '{} {}'.format(
            self.access_token_json['token_type'], 
            self.access_token_json['access_token'])}

        req = urllib.request.Request(   URL_GET_TRACK + track_id,
                                        headers = track_head)
        res = urllib.request.urlopen(req)

        track_json = json.loads(res.read().decode(ENCODING))

        # Parse track info json
        try:
            track = track_json['name']
            artists = [artist['name'] for artist in track_json['artists']]
            album = track_json['album']['name']
            art_url = max(track_json['album']['images'], key=lambda x:x['width'])['url']
            art_thumb_url = next(
                (image['url'] 
                    for image in track_json['album']['images'] 
                    if image['height'] <= ART_THUMB_SIZE or image['width'] <= ART_THUMB_SIZE), 
                None)

        except:
            logging.error("Failed to parse track info json: {}".format(track_json))
        
        track_info = {  'artists' : artists,
                        'album' : album,
                        'track' : track,
                        'art_url' : art_url,
                        'art_thumb_url' : art_thumb_url} 

        logging.info("Received track info: {}".format(track_info)) 

        return track_info
