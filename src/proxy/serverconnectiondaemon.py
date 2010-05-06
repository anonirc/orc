"""
@author: Lars Vonli(lars@vonli.no)

"""
import threading
import socket
import time

import ircparse as parse


CONNECTIONS = {}

IDENT_CONNECTIONS = []
IDENT_RESPONSES = {}

class ServerConnectionDaemon(threading.Thread):
    """Opens connections to servers and polls for events
    on the socket object
    """

    def __init__(self):
        """
        """
        threading.Thread.__init__(self)

    def run(self):
        """
        Arguments:
        - `self`:
        """
        while 1:
            time.sleep(1)
            #goes through connections and calls ircParse's
            #on them, returning an Event object, or None
            if(CONNECTIONS):
                event_list = map(lambda x:parse.process_data(x, None), CONNECTIONS.items())
                event_list = filter(lambda x:x!=None, event_list)
                for events in event_list:
                    for event in events:
                        event.apply_handler()


def connect_to_server(nick, connection, server_address,
                          password=None, port=6667):
    """
    Arguments:
    - nick : The nick you wish to connect with
    - connection : the socket object wishing to establish a connection
    - server_address : the address of the external server
    - password: password on the receiving server
    - port: port with which you wish to connect
    """
    tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        tmp.connect((server_address, port))
        tmp.settimeout(.5)
        IDENT_RESPONSES[(tmp.getsockname()[1], port)] = "identOCTETstring"
        tmp = (tmp, server_address)
        CONNECTIONS[tmp] = connection
    except e:
        tmp =  None
    return tmp

def disconnect_from_server(server_socket_tuple):
    """ Takes a server_socket,disconnects and deletes it from the
    dictionary of connections.
    
    Arguments:
    - `server_socket_tuple`:
    """
    #TODO: Also fix idents
    server_socket_tuple[0].close()
    del CONNECTIONS[server_socket_tuple]

    

def accept_ident_connections():
    """ Accepts connections to 113 for ident responses
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 113))
    sock.listen(10)
    while 1:
        try:
            tmp = sock.accept()
            tmp[0].settimeout(.5)
            IDENT_CONNECTIONS.append(tmp)
        finally:
            time.sleep(1)
            
def respond_to_ident():
    """ Listens to the IDENT_CONNECTIONS, and responds
    to ident requests
    """
    if(IDENT_CONNECTIONS):
        data = map(_receive_or_none, IDENT_CONNECTIONS)
        data = filter(lambda x:x!=None, data)
        for d in data:
            d[0].strip().split(",")
            if(IDENT_RESPONSES.has_key((int(d[0][0]),int(d[0][1])))):
                print IDENT_RESPONSES[(int(d[0][0]),int(d[0][1]))]
                d[1][0].send(d[0][0]+d[0][1]+" :USERID:UNIX:"+IDENT_RESPONSES[(int(d[0][0]),int(d[0][1]))]+"\r\n")

def _receive_or_none(sock):
    try:
        tmp = (sock[0].recv(2**14), sock)
        return tmp
    except socket.error, err:
        return None
