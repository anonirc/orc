'''
Created on 11. mars 2010

@author: harahauk
'''
import banhandler as dbmodule

db = dbmodule.BanHandler()
#db.add_ban(1, "iampermbanned2", "bannet", "", 1)
#db.add_ban(1, "thiswillsoonberemoved", "testnet", "testchan", 0)
#db.remove_ban("imapseudonym", "testnet", "testchan", False)
#db.print_db();
#import time
#time.mktime(tuple)
#db.remove_expired_bans()
#res = db.is_banned_from_server("iampermbanned", "bannet")
#res = db.is_banned_from_channel("imasdpseudonym", "testnet", "testchan")
print res
#db.print_db()
db.close()
