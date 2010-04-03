import thread
import socket
import time

import  ircParse as parse


HOST=socket.gethostname()
PORT=31340

S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.bind((HOST,PORT))
S.listen(5)

sender=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender.connect((HOST, PORT))

conn=S.accept()

def send_Recv_and_Parse(send, receiver):
    while 1:      
        send.send(":guntbert!~re@unaffiliated/guntbert PRIVMSG #ubuntu :enthus: like histo just said: carry the app and all its dependencies")
        parse.process_data(receiver)
        time.sleep(2)

thread.start_new_thread(send_Recv_and_Parse, (sender, conn))


