import socket

#########################################
# Functions for sending broadcasts to clients
# Replaced by a hack in fradio-client
#########################################

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

def prepend_message_size(message):
    return "{}\n{}".format(len(message), message)
