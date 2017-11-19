import os, sys
import datetime
import time
import socket
import json
sys.path.append(os.path.dirname(__file__))
import fradiodb


from flask import Flask
from flask import request
app = Flask(__name__)

CLIENT_PORT = 16987
ENCODING = 'utf-8'

@app.route("/")
def hi():
    return "Hi"

# Tell the fradio server what song a user is listening to
# And tell all the listeners about the song change
@app.route("/broadcast")
def broadcast():
    # Get values from the incoming request
    spotify_username = request.args.get('spotifyusername', type = str)
    spotify_track_id = request.args.get('trackid', type = str) 
    scroll_time = request.args.get('t', type = int)
    track_length = request.args.get('len', type = int)
    is_playing = request.args.get('isplaying', type = bool)
    start_time = posix_time()

    # Send query to add broadcast
    add_broadcast(spotify_username, spotify_track_id, start_time, scroll_time, track_length, is_playing)

    # Let listeners know about the broadcast
    # send_message_to_listeners(spotify_username, get_broadcast_json(spotify_username));

    # Format and send response
    response = json.dumps({ 'status':'OK' })
                            #'spotify_username': spotify_username,
                            #'spotify_track_id': spotify_track_id,
                            #'start_time': start_time,
                            #'scroll_time': scroll_time })
    return response

# Let the client know what song the host_username is listening to, and when
@app.route("/listen")
def listen():
    # Get values from the incoming request
    host_spotify_username = request.args.get('hostspotifyusername', type = str) # TODO: change in client
    listener_spotify_username = request.args.get('listenerspotifyusername', type = str)
    request_ip_address = request.remote_addr
    
    # Update listener status
    if user_exists(listener_spotify_username):
        update_user(listener_spotify_username, host_spotify_username, request_ip_address)
    else:
        add_user(listener_spotify_username, host_spotify_username, request_ip_address)

    # Send broadcast info
    response = get_broadcast_json(host_spotify_username)
    return response

# Returns list of streamers to listen to
# (all of them for now)
@app.route("/streamers")
def get_streamers():
    get_streamers = """SELECT DISTINCT spotifyUsername FROM broadcast;"""
    streamers = fradiodb.query_all(get_streamers);  
    streamers = [streamer[0] for streamer in streamers]

    response = json.dumps({'streamers':streamers})
    return response

def add_broadcast(username, track_id, start_time, scroll_time, trackLength, is_playing):
    broadcast = """INSERT INTO broadcast (spotifyUsername, spotifyTrackID, startTime, scrollTime, trackLength, isPlaying) \
                    VALUES(%s, %s, %s, %s, %s, %s)"""
    broadcast_args = (username, track_id, start_time, scroll_time, trackLength, is_playing)
    return fradiodb.transact(broadcast, broadcast_args)

def user_exists(spotify_username):
    get_listener = """SELECT spotifyUsername FROM user WHERE spotifyUsername = %s"""
    get_listener_args = (spotify_username,)
    listener = fradiodb.query(get_listener, get_listener_args)
    return listener != None

def update_user(user, listening, ip_address):
    listen = """UPDATE user SET listening = %s, ipAddress = %s WHERE spotifyUsername = %s;"""
    listen_args = (listening, ip_address, user)
    return fradiodb.transact(listen, listen_args)

def add_user(user, listening, ip_address):
    # Insert listener
    insert_listener = """INSERT INTO user (spotifyUsername, listening, ipAddress) \
                            VALUES (%s, %s, %s);"""
    insert_listener_args = (user, listening, ip_address)
    return fradiodb.transact(insert_listener, insert_listener_args)

def get_broadcast_json(username):
    # Get broadcast info
    get_broadcast_info = """SELECT spotifyTrackID, startTime, scrollTime, trackLength, broadcastID FROM broadcast \
                        WHERE broadcastID IN (SELECT MAX(broadcastID) FROM broadcast WHERE spotifyUsername = %s);"""
    get_broadcast_info_args = (username,)
    try:
        spotify_track_id, start_time, scroll_time, track_length, broadcast_id = fradiodb.query(get_broadcast_info, get_broadcast_info_args)
    except:
        return json.dumps({'status':'Error: The requested user could not be found'})

    track_time = int(posix_time() - start_time) + scroll_time

    # Format and send response with broadcast info
    j = json.dumps({'status': 'OK',
                    'broadcast_id': broadcast_id,
                    'spotify_track_id': spotify_track_id,
                    'track_time': track_time,
                    'server_time': posix_time(),
                    'track_length' : track_length})
    return j

def send_message_to_listeners(host_spotify_username, message):

    # Get list of listeners
    get_listener_ips = """SELECT ipAddress FROM user WHERE listening = %s"""
    get_listener_ips_args = (host_spotify_username,)
    listner_ips = fradiodb.query_all(get_listener_ips, get_listener_ips_args)

    # Send message to list of listeners
    for listener_ip in listner_ips:
        listener_ip = listener_ip[0] # because listener_ips is a tuple of tuples
        
        send_tcp_message(listener_ip, CLIENT_PORT, message)

def send_tcp_message(ip, port, message):
    sock = _connect_tcp((ip,port))
    print("Sending message to {}:{}:\n{}".format(ip,port,message))

    if sock is None:
        return None
    sock.send(prepend_message_size(bytes(message, ENCODING)))
    sock.close()


    return None

def _connect_tcp(connectinfo):
    """
    Connect to the device using the given IP, port pairing
    :return: The created TCP socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect(connectinfo)
    except OSError as e:
        print('Connection error')
        print(str(e))
        return None
    except (EOFError, KeyboardInterrupt):
        print('Connect cancelled')
        return None

def posix_time():
    return int(time.time()*1000)

def prepend_message_size(message):
    return "{}\n{}".format(len(message), message)
