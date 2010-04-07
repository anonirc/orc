'''
Created on 10. mars 2010

@author: Harald Hauknes(harald@hauknes.org)

The database currently looks like this:
+---------------+-------------+------+-----+-------------------+---------------
| Field         | Type        | Null | Key | Default           | Extra          
+---------------+-------------+------+-----+-------------------+---------------
| banid         | int(11)     | NO   | PRI | NULL              | auto_increment 
| timestamp     | timestamp   | NO   |     | CURRENT_TIMESTAMP |                
| duration_mins | int(11)     | NO   |     | NULL              |                
| pseudonym     | varchar(50) | NO   |     | NULL              |                
| network       | varchar(20) | NO   |     | NULL              |                
| channel       | varchar(30) | NO   |     | NULL              |                
| serverban     | tinyint(1)  | NO   |     | NULL              |                
+---------------+-------------+------+-----+-------------------+---------------

'''
import time

# This module relies on the module mysqldb
# Windows source found at http://www.codegood.com/downloads
# *nix source found at http://sourceforge.net/projects/mysql-python
import MySQLdb

class BanHandler:
    '''
    This module is the abstraction layer for the banlist database of the ORC
    proxy server. It contains all the functions to manipulate that database.
    '''
    def __init__(self, host, user, passwd, database):
        '''
        Creates the BanHandler object and initializes a connection to the mySQL
        database.
        '''
        self.con = MySQLdb.connect(host, user, passwd, database)
        self.cursor = self.con.cursor()
        
    def add_ban(self, duration, pseudonym, network, channel, serverban):
        '''
        Add a ban to the banlist database.
        '''
        self.cursor.execute("INSERT INTO bandb (duration_mins, pseudonym, " +
        "network, channel, serverban) VALUES (%s, %s, %s, %s, %s)", \
                            (duration, pseudonym, network, channel, serverban))
        return
    
    def remove_ban(self, pseudonym, network, channel, serverban):
        '''
        Removes a ban from the server.
        '''
        if(serverban):
            self.cursor.execute("DELETE FROM bandb WHERE pseudonym='" +
            pseudonym + "' AND serverban='" + serverban + \
                                "' AND network='" + network + "'")
        if(len(channel) > 1):
            self.cursor.execute("DELETE FROM bandb WHERE pseudonym='" +
            pseudonym + "' AND channel='" + channel + \
                                "' AND network='" + network + "'")
        return
    
    def remove_ban_id(self, banid):
        '''
        Called from remove_expired_bans when an expired ban is found
        Takes one argument, banid - removes that ban from the db and
        returns nothing.
        '''
        self.cursor.execute("DELETE FROM bandb WHERE banid='"
        + str(banid) + "'")
        return
        
    def remove_expired_bans(self):
        '''
        Iterates throught the bans and removes the ones that has expired.
        Takes no arguments and returns nothing.
        '''
        self.cursor.execute("SELECT banid, unix_timestamp(timestamp), " +
        "duration_mins FROM bandb")
        # Get the resultset as a tuple
        result = self.cursor.fetchall()
        # Iterate through resultset
        current_time = time.time()
        for record in result:
            # If the timestamp + duration is greater than current timestamp -
            # remove the ban
            if((record[1] + (record[2]*60) <  current_time)):
                self.remove_ban_id(record[0])
        return
    
    def is_banned_from_channel(self, pseudonym, server, channel):
        '''
        Takes three arguments, pseudonym, server and channel
        Then returns a boolean value reflecting whether the user is banned
        and connection to the channel should be denied.
        '''
        self.cursor.execute("SELECT * FROM bandb where pseudonym='" +
        pseudonym + "' AND network='" + server + "' AND channel='"
        + channel + "'")
        # Get the resultset as a tuple
        result = self.cursor.fetchall()
        # Iterate through resultset
        for record in result:
            if(record[0] > 0):
                return True
        return False
    def is_banned_from_server(self, pseudonym, server):
        '''
        Takes two arguments, pseudonym and server.
        Then returns a boolean value reflecting whether the user is banned
        and connection to the channel should be denied
        '''
        self.cursor.execute("SELECT * FROM bandb where pseudonym='" +
        pseudonym + "' AND network='" + server +"' AND serverban='1'")
        # Get the resultset as a tuple
        result = self.cursor.fetchall()
        # Iterate through resultset
        for record in result:
            if(record[0] > 0):
                return True
        return False

    def print_db(self):
        '''
        Prints the entire banlist database, primarily used for debugging.
        Takes no arguments and returns nothing.
        '''
        self.cursor.execute("SELECT * FROM bandb")
        # Get the resultset as a tuple
        result = self.cursor.fetchall()
        # Iterate through resultset
        for record in result:
            print record[0] , "-->", record[1], "-->", record[2], "-->",
            record[3], "-->", record[4], "-->", record[5], "-->", record[6]
            
        return
    
    def close(self):
        '''
        Closes the database connection to the server.
        Not likely to ever be used in a production enviroment.
        '''
        self.con.close()
        return
    
