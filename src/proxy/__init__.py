'''
Created on 22. March 2010

@author: Harald Hauknes

The purpose of this script is to set up and configure
the test enviroment of the proxy.
All global variables will be configured from here.
'''
import os
import ConfigParser

import orcbot
import banhandler
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
    print ("Unknown user, make sure you have the correct permissions for GPG" + 
    " validation")
# If another user then root or www-data is running, we assume it's for
# testing purposes and the resources the script requires reside on the
# user's home directory

#Reading the config from file
config = ConfigParser.RawConfigParser()
config.read('orc.conf')

#should set up sender and receiver threads
print "starting receiver"
receiver = incoming.IncomingConnectionDaemon()
receiver.init(config.get('ORC', 'icd_host'), 
              config.get('ORC', 'icd_port'))
receiver.start()

print "starting sender"
sender = outgoing.ServerConnectionDaemon()
sender.start()

print "starting banhandler"
bh = banhandler.BanHandler(config.get('ORC', 'bh_host'),
                           config.get('ORC', 'bh_user'), 
                           config.get('ORC', 'bh_passwd'), 
                           config.get('ORC', 'bh_db'))

print "starting bot"
bot = orcbot.ORCBot(config.get('ORC', 'orcbot_keyring'), 
                    config.get('ORC', 'orcbot_keyid'), 
                    bh, 
                    sender, 
                    config.get('ORC', 'orcbot_pmname'))
