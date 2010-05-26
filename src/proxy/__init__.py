'''
Created on 22. March 2010

@author: Harald Hauknes

The purpose of this script is to set up and configure
the test enviroment of the proxy.
All global variables and instances will be configured from here.
'''
import os
import ConfigParser
import sys
import _mysql_exceptions

import orcbot
import banhandler
import incomingconnections as incoming
import serverconnectiondaemon as outgoing
import event as event

# Check what user has initiated the script
PROCESS = os.popen("whoami")
OUTPUT = PROCESS.read()

if("root" in OUTPUT):
    print "root permissions not needed, running as www-data."
    # On the test system, the uid of www-data is 33 (and on most Debian
    # systems.
    os.setuid(33)

# Reading the config from file
CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('orc.conf')

# Sets up sender and reciever threads
print "Starting receiver.."
try:
    RECEIVER = incoming.IncomingConnectionDaemon()
    RECEIVER.init(CONFIG.get('ORC', 'icd_host'),
                  int(CONFIG.get('ORC', 'icd_port')))
except ValueError:
    print ("ERROR: Accessing the options for the receiver failed, " +
           "please review your orc.conf file.")
    sys.exit(1)
except ConfigParser.NoSectionError:
    print ("ERROR: Section [ORC] not found or file does not exist, " +
    "please review your orc.conf file.")
    sys.exit(1)
RECEIVER.start()

print "Starting sender.."
SENDER = outgoing.ServerConnectionDaemon()
SENDER.start()

print "Starting banhandler.."
try:
    BH = banhandler.BanHandler(CONFIG.get('ORC', 'bh_host'),
                               CONFIG.get('ORC', 'bh_user'),
                               CONFIG.get('ORC', 'bh_passwd'),
                               CONFIG.get('ORC', 'bh_db'))
    #setting the reference to the banhandler in event
    event.BANHANDLER = BH
except ValueError:
    print ("ERROR: Accessing the options for the banhandler failed, " +
           "please review your orc.conf file.")
    sys.exit(1)
except _mysql_exceptions.OperationalError:
    print ("ERROR: Accessing the options for the banhandler failed, " +
           "please review your orc.conf file.")
    sys.exit(1)

print "Starting bot.."
try:
    BOT = orcbot.ORCBot(# Server info
                        (CONFIG.get('ORC', 'orcbot_server'),
                         (CONFIG.get('ORC', 'orcbot_port'))),
                         # GPG
                         (CONFIG.get('ORC', 'orcbot_keyring'),
                          CONFIG.get('ORC', 'orcbot_keyid')),
                          # BanHandler and URI of PM
                          BH,
                          CONFIG.get('ORC', 'orcbot_pmname'),
                          CONFIG.get('ORC', 'pseudonym_dur')
                          )
except ValueError:
    print ("ERROR: Accessing the options for the ORCBot failed, " +
           "please review your orc.conf file.")
    sys.exit(1)
BOT.start()
