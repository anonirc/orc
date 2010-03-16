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
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr

#import verify_sign
# I have not gotten Runa's code to run yet, we'll solve it tomorrow.
class Orcbot:
    def __init__(self, parent):
        # This dict establishes whether a user is currently undergoing a validation process
        self.validation_in_progress = dict()
        self.parent = parent
        #self.gpgverifier = verify_sign 
    def get_certificate(self, cmd, nick):
        self.validation_in_progress[nick] += cmd
        
    def do_command(self, cmd, c, nick):
        '''
        Takes command input from the user an calls the corresponding logic
        '''
        # If the nick is in the list, we collect data untill we receive "done" from the user
        if(self.validation_in_progress.has_key(nick)): #Here we check if the nick is in the dictionary, 
            # If it is it means that the nick is currently involved in a validation process. 
            if(cmd!="done"):
                self.get_certificate(cmd,nick)
            else:
                # Used for debugging
                c.privmsg(nick, "Your certificate was retrieved, it was " + self.validation_in_progress.get(nick))
                #TODO sanitize input
                #pseudonym = self.gpgverifier(self.validation_in_progress.get(nick))
                # Calls the verifyer, untested. Sets true for debug.
                pseudonym = "Fakepseudonymfornow"
                # We have a pseudonym or a empty string, remove the nick from the validation dictionary as that process is done
                del self.validation_in_progress[nick]
                if(len(pseudonym) > 0):
                    #parent.add_pseudonym_to_validated_users()
                    # TODO add to validated users and allow user to connect
                    return
        elif (cmd=="connect"):
            #self.parent.validatedusers.haskey(nick)
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
            c.privmsg(nick, "Connects you to an irc server of your choice:")
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
        '''
        Adds the orcbot code to the testbot
        '''
        self.orc = Orcbot(self)

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
        '''
        Do command replaced by orcbot
        '''
        self.orc.do_command(cmd, c, nick)
        
def main():
    print "Starting bot..."
    # Starts an instance of SingleServerIRCBot from the irclib project
    bot = TestBot()
    bot.start()

if __name__ == "__main__":
    main()
