class ValidatedUsers():
    '''
    A object to hold the connections who are
    currently connected and whose pseudonyms have been validated
    '''
    def __init__(self):
        #TODO: Handle exceptions?
        self.dict_nick_to_pseudonym = dict()

    def add(self, nick, pseudonym):
        self.dict_nick_to_pseudonym[nick] = pseudonym

    def is_validated(self, nick):
        if(self.dict_nick_to_pseudonym.has_key(nick)):
            return True
        return False

    def get_pseudonym(self, nick):
        return self.dict_nick_to_pseudonym.get(nick)

    def remove_user(self,  nick):
        """Removes a user from the validated users dict

        Arguments:
        - `self`:
        - `nick`:
        """
        if(self.dict_nick_to_pseudonym.has_key(nick)):
            del self.dict_nick_to_pseudonym[nick]
