import threading
import socket

import ircParse as parse


connections=[]

class ServerConnectionDaemon(threading.Thread):
    """Opens connections to servers and polls for events
    on the socket object
    TODO skrive fornuftig docstring
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
            """goes through connections and calls ircParse's
            on them, returning an Event object, or None
              """
            events=map(lambda x:parse.process_data(x), connections)
            events=filter(lambda x:x!=None, events)
            for e in events:
                e.printC()

    def connect_to_server(nick, connection, server_address, password=None, port=6667):
        """
        Arguments:
        - nick:
        - connection :
        - server_address:
        - password:
        """
        #TODO Write messages for sending nick password and identifing information to IRC
        tmp=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp.connect((server_address, port))

        #Adds the connection to the list of Sockets to pull for events
        connection.append(tmp)
    
    
        
        

