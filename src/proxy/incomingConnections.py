""" Defines the incomingConnectionDaemon class
"""
import threading
import thread
import socket

import ircParse as parse

#connections[] holds a tuple containing the socket object of a connection,
#and the socket object of the server it's connected to
connections = {}

class IncomingConnectionDaemon(threading.Thread):
    """ Class for receiving incoming connections and handle
    incoming traffic
    """
    def init(self, host, port):
        """Threading.Thread does not like having it's __init__
        overridden, thus the necessity for a different init method
        """
        self.host = host
        self.port = port
        self.backlog = 10
        self.size = 1024
        threading.Thread.__init__(self)
    
    def run(self):
        """ Starts listening to a socket and adds
        incoming connections to the connections array
        """
        print "-----------------------"
        print self.host
        print self.port
        print "-----------------------"
        #Instantiates a socket object and binds it to a port.
        SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCK.bind((self.host,self.port))
        SOCK.listen(self.backlog)
        #An array to keep incoming connection
        spawn_look_for_events(self.host, connections)
        #Accepts new connections
        while 1:
            connections[SOCK.accept()]= None
            print("connected")

def spawn_look_for_events(lhost, lconnections):
    """Starts the look_for_events function in  new thread
    and passes connections to it
    """
    try:
        thread.start_new_thread(look_for_events, (lhost, lconnections, ))
    except :
        print "Erro: unable to start thread"
        
def look_for_events(host, lconnections):
    """
    Looks for new data in all connections
    Arguments: host, connectxions
    """
    while 1:
        #goes through connections and calls ircParse's process_data
        #on them, returning an Event object, or None
        events = map(lambda x:parse.process_data(x), lconnections.items())
        #filters out the None's, in other words the ones without new data
        events = filter(lambda x:x!=None, events)
        for ev in events:
            ev.apply_handler()
        
def add_target(connection, target):
    connections[connection]=target
