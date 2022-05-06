import os, json, glob
from operator import itemgetter

def bestkn(k,n,myID,srcID):
    """
    Determines best K out of N destinions to send to

    Arguments:
        k       - number of destination
        n       - maximum number of destinations (CAN PROBABLY REMOVE VALUE)
        myID    - ID of routing being run on
        srcID   - ID of host sending multicast packet

    Returns:
        sortedDest - list of IDs of best K out of N destinations
    """
    #Open current routers routing table
    with open(str(myID) + '.json', 'r') as f:
        routingTable = json.load(f)
    #Iterate through routing table and gather all destinations
    destRouting = {}
    for dest in routingTable['destination']:
        #Destinations are between ID's 100 and 199
        #Also excluding the host sending the multicast packet
        if (int(dest) >= 100) & (int(dest) < 200) & (int(dest) != srcID):
            destRouting.update({dest: routingTable['destination'][dest]['cost']})
    #print(destRouting)
    #Sort inforation by cost to destination
    sortedDest = sorted(destRouting.items(), key=itemgetter(1))
    #Remove tuple value so only ID remains
    sortedDest = map(itemgetter(0), sortedDest)
    #print(sortedDest)
    #Narrow down to only K number of destinations
    for ii in range(len(sortedDest) - k):
        sortedDest.pop()
    #print(sortedDest)
    return sortedDest


def selectRP(k,n,myID,srcID):
    """
    Selects the router that should become the RP

    Arguments:
        k       - number of destination
        n       - maximum number of destinations (CAN PROBABLY REMOVE VALUE)
        myID    - ID of routing being run on
        srcID   - ID of host sending multicast packet

    Returns:
        selectedRP - ID of selected RP
    """
    #Determine best K out of N destinations
    dest = bestkn(k,n,myID,srcID)
    #Threshold value for how far destinations can be from RP
    threshold = 3
    #initalize centralTable JSON
    ceteralTable = []

    #Create array to store names of all routing tables
    contents = []
    #Open folder containing all routing tables
    routingTablePath = os.getcwd()
    json_pattern = os.path.join(routingTablePath, '*.json')
    file_list = glob.glob(json_pattern)
    for file in file_list:
        contents.append(file)

    #Loop over all routing tables and build centeralTable
    for file in contents:
        with open(file,'r') as f:
            data = json.load(f)
        #Pull costs for each destination on a given router
        #Store them in a serpate array so they can be indiviually parsed later
        destCost = []

        for node in data['destination']:
            #print(node)
            #print(data["destination"][node])
            #print(data["destination"][node]["cost"])
            if node in dest:
                destCost.append(data['destination'][node]['cost'])

        #Get Filename
        #Which is also router ID
        (fileName, ext) = os.path.splitext(os.path.basename(file))
        #Create JSON for each router entry
        tableElement = {
            "router": fileName,
            "destDist": destCost,
            "totCost": sum(destCost)
        }

        #Update entry to centeralTable
        ceteralTable.append(tableElement)

    #print(json.dumps(ceteralTable, indent = 3, sort_keys=True))

    #Select RP from centeralized table
    selectedRP = ""
    costRP = 256
    for ii in range(len(ceteralTable)):
        #If router has lower cost it is eligible RP
        if ceteralTable[ii]["totCost"] < costRP:
            #Check destDist against threshold
            #This help in tie breaking if necessary
            if all(yy <= threshold for yy in ceteralTable[ii]["destDist"]):
                selectedRP = ceteralTable[ii]["router"]
                costRP = ceteralTable[ii]["totCost"]
            else:
                continue
        #if ceteralTable[ii]["totCost"] == costRP:

    print("The selected RP is : {}".format(selectedRP))
    return int(selectedRP), dest

#selectRP(1,3,202,102)
