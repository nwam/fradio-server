import fradiodb

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

TOKEN_TYPE = "Bearer"

def _init_logging():
    logging.basicConfig(level=logging.INFO, 
        filename="fradio-server-spotify.log", 
        format='%(asctime)s %(message)s')

def _get_valid_access_token():
    access_token, access_token_expire = fradiodb.get_access_token()
    if access_token_expire < time.time():
        access_token = _get_new_access_token(CLIENT_ID_SECRET)
    return access_token

def _get_new_access_token(credentials):
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

    # Store the new access token in the database
    access_token_expiry = int(time.time()) + int(access_token_json['expires_in'])
    access_token_value = access_token_json['access_token']
    fradiodb.store_access_token(access_token_value, access_token_expiry)

    return access_token_value

def get_track_info(track_id):
    """Get and parse track info from Spotify

    Args:
        track_id (str): A Spotify track ID
            "4UoKkZIx4l2cMUoLUy5l5S", for example

    Returns:
        dictionary: Selected track information
    """
    _init_logging()
    access_token = _get_valid_access_token()

    # Request Spotify for track info
    logging.info("Geting spotify track {}".format(track_id))
    track_head = {'Authorization' : '{} {}'.format(
        TOKEN_TYPE, #access_token_json['token_type'], 
        access_token)}

    # Get a new token if the first one doest work
    for i in range(2):
        try:
            req = urllib.request.Request(   URL_GET_TRACK + track_id,
                                            headers = track_head)
            res = urllib.request.urlopen(req)
            break
        except:
            logging.error("Error getting track information from Spotify")
            access_token = _get_new_access_token(CLIENT_ID_SECRET)
            return None

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
    
    track_info = {  'id': track_id,
                    'artists' : artists,
                    'album' : album,
                    'track' : track,
                    'art_url' : art_url,
                    'art_thumb_url' : art_thumb_url} 

    logging.info("Received track info: {}".format(track_info)) 

    return track_info
