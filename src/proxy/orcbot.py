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
        
        ### Verify gpg_output of user input using GPG 
        
        # Write user input to a random file in /tmp, so that the gpg_output
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
    
        # Verify the gpg_output
        clearsign = gnupg.run(['--no-tty'], ['--decrypt'],
        create_fhs=['stdout','stderr'], attach_fhs={'stdin': verify})
        
        # Read the output from gnupg, and split it into an array so that it
        # can be evaluated.
        gpg_output = clearsign.handles['stderr'].read()
        
        if(self.has_expired(gpg_output)):
            con.privmsg(nick, "Validation failed, sorry this " + 
                                "signature is too old.")
            return False
    
        # Check if the signature is valid. Do not accept a bad signature.
        if "BAD" in gpg_output:
            con.privmsg(nick, "Validation failed, Sorry, this signature is " + 
                      "not valid")
            return False
        
        # Accept a good signature if it is signed by the right key ID. If it
        # is a good signature, and the right key ID have been used, check
        # when the signature was made.
        if ("Good" in gpg_output):
            if (keyid in gpg_output): 
                # Check that the signature is not too old
                # Parses the output from GPG to create a timestamp, then
                # compares it to the local time to see if the sig. is expired
                #TODO: Look in to possible timezone bug.

                con.privmsg(nick, "Validation succeded, good signature made.") 
                return True
            else:
                con.privmsg(nick, "Validation failed, wrong key id.") 
                return False
        
        # The signature can not be checked if the public key is not found
        if "public key not found" in gpg_output:
            con.privmsg(nick, "Validation failed, It seems like the key has " + 
                      "not been imported.")
            return False
            
        # If no if sentences has kicked in, system is broken
        con.privmsg(nick, "Validation reached end of function. " + 
                  "Something is wrong with the validation. Please contact "
                  + "the server administrator.")
        return False
    
    def has_expired(self, gpg_output):
        '''
        Takes the output of a gpg verification attempt and returns True
        or False depending on the proxy configuration of pseudonym durations.
        '''
        print "Timeout stuff"
        print gpg_output[20:47]
        print time.strptime(gpg_output[20:47], "%a %d %b %Y %H:%M:%S %p")
        
        timesigned = time.mktime(
                    time.strptime(gpg_output[20:47], "%a %d %b %Y %H:%M:%S %p"))
        timediff = time.time() - timesigned
        minutes = timediff / 60
        print timediff
        
        if ((minutes > 0) and (minutes > self.pseudonym_dur)):
            return True
        return False

    def user_interaction(self, cmd, con, nick):
        '''
        This is the hub of user interaction in OrcBot
        Takes command input from the user an calls the corresponding logic
        '''
        # If the nick is in the dictionary of users currently undergoing 
        # validation, we collect data till we receive "done" from the user.
        if(self.validation_in_progress.has_key(nick)):  
            # Store all input in a string. 
            self.enter_pseudonym(nick, cmd, con)

        elif (cmd == "validate"):
            # Add to dictionary, add initialize the pseudonym as a string
            con.privmsg(nick, "Validation begun, paste your pseudonym now, " +
            "it is important that you paste the pseudonym in the format you " +
            "received it, paste one line at a time." + " Ignore the blank " +
            "lines, we will fill them in for you." +
            " Complete the process by typing 'done' on a single line.")
            con.privmsg(nick, "WARNING: after typing 'done' please allow " + 
                    "at least one minute before receiving validation results")
            # Add user to the validation_in_progress list, orcbot now accepts
            # all input given.
            self.validation_in_progress[nick] = ""

        elif (cmd[0:7] == "connect"):
            self.connect(cmd, con, nick)
            
        elif (cmd=="help"):
            con.privmsg(nick, "Greetings, this bot support the following " + 
                      "commands:")
            con.privmsg(nick, "help     - This dialog.")
            con.privmsg(nick, "validate - Validate a pseudonym.")
            con.privmsg(nick, "connect  - Connect to an IRC server. " + 
                      "requires validation.")
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
            con.privmsg(nick, "The command may take two or three arguments, "
                      + "nick, servername and port. If no port is defined, " + 
                      "port 6667 is selected by default.")
            con.privmsg(nick, "Example: 'connect mynick irc.oftc.net 6667'")
            
        else:
            con.privmsg(nick, "You wrote: '" + cmd + "' this is not a " + 
                     "recognized command, try typing 'help'")
            
    def connect(self, cmd, con, nick):
        '''
        Called when the user has issued a wish to connect.
        Determines next action by checking the rest of the user's input and
        if the user is authorized to connect.
        '''
        if(not self.val_users.is_validated(nick)):
            con.privmsg(nick, "You are not validated and may not " +
                        "connect. Type 'help validate' for instructions.")
            return
        
        # This regexp returns a string array of words, which it parses by
        # seperating them by whitespace.
        words = [p for p in re.split("( |\\\".*?\\\"|'.*?')", cmd) if p.strip()]
        # Set the default port in case the user does not specify one
        port = 6667
        if(len(words) < 3):
            con.privmsg(nick, "You supplied too few arguments (at least"
            + " two needed), type 'help connect' for more info.")
            return
            
        server =  words[2] # Server should be the second argument
        serverban = self.ban_han.is_banned_from_server(
                self.val_users.get_pseudonym(nick), server)
        if (serverban):
            con.privmsg(nick, "ERROR: You are banned from " +
                            "this server.")
            return
        try:      
            if (words[3]): #If the user has specified a port, we use that instead
                if(re.match("[0-9]+", words[3])):
                    port = int(words[3])
                else:
                    con.privmsg(nick, "Port cannot contain anything " +
                            "but numbers. Try again. For help type 'help connect'")
                    return
        except IndexError:
            pass
        #words[1] is the nick
        event.connect(nick, server, port, words[1])

# Tell the user what happened
        if(words[2]):
            con.privmsg(nick, "Connecting you to " + server + 
            " at port " + str(port) +  ". You should now be able " + 
            "to join a channel. Do so as you normally would.")
            return
        #TODO: Implement nick functionality to the connect statement 
        else:
            con.privmsg(nick, "You specified no port, defaulting to port " + 
                        str(port) + ". You should now be able to join a " +
                        "channel. Do so as you normally would.")
            return
                    
        # If function is still running, something has gone wrong
        con.privmsg(nick, "Something went wrong, please " +
                    "contact the system administrator.")
        
    def enter_pseudonym(self, nick, cmd, con):
        '''
        This function is called as long as the user is in the validation 
        dictionary and haven't finished their validation.
        '''
        #TODO: Set a timeout, people can get confused with no response.
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
        # This means:
        # self.orc.user_interaction(cmd, con, nick)
