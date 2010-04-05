import string
import serverConnectionDaemon as server
import incomingConnections as incoming
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
        print 
        print self.event_type
        print "****Source**"
        print self.source
        print "*******target**"
        print self.target
        print "*****data***"    
        print self.data
        print "***orcbot****"
        print self.orcbot
        if(self.data[0]=="orcbot"):
            print "target = orcbot"
            self.target = self.orcbot

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

