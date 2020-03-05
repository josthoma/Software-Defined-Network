import socket
import sys
from pprint import pprint as pp
from threading import Thread, Lock

import time
import ast 
import queue
from datetime import datetime

threadlist=[]
K = 2.0 
M = 4.0 
que = queue.Queue()
que1 = queue.Queue()
alivelist = set({})
notdead = set({})
counter = 0
bit = 0
nswtichtime = []

#CLI Example
#python Client.py {id} {hostname} 1234

#Example run
#python Client.py 1 DESKTOP-865AFU4 1234

def sendKeepAlive(ID,table, nID): 
    for i in range(len(table['Neighbours Alive Flag'])):
        if int(table['Neighbours Alive Flag'][i]) == 1 and int(table['Neighbours'][i]) != nID and int(table['Neighbours'][i]) in alivelist:
            message= ('KEEP_ALIVE ' +ID)
            t= bytes(message, 'utf-8')
            d.sendto(t,(table['Neighbours Hostname'][i],int(table['Neighbours Port'][i])))
            if skey == '-v':
                print(message + ' sent @ ' +  str(datetime.now())) #Logging


def sendTop(alivelist,ID):
    message= ('TOPOLOGY_UPDATE FROM ' + ID + ' ' + str(alivelist))
    t= bytes(message, 'utf-8')
    
    d.sendto(t,(controller_hostname,controller_port))

def deathupdate(ID,table,alivelist,notdead ):
    Dead = alivelist.difference(notdead) #Check
    Revived = notdead.difference(alivelist)
    if len(Dead) > 0:
        print(str(Dead) + ' is not reachable @ ' +  str(datetime.now())) #Logging
    if len(Dead) == 0 and len(Revived) == 0:
        notdead = set({})
    elif len(Dead) == 0 and len(Revived) != 0:
        notdead = set({})
    else:
        alivelist = notdead
        sendTop(alivelist,ID)
        notdead = set({})
    return alivelist, notdead

def sendhandler(skey, ID, nID):
    global alivelist 
    global notdead 
    global nswtichtime
    while True:
        deadlink =[]
        diff = []
        for i in range(len(nlist)):
            diff.append(time.time()-nswtichtime[i])
            if diff[i] > M*K:
                deadlink.append(nlist[i])
        if len(deadlink) != 0:
            lockdead.acquire()
            lockalive.acquire()
            alivelist, notdead = deathupdate(ID,table,alivelist,notdead) #Send updated top
            lockalive.release()
            lockdead.release()
        if skey == '-f':
            sendKeepAlive(ID,table, nID)
        else:
            sendKeepAlive(ID,table, None)
        sendTop(alivelist,ID)
        time.sleep(K)


def receivehandler(skey):
    global alivelist 
    global notdead 
    global nswtichtime
    global table
    global neighbourlist
    while True: 
        try:
            data =d.recv(4096)
        except ConnectionResetError:
            pass
        serverdata = data.decode("utf-8")
        if ('KEEP_ALIVE' in serverdata):
            s = serverdata.split()
            if skey == '-v':
                print(str(s[0]) + ' ' + str(s[1]) + ' Received @ ' + str(datetime.now()))  # Logging
            if skey == '-f':
                badn = nID
            else:
                badn = None
            
            for i in range(len(table['Neighbours'])):
                if (table['Neighbours'][i]) == int(s[1]) and int(s[1]) != badn:
                    time.sleep(.2)
                    notdead.add(int(s[1]))

                    for j in range(len(nlist)):
                        if int(nlist[j]) == int(s[1]):

                            nswtichtime[j] = time.time()

                    if int(s[1]) not in alivelist:
                        if len(s[1]) >= 0:
                            print(str(s[1]) + ' is now reachable @ ' + str(datetime.now()))  # Logging
                        lockalive.acquire()
                        alivelist.add(int(s[1]))
                        lockalive.release()
                        sendTop(alivelist, ID)

        if ('REGISTER_RESPONSE' in serverdata):
            s = serverdata.split()
            print(str(s[0]) + ' received @ ' +  str(datetime.now())) #Logging
            neighbourlist = []
            for index, values in enumerate(s[2]):
                if index %2 == 1:
                    try:
                        neighbourlist.append(int(values))
                    except ValueError:
                        pass
            aliveflag = []
            neighbourhostnames = []
            neighbourports = []
            for parameters in range(4, len(s),8): 
                try:
                    aliveflag.append(int(s[parameters]))
                    neighbourhostnames.append(s[parameters+4])
                    neighbourports.append(int(s[parameters+6]))
                except IndexError:
                    print('end of list reached')
                except ValueError:
                    pass
            table = {'Neighbours' : neighbourlist,
                    'Neighbours Alive Flag': aliveflag,
                    'Neighbours Hostname': neighbourhostnames,
                    'Neighbours Port': neighbourports}

        if ('ROUTE_UPDATE' in serverdata):
            s = serverdata.split()
            rtable = s[1]
            rtable = list(ast.literal_eval(rtable))
            src = int(ID)
            for element in rtable:
                if src == int(element[0]):
                    des = int(element[1])
                    hoplist = element[4]
                    if len(hoplist) == 0:
                        hop = des
                    elif len(hoplist) >=2:
                        for i in hoplist:
                            if i in neighbourlist:
                                hop = i
                    else:
                        hop = element[4][0]
                    print(str(src) + ',' + str(des)+ ':' + str(hop))
                elif src == int(element[1]):
                    des = int(element[0])
                    hoplist = element[4]
                    if len(hoplist) == 0:
                        hop = des
                    elif len(hoplist) >=2:
                        for i in hoplist:
                            if i in neighbourlist:
                                hop = i
                    else:
                        hop = element[4][0]
                    print(str(src) + ',' + str(des) + ':' + str(hop) )
                else:
                    pass
            print('Logged Routing Table @ ' +  str(datetime.now())) #Logging
        


ID = None # to check type of ID to type cast
controller_hostname = None
controller_port = None
skey = None
nID = None
#command-line arguments assigning
for i in range(len(sys.argv)):
    if i == 1:
        ID = sys.argv[1]
    if i ==2: 
        controller_hostname = sys.argv[2]
    if i ==3: 
        controller_port=  int(sys.argv[3])
    if i == 4: 
        skey = sys.argv[4]
    if i == 5:
        nID = int(sys.argv[5])
    else:
        pass

#socket creation
d= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)




#concatenation of register request with ID
registermessage= ('REGISTER_REQUEST ' +ID)
b= bytes(registermessage, 'utf-8') #encoding to typecast string type to byte type

print(registermessage + ' Sent @ ' +  str(datetime.now())) #Logging
#send to controller
d.sendto(b,(controller_hostname,controller_port))

#wait and receive register response from controller

data =d.recv(4096)
serverdata = data.decode("utf-8")

while ('KEEP_ALIVE' in serverdata):
    data =d.recv(4096)
    serverdata = data.decode("utf-8")

if ('REGISTER_RESPONSE' in serverdata):
    s = serverdata.split()
    print(str(s[0]) + ' received @ ' +  str(datetime.now())) #Logging
    neighbourlist = []
    for index, values in enumerate(s[2]):
        if index %2 == 1:
            try:
                neighbourlist.append(int(values))
            except ValueError:
                pass
    aliveflag = []
    neighbourhostnames = []
    neighbourports = []
    for parameters in range(4, len(s),8): 
        try:
            aliveflag.append(int(s[parameters]))
            neighbourhostnames.append(s[parameters+4])
            neighbourports.append(int(s[parameters+6]))
        except IndexError:
            print('end of list reached')
        except ValueError:
            pass
    table = {'Neighbours' : neighbourlist,
            'Neighbours Alive Flag': aliveflag,
            'Neighbours Hostname': neighbourhostnames,
            'Neighbours Port': neighbourports}
    alivelist = set(table['Neighbours'])
    nlist = list(alivelist)
    for i in range(len(nlist)):
        nswtichtime.append(time.time())

    bit = 1 - bit
    lockalive = Lock()
    lockdead = Lock()
    locktime = Lock()
    receive =  Thread(target=receivehandler, args= (skey,))
    sender = Thread(target=sendhandler ,args= (skey, ID, nID))

    
    receive.start()
    sender.start()

