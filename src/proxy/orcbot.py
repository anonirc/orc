#! /usr/bin/env python
# coding=UTF-8
'''
Created on 9. mars 2010

@author: Harald Hauknes(harald@hauknes.org)

'''
# The with statement is not available in Python 2.5, so import it
from __future__ import with_statement

import GnuPGInterface
from hashlib import md5
import random
import re
import time

import event as event
from ircbot import SingleServerIRCBot
from irclib import nm_to_n
import validated_users

class ORCBot:
    '''
    This is the bot which serves as the communication medium between the proxy
    and the end-user.
    
    This program is reliant on code written by Joel Rosdahl <joel@rosdahl.net>
    of the irclib project http://python-irclib.sourceforge.net/
    Code used includes all references to ircbot or irclib.
    '''
    #TODO: Handle exceptions throughout the class?
    def __init__(self, server_info, gpg_info, ban_db, pm_name, pseudonym_dur):
        '''
        Initializes the OrcBot object.
        Takes arguments: 
        - gpg_info, and key id - used by gnupg for the validation process
        - ban_db - an instance of the banhandler, share by the other classes
        - scd - the instance of the ServerConnectionDaemon 
        - pm_name - the URI for the Pseudonym Manager
        '''
        # This dictonary establishes whether a user is currently undergoing a
        # validation process. Basicly if the user is present in the list, 
        # the user is in a validation process.
        self.validation_in_progress = dict()
        # The GPG validation requires a keyring and a key id, 
        # the argument under is a tuple of location and keyid
        self.gpg_info = gpg_info
        # We keep a list of connections that have validated themselves
        self.val_users = validated_users.ValidatedUsers()
        # Share the validatedUsers with event
        event.VALIDATED_USERS = self.val_users
        # To tell the users of orcbot where they can aquire a pseuodonym
        self.pm_name = pm_name
        # OrcBot needs to know if users are authorized to connect to servers 
        # and channels therefore it contains a banhandler.
        self.ban_han = ban_db                
        # Starts an instance of SingleServerIRCBot from the irclib project 
        # with OrcBot as its parent.
        self.irclibbot = IRCLibBot(self, server_info)
        # Set how long the pseudonym will be valid
        self.pseudonym_dur = long(pseudonym_dur)

        
    def validate_pseudonym(self, user_input, nick, con):
        '''
        Based on code by Runa Sandvik and rewritten for IRC use.
        
        Takes the argument pseudonym and performs gpg verication on the 
        pseudonym against the keyring.
        '''
          
        # Define GnuPGInterface
        gnupg = GnuPGInterface.GnuPG()
        
        ### Start config ###
        
        # Tell gnupg where to find the GPG keyring. That is, the .gnupg
        # directory. Do not add the trailing slash.
        gnupg.options.homedir = self.gpg_info[0]
        
        # The ID of the key that was used to sign the user input.
        keyid = self.gpg_info[1]
        ### End config ###
        
        ### Verify signature of user input using GPG 
        
        # Write user input to a random file in /tmp, so that the signature
        # can be verified later on. Use small letters, big letters and
        # digits for the filename.
        letters = "abcdefghijklmnopqrstuvwxyz"
        letters += letters.upper () + "0123456789"

        # Actually write user input to file
        #TODO: Write files sequentially, and delete them afterwards
        input_file = "/tmp/"
        count = 0
        while (count < 10):
            input_file += random.choice(letters)
            count = count + 1
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
        # For debugging
        # con.privmsg(nick, signature)
        # print signature
    
        # The signature can not be checked if the public key is not found
        if "public key not found" in signature:
            con.privmsg(nick, "Validation failed, It seems like the key has " + 
                      "not been imported.")
            return False
    
        # Check if the signature is valid. Do not accept a bad signature.
        if "BAD" in signature:
            con.privmsg(nick, "Validation failed, Sorry, this signature is " + 
                      "not valid")
            return False
        
        # Accept a good signature if it is signed by the right key ID. If it
        # is a good signature, and the right key ID have been used, check
        # when the signature was made.
        if ("Good" in signature):
            if (keyid in signature):
                # Check that the signature is not too old
                timesigned = time.mktime(
                    time.strptime(signature[20:47], "%a %d %b %Y %H:%M:%S %p"))
                timediff = time.time() - timesigned
                hours = timediff / 60 / 60
                #days = hours / 24
                if (hours > self.pseudonym_dur):
                    con.privmsg(nick, "Validation failed, sorry this " + 
                                "signature is too old.")
                    return False

                con.privmsg(nick, "Validation succeded, good signature made.") 
                return True
            else:
                con.privmsg(nick, "Validation failed, wrong key id.") 
            
        # If no if sentences has kicked in, system is broken
        con.privmsg(nick, "Validation reached end of function. " + 
                  "Something is wrong with the validation. Please contact "
                  + " the server administrator.")
        return False

    def user_interaction(self, cmd, con, nick):
        '''
        This is the hub of user interaction in OrcBot
        Takes command input from the user an calls the corresponding logic
        '''
        # If the nick is in the dictionary of users currently undergoing 
        # validation, we collect data till we receive "done" from the user.
        if(self.validation_in_progress.has_key(nick)):  
            # If True it is it means that the nick is currently involved 
            # in a validation process. And we should fetch the pseudonym. 
            self.enter_pseudonym(nick, cmd, con)

        elif (cmd == "validate"):
            # Add to dictionary, add initialize the pseudonym as a string
            con.privmsg(nick, "Validation begun, paste your pseudonym now, " +
            "it is important that you paste the pseudonym in the format you " +
            "received it, paste one line at a time." + " Ignore the blank " +
            "lines, we will fill them in for you." +
            " Complete the process by typing 'done' on a single line.")
            con.privmsg(nick, "WARNING: after typing 'done' please allow " + 
                    "atleast one minute before receiving validation results")
            #Placeholder for pseudonym input
            self.validation_in_progress[nick] = ""

        elif (cmd[0:7] == "connect"):
            #if(not self.val_users.haskey(nick)):
            if(not self.val_users.is_validated(nick)):
                con.privmsg(nick, "You are not validated and may not " +
                            "connect. Type 'help validate' for instructions.")
                return
            # This regexp returns a string array of word, which it parses by
            # seperating them by whitespace.
            pieces = [p for p in re.split("( |\\\".*?\\\"|'.*?')", cmd) if
            p.strip()]
            # Set the default port in case the user does not specify one
            port = 6667
            if(len(pieces) < 2):
                con.privmsg(nick, "You supplied too few arguments (atleast"
                + " one needed), type 'help connect' for more info.")
            elif(len(pieces) < 3): 
                server =  pieces[1] # Server
                con.privmsg(nick, "You specified no port, defaulting to " + 
                str(port) +
                ". In seconds you will be able to join a channel. Do so as " +
                "you normally would.")
                # Get the connection object from SCD and check if it is banned
                serverban = self.ban_han.is_banned_from_server(
                                self.val_users.get_pseudonym(nick), server)
                if (serverban):
                    con.privmsg(nick, "ERROR: You are banned from " +
                                    "this server.")
                else:
                    event.connect(nick, server, port)
                    
            elif(len(pieces[2]) > 1):
                # This triggers if the user has supplied two arguments
                server =  pieces[1] # Server
                port =  pieces[2]
                if(re.match("[0-9]+", port)):
                    serverban = self.ban_han.is_banned_from_server(
                                self.val_users.get_pseudonym(nick), server)
                    if (serverban):                        
                        con.privmsg(nick, "ERROR: You are banned from " +
                                            "this server.")
                    else:    
                        con.privmsg(nick, "Connecting you to " + server + 
                        " at port " + port +  ". In seconds you will be able" + 
                        "to join a channel. Do so as you normally would.")
                        event.connect(nick, server, int(port))
                else:
                    con.privmsg(nick, "Port cannot contain anything " +
                    "but numbers. Try again. For help type 'help connect'")
                    return
            else:
                con.privmsg(nick, "Something went wrong, please " +
                "contact the system administrator.")

        elif (cmd=="help"):
            con.privmsg(nick, "Greetings, this bot support the following " + 
                      "commands:")
            con.privmsg(nick, "help     - This dialog.")
            con.privmsg(nick, "validate - Validate a pseudonym.")
            con.privmsg(nick, "connect  - Connect to an IRC server. " + 
                      "requires validation.")
            #con.privmsg(nick, "join     - Join a channel. requires " + 
            #"validation and a active server connection.")
            con.privmsg(nick, "Type 'help <commandname>' to get more info" + 
                      "about each command.")
            
        elif (cmd=="help validate"):
            con.privmsg(nick, "Validates a pseudonym, it makes orcbot " + 
                      "temporarily accept any data you send it for " +
                      "validation, paste the pseudonym you've obtained line " +
                      "for line and ignore any empty lines.")
            con.privmsg(nick, "The process is concluded by typing 'done'. " + 
                      "on a single line.")
            con.privmsg(nick, "You can obtain a pseudonym at " + 
                        self.pm_name)
             
        elif (cmd=="help connect"):
            con.privmsg(nick, "Connects you to an IRC server of your choice.")
            con.privmsg(nick, "The command may take one or two arguments, "
                      + "servername and port. If no port is defined, " + 
                      "port 6667 is selected by default.")
            con.privmsg(nick, "Example: 'connect irc.oftc.net 6667'")
            
        else:
            con.privmsg(nick, "You wrote: '" + cmd + "' this is not a " + 
                     "recognized command, try typing 'help'")
        
    def enter_pseudonym(self, nick, cmd, con):
        '''
        This function is called as long as the user is in the validation 
        dictionary and havent finished their validation.
        '''
        if(cmd!="done"):
            self.validation_in_progress[nick] += cmd + "\n"
            if(("Version" in cmd) or ("Hash" in cmd)):
                self.validation_in_progress[nick] += "\n"
        else:
            pseudonym = self.validation_in_progress.get(nick)
            con.privmsg(nick, "Your pseudonym was retrieved, validating..")
            validation_result = self.validate_pseudonym(pseudonym, nick, con)
            # Remove nick from the validation process list
            del self.validation_in_progress[nick]
            if(validation_result):
                con.privmsg(nick, "Validation performed successfully, " + 
                          "you may now connect.")
                con.privmsg(nick, "For instructions type 'help connect'")
                self.val_users.add(nick, create_md5(pseudonym))
                
            else:
                con.privmsg(nick, "Check that you are " + 
                          "using a valid pseudonym. Type 'help validate' " +
                          "for more information." )
    def start(self):
        '''
        Runs this ORCBot instance.
        '''
        self.irclibbot.start()
                
def create_md5(pseudonym):
    '''
    Create a md5 checksum from a string
    '''
    pseudonymasmd5 = md5(pseudonym)
    return pseudonymasmd5.hexdigest()
    
class IRCLibBot(SingleServerIRCBot):
    '''
    IRCLibBot from the irclib library.
    '''
    def __init__(self, parent, server_info, nickname ="orcbot"):
                        
        server = server_info[0]
        port = int(server_info[1])
        self.orc = parent
        
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)

    #TODO: Add DCC support 
    def on_privmsg(self, con, eee):
        '''
        Define what to do when someone sends a message to the bot
        '''
        # We have written our own user interaction code: user_interaction,
        # from here OrcBot code takes over SingleServerIRCBot
        self.orc.user_interaction(eee.arguments()[0], con, 
                                  nm_to_n(eee.source()))
        # self.orc.user_interaction(cmd, con, nick)
                
def main():
    '''
    If OrcBot is not called from a init script externally, fill it with
    dummy values.
    '''
    ORCBot("HERE GOES THE LOCATION OF THE KEYRING", "HERE GOES KEYID",
    "Placeholder", "Placeholder")

if __name__ == "__main__":
    main()
