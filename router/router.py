import routerFunctions
import commonFunctions
import dataPktFunctions
import selectRP
import time
import threading
import sys
import struct
import json
import os
import itertools
from socket import *

if __name__ == "__main__":

    #read the router's ID from the command line input -id
    myID = int(commonFunctions.getID())
    print("My ID is : {}".format(myID))

    nodeGraph = {str(myID): []}
    #print(nodeGraph)

    #Data structure to keep track of sequence number of received 
    #link state packets
    linkStateSeqNumber = {}

    #if device has no routing table, a file and template will be created
    if(routerFunctions.checkForRoutingTable(myID) == 0):
        print("Creating Initial Routing Table")
        routerFunctions.createFirstRoutingTable(myID)

    #prepare hello packet
    pkttype = 0x05
    #src = myID
    seq = 0x01
    helloACKCounter = 0
    length = len(routerFunctions.getIpFromRoute())
    #routerHelloPacket = struct.pack('BBB', pkttype, seq, src)
    routerHelloPacket = struct.pack('BBB', pkttype, seq, myID)

    ipAddresses = routerFunctions.getIpFromRoute()
    localStoreIPAddresses = ipAddresses
    
    """
    Router "Hello" logic. The router spins a new thread every iteration of the loop. The thread
    loops through the ipAddresses array and sends a router hello packet. If the logic succesfully 
    receives an ACK, the ip address for that ACK is removed from the ipAddresses array. 
    """
    while(helloACKCounter != length):
        routerHelloThread = threading.Thread(target = routerFunctions.sendRouterHello, args=(myID, routerHelloPacket, ipAddresses))
        routerHelloThread.start()
        temp, nodeGraph, ipOfACK = routerFunctions.receiveRouterHello(myID, nodeGraph)
        if(ipOfACK is not None):
            try:
                localStoreIPAddresses.remove(ipOfACK)
            except:
                print("No such IP")
        helloACKCounter = helloACKCounter + temp
        routerHelloThread.join()
        ipAddresses = localStoreIPAddresses
    
    #initializes Link State transmission to occur every 10 seconds
    routerFunctions.sendLinkState(myID, nodeGraph)

    while True:
        #listen on all ports logic here

        receivedPkt, addr = routerFunctions.receive_packet('0.0.0.0', 8888)
        packetType = routerFunctions.decodePktType(receivedPkt)
        
        #if packet type 1, Hello, respond with Hello ACK
        if(packetType == 1):
            helloType, helloSeq, helloSrc = routerFunctions.read_hello(receivedPkt)
            print("HelloSrc is: {}".format(helloSrc))

            #Call a function to DO something with the SRC you got.
            routerFunctions.sendHelloACK(helloSrc)

            #!! This should be an append situation, not a completely new file
            #This is an artifact from testing, should be replaced with an append
            routerFunctions.addHostToGraph(helloSrc, myID, nodeGraph)

        if(packetType == 2):
            ipAddresses = routerFunctions.getIpFromRoute()
            seq, length, src, data = routerFunctions.decodeLinkStatePkt(receivedPkt)
            """
            print("Here's the src value")
            print(src)
            print("Here the data")
            print(data)
            print(linkStateSeqNumber)
            """
            if(src != myID):
                if(src > 150):
                    ipAddresses = routerFunctions.getIpFromRoute()
                    ipAddresses.remove(addr[0])   
                linkStateForwardThread = threading.Thread(target=routerFunctions.forwardLinkState, args=(ipAddresses, receivedPkt))
                linkStateForwardThread.run()
                nodeGraph = routerFunctions.updateGraph(seq, src, linkStateSeqNumber, data, nodeGraph)
                #Run dijkstra after updating nodeGraph
                routerFunctions.runDijkstra(nodeGraph, myID)
 
                #Seeing if clearing this slows things down..?
                packetType = 0
                
            #spin new thread to forward link state on all nodes except the node it
            #came in on!!

        #In the event a router hello packet was previously missed
        if(packetType == 5):
            helloACKpkt = struct.pack('BBB', 0x04, 0x01, myID)
            pkttype, seq, srcVal = struct.unpack('BBB', receivedPkt)
            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.sendto(helloACKpkt, (commonFunctions.convertID(srcVal), 8888))
            my_socket.close()
            print("Got a hello message!")

        if(packetType == 7):
            print("Recveied Data Packet")
            #print("Sending dataACK")
            #print(addr)
            time.sleep(1)
            routerFunctions.sendDataACK(addr[0])
            #decode packet
            seq, recID, ndest, rdest, dest1, dest2, dest3, data = commonFunctions.decodeDataPkt(receivedPkt)
            pktType = 0x07
            n = 3
            print("Received PKT     pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data")
            print("with information   {}       {}   {}    {}       {}           {}         {}         {}      {}".format(pktType, seq, recID, ndest, rdest, dest1, dest2, dest3, data))
            #Determine Core router runctionality or RP router functionality
            if (int(dest1) == int(dest2) == int(dest3) == 0):
                print("Received data packet from hostSender")
                #Assume Core Router functionality
                #If ndest is 1 unicast message to dest1
                #n from k out of n (hardcoded to 3 for this project)
                selectedRP, selectedDests = selectRP.selectRP(ndest,n,myID,recID)
                dests = [0] * 3
                dests[0:len(selectedDests)] = selectedDests
                
                if (ndest == 1):
                    print("ndest was 1, preparing to send unicast to destination")
                    #send datapkt to dest1
                    selectedRP = 0
                    datapkt = commonFunctions.createDataPacket(pktType, seq, recID, ndest, selectedRP, dests[0], dests[1], dests[2], data)
                    nextHop = commonFunctions.getNextHop(myID,dests[0])
                    print("Created PKT      pktType, seq, src, ndest, rdest, dests[0], dests[1], dests[2], data")
                    print("with information   {}       {}   {}    {}       {}     {}       {}        {}        {}".format(pktType, seq, recID, ndest, selectedRP, dests[0], dests[1], dests[2], data))
                    routerFunctions.sendData(datapkt, nextHop, myID)

                else:
                    if myID == selectedRP:
                        print("Core Router is also RP")
                        rdest = 0
                        dataPktFunctions.rpFunction(myID, pktType, n, seq, recID, ndest, rdest, dests[0], dests[1], dests[2], data)
                    else:
                        print("ndest was {}, preparing to send to RP".format(ndest))
                        dataPktFunctions.sendToRP(myID, pktType, n, seq, recID, ndest, rdest, selectedRP, dests, data)

            elif (ndest == 1 and rdest == 0):
                print("router along path to destination, preparing to forward along message")
                dataPktFunctions.forwardDataPkt(myID, dest1, receivedPkt)

            elif (rdest != 0 and myID != rdest):
                print("router along path to RP, preparing to forward along message")
                dataPktFunctions.forwardDataPkt(myID, rdest, receivedPkt)

            else:
                print("router along path to multiple destinations, checking to see how to forward message along")
                dataPktFunctions.rpFunction(myID, pktType, n, seq, recID, ndest, rdest, dest1, dest2, dest3, data)

