import os, sys
import datetime
import time
import json
sys.path.append(os.path.dirname(__file__))
import fradiodb


from flask import Flask
from flask import request
app = Flask(__name__)

# Tell the fradio server what song a user is listening to
@app.route("/broadcast")
def broadcast():
    broadcast = """INSERT INTO broadcast (spotifyUsername, spotifyTrackID, startTime, scrollTime) \
                    VALUES(%s, %s, %s, %s)"""

    # Get values from the request
    spotify_username = request.args.get('spotifyusername', type = str)
    spotify_track_id = request.args.get('spotifytrackid', type = str) 
    scroll_time = request.args.get('scrolltime', type = int)
    start_time = posix_time()

    # Send query
    broadcast_args = (spotify_username, spotify_track_id, start_time, scroll_time)
    fradiodb.transact(broadcast, broadcast_args)

    response = "Broadcasting: User: {}, SongID: {}, Time: {}, Scroll Time: {}".format(spotify_username, spotify_track_id, start_time, scroll_time)
    response = json.dumps({ 'status':'OK',
                            'spotify_username': spotify_username,
                            'spotify_track_id': spotify_track_id,
                            'start_time': start_time,
                            'scroll_time': scroll_time })

    return response

# Let the client know what song the host_username is listening to, and when
@app.route("/listen")
def listen():
    listen = """SELECT spotifyTrackID, startTime, scrollTime FROM broadcast \
                        WHERE broadcastID IN (SELECT MAX(broadcastID) FROM broadcast WHERE spotifyUsername = %s);"""

    # Get values from the request
    host_spotify_username = request.args.get('spotifyusername', type = str)

    # Get broadcast info
    listen_args = (host_spotify_username,)
    try:
        spotify_track_id, start_time, scroll_time = fradiodb.query(listen, listen_args)
    except:
        return json.dumps({'status':'Error: The requested user could not be found'})

    track_time = int(posix_time() - start_time) + scroll_time

    # Format response
    response = json.dumps({  'status': 'OK',
                            'spotify_track_id': spotify_track_id,
                            'track_time': track_time,
                            'server_time': posix_time()})
    return response

def posix_time():
    return int(time.time()*1000)
