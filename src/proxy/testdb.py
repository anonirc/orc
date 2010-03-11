'''
Created on 11. mars 2010

@author: harahauk
'''
import db as dbmodule

db = dbmodule.db()
db.add_ban(1, "imapseudonym", "testnet", "testchan", 0)
db.add_ban(1, "thiswillsoonberemoved", "testnet", "testchan", 0)
#db.remove_ban("imapseudonym", "testnet", "testchan", False)
#db.print_db();
#import time
#time.mktime(tuple)
db.remove_expired_bans()
db.print_db()
db.close()
