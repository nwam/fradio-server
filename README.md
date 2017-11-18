# Requests
## start stream
    - track id
    - streamer id
    - start time

## join stream
    - listener id
    - streamer id

## create/delete/update user
    - user id
    - other info

## check for stream
    - streamer id

## follow
    - listener id

# Client
## login

# TODO
- client sends system time of request to eliminate lag
- add play/pause to request/db
- account for broadcaster switching song by having client listen and having server send message to all listeners about song change (not ez)
