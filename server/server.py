import fradiodb

# Tell the fradio server what song a user is listening to
# This will either be done through lastFM or directly from the client
def broadcast(username, songID, time, scroll_time):
    pass

# Stream the music that username_radio is listening to
# Query username_radio's current song from fradiodb.playing,
# then stream from Spotify to username's device
def listen(username_radio, username):
    pass

