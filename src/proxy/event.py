import string
import socket
import serverconnectiondaemon as server
import incomingconnections as incoming

#holds the made up nicks that each connection has when talking
#with orcbot
socket_to_nick = {}
nick_to_socket = {}
""" Defines the Event class
"""
class Event:
    """Holds the type and handler function for irc events
    """

    def __init__(self, event_type, source, target, orcbot, raw, data=None):
        """Holds an event with event type, source, target,
        and optionally data needed for the event
        """
        self.event_type = event_type
        self.source = source
        self.target = target
        self.data = data
        self.socket = source
        self.message = raw
        self.orcbot = orcbot  

    def apply_handler(self):
        """the code that calls the event handler for the event
        type
        """
        print "handlin'"
        tmp = self.event_type
        if hasattr(self, tmp):
            #if message is for orcbot, set orcbot as target
            if(self.data[0]=="orcbot"):
                print "target = orcbot"
                self.target = self.orcbot
            
            getattr(self, tmp)()

    def get_type(self):
        """ Gets the type of an event"""
        return self.event_type
   
    def get_source(self):
        """ Gets the source of an event"""
        return self.source
   
    def get_target(self):
        """Gets the target"""
        return self.target
   
    def get_data(self):
        """Gets the data"""
        return self.data
   
    def printC(self):
        """print function, used for debugging/testing"""
        print(self.event_type)

    def error(self):
        """TODO:
        """
        
    def join(self):
        """TODO:
        """
                         
    def kick(self):
        """TODO
        """
    def mode(self):
        """TODO
        """
        
    def part(self):
        """TODO
        """
        
    def ping(self):
        """TODO
        """
        
    def privmsg(self):
        """ Handles privmsg event
        """
        print "Raw message"
        print self.message
        print "****Source**"
        print self.source
        #if message is for orcbot, set orcbot as target
        if(self.data[0]=="orcbot"):
            print "target is orcbot"
            self.target = self.orcbot
            self.message = ":" + socket_to_nick[self.source] + "!~@localhost " + self.message

        if(self.source == self.orcbot):
            print "source is orcbot"
            self.target = nick_to_socket[self.data[0]]
            self.message = ":orcbot!~@localhost "+self.message
        self.message = self.message +"\r\n"
        print "*******target**"
        print self.target
        print "*******message to send"
        print self.message
        #TODO alter message to reflect hostmasks and such
        try:
            self.target[0].sendall(self.message)
        except socket.error, err:
            print "can't send"
            print err
        
            
    def privnotice(self):
        """TODO
        """
        
    def pubmsg(self):
        """TODO
        """
    def nick(self):
        print "Assigning nick"
        nick_to_socket[self.data[0]] = self.source
        socket_to_nick[self.source] = self.data[0]
        
    def pubnotice(self):
        """TODO
        """
    def quit(self):
        """TODO
        """

    def invite(self):
        """TODO
        """
    def pong(self):
        """TODO
        """
def connect(nick, server_address = "irc.oftc.net",
            port = 6667, password = None):
    incoming.add_target(nick_to_socket[nick],
                        server.connect_to_server(
                            nick, nick_to_socket[nick],
                            server_address, password, port))

