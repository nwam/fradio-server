import os, sys
import json
sys.path.append(os.path.dirname(__file__))
import fradiodb
import send_broadcasts
import util
import glob
import io

from flask import Flask
from flask import request
from flask import send_file

app = Flask(__name__)

CLIENT_PORT = 16987
ENCODING = 'utf-8'

STATUS_OK = "OK"

@app.route("/")
def hi():
    return "Say hello to the Fradio server"

# Tell the fradio server what song a user is listening to
# And tell all the listeners about the song change
@app.route("/broadcast")
def broadcast():

    # Get values from the incoming request
    spotify_username = request.args.get('spotifyusername', type = str)
    spotify_track_id = request.args.get('trackid', type = str) 
    scroll_time = request.args.get('t', type = int)
    track_length = request.args.get('len', type = int)
    is_playing = request.args.get('playing', type = int)
    start_time = util.posix_time()

    # Add track information to db
    fradiodb.store_track_info(spotify_track_id)

    # Send query to add broadcast
    fradiodb.add_broadcast(spotify_username, spotify_track_id, start_time, scroll_time, track_length, is_playing)

    # The hack is living on :'(
    # Let listeners know about the broadcast
    # send_broadcasts.send_message_to_listeners(spotify_username, get_broadcast_json(spotify_username));

    # Format and send response
    return json.dumps({ 'status':STATUS_OK })

# Let the client know what song the host_username is listening to, and when
@app.route("/listen")
def listen():
    # Get values from the incoming request
    host_spotify_username = request.args.get('hostspotifyusername', type = str) 
    listener_spotify_username = request.args.get('listenerspotifyusername', type = str)
    request_ip_address = request.remote_addr
    
    # Update listener status
    if fradiodb.user_exists(listener_spotify_username):
        fradiodb.update_user(listener_spotify_username, host_spotify_username, request_ip_address)
    else:
        fradiodb.add_user(listener_spotify_username, host_spotify_username, request_ip_address)

    # Send broadcast info
    response = fradiodb.get_broadcast_json(host_spotify_username)
    return response

# Let the db know that a user is not listening
@app.route("/stop_listen")
def stop_listen():
    username = request.args.get('spotifyusername', type = str) 
    fradiodb.stop_listening(username)
    return json.dumps({'status': STATUS_OK })

# Let the db know that a user is not streaming
@app.route("/stop_stream")
def stop_stream():
    username = request.args.get('spotifyusername', type = str) 
    fradiodb.stop_streaming(username)
    return json.dumps({'status': STATUS_OK })

@app.route("/disconnect")
def disconnect():
    username = request.args.get('spotifyusername', type = str) 
    fradiodb.disconnect_user(username)
    return json.dumps({'status': STATUS_OK })

# Returns list of all users who are currently streaming
@app.route("/streamers")
def get_streamers():
    streamers = fradiodb.get_streamers()
    response = json.dumps(streamers)
    response = '{"streamers":' + response + '}'
    return response

# Get a list of all users and their current status
@app.route("/users")
def get_users():
    users = fradiodb.get_users()
    response = json.dumps(users)
    response = '{"users":' + response + '}'
    return response
