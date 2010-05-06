"""
Copies a lot from IRClib, adapted to be usable for making a bouncer

@author: Lars Vonli(lars@vonli.no)

See LICENSE for licensing information.

"""
import re
import socket
import event

from irclib import numeric_events

#Regex that groups the different parts of a IRC message.
_rfc_1459_command_regexp = re.compile(
    "^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?")


#splits lines. RFC standard is \r\n, but a
#fair number of ircd's violate this
_linesep_regexp = re.compile("\r?\n")

def process_data(connection, orcbot_address):
    """ Takes in a connection, tries to read data from
    the socket, and returns an Event of it
    """
    event_list = []
    try:
        new_data = connection[0][0].recv(2**14)
        print new_data
        
    except socket.error, err:
        return None
    
    if (new_data == ''):
        return [event.Event("connection_closed", connection[0], connection[1], orcbot_address, [],  [])]
    
    lines = _linesep_regexp.split(new_data)
   
    prefix = None
    command = None
    arguments = None
    
    for line in lines:
        if not line:
            continue

        msg = _rfc_1459_command_regexp.match(line)
        
        if msg.group("prefix"):
            prefix = msg.group("prefix")
          
        if msg.group("command"):
            command = msg.group("command").lower()

        if msg.group("argument"):
            arg = msg.group("argument").split(" :", 1)
            arguments = arg[0].split()
            if len(arg) == 2:
                arguments.append(arg[1])

        # Translate numerics into more readable strings.
        if command in numeric_events:
            command = numeric_events[command]     
        event_list.append(event.Event(command, connection[0], connection[1], orcbot_address, line, arguments))
    return event_list
