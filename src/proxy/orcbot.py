#! /usr/bin/env python

'''
Created on 9. mars 2010

@author: Harald Hauknes(harald@hauknes.org)

This is the bot which serves as the communication medium between the proxy
and the end-user.

This program is reliant on code written by Joel Rosdahl <joel@rosdahl.net>
of the irclib project http://python-irclib.sourceforge.net/
Code used includes all references to ircbot or irclib. It is used without 
the authors permission, but in compliance with the license terms of irclib.

Communicastion to the proxy goes through system calls(proc), 
communication with the user goes through the IRC protocol
'''
# The with statement is not available in Python 2.5, so import it
#from __future__ import with_statement
import sys
#import GnuPGInterface
#import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

import banhandler

class ORCBot:
    def __init__(self, keyring_loc, key_id):
        '''
        Initializes the OrcBot object.
        Takes arguments keyring_loc, and key id - used by gnupg for the validation process
        '''
        # The system calls are the bots communication with ORC proxy
        self.sc = SystemCalls()
        # This dictonary establishes whether a user is currently undergoing a validation process
        # Basicly if the user is present in the list, he is in a validation process
        self.validation_in_progress = dict()
        # The GPG validation requires a keyring and a key id, these are the location
        # in the filesystem
        self.keyring_location = keyring_loc
        self.key_id = key_id
        # OrcBot needs to know if users are authorized to connect to servers and channels
        # therefore it contains a banhandler
        self.banhandler= banhandler.BanHandler()
        # Starts an instance of SingleServerIRCBot from the irclib project with OrcBot as its parent
        self.irclibbot = IRCLibBot(self)
    '''
    TODO: Make this code work        
    def validate_pseudonym(self, user_input):
        #docstringstart
        #Takes the argument pseudonym and performs validation on the 
        #pseudonym against the cert.
        #docstringend                
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
            print "It seems like the key has not been imported"
            return False
    
        # Check if the signature is valid. Do not accept a bad signature.
        if "BAD" in signature:
            print "Sorry, this signature is not valid"
            return False
        
        # Accept a good signature if it is signed by the right key ID. If it
        # is a good signature, and the right key ID have been used, check
        # when the signature was made.
        if "Good" in signature and keyid in s[14]:
                print "Good signature made", s[4], s[5], s[6], s[7], s[8], s[9]
                return True
    '''
    def user_interaction(self, cmd, c, nick):
        '''
        This is the hub of user interaction in OrcBot
        Takes command input from the user an calls the corresponding logic
        '''
        # If the nick is in the dictionary of users currently undergoing validation, we collect 
        # data till we receive "done" from the user
        if(self.validation_in_progress.has_key(nick)):  
            # If it is it means that the nick is currently involved in a validation process. 
            self.enter_pseudonym(nick, cmd, c)
        elif (cmd=="validate"):
            # Add to dictionary, add initialize the pseudonym as a string
            c.privmsg(nick, "Validation begun, paste your pseudonym now, end the process by typing 'done' on a single line.")
            self.validation_in_progress[nick] = ""
        elif (cmd=="connect"):
            if(self.validated_users.haskey(nick)):
                #TODO: play with the ServerConnectionDaemon
                return            
        elif (cmd=="help"):
            c.privmsg(nick, "Greetings, this bot support the following commands:")
            c.privmsg(nick, "help     - This dialog.")
            c.privmsg(nick, "validate - Validate a pseudonym.")
            c.privmsg(nick, "connect  - Connect to an irc server. requires validation.")
            c.privmsg(nick, "join     - Join a channel. requires validation and a active server connection.")
            c.privmsg(nick, "Type 'help <commandname>' to get more info about each command.")
            
        elif (cmd=="help validate"):
            c.privmsg(nick, "Validates a pseudonym, it makes the bot temporarily accept any data you send it for validation.")
            c.privmsg(nick, "The process is concluded by typing 'done'. on a single line.")
            #TODO: Finish this method stub.
        elif (cmd=="help connect"):
            c.privmsg(nick, "Connects øyou to an irc server of your choice.")
            c.privmsg(nick, "The command may take one or two arguments, servername and port")
            c.privmsg(nick, "If no port is defined, the command will try connecting on the standard port.")
            #TODO: Finish this method stub.
        elif (cmd=="die"):
            #TODO: Remove this, its a debugging method
            print "Terminating by user request.."
            c.privmsg(nick, "Bye now..")
            sys.exit(0)
            
        else:
            c.notice(nick, "You wrote: '" + cmd + "' this is not a recognized command, try typing 'help'")
        
    def enter_pseudonym(self,nick,cmd,c):
        if(cmd!="done"):
            self.validation_in_progress[nick] += cmd
        else:
            pseudonym = self.validation_in_progress.get(nick)
            # Used for debugging
            c.privmsg(nick, "Your certificate was retrieved, it was " + pseudonym)
            # TODO: sanitize input?
            # Validation_result = self.validate_pseudonym(pseudonym)
            validation_result = True
            # Remove nick from the validation process list
            del self.validation_in_progress[nick]
            if(validation_result):
                c.privmsg(nick, "Validation performed succesfully, you may now connect.")
                c.privmsg(nick, "For instructions type 'help connect'")
                # self.validated_users.add(connection, pseudonym)
                # TODO figure out how the connection or nick should be stored
            else:
                c.privmsg(nick, "Validation failed, check that you are using a valid pseudonym.")
            
            
class SystemCalls:
    #TODO: Figure out how to do unix system calls to running processes
    def add_validated_user(self):
        return
            
class IRCLibBot(SingleServerIRCBot):
    def __init__(self, parent, channel="#it2901-tp", nickname="orcbot", server="localhost", port=6667):
        self.orc = parent
        #TODO: Remove this, its for debug only, OrcBot will run on localhost of the proxy
        server="irc.oftc.net"
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        #TODO: Remove this, its for debug only, OrcBot will never join a channel
        self.channel = channel
        print "Bot started.."
        self.start()

    #TODO: Add DCC support 
    def on_privmsg(self, c, e):
        '''
        Define what to do when someone sends a message to the bot
        '''
        # We have written our own user interaction code: user_interaction,
        # from here OrcBot code takes over SingleServerIRCBot
        self.orc.user_interaction(e.arguments()[0], c, nm_to_n(e.source()))
        # self.orc.user_interaction(cmd, c, nick)
        
    def on_welcome(self, c, e):
        #TODO: Remove this, its for debug only, OrcBot will never join a channel
        c.join(self.channel)
                
def main():
    #TODO: Make this happen from config file
    ORCBot("HERE GOES THE LOCATION OF THE KEYRING", "HERE GOES KEYID")

if __name__ == "__main__":
    main()
