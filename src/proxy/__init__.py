'''
Created on 22. March 2010

@author: Harald Hauknes

The purpose of this script is to set up and CONFIGure
the test enviroment of the proxy.
All global variables will be CONFIGured from here.
'''
import os
import ConfigParser

import orcbot
import banhandler
import incomingconnections as incoming
import serverconnectiondaemon as outgoing

# Check what user has initiated the script
PROCESS = os.popen("whoami")
OUTPUT = PROCESS.read()
TESTUSER = True
if("root" in OUTPUT):
    print "We do not need root permissions, running the script as www-data."
    # On the test system, the uid of www-data is 33 (and on most Debian
    # systems. In a prod enviroment, we would likely run the PM
    # as www-data and the proxy as another user.
    os.setuid(33)
    TESTUSER = False
elif("www-data" in OUTPUT):
    TESTUSER = False
if(TESTUSER):
    print ("Script run as " + str(OUTPUT) + ", make sure you have the " +
           "correct permissions for GPG keyring specified in orc.conf.")
# If another user then root or www-data is running, we assume it's for
# testing purposes and the resources the script requires reside on the
# user's home directory

#Reading the CONFIG from file
CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('orc.conf')

#should set up sender and RECEIVER threads
print "starting RECEIVER"
RECEIVER = incoming.IncomingConnectionDaemon()
RECEIVER.init(CONFIG.get('ORC', 'icd_host'), 
              int(CONFIG.get('ORC', 'icd_port')))
RECEIVER.start()

print "starting sender"
SENDER = outgoing.ServerConnectionDaemon()
SENDER.start()

print "starting banhandler"
BH = banhandler.BanHandler(CONFIG.get('ORC', 'bh_host'),
                           CONFIG.get('ORC', 'BH_user'), 
                           CONFIG.get('ORC', 'BH_passwd'), 
                           CONFIG.get('ORC', 'BH_db'))

print "starting bot"
BOT = orcbot.ORCBot(#Server
                    (CONFIG.get('ORC', 'orcbot_server'),
                    (CONFIG.get('ORC', 'orcbot_port'))),
                    # GPG
                    (CONFIG.get('ORC', 'orcbot_keyring'), 
                    CONFIG.get('ORC', 'orcbot_keyid')),
                    # Banhandler and URI of PM 
                    BH, 
                    CONFIG.get('ORC', 'orcbot_pmname')
                                                        )
