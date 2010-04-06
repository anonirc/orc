'''
Created on 22. March 2010

@author: Harald Hauknes

The purpose of this script is to set up and configure
the test enviroment of the proxy.
All global variables will be configured from here.
'''
import os

# TODO: Possibly remove the socket import
import socket
import orcbot
import banhandler as banhandler
import incomingconnections as incoming
import serverconnectiondaemon as outgoing

# Check what user has initiated the script
process = os.popen("whoami")
output = process.read()
testuser = True
if("root" in output):
    print "We do not need root permissions, running the script as www-data."
    # On the test system, the uid of www-data is 33 (and on most Debian
    # systems. In a prod enviroment, we would likely run the PM
    # as www-data and the proxy as another user.
    os.setuid(33)
    testuser = False
elif("www-data" in output):
    testuser = False
if(testuser):
    print "Unknow user, globals will default to you home directory."
# If another user then root or www-data is running, we assume it's for
# testing purposes and the resources the script requires reside on the
# user's home directory
#
# TODO: Make the init script load constants from config file

host = "localhost"
port = 6667

#should set up sender and receiver threads
print "starting receiver"
receiver = incoming.IncomingConnectionDaemon()
receiver.init(host, port)
receiver.start()

print "starting sender"
sender = outgoing.ServerConnectionDaemon()
sender.start()

print "starting banhandler"
bh = banhandler.BanHandler()

print "starting bot"
pmservername = "http://nameofpmserver.org/"
bot = orcbot.ORCBot("~/.gnupg", "KEYID?", bh , sender, pmservername)
