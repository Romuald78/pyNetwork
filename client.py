# coding: utf-8

import socket
from threading import Thread
from serverUtils import *


class Client(Thread):
    # -----------------------------------------
    # Constructor
    # -----------------------------------------
    def __init__(self, hst, prt):
        # Parent constructor
        Thread.__init__(self);
        # store attributes
        self.host = hst
        self.port = prt
        # Create socket
        self.sock = None
        self.createSocket()

    def createSocket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(0.1)
        except Exception as ex:
            self.killThread(ex)

    # ---------------------------------------------------

    def isRunning(self):
        return self.sock != None

    def killThread(self, reason, info="[ERROR]"):
        Utils.log( Utils.getClrStr(info, Utils.RED, Utils.BOLD) + " : " + Utils.getClrStr(reason, Utils.RED))
        self.sock = None

    def receiveMessage(self):
        try:
            response = self.sock.recv(255)
            response = response.decode()
            if len(response) > 0:
                Utils.log( "<<< " + Utils.getClrStr(response, Utils.YELLOW) )
        except socket.timeout as sto:
            err = sto.args[0]
            # this next if/else is a bit redundant, but illustrates how the
            # timeout exception is setup
            if err == 'timed out':
                pass
            else:
                self.killThread(sto)

        except socket.error as ser:
            # Something else happened, handle error, exit, etc.
            self.killThread(ser)
        else:
            if len(response) == 0:
                self.killThread('Shutdown requested on server end',"[INFO]")

    def sendMessage(self,msg):
        print( ">>> "+ Utils.getClrStr(msg,Utils.BLUE) )
        self.sock.sendall(msg.encode())

    def run(self):
        if self.sock != None:
            Utils.log("client is connected on port #"+str(self.port))
        while self.sock != None:
            self.receiveMessage()

#---------------------------------------------------
# MAIN PROCESS
#---------------------------------------------------
cli = Client("localhost",15555)
cli.start()


txt = ""
while (txt.encode() != Utils.getEndRequest() ) and cli.isAlive():
    txt = input()
    cli.sendMessage( txt )

if cli.isDaemon():
    cli.close()

