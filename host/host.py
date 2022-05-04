import sys
sys.path.append('../')
import commonFunctions
import hostFunctions
import time
import struct
import os, subprocess
from socket import *

if __name__ == "__main__":

    #read the hosts's ID from the command line input -id
    myID = int(commonFunctions.getID())
    #host maintains and broadcasts it's single link state
    #does not maintain data about the rest of the network
    myLink = {str(myID): []}
    
    #Maybe, need function here to setup particular host as the
    #broadcast node or not

    #create hello packet
    pkttype = 0x01
    src = myID
    #print("src is : ".format(src))
    seq = 0x01
    hello = struct.pack('BBB', pkttype, seq, src)
    #hello = hostFunctions.createHelloPacket()
    #Sends hello on its broadcast IP address

    data, addr, myLink = hostFunctions.sendHelloPacket(commonFunctions.convertID(myID), hello, '192.168.1.255', myLink, myID)
    
    hostFunctions.broadcastLinkState(myID, '192.168.1.255', myLink)

    while True:
        """
        #**** for testing, remove before flights ******
        #create hello packet
        pkttype = 0x08
        src = myID
        #print("src is : ".format(src))
        seq = 0x01
        hello = struct.pack('BBB', pkttype, seq, src)
        
        my_socket = socket(AF_INET, SOCK_DGRAM)
        my_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) 
        my_socket.sendto(hello, ('192.168.1.255', 8888))
        my_socket.close()
        print("Sent ACK Packet")
        time.sleep(1)
        """

        data = hostFunctions.receive_packet('0.0.0.0', 8888)
        #NEED to update function to move on after receiving ACK

        packetType = hostFunctions.decodePktType(data)

        if(packetType[0] == 8):
            print("I'm a host and got some data")

    #create data packet
    pktType = 0x07
    src = myID
    seq = 0x01
    #k out of n destinations 1-3
    ndest = 3
    data = "This is a {} out of 3 multicast message".format(ndest)
    #rdest, dest1-3, will not be set when host sends pkt
    #Core router will determine those values
    #At this point the host should know the attached router
    #Does it make sense to send to that router or still broadcast like hellopkt?
    rdest = 0
    dest1 = 0
    dest2 = 0
    dest3 = 0
    datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, rdest, dest1, dest2, dest3, data)
    #code to send datapkt
