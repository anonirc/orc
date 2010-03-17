#! /usr/bin/env python

'''
Created on 9. mars 2010

@author: Harald Hauknes(harald@hauknes.org)

This is the bot which serves as the communication medium between the proxy
and the end-user.

Currently this program is reliant on code written by Joel Rosdahl <joel@rosdahl.net>
of the irclib project http://python-irclib.sourceforge.net/
Code used includes all references to ircbot or irclib. It is used without 
the authors permission, but in compliance with the license terms of irclib.
This is meant as a temporary solution till the Event handler and ServerConnectionDaemon
is written.
'''
# The with statement is not available in Python 2.5, so import it
from __future__ import with_statement
import GnuPGInterface
import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr

from proxy.validated_users import ValidatedUsers

class ORCBot:
    def __init__(self, keyring_loc, key_id):
        '''
        Initializes the OrcBot object.
        Takes arguments keyring_loc, and key id, used by gnupg for the validation process
        '''
        # This dict establishes whether a user is currently undergoing a validation process
        self.validation_in_progress = dict()
        self.keyring_location = keyring_loc
        self.key_id = key_id
        # Creates the validated users as a child process of OrcBot for now
        self.validated_users = ValidatedUsers()
        
    def validate_pseudonym(self, user_input):
        '''
        Takes the argument pseudonym and performs validation on the 
        pseudonym against the cert.
        '''                
        # Define GnuPGInterface
        gnupg = GnuPGInterface.GnuPG()
        
        ### Start config ###
        
        # Tell gnupg where to find the GPG keyring. That is, the .gnupg
        # directory. Do not add the trailing slash.
        gnupg.options.homedir = self.keyring_location
        
        # The ID of the key that was used to sign the user input.
        keyid = self.key_id
        
        ### End config ###
        
        """Verify signature of user input using GPG"""
        
        # Write user input to a random file in /tmp, so that the signature
        # can be verified later on. Use small letters, big letters and
        # digits for the filename.
        letters = "abcdefghijklmnopqrstuvwxyz"
        letters += letters.upper () + "0123456789"
    
        # Actually write user input to file
        input_file = "/tmp/"
        for i in range(10):
            input_file += random.choice(letters)
        with open(input_file, 'w') as write_input:
            write_input.write(user_input)
    
        # Open the file to read the contents
        verify = open(input_file, 'r')
    
        # Verify the signature
        clearsign = gnupg.run(['--no-tty'], ['--decrypt'],
        create_fhs=['stdout','stderr'], attach_fhs={'stdin': verify})
    
        # Read the output from gnupg, and split it into an array so that it
        # can be evaluated.
        signature = clearsign.handles['stderr'].read()
        s = signature.split()
    
        # The signature can not be checked if the public key is not found
        if "public key not found" in signature:
            #print "It seems like the key has not been imported"
            return False
    
        # Check if the signature is valid. Do not accept a bad signature.
        if "BAD" in signature:
            #print "Sorry, this signature is not valid"
            return False
        
        # Accept a good signature if it is signed by the right key ID. If it
        # is a good signature, and the right key ID have been used, check
        # when the signature was made.
        if "Good" in signature and keyid in s[14]:
                #print "Good signature made", s[4], s[5], s[6], s[7], s[8], s[9]
                return True
        
    def get_pseudonym_input(self, cmd, nick):
        # Adds more of the pseudonym to the dictionary.
        self.validation_in_progress[nick] += cmd
        
    def do_command(self, cmd, c, nick):
        '''
        Takes command input from the user an calls the corresponding logic
        '''
        # If the nick is in the dictionary of users currently undergoing validation, we collect 
        # data till we receive "done" from the user
        if(self.validation_in_progress.has_key(nick)):  
            # If it is it means that the nick is currently involved in a validation process. 
            if(cmd!="done"):
                self.get_pseudonym_input(cmd,nick)
            else:
                pseudonym = self.validation_in_progress.get(nick)
                # Used for debugging
                c.privmsg(nick, "Your certificate was retrieved, it was " + pseudonym)
                #TODO sanitize input?
                validation_result = self.validate_pseudonym(pseudonym)
                # Remove nick from the validation process list
                del self.validation_in_progress[nick]
                if(validation_result):
                    c.privmsg(nick, "Validation performed succesfully, you may now connect.")
                    c.privmsg(nick, "For instructions type 'help connect'")
                    # self.validated_users.add(connection, pseudonym)
                    # TODO figure out how the connection or nick should be stored
                else:
                    c.privmsg(nick, "Validation failed, check that you are using a valid pseudonym.")
        elif (cmd=="connect"):
            if(self.validated_users.haskey(nick)):
                #TODO play with the ServerConnectionDaemon
                return            
        elif (cmd=="help"):
            c.privmsg(nick, "Greetings, this bot support the following commands:")
            c.privmsg(nick, "help     - This dialog.")
            c.privmsg(nick, "validate - Validate a pseudonym.")
            c.privmsg(nick, "connect  - Connect to an irc server. requires validation.")
            c.privmsg(nick, "join     - Join a channel. requires validation and a active server connection.")
            c.privmsg(nick, "Type 'help <commandname>' to get more info about each command.")
            
        elif (cmd=="validate"):
            # add to dictionary, add add the certificate as a string
            c.privmsg(nick, "Validation begun, paste your pseudonym now, end the process by typing 'done' on a single line.")
            self.validation_in_progress[nick] = ""
        elif (cmd=="help validate"):
            c.privmsg(nick, "Validates a pseudonym, it makes the bot temporarily accept any data you send it for validation.")
            c.privmsg(nick, "The process is concluded by typing 'done'. on a single line.")
            #TODO
        elif (cmd=="help connect"):
            c.privmsg(nick, "Connects you to an irc server of your choice.")
            c.privmsg(nick, "The command may take one or two arguments, servername and port")
            c.privmsg(nick, "If no port is defined, the command will try connecting on the standard port.")
            #TODO
        elif (cmd=="die"):
            # Used for debugging
            print "Terminating by user request..."
            c.privmsg(nick, "Bye now..")
            self.parent.die()
            
        else:
            c.notice(nick, "You wrote: '" + cmd + "' this is not a recognized command, try typing 'help'")
            

class TestBot(SingleServerIRCBot):
    def __init__(self, channel="#it2901-tp", nickname="orcbot", server="irc.oftc.net", port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        
        # Adds the orcbot code to the testbot, needs to know where the GPG cert is
        # TODO
        self.orc = ORCBot("/home/???", "???")

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        a = e.arguments()[0].split(":", 1)
        if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def on_dccchat(self, c, e):
        if len(e.arguments()) != 2:
            return
        args = e.arguments()[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection
        
        # Do command replaced by OrcBot
        self.orc.do_command(cmd, c, nick)
        
def main():
    print "Starting bot..."
    # Starts an instance of SingleServerIRCBot from the irclib project
    bot = TestBot()
    bot.start()

if __name__ == "__main__":
    main()
