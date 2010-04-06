'''
Created on 11. mars 2010

@author: harahauk
'''
#import banhandler as dbmodule

#db = dbmodule.BanHandler()
#db.add_ban(1, "iampermbanned2", "bannet", "", 1)
#db.add_ban(1, "thiswillsoonberemoved", "testnet", "testchan", 0)
#db.remove_ban("imapseudonym", "testnet", "testchan", False)
#db.print_db();
#import time
#time.mktime(tuple)
#db.remove_expired_bans()
#res = db.is_banned_from_server("iampermbanned", "bannet")
#res = db.is_banned_from_channel("imasdpseudonym", "testnet", "testchan")
#print res
#db.print_db()
#db.close()

#from hashlib import md5

#text = "Hello world!"
#text = text + text
#textasmd5 = md5(text)
#print "Hash:" + textasmd5.hexdigest()
'''
### Configuration file for Onion Relay Chat - ORC ###

### IncomingConnectionDaemon ###

# The host interface that the proxy will bind to. 
# e.g icd_host = "localhost"
#icd_host =
 
# The port that the proxy will listen for new connections.
# e.g icd_port = "6667"
#icd_port = 

### ORCBot ###

# The location of the GNUGPG keyring file.
# e.g orcbot_keyring = ~/.gnupgp
#orcbot_keyring = 

# The key id used by GNUGPG
# e.g orcbot_keydid = "1EFNU"
#orcbot_keyid = 

# The URI of the Pseudonym Manager server
# e.g orcbot_pmname = "http://pm.onion/"
#orcbot_pmname = 
'''
import ConfigParser

config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
config.add_section('ORC')
config.set('ORC', 'icd_host', '15')
config.set('ORC', 'icd_port', 'true')
config.set('ORC', 'orcbot_keyring', '3.1415')
config.set('ORC', 'orcbot_keyid', 'fun')
config.set('ORC', 'orcbot_pmname', 'Python')

# Writing our configuration file to 'example.cfg'
with open('example.cfg', 'wb') as configfile:
    config.write(configfile)
