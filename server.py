# coding: utf-8

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from threading import Thread
from random import *
import ipaddr
import socket
import sys
from nicknames import *
from serverUtils import *



# =============================================================================
# CLIENT LINK CLASS
# =============================================================================
class ClientServerLink(Thread):
    # -----------------------------------------
    # Constructor
    # -----------------------------------------
    def __init__(self, srv, cli, raddr, allLnk):
        # Parent constructor
        Thread.__init__(self);
        # attributes initialization
        self.client        = cli
        self.server        = srv
        self.remoteAddress = raddr[0]
        self.remotePort    = raddr[1]
        self.allLinks      = allLnk
        self.nickname      = Nicknames.getNickname( "CLIENT"+str(self.remoteAddress)+str(self.remotePort) )

    # -----------------------------------------
    # Thread main loop
    # -----------------------------------------
    def run(self):
        try:
            # send welcome message when a new client is connected
            Utils.log("A new client is connected : "+ self.getColorInfo() )
            self.sendMessage("Welcome ["+self.getNickname()+"]")
            # thread loop
            while True:
                # Receive message from client
                msg = self.client.recv(8*1024)
                # It seems the client has closed the connection : sets the message to "the exit one"
                if len(msg) <= 0:
                    msg = Utils.getEndRequest()
                # exit if the message is the requested one
                if msg == Utils.getEndRequest():
                    # decode last message before exiting
                    msg = msg.decode()
                    Utils.log("Reveived a message from " + self.getColorNickname() + " > '" + str(msg) + "'")
                    # exit and finish the thread
                    break
                # in all other cases, just process the message
                else:
                    #display user list on user command
                    if msg == Utils.getDisplayRequest():
                        msg = msg.decode()
                        Utils.log("Reveived a message from " + self.getColorNickname() + " > '" + str(msg) + "'")
                        self.displayUsers()
                    else:
                        # decode message before process
                        msg = msg.decode()
                        Utils.log("Reveived a message from " + self.getColorNickname() + " > '" + str(msg) + "'")
                        # send the incoming message to ALL clients
                        for lnk in self.allLinks:
                            # if lnk != self:   ### Use it to avoid sending the message back to the sender
                                Utils.log( "Redispatch to "+lnk.getColorNickname() )
                                lnk.sendMessage( str(msg) )
        except Exception as ex:
            Utils.log( self.getColorError() + Utils.getClrStr(" with ",Utils.RED) + self.getColorInfo() +" > "+ Utils.getClrStr(ex,Utils.RED) )

    # -----------------------------------------
    # GETTERS
    # -----------------------------------------
    def getNickname(self):
        return self.nickname
    def getAddress(self):
        return self.remoteAddress 
    def getPort(self):
        return self.remotePort

    # -----------------------------------------
    # DISPLAY
    # -----------------------------------------
    def getColorError(self):
        return Utils.getClrStr("[ERROR]",Utils.RED,Utils.BOLD)
    def getColorAddress(self):
        return Utils.getClrStr("@"+ str(self.remoteAddress) +":"+ str(self.remotePort),Utils.BLUE)
    def getColorNickname(self):
        return Utils.getClrStr("["+ self.nickname +"]", Utils.GREEN, Utils.BOLD)
    def getColorInfo(self):
        return self.getColorNickname()+" "+self.getColorAddress()

    def displayUsers(self):
        for lnk in self.allLinks:
            self.sendMessage( str(lnk.getNickname())+"\n" )

    def sendMessage(self, msg):
        self.client.sendall( msg.encode())


# =============================================================================
# SERVER CLASS
# ============================================================================= 
class Server(Thread):

    # -----------------------------------------
    # Constructor
    # -----------------------------------------
    def __init__(self,prt):
        # Parent constructor
        Thread.__init__(self);
        # attributes initialization
        ipAddresses = socket.gethostbyname_ex(socket.gethostname())[-1]
        self.ID           = Nicknames.getNickname( str(ipAddresses) )
        self.serverSocket = None
        self.port         = prt
        self.clients      = []
        
    # -----------------------------------------
    # Private methods
    # -----------------------------------------
    # Create a server socket
    def createServerSocket(self):
        # open server socket
        self.serverSocket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('', self.port))
        self.serverSocket.settimeout(0.1)
        Utils.log("Server "+self.getColorNickname()+" socket has been created.")

    # Check if a client wants to connect to the server
    def waitForClient(self):
        try:
            # Wait for 1 second to get a new client
            self.serverSocket.listen(10)
            client, address = self.serverSocket.accept()
            self.createLink(client,address)
        except socket.timeout as sto:
            pass

    # Create a socket link with a client (new thread)
    def createLink(self, client, address):
        try:
            # Create new client link and add it to list
            link = ClientServerLink(self, client, address, self.clients)
            link.start()
            self.clients.append(link)
        except Exception as ex:
            Utils.log( self.getColorError() + " an error occured while trying to add a new link : " + Utils.getClrStr(ex,Utils.BLUE) )

    # Remove unused links (finished threads)
    def checkLinks(self):
        for lnk in self.clients:
            if not lnk.is_alive():
                Utils.log( Utils.getClrStr("Closed link -> ",Utils.RED) + lnk.getColorInfo() )
                self.clients.remove(lnk)

    # -----------------------------------------
    # DISPLAY
    # -----------------------------------------
    def getColorError(self):
        return Utils.getClrStr("[ERROR]",Utils.RED,Utils.BOLD)
    def getColorPort(self):
        return Utils.getClrStr(self.port,Utils.BLUE)
    def getColorNickname(self):
        return Utils.getClrStr("["+ self.ID +"]",Utils.YELLOW,Utils.BOLD)
    def getColorDetails(self):
        return Utils.getClrStr(self.serverSocket,Utils.BLUE)
    def displayInfo(self):
        Utils.log("Server "+self.getColorNickname()+" information : ")
        Utils.log("    "+self.getColorDetails() )

    # -----------------------------------------
    # Main loop thread
    # -----------------------------------------
    def run(self):
        Utils.log( "Server "+self.getColorNickname()+" is now running..." )
        try:
            # create server socket
            self.createServerSocket()
            # display information
            self.displayInfo()

            # listen to clients infinite loop
            Utils.log("Server "+self.getColorNickname()+" listening on port " +self.getColorPort()+"...")
            while True:
                # wait for a client to connect
                self.waitForClient()
                # Check all clients are still update
                self.checkLinks()

        except Exception as e:
            # Display error message
            Utils.log( self.getColorError() + " " + Utils.getClrStr(e,Utils.RED) )
        # end of thread life
            Utils.log("Server "+self.getColorNickname()+" has been shut down.")


# =============================================================================
# MAIN PROCESS
# ============================================================================= 
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        srv1 = Server(int(sys.argv[1]))
        srv1.start()

        #mask = ipaddr.IPv4Network('127.0.0.1/8')
        #print()
        #print("----------")
        #print(mask.netmask)
        #print(mask.network)
        #print(mask.is_private)
        #print(mask.broadcast)
        #itr = mask.iterhosts()
        # for i in itr:
        #     print(i)

