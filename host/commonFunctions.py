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

    #print("DATA: {} ADDR: {} MYLINK: {}".format(data, addr, myLink))

    while True:
        """
        try:
            while True:
                receivedPkt, addr = hostFunctions.receive_packet('0.0.0.0', 8888)

                packetType = hostFunctions.decodePktType(receivedPkt)

                if(packetType == 8):
                    print("Received dataACK")

        #Interupting the code by hitting CTRL+C lets you send a data packet on demand
        except KeyboardInterrupt:
        """
        #k out of n destinations 1-3
        ndest = input("Enter K out of N (1-3):")
        print("Multicasting to {} out of 3".format(ndest))
        #create data packet
        pktType = 0x07
        src = myID
        seq = 0x01
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
        #hostFunctions.sendData(datapkt, 201, myID)
        hostFunctions.sendData(datapkt, myLink[str(myID)][0], myID)
        print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, rdest, dest1, dest2, dest3, data))
