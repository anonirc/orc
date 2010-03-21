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

        

