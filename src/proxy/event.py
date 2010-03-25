class Event:
    """Holds the type and handler function for irc events
    """

    def __init__(self, type, source, target, data=[]):
        """Holds an event with event type, source, target,
        and optionally data needed for the event
        """
        self.type=type
        self.source=source
        self.target=target
        self.data=data
        self.socket=source

    def apply_handler(self):
        #the code that calls the event handler for the event
        #type
        m = self.type()
        if hasattr(self, m):
            getattr(self, m)()

    def get_type(self):
        return self.type
   
    def get_source(self):
        return self.source
   
    def get_target(self):
        return self.target
   
    def get_data(self):
        return self.data
   
    def printC(self):
        print(self.type)

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
        """
        """
        for i in self.data:
            print i
        
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

