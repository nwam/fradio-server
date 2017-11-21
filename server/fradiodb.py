import MySQLdb
import json
import util

STATUS_OK = "OK"

IS_PLAYING = 1
IS_PAUSED = 0
IS_STOPPED = -1

############################
# Generic db helper methods
############################

# Returns one row obtained from the query
def query(q, args=None, cols=None):
    cursor = MySQLdb.connect(user='root', db='fradio').cursor()
    cursor.execute(q, args)
    query_response = cursor.fetchone()

    return query_response

# Returns one row obtained from the query
def query_all(q, args=None, cols=None):
    cursor = MySQLdb.connect(user='root', db='fradio').cursor()
    cursor.execute(q, args)
    query_response = cursor.fetchall()

    return query_response

# Commits a query, returns number of rows changed
def transact(q, args=None):
    connection = MySQLdb.connect(user='root', db='fradio')
    cursor = connection.cursor()
    rows_changed = cursor.execute(q, args)
    connection.commit()

    return rows_changed


###########################
# Non-generic db functions
###########################

def add_broadcast(username, track_id, start_time, scroll_time, trackLength, is_playing):
    broadcast = """INSERT INTO broadcast (spotifyUsername, spotifyTrackID, startTime, scrollTime, trackLength, isPlaying) \
                    VALUES(%s, %s, %s, %s, %s, %s)"""
    broadcast_args = (username, track_id, start_time, scroll_time, trackLength, is_playing)
    return transact(broadcast, broadcast_args)

# Returns if username is found in user TABLE
def user_exists(spotify_username):
    get_listener = """SELECT spotifyUsername FROM user WHERE spotifyUsername = %s"""
    get_listener_args = (spotify_username,)
    listener = query(get_listener, get_listener_args)
    return listener != None

def update_user(user, listening, ip_address):
    listen = """UPDATE user SET listening = %s, ipAddress = %s WHERE spotifyUsername = %s;"""
    listen_args = (listening, ip_address, user)
    return transact(listen, listen_args)

def add_user(user, listening, ip_address):
    insert_listener = """INSERT INTO user (spotifyUsername, listening, ipAddress) \
                            VALUES (%s, %s, %s);"""
    insert_listener_args = (user, listening, ip_address)
    return transact(insert_listener, insert_listener_args)

# Gets and formats a user's most recent broadcast
def get_broadcast_json(username):
    # Get broadcast info
    get_broadcast_info = """SELECT spotifyTrackID, startTime, scrollTime, trackLength, broadcastID, isPlaying FROM broadcast \
                        WHERE broadcastID IN (SELECT MAX(broadcastID) FROM broadcast WHERE spotifyUsername = %s);"""
    get_broadcast_info_args = (username,)
    try:
        spotify_track_id, start_time, scroll_time, track_length, broadcast_id, is_playing = query(get_broadcast_info, get_broadcast_info_args)
    except:
        return json.dumps({'status':'Error: The requested user could not be found'})

    track_time = int(util.posix_time() - start_time) + scroll_time

    # Format and send response with broadcast info
    j = json.dumps({'status': STATUS_OK,
                    'broadcast_id': broadcast_id,
                    'spotify_track_id': spotify_track_id,
                    'track_time': track_time,
                    'server_time': util.posix_time(),
                    'track_length' : track_length,
                    'is_playing': is_playing})

    return j

def get_streamers():
    get_streamers = """SELECT spotifyUsername, isPlaying FROM broadcast WHERE isPlaying >= 0 AND broadcastID IN (SELECT MAX(broadcastID) FROM broadcast GROUP BY spotifyUsername) AND startTime + trackLength - scrollTime + 1000 > UNIX_TIMESTAMP() * 1000;""" 
    streamers = query_all(get_streamers)
    streamers = [{'name':streamer[0], 'status':streamer[1]} for streamer in streamers]
   
    return streamers

def get_users():
    get_users = """SELECT spotifyUsername, listening FROM user;"""
    users = query_all(get_users)
    users = [{'name':user[0], 'listening':user[1]} for user in users]
    return users

def disconnect_user(user):
    stop_listening(user)
    stop_streaming(user)

# Insert data which allows queries to determine user status
def stop_listening(user):
    stop_listening = """UPDATE user SET listening = NULL WHERE spotifyUsername = %s;"""
    stop_listening_args = (user,)
    return transact(stop_listening, stop_listening_args);

# Insert data which allows queries to determine streamer status
def stop_streaming(user):
    stop_streaming = """INSERT INTO broadcast (spotifyUsername, isPlaying) \
                        VALUES (%s, %s);"""
    stop_streaming_args = (user, IS_STOPPED)
    return transact(stop_streaming, stop_streaming_args);
