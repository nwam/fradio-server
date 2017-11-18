import os, sys
import datetime
sys.path.append(os.path.dirname(__file__))
import fradiodb


from flask import Flask
from flask import request
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hi"

# Tell the fradio server what song a user is listening to
# This will either be done through lastFM or directly from the client
@app.route("/broadcast")
def broadcast():
    broadcast = """INSERT INTO playing (spotifyUsername, spotifyTrackID, startTime, scrollTime) \
                    VALUES(%s, %s, %s, %s)"""

    # Get values from the request
    spotify_username = request.args.get('spotifyusername', type = str)
    spotify_track_id = request.args.get('spotifytrackid', type = str) 
    scroll_time = request.args.get('scrolltime', type = long)

    # Get current time formatted as SQL input
    now = datetime.datetime.now() 
    start_time = "{}-{}-{} {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)

    # Send query
    broadcast_args = (spotify_username, spotify_track_id, start_time, scroll_time)
    fradiodb.transact(broadcast, broadcast_args)

    response = "Broadcasting: User: {}, SongID: {}, Time: {}, Scroll Time: {}".format(spotify_username, spotify_track_id, start_time, scroll_time)
    return response

# Stream the music that username_radio is listening to
# Query username_radio's current song from fradiodb.playing,
# then stream from Spotify to username's device
def listen(username_radio, username):
    pass
