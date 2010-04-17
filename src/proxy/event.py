import socket
import random
import serverconnectiondaemon as server
import incomingconnections as incoming

# Holds the made up nicks that each connection has when talking
# with ORCBot
SOCKET_TO_NICK = {}
NICK_TO_SOCKET = {}
ALPHABET = "abcdefghijklmnopqrstuvwxABCDEFGHIJKLMNOPQRSTUVWX"
NICK_LENGTH = 8

class Event:
    """ Holds the type and handler function for irc events """

    def __init__(self, event_type, source, target, orcbot, raw, data=None):
        """
        Holds an event with event type, source, target,
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
        """ The code that calls the event handler for the event type """
        print "handlin'"
        tmp = self.event_type
        if hasattr(self, tmp):
            getattr(self, tmp)()
        elif(self.target):
            self.message = self.message +"\r\n"
            self.target[0].send(self.message)

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
        
    def ping(self):
        ''' 
        If irssi or other client tries to ping ORC while
        the user is not connected, return a pong.
        Else some clients disconnect.
        '''
        # If it's the ORC proxy being pinged, return a pong.
        if(self.data[0] == "ORC"):
            self.message = "PONG " + self.data[0] + "\r\n"
            self.source[0].send(self.message)
        # If user connected to another IRC server, forward the ping.
        elif(self.target):
            self.target[0].send(self.message + "\r\n")
        
        
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
            self.message = ":" + SOCKET_TO_NICK[self.source] + "!~@localhost "+ self.message

        if(self.source == self.orcbot):
            print "source is orcbot"
            self.target = NICK_TO_SOCKET[self.data[0]]
            self.message = ":orcbot!~@localhost " + self.message
        self.message = self.message + "\r\n"
        print "*******target**"
        print self.target
        print "*******message to send"
        print self.message
        if(self.target):
            try:
                self.target[0].sendall(self.message)
            except socket.error, err:
                print "can't send"
                print err

    def nick(self):
        print "Assigning nick"
        if(not SOCKET_TO_NICK.has_key(self.source)):
            new_nick = char_list_to_string(random.sample(ALPHABET, NICK_LENGTH))
            while(NICK_TO_SOCKET.has_key(new_nick)):
                new_nick = char_list_to_string(random.sample(ALPHABET, NICK_LENGTH))
            NICK_TO_SOCKET[new_nick] = self.source
            SOCKET_TO_NICK[self.source] = new_nick
        else:
            self.message = self.message +"\r\n"
            self.target[0].send(self.message)

def connect(nick, server_address = "irc.oftc.net",
            port = 6667, password = None):
    ''' Connects a user to a IRC server '''
    user_connection = NICK_TO_SOCKET[nick]
    server_connection = server.connect_to_server( nick,
                                                  NICK_TO_SOCKET[nick],
                                                  server_address,
                                                  password,
                                                  port)    
    incoming.add_target(user_connection, server_connection)
    server_connection[0].send("NICK " + nick + "\r\n")
    server_connection[0].send("USER " + nick + " orc orc :orc \r\n")

def char_list_to_string(char_list):
    ret = ""
    for i in char_list:
        ret+=i
    return ret
