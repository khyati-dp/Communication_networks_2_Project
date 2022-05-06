import subprocess
import struct
import json

def getID():
    p = subprocess.Popen("ifconfig | grep 192 | awk '{print $2}' | awk -F. '{print $4}'", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return output

def convertID(id):
    return "192.168.1." + str(id)

def createDataPacket(pktType, seq, src, ndest, rdest, dest1, dest2, dest3, data):
    """
    Create data packet
    """
    pktFormat = "BBBBBBBBB"
    dataPkt = struct.pack(pktFormat, pktType, seq, src, len(data), int(ndest), int(rdest), int(dest1), int(dest2), int(dest3))+data
    return dataPkt

def decodeDataPkt(pkt):
    """
    Decodes Data Packet as byte, int, int, byte and 
    assumes that data has been concatenaged to the end of the 
    incoming packet

    Arguments:
        pkt {packed struct} -- Data that needs to be unpacked

    Returns:
        seq, src, length, ndest, rdest, dest1, dest2, dest3 -- Returns all unpacked data except pktType
    """
    pktFormat = "BBBBBBBBB"
    pktSize = struct.calcsize(pktFormat)
    pktHeader = pkt[:pktSize]

    pktType, seq, src, length, ndest, rdest, dest1, dest2, dest3 = struct.unpack(pktFormat, pktHeader)
    data = pkt[pktSize:]

    return seq, src, ndest, rdest, dest1, dest2, dest3, data

def getNextHop(myID, destID):
    #print("myID: {} destID: {}".format(myID,destID))
    with open(str(myID) + '.json', 'r') as f:
        routingTable = json.load(f)
    #print("Next hop is {}".format(routingTable['destination'][str(destID)]['path'][0]))
    return routingTable['destination'][str(destID)]['path'][0]
