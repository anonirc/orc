import string
import serverconnectiondaemon as server
import incomingconnections as incoming

#holds the made up nicks that each connection has when talking
#with orcbot
orcbot_nicks = []
#TODO: Replace index with hash of something, maybe timestamp

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
        print 
        print self.event_type
        print "****Source**"
        print self.source
        print "*****data***"    
        print self.data
        print "***orcbot****"
        print self.orcbot

        #if message is for orcbot, set orcbot as target
        if(self.data[0]=="orcbot"):
            print "target = orcbot"
            self.target = self.orcbot
            if(orcbot_nicks.count(self.source)==0):
                orcbot_nicks.append(self.source)
            self.message = ":" + str(orcbot_nicks.index(self.source)) + " " + self.message
        #TODO: The nicks for orcbot chats shouldnt be integers, and the lookup shouldnt
        #be an array access
        if(self.source == self.orcbot):
            print "source is orcbot"
            self.target = orcbot_nicks[int(self.data[0])]
            self.message = ":orcbot "+self.message
        print "*******target**"
        print self.target
            
        #TODO alter message to reflect hostmasks and such
        self.target[0].send(self.message)
            
    def privnotice(self):
        """TODO
        """
        
    def pubmsg(self):
        """TODO
        """
        
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

