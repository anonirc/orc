"""
@author: Lars Vonli(lars@vonli.no)
See LICENSE for licensing information.

"""

import socket
import re
import random
import time
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
#Holds the time to wait between connections to server. To avoid being
#denied access to some IRCd's.   Given in seconds
QUEUE_TIME = 5
CONNECTION_TIMESTAMPS = {}

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

    def connection_closed(self):
        """ Handles connection closed events

        Arguments:
        - `self`:
        """
        if(SOCKET_TO_USERID.has_key(self.source)):
            if( VALIDATED_USERS.is_validated(SOCKET_TO_USERID[self.source])):
                VALIDATED_USERS.remove_user(self.source)
            tmp = incoming.disconnect_user(self.source)
            if(tmp):
                server.disconnect_from_server(tmp)
        elif(server.CONNECTIONS.has_key(self.source)):
            tmp = server.disconnect_from_server(self.source)
            incoming.disconnect_user(tmp)

    def notice(self):
        """ Handles notices. Checks for serverbans and handles those,
        otherwise sends them on. No support for the difference between
        klines,  and glines(treats all as klines).
        Arguments:
        - `self`:
        """
        if(self.data[1][0:18:] == "*** You are banned"):
            username = SOCKET_TO_USERID[self.target]
            user_pseudonym = VALIDATED_USERS.get_pseudonym(username)
            network = self.source[1]
            BANHANDLER.add_ban(10080, user_pseudonym, network, self.data[0], 1)
            self.message = self.message + "\r\n :orcbot!@localhost PRIVMSG "+SOCKET_TO_USERID[self.source]+" :You've been banned from this server"

        self.send()

    def join(self):
        """Checks if a pseudonym is banned from a channel, if it is you are denied
        access. If not, sends the join message on to the remote IRC server
        """
        channel = self.data[0]
        user_pseudonym =  VALIDATED_USERS.get_pseudonym(SOCKET_TO_USERID.get(self.source, None))

        if user_pseudonym and self.target:
            target_server = self.target[1]
            if(BANHANDLER.is_banned_from_channel(user_pseudonym, target_server, channel)):
                self.source[0].send(":orcbot!~@localhost PRIVMSG "+SOCKET_TO_USERID[self.source]+" :You're banned from "+channel+"\r\n")
            elif(self.target):
                self.message = self.message +"\r\n"
                self.target[0].sendall(self.message)
        self.send()

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
        self.send()


    def privmsg(self):
        """ If a privmsg is for orcbot, it's target is set to orcbot. The message
        is then sent to event.target, unless it doesnt have one
        """
        if(self.data[0]=="orcbot"):
            print "target is orcbot"
            self.target = self.orcbot_socket
            self.message = ":" + SOCKET_TO_USERID[self.source] + "!~@localhost "+ self.message
        if(self.source == self.orcbot_socket):
            print "source is orcbot"
            self.target = USERID_TO_SOCKET[self.data[0]]
            self.message = ":orcbot!~@localhost " + self.message
        self.send()

    def mode(self):
        """Detect if a mode message contains a ban
        for the current user, if so, adds it to the ban database, before
        it passes the message on
        """
        #TODO: detection of channelbans be optional and moved into config
        if(len(self.data)==3):
            print self.data
            if re.match("\+b", self.data[1]):
                username = SOCKET_TO_USERID[self.target]
                banned_user = self.data[2].split("!")[1].split("@")[0].strip("*").strip("~")
                if(username == banned_user):
                    print "about to be BANNED", username, "   ", banned_user
                    user_pseudonym = VALIDATED_USERS.get_pseudonym(username)
                    network = self.source[1]
                    BANHANDLER.add_ban(10080, user_pseudonym, network, self.data[0], 0)
        self.send()

    def nick(self):
        """ Sets a userid when the client tries to register with the proxy for the first time.
        If the client is already connected to a server, passes the nick message on. Otherwise,
        it's ignored
        """
        if(not SOCKET_TO_USERID.has_key(self.source)):
            new_userid = _char_list_to_string(random.sample(ALPHABET, USERID_LENGTH))
            while(USERID_TO_SOCKET.has_key(new_userid)):
                new_userid = _char_list_to_string(random.sample(ALPHABET, USERID_LENGTH))
            USERID_TO_SOCKET[new_userid] = self.source
            SOCKET_TO_USERID[self.source] = new_userid
        self.send()

    def send(self):
        """ Tries to send message to target
        """
        if(self.target):
             try:
                 self.message = self.message +"\r\n"
                 self.target[0].send(self.message)
             except socket.error, err:
                 print err

def connect(userid, server_address = "irc.oftc.net",
            port = 6667,nick = None, password = None):
    ''' Connects a user to an IRC server and handles initial user
    registration
    '''
    if(CONNECTION_TIMESTAMPS and CONNECTION_TIMESTAMPS.has_key(server_address)):
        timestamp = CONNECTION_TIMESTAMPS[server_address]
        if(timestamp + QUEUE_TIME >= time.time()):
            time.sleep(QUEUE_TIME + timestamp - time.time())

    if(not nick):
        nick = userid
    user_connection = USERID_TO_SOCKET[userid]
    server_connection = server.connect_to_server( userid,
                                                  USERID_TO_SOCKET[userid],
                                                  server_address,
                                                  password,
                                                  port)
    if(server_connection):
        incoming.add_target(user_connection, server_connection)
        server_connection[0].send("NICK " + nick + "\r\n")
        server_connection[0].send("USER " + userid + " orc orc :orc \r\n")
        CONNECTION_TIMESTAMPS[server_address] = time.time()
    else:
        user_connection.send(":orcbot!~@localhost PRIVMSG " + userid + " ORC was unable to connect to the server requested. Make sure you entered a valid servername\r\n")


def _char_list_to_string(char_list):
    """ Takes a list of chars and returns a string"""
    ret = ""
    for i in char_list:
        ret+=i
    return ret
