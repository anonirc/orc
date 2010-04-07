""" Defines the incomingConnectionDaemon class
"""
import threading
import thread
import socket
import time

import ircparse as parse

#connections[] holds a tuple containing the socket object of a connection,
#and the socket object of the server it's connected to
CONNECTIONS = {}

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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(self.backlog)
        
        orcbot = sock.accept()
        orcbot[0].settimeout(.5)
        print "OrcBot connected"
        print orcbot
        #starts the method that looks for events in connections
        spawn_look_for_events(CONNECTIONS, orcbot)
        #first connection should be from orcbot
        
        while 1:
            try:
                tmp = sock.accept()
                tmp[0].settimeout(.5)
                tmp[0].send(":orcbot 001 orcbot :Welcome to ORC. Type " +
                            "/msg orcbot to begin.\r\n")
                CONNECTIONS[tmp] = None
                print("connected")
            finally:
                time.sleep(1)
                
def spawn_look_for_events(lconnections, orcbot):
    """Starts the look_for_events function in  new thread
    and passes connections to it
    """
    try:
        thread.start_new_thread(look_for_events, (lconnections, orcbot))
    except :
        print "Error: unable to start thread"
        
def look_for_events(lconnections, orcbot):
    """
    Looks for new data in all connections
    Arguments: host, connectxions
    """
    while 1:
        #TODO: remove this when the app doesnt kill all performance anymore
        time.sleep(1)
        if(lconnections):
            print "loopin'"
            #goes through connections and calls ircParse's process_data
            #on them, returning an Event object, or None
            events = map(lambda x:parse.process_data(x, orcbot), 
                                            lconnections.items())
            #filters out the None's, in other words the ones without new data
            events = filter(lambda x:x!=None, events)
            for socket_events in events:
                for socket_event in socket_events:
                    socket_event.apply_handler()
            orcbot_events = parse.process_data((orcbot, None), orcbot)
            if orcbot_events:
                for orcbot_event in orcbot_events:
                    orcbot_event.apply_handler()
        
def add_target(connection, target):
    '''
    '''
    CONNECTIONS[connection] = target
