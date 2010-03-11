

class Event:
    """Holds the type and handler function for irc events
    """

    def __init__(self, type, handler):
        """Takes in a event type as a string and a
        handler function for this type of event
        """
        self.type=type
        self.handler=handler

    def apply_event_handler():
        """Calls the handler function on the event data.
        """
        
        
        

