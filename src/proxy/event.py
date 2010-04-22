import socket
import re
import random
import serverconnectiondaemon as server
import incomingconnections as incoming

# Holds the made up nicks that each connection has when talking
# with ORCBot
SOCKET_TO_USERID = {}
USERID_TO_SOCKET = {}
ALPHABET = "abcdefghijklmnopqrstuvwxABCDEFGHIJKLMNOPQRSTUVWX"
USERID_LENGTH = 8
BANHANDLER = None
VALIDATED_USERS = None

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
        self.orcbot_socket = orcbot  

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

    def join(self):
        channel = self.data[0]
        target_server = self.target[1]        
        user_pseudonym =  VALIDATED_USERS.get_pseudonym(SOCKET_TO_USERID.get(self.source, None))
        
        if user_pseudonym:
            if(BANHANDLER.is_banned_from_channel(user_pseudonym, target_server, channel)):
                self.source[0].send(":orcbot!~@localhost PRIVMSG "+SOCKET_TO_USERID[self.source]+" :You're banned from "+channel+"\r\n")
            elif(self.target):
                self.message = self.message +"\r\n"
                self.target[0].sendall(self.message)
        elif(self.target):
            self.message = self.message +"\r\n"
            self.target[0].sendall(self.message)
    
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
        # print "Raw message"
#         print self.message
#         print "****Source**"
#         print self.source
        #if message is for orcbot, set orcbot as target
        if(self.data[0]=="orcbot"):
            print "target is orcbot"
            self.target = self.orcbot_socket
            self.message = ":" + SOCKET_TO_USERID[self.source] + "!~@localhost "+ self.message
        if(self.source == self.orcbot_socket):
            print "source is orcbot"
            self.target = USERID_TO_SOCKET[self.data[0]]
            self.message = ":orcbot!~@localhost " + self.message
        self.message = self.message + "\r\n"
       #  print "*******target**"
#         print self.target
#         print "*******message to send"
#         print self.message
        if(self.target):
            try:
                self.target[0].sendall(self.message)
            except socket.error, err:
                print "can't send"
                print err
                
    def mode(self):
        """Detect if a mode message contains a ban
        for the current user, if so, adds it to the ban database, before
        it passes the message on
        """
        if(len(self.data)==3):
            print self.data
            if re.match("\+b", self.data[1]):
                #TODO: Currently you'll get banned if anyone with your username is banned
                #TODO: Detect the difference between klines and channelbans
                username = SOCKET_TO_USERID[self.target]                
                banned_user = self.data[2].split("!")[1].split("@")[0]
                if(username == banned_user):
                    print "about to be BANNED", username, "   ", banned_user
                    user_pseudonym = VALIDATED_USERS.get_pseudonym(username)
                    network = self.source[1]
                    BANHANDLER.add_ban(10080, user_pseudonym, network, self.data[0], 0)
        if(self.target):
            self.message = self.message +"\r\n"
            self.target[0].send(self.message)


    def nick(self):
        if(not SOCKET_TO_USERID.has_key(self.source)):
            new_userid = _char_list_to_string(random.sample(ALPHABET, USERID_LENGTH))
            while(USERID_TO_SOCKET.has_key(new_userid)):
                new_userid = _char_list_to_string(random.sample(ALPHABET, USERID_LENGTH))
            USERID_TO_SOCKET[new_userid] = self.source
            SOCKET_TO_USERID[self.source] = new_userid
        elif(self.target):
            self.message = self.message +"\r\n"
            self.target[0].send(self.message)

def connect(userid, server_address = "irc.oftc.net",
            port = 6667,nick = None, password = None):
    ''' Connects a user to an IRC server and handles initial user
    registration
    '''
    if(not nick):
        nick = userid
    user_connection = USERID_TO_SOCKET[userid]
    server_connection = server.connect_to_server( userid,
                                                  USERID_TO_SOCKET[userid],
                                                  server_address,
                                                  password,
                                                  port)
    incoming.add_target(user_connection, server_connection)
    server_connection[0].send("NICK " + nick + "\r\n")
    server_connection[0].send("USER " + userid + " orc orc :orc \r\n")

def _char_list_to_string(char_list):
    """ Takes a list of chars and returns a string"""
    ret = ""
    for i in char_list:
        ret+=i
    return ret
