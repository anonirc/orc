import thread
import socket
import time

import incomingconnections as ic


#settings for accepting connections
HOST=socket.gethostname()
PORT=31331

#starts the incoming connections daemon.
daemon=ic.IncomingConnectionDaemon()
daemon.init(HOST, PORT)
daemon.start()

def runDumbSender(message, host, port):
    """ Sends message to (host, port) until
    interrupted
    """
    conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((host, port))
    #    while 1:
    #       time.sleep(2)
    conn.send(message)

#for i in range(5):
#   time.sleep(1)
thread.start_new_thread(runDumbSender, (":guntbert!~re@unaffiliated/guntbert PRIVMSG #orcbot :connect:littlelaptop", HOST, PORT ))
