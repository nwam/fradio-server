import os, sys
import datetime
import time
import urllib
import json
#sys.path.insert(0, '/var/www/html/flaskapp')
sys.path.append(os.path.dirname(__file__))
import fradiodb


from flask import Flask
from flask import request
app = Flask(__name__)

@app.route("/")
def hi():
    return "Hi"

# Tell the fradio server what song a user is listening to
@app.route("/broadcast")
def broadcast():
    # Get values from the request
    spotify_username = request.args.get('spotifyusername', type = str)
    spotify_track_id = request.args.get('spotifytrackid', type = str) 
    scroll_time = request.args.get('scrolltime', type = int)
    start_time = posix_time()


    # Send query to add broadcast
    broadcast = """INSERT INTO broadcast (spotifyUsername, spotifyTrackID, startTime, scrollTime) \
                    VALUES(%s, %s, %s, %s)"""
    broadcast_args = (spotify_username, spotify_track_id, start_time, scroll_time)
    fradiodb.transact(broadcast, broadcast_args)

    # Format and send response
    response = "Broadcasting: User: {}, SongID: {}, Time: {}, Scroll Time: {}".format(spotify_username, spotify_track_id, start_time, scroll_time)
    response = json.dumps({ 'status':'OK',
                            'spotify_username': spotify_username,
                            'spotify_track_id': spotify_track_id,
                            'start_time': start_time,
                            'scroll_time': scroll_time })

    # Let listeners know about the broadcast
    send_broadcast_to_listeners(spotify_username);

    return response

# Let the client know what song the host_username is listening to, and when
@app.route("/listen")
def listen():
    # Get values from the request
    host_spotify_username = request.args.get('hostspotifyusername', type = str) # TODO: change in client
    listener_spotify_username = request.args.get('listenerspotifyusername', type = str)
    request_ip_address = request.remote_addr
    
    # Check if listener exists
    get_listener = """SELECT spotifyUsername FROM user WHERE spotifyUsername = %s"""
    get_listener_args = (listener_spotify_username,)
    listner = fraidio.query(get_listener, get_listener_args)
    if listener == None:
        # Insert listener
        insert_listener = """INSERT INTO user (spotifyUsername, listening, ipAddress) \
                                VALUES (%s, %s, %s);"""
        insert_listener_args = (listener_spotify_username, rost_spotify_username, request_ip_address)
        fraidio.transact(insert_listener, insert_listener_args)
    else:
        # Set listener status
        listen = """UPDATE user SET listening = %s, ipAddress = %s WHERE spotifyUsername = %s;"""
        listen_args = (host_spotify_username, request_ip_address, listener_spotify_username)
        fradiodb.transact(listen, listen_args)

    # Get broadcast info
    get_broadcast_info = """SELECT spotifyTrackID, startTime, scrollTime FROM broadcast \
                        WHERE broadcastID IN (SELECT MAX(broadcastID) FROM broadcast WHERE spotifyUsername = %s);"""
    get_broadcast_info_args = (host_spotify_username,)
    try:
        spotify_track_id, start_time, scroll_time = fradiodb.query(get_broadcast_info, get_broadcast_info_args)
    except:
        return json.dumps({'status':'Error: The requested user could not be found'})

    track_time = int(posix_time() - start_time) + scroll_time

    # Format and send response with broadcast info
    response = json.dumps({  'status': 'OK',
                            'spotify_track_id': spotify_track_id,
                            'track_time': track_time,
                            'server_time': posix_time()})
    return response

def send_broadcast_to_listeners(host_spotify_username):
    pass
#    # Get list of listeners
#    get_listener_ips = """SELECT ipAddress FROM user WHERE listening = %s"""
#    get_listener_ips_args = (host_spotify_username,)
#    listner_ips = fradiodb.query_all(get_listener_ips, get_listener_ips_args)
#
#    # Send broadcast to list of listeners
#    for listener_ip in listner_ips:
#        listener_ip = listener_ip[0] # because listener_ips is a tuple of tuples
#        http = urllib.PoolManager()
#        request = http.request('POST', listener_ip 



def posix_time():
    return int(time.time()*1000)
