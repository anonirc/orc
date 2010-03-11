'''
Created on 10. mars 2010

@author: Harald Hauknes(harald@hauknes.org)

This module is the abstraction layer for the banlist database of the ORC
proxy server.

The database currently looks like this:

mysql> describe bandb;
+---------------+-------------+------+-----+-------------------+----------------+
| Field         | Type        | Null | Key | Default           | Extra          |
+---------------+-------------+------+-----+-------------------+----------------+
| banid         | int(11)     | NO   | PRI | NULL              | auto_increment |
| timestamp     | timestamp   | NO   |     | CURRENT_TIMESTAMP |                |
| duration_mins | int(11)     | NO   |     | NULL              |                |
| pseudonym     | varchar(50) | NO   |     | NULL              |                |
| network       | varchar(20) | NO   |     | NULL              |                |
| channel       | varchar(30) | NO   |     | NULL              |                |
| serverban     | tinyint(1)  | NO   |     | NULL              |                |
+---------------+-------------+------+-----+-------------------+----------------+

'''
import datetime
import time

# This module relies on the module mysqldb
# Windows source found at http://www.codegood.com/downloads
# *nix source found at http://sourceforge.net/projects/mysql-python
import MySQLdb #@UnresolvedImport

class db:
    '''
    Creates the db object and initializes a connection to the mySQL database
    '''
    def __init__(self):
        self.server = "hauknes.org"
        self.con = MySQLdb.connect(host="hauknes.org", user="site_visitor", passwd="visitor",db="bandb")
        self.cursor = self.con.cursor()
    def add_ban(self, duration, pseudonym, network, channel, serverban):
        self.cursor.execute("INSERT INTO bandb (duration_mins, pseudonym, network, channel, serverban) VALUES (%s, %s, %s, %s, %s)", \
                            (duration, pseudonym, network, channel, serverban))
        return
    '''
    '''
    def remove_ban(self, pseudonym, network, channel, serverban):
        #TODO check if the ban is in the database perhaps?
        if(serverban):
            self.cursor.execute("DELETE FROM bandb WHERE pseudonym='" + pseudonym + "' AND serverban='" + serverban + \
                                "' AND network='" + network + "'")
        if(len(channel) > 1):
            self.cursor.execute("DELETE FROM bandb WHERE pseudonym='" + pseudonym + "' AND channel='" + channel + \
                                "' AND network='" + network + "'")
        return
    '''
    '''
    def remove_expired_bans(self):
        self.cursor.execute("SELECT * FROM bandb")
        # Get the resultset as a tuple
        result = self.cursor.fetchall()
        # Iterate through resultset
        currentTime = time.time()
        for record in result:
            print "lol"
        
        return
    '''
    Prints the entire banlist database, primarily used for debugging.
    Takes no arguments and returns nothing.
    '''
    def print_db(self):
        self.cursor.execute("SELECT * FROM bandb")
        # Get the resultset as a tuple
        result = self.cursor.fetchall()
        n = datetime.datetime.now()
        # Iterate through resultset
        for record in result:
            print record[0] , "-->", record[1], "-->", record[2], "-->", record[3], "-->", record[4], "-->", record[5], "-->", record[6]
            timenow = n.timetuple(record[1])
            print "timetubple = " + str(timenow) 
    
