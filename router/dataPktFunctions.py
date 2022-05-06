import sys
sys.path.append('../')
import commonFunctions
import routerFunctions
import time
from socket import *
import struct
import select
import random
import asyncore
import threading
import json
import os
import subprocess
import re
from collections import defaultdict
import dijkstra
import itertools

def sendToRP(myID, pktType, n, seq, recID, ndest, rdest, selectedRP, dests, data):
    #print("ndest was {}, preparing to send to RP".format(ndest))
    #If ndest > 1 then need to send information to RP
    #Send pkt to selectedRP
    emptyDests = dests.count(0)
    ndest = n - emptyDests
    datapkt = commonFunctions.createDataPacket(pktType, seq, recID, ndest, selectedRP, dests[0], dests[1], dests[2], data)
    nextHop = commonFunctions.getNextHop(myID, selectedRP)
    print("Created PKT      pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data")
    print("with information   {}       {}  {}      {}      {}        {}       {}        {}      {}".format(pktType, seq, recID, ndest, selectedRP, dests[0], dests[1], dests[2], data))
    routerFunctions.sendData(datapkt, nextHop, myID)    

def forwardDataPkt(myID, dest, receivedPkt):
    #print("router along path to destination, preparing to forward along message")
    #Forward packet to dest1 (which is the only destination)
    nextHop = commonFunctions.getNextHop(myID, dest)
    routerFunctions.sendData(receivedPkt, nextHop, myID)
    print("Forwading data to {} next hop is {} ".format(dest, nextHop))

def rpFunction(myID, pktType, n, seq, recID, ndest, rdest, dest1, dest2, dest3, data):
    #print("router along path to multiple destinations, checking to see how to forward message along")
    #Assume RP functionality

    print("Bifurcate Info   pktType, seq, src, ndest, rdest, dests[0], dests[1], dests[2], data")
    print("with information   {}       {}  {}      {}      {}        {}       {}        {}      {}".format(pktType, seq, recID, ndest, rdest, dest1, dest2, dest3, data))

    #Get paths for 
    dests = []
    destsPath = []
    for id in (dest for dest in [dest1, dest2, dest3] if dest != 0):
        dests.append(id)
        destsPath.append(routerFunctions.getPath(myID,id))

    #Check combinations of paths to see if next hop is the same
    lookaheadFlag = []
    index = range(len(destsPath))
    for a, b in itertools.combinations(index, 2):
        if destsPath[a][0] == destsPath[b][0]:
            lookaheadFlag.append([a,b])
        #print("DestPathA {}: {} DestPathB {}: {}".format(a,destPath[a][0], b, destPath[b][0]))

    #Determine how to send packets based on if other destinations
    #have the same next hop
    if len(lookaheadFlag) == len(destsPath):
        print("all destinations have the same next hop, only sending one data packet")
        #All messages going to same next hop
        ndest = len(dests)
        rdest = 0
        for ii in range(n - ndest):
            dests.append(0)
        datapkt = commonFunctions.createDataPacket(pktType, seq, recID, ndest, rdest, dests[0], dests[1], dests[2], data)
        nextHop = commonFunctions.getNextHop(myID,dests[0])
        print("Created PKT      pktType, seq, src, ndest, rdest, dests[0], dests[1], dests[2], data")
        print("with information   {}       {}  {}      {}      {}        {}       {}        {}      {}".format(pktType, seq, recID, ndest, rdest, dests[0], dests[1], dests[2], data))
        routerFunctions.sendData(datapkt, nextHop, myID)
        
    else:
        print("Need to bifurcate, will split and send messages accordingly")
        #Just send dests[lookaheadFlag[0][0]] and dests[lookaheadFlag[0][1]] to gether but
        #not the other value
        #If this condition is hit there will only be one entry in the lookaheadFlag
        #send(dests[lookaheadFlag[0][0]] and dests[lookaheadFlag[0][1]])
        if len(lookaheadFlag) == 0:
            ndest = 1
            rdest = 0
            for id in dests:
                datapkt = commonFunctions.createDataPacket(pktType, seq, recID, ndest, rdest, id, 0, 0, data)
                nextHop = commonFunctions.getNextHop(myID,id)
                print("Created PKT      pktType, seq, src, ndest, rdest, dests[0], dests[1], dests[2], data")
                print("with information   {}       {}  {}      {}      {}        {}       {}        {}      {}".format(pktType, seq, recID, ndest, rdest, id, 0, 0, data))
                routerFunctions.sendData(datapkt, nextHop, myID)
        else:
            ndest = 2
            rdest = 0
            datapkt = commonFunctions.createDataPacket(pktType, seq, recID, ndest, rdest, dests[lookaheadFlag[0][0]], dests[lookaheadFlag[0][1]], 0, data)
            nextHop = commonFunctions.getNextHop(myID,dests[lookaheadFlag[0][0]])
            print("Created PKT      pktType, seq, src, ndest, rdest, dests[0], dests[1], dests[2], data")
            print("with information   {}       {}  {}      {}      {}        {}       {}        {}      {}".format(pktType, seq, recID, ndest, rdest, dests[lookaheadFlag[0][0]], dests[lookaheadFlag[0][1]], 0, data))
            routerFunctions.sendData(datapkt, nextHop, myID)            
            if len(destsPath) == 3:
                dests.pop(lookaheadFlag[0][0])
                dests.pop(lookaheadFlag[0][1])
                ndest = 1
                datapkt = commonFunctions.createDataPacket(pktType, seq, recID, ndest, rdest, dests[0], 0, 0, data)
                nextHop = commonFunctions.getNextHop(myID,dests[0])
                print("Created PKT      pktType, seq, src, ndest, rdest, dests[0], dests[1], dests[2], data")
                print("with information   {}       {}  {}      {}      {}        {}       {}        {}      {}".format(pktType, seq, recID, ndest, rdest, dests[0], 0, 0, data))
                routerFunctions.sendData(datapkt, nextHop, myID)

rpFunction(201, 7, 3, 1, 101, 2, 0, 102, 103, 0, "This is a 2 out of 3 multicast message")
