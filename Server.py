import socket
import sys
import os 
import json 
from pprint import pprint as pp
import itertools
import Algo as A
import ast
import threading
from threading import Thread, Lock 
import time
import queue
import routemod as rmod 
from datetime import datetime

#Generate Table for data Storage
topology = { "data":[]}
table = {"data":[]}
routing = {"data":[]}
temprouting = {"data":[]}
newtop={}
oldtop={}
topfromswitch = {}
oldtopfromswitch = {}
Mcounter = []
K = 2.0
M = 4.0
bit = 0
counter = 0
badconnectionlist = []
que = queue.Queue()
switchtime = []
timelock = Lock()
ntoplock = Lock()
otoplock = Lock()
temprlock = Lock()


#For Table with neighbors
def fil_table(ID,hostname,port,table):
    user = {}
    user["ID"]=ID
    user["Hostname"]=hostname
    user["Port"]=port
    user["Neighbor"] = getmatchingpair(ID,topology)
    table["data"].append(user)

#For Table with Toplogy 
def fil_topology(line1):
    user = {}
    user["pair1"]=line1[0]
    user["pair2"]=line1[1]
    user["BW"]=line1[2]
    user["Delay"]=line1[3]
    topology["data"].append(user)

def fil_temprouting(line1, temprouting2):
    user = {}
    user["pair1"]=line1["pair1"]
    user["pair2"]=line1["pair2"]
    user["BW"]=line1["BW"]
    user["Delay"]=line1["Delay"]
    temprouting2["data"].append(user)

def getcurrentlist(temprouting):
    currentlist = []
    for index in temprouting['data']:
        if int(index["pair1"]) not in currentlist:
            currentlist.append(int(index["pair1"]))
        if int(index["pair2"]) not in currentlist:
            currentlist.append(int(index["pair2"]))
        else: 
            pass
    return currentlist

def routingtable(ID,table,topology,registercounter):
    for i in range(len(TxtLines)-1):
        if (ID == int(topology["data"][i]["pair1"])) and (int(topology["data"][i]["pair2"]) in registercounter):
            fil_temprouting(topology["data"][i],routing)
        elif (ID == int(topology["data"][i]["pair2"])) and (int(topology["data"][i]["pair1"]) in registercounter):
            fil_temprouting(topology["data"][i],routing)
        else:
            pass

#Function for sending neighbors to each active switch
def sendswitchesinfo():
    for  i in range(int(NumofSwitches)):
        switchneighbors = table["data"][i]["Neighbor"] 
        responsemessage =" "
        responsemessage = responsemessage +'REGISTER_RESPONSE'
        responsemessage = responsemessage + " Neighbors: " + str(switchneighbors).replace(" ", "")
        for elements in switchneighbors:
            if alivelist[elements-1] == 1:
                for j in range(int(NumofSwitches)):
                    if elements == table["data"][j]["ID"]:
                        responsemessage = responsemessage + " Alivelist: " + str(1)   
                        responsemessage = responsemessage + " ID: " + str(elements)
                        responsemessage = responsemessage + " Host: " + str(table["data"][j]["Hostname"])
                        responsemessage = responsemessage + " PortNumber: "+ str(table["data"][j]["Port"] )
        s.sendto(bytes(str(responsemessage), 'utf-8'),(str(table["data"][i]["Hostname"]),int(table["data"][i]["Port"])))
        print('REGISTER_RESPONSE '+ str(table["data"][i]["ID"]) + ' Sent @ ' +  str(datetime.now())) #Logging

#

def sendnewswitchesinfo():
    for  i in range(len(table["data"])):
        switchneighbors = table["data"][i]["Neighbor"]
        responsemessage =" "
        responsemessage = responsemessage +'REGISTER_RESPONSE'
        responsemessage = responsemessage + " Neighbors: " + str(switchneighbors).replace(" ", "")
        for elements in switchneighbors:
            if alivelist[elements-1] == 1:
                for j in range(int(NumofSwitches)):
                    if elements == table["data"][j]["ID"]:
                        responsemessage = responsemessage + " Alivelist: " + str(1)
                        responsemessage = responsemessage + " ID: " + str(elements)
                        responsemessage = responsemessage + " Host: " + str(table["data"][j]["Hostname"])
                        responsemessage = responsemessage + " PortNumber: "+ str(table["data"][j]["Port"] )
        s.sendto(bytes(str(responsemessage), 'utf-8'),(str(table["data"][i]["Hostname"]),int(table["data"][i]["Port"])))
        print('REGISTER_RESPONSE '+ str(table["data"][i]["ID"]) + ' Sent @ ' +  str(datetime.now())) #Logging


def sendrtable(rtable):
    responsemessage = 'ROUTE_UPDATE ' + str(rtable).replace(" ", "")
    time.sleep(.2)
    for i in range(int(NumofSwitches)):
        s.sendto(bytes(str(responsemessage), 'utf-8'),(str(table["data"][i]["Hostname"]),int(table["data"][i]["Port"])))
    print(responsemessage + ' Sent @ ' + str(datetime.now())) #Logging

#Reads Topology.txt file for infomation on neighbors and # of switch
with open("topology.txt", "r") as pyFile:
            Txt = pyFile.read()
            TxtLines = Txt.splitlines()
            NumofSwitches=TxtLines[0]
            for i in range(1,len(TxtLines)):
                line1 = TxtLines[i].split()
                fil_topology(line1)
            y = json.dumps(topology)

#Create two lists for reference, one with the counter of switches and 
#the other for the bit vector of liveness 
alivelist = []
registercounter = []
#Generate Switch List from Topology
def switchlist(topology):
    switchcounter = []
    for i in range(len(TxtLines)-1):
            if (int(topology["data"][i]["pair1"]) not in switchcounter):
                switchcounter.append(int(topology["data"][i]["pair1"]))
            elif (int(topology["data"][i]["pair2"]) not in switchcounter):
                switchcounter.append(int(topology["data"][i]["pair2"]))
            else:
                pass
    print('Controller Started, waiting for Switches')
    return switchcounter

switchcounter = switchlist(topology)
for i in range(1,int(NumofSwitches)+1):
    alivelist.append(1)

#Find neighbor
def getmatchingpair(id,topology):
    neighborid = [] 
    for i in range(1,len(TxtLines)):
        if (int(id) == int(topology["data"][i-1]["pair1"])):    
            neighborid.append(int(topology["data"][i-1]["pair2"]))
        elif (int(id) == int(topology["data"][i-1]["pair2"])):    
            neighborid.append(int(topology["data"][i-1]["pair1"]))
        else: 
            pass
    return neighborid

def makestringtoset(a):
    if a == set({}):
        holder = set({})
        return holder
    holder =''
    for i in range(len(a)):
        if a[i] == a[-1]:
            holder=holder+a[i]
        elif i >= 3:
            holder=holder+a[i]+' '
    holder=ast.literal_eval(holder)
    return holder

def checkdeadswitch(first_dict, second_dict): 
    diff = set(first_dict.keys()) - set(second_dict.keys())
    return diff

def checkdeadlink(first, second):
    sharedKeys = set(first.keys()).intersection(second.keys())
    deadlist = []
    for key in sharedKeys:
        if first[key] != second[key]:
            deadlist.append((key, first[key].difference(second[key])))
    return deadlist

def checkrevlink(first, second):
    sharedKeys = set(first.keys()).intersection(second.keys())
    revlist = []
    for key in sharedKeys:
        if first[key] != second[key]:
            revlist.append((key, second[key].difference(first[key])))
    return revlist

def serversendhandler():
    global temprouting
    global newtop
    global oldtop 

    while True: 
        diff = []
        deadswitch = []

        for i in range(len(registercounter)):
            diff.append(time.time()-switchtime[i])
            if diff[i] > M*K:
                deadswitch.append(registercounter[i])
        if len(deadswitch) != 0:
            try:
                for element in deadswitch:
                    otoplock.acquire()
                    oldtop.pop(element)
                    otoplock.release()
                    temprlock.acquire()
                    temprouting, rtable = rmod.modifyroutingdead(temprouting, deadswitch) #TODO: Add Badconnectionlist
                    temprlock.release()
                    if rtable != None:
                        sendrtable(rtable)
            except KeyError:
                otoplock.release()
                
        time.sleep(K)
    
#Specifying UDP
s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

#binding process
s.bind((socket.gethostname(),1234))

#wait for dynamic register requests from switches
while True:
    try:
        data, addr=s.recvfrom(2048)
    except ConnectionResetError:
        pass
    clientdata = data.decode("utf-8")
    if ('REGISTER_REQUEST' in clientdata):
        ID = int(data.split()[1]) #get ID
        print('REGISTER_REQUEST' + ' ' + str(ID)+ ' Received @ ' +  str(datetime.now())) #Logging
        if ID in switchcounter:
            switchcounter.remove(ID) #remove ID from list
            registercounter.append(ID)
            switchtime.append(time.time())
        else:
            switchcounter.append(ID)
            rtable = []
            rtable = A.widest_path(routing, sorted(registercounter), [])
            for i in range(len(table['data'])):
                if table['data'][i]['ID'] == ID:
                    table['data'][i]['Port'] = addr[1]
            sendnewswitchesinfo()
            sendrtable(rtable)



        hostname = addr[0] #get hostname 
        port = addr[1] #get port
        fil_table(ID,hostname,port,table) #file table
        routingtable(ID,table,topology,registercounter)
        if (len(switchcounter) == 0): #if all switch are registered, send info to everyone 
            print("All Switches have been registered")
            for i in range(len(table['data'])):
                oldtop.update({int(table["data"][i]["ID"]) : set(table["data"][i]["Neighbor"])})
            temprouting = routing
            rtable = []
            rtable = A.widest_path(routing,sorted(registercounter),[])
            sendswitchesinfo()
            sender =  Thread(target=serversendhandler, args= ())
            sender.start()
            if rtable != []:
                sendrtable(rtable)

    
    if ('TOPOLOGY_UPDATE' in clientdata):
        c = clientdata.split()
        ntoplock.acquire()
        newtop.update( {int(c[2]) : makestringtoset(c)} )
        ntoplock.release()
        
        for i in range(len(registercounter)):
            if int(registercounter[i]) == int(c[2]):
                timelock.acquire()
                switchtime[i] = time.time()
                timelock.release()

        if len(oldtop) > len(newtop):
            pass
        elif len(oldtop) < len(newtop):
            revswitch = rmod.checkdeadswitch(newtop, oldtop)
            temprouting, rtable = rmod.modifyroutingrev(temprouting, routing, revswitch)
            if rtable != []:
                sendrtable(rtable)
            
            otoplock.acquire()
            oldtop = newtop
            otoplock.release()

        elif newtop.keys() == oldtop.keys():
            deadlinks = rmod.checkdeadlink(oldtop, newtop)
            temprlock.acquire()
            temprouting, rtable,badconnectionlist = rmod.modifyroutingdeadlink(temprouting, deadlinks,badconnectionlist)
            temprlock.release()
            if rtable != []:
                sendrtable(rtable)
            revlinks = rmod.checkrevlink(oldtop, newtop)
            temprlock.acquire()
            temprouting, rtable,badconnectionlist = rmod.modifyroutingrevlink(temprouting, routing, revlinks,badconnectionlist)
            temprlock.release()
            if rtable != []:
                sendrtable(rtable)
            
            otoplock.acquire()
            ntoplock.acquire()
            
            oldtop = newtop
            newtop ={}
            
            otoplock.release()
            ntoplock.release()
        else: 
            pass
