class ValidatedUsers():
    '''
    A object to hold the connections who are
    currently connected and whose pseudonyms have been validated
    '''
    def __init__(self):
        #TODO work out communication by depending classes
        #TODO: Handle exceptions?
        self.dictionary = dict()
        
    def add_connection(self, connection, pseudonym):
        self.dictionary[connection] = pseudonym

    def remove_connection(self, connection):
        del self.dictionary[connection]
        
    '''
    '''
    def remove_disconnected_users(self):
        # possible triggered by an event and may not need implementation
        return
        

