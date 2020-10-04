import Algo as A


def fil_temprouting2(line1, temprouting2):
    user = {}
    user["pair1"]=line1["pair1"]
    user["pair2"]=line1["pair2"]
    user["BW"]=line1["BW"]
    user["Delay"]=line1["Delay"]
    temprouting2["data"].append(user)

def checkdeadswitch(first_dict, second_dict): 
    diff = set(first_dict.keys()) - set(second_dict.keys())
    return diff


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

def modifyroutingrev(temprouting, routing, revswitch):
    rtable = []
    temprouting2 = {"data":[]}
    if len(revswitch)> 0:
        for element in revswitch:
            for i in range(len(routing['data'])):
                if int(routing["data"][i]["pair1"]) == int(element):
                    fil_temprouting2(routing["data"][i],temprouting2)
                if int(routing["data"][i]["pair2"]) == int(element):
                    fil_temprouting2(routing["data"][i],temprouting2)
                else: 
                    pass 

        for element in temprouting['data']:
            if element not in temprouting2['data']:
                fil_temprouting2(element,temprouting2)
        temprouting = temprouting2
        currentlist = getcurrentlist(temprouting)
        rtable = []
        rtable = A.widest_path(temprouting,sorted(currentlist),[])
    return temprouting, rtable

def modifyroutingdead(temprouting, deadswitch):
    rtable = []
    temprouting2 = {"data":[]}
    if len(deadswitch)>= 0:
        for index in temprouting['data']:
            if int(index["pair1"]) in deadswitch or int(index["pair2"]) in deadswitch:                
                pass
            else:
                fil_temprouting2(index,temprouting2)
        temprouting = temprouting2
        currentlist = getcurrentlist(temprouting)
        
        rtable = []
        rtable = A.widest_path(temprouting,sorted(currentlist),[])
    return temprouting, rtable

def modifyroutingdeadlink(temprouting, Deadlinks,badconnectionlist):
    rtable = []
    temprouting2 = {"data":[]}
    if len(Deadlinks)> 0:
        tracker =0
        for element in Deadlinks:
            if element[1] == []:
                tracker = tracker+1
        if tracker == len(Deadlinks):
            pass
        else: 
            for element in Deadlinks:
                for element2 in element[1]:
                    badconnectionlist.append((element[0],element2))
            for deadlink in badconnectionlist:
                for index in temprouting['data']:
                    if int(index["pair1"]) == int(deadlink[0]) and int(index["pair2"]) == int(deadlink[1]):                
                        pass
                    elif int(index["pair1"]) == int(deadlink[1]) and int(index["pair2"]) == int(deadlink[0]): 
                        pass
                    else:
                        fil_temprouting2(index,temprouting2)
                temprouting = temprouting2
                temprouting2 = {"data":[]}
            currentlist = getcurrentlist(temprouting)
            if len(badconnectionlist)==0:
                badconnectionlist = []
            rtable = A.widest_path(temprouting,sorted(currentlist),badconnectionlist)
    return temprouting, rtable, badconnectionlist


def modifyroutingrevlink(temprouting, routing, Revlinks,badconnectionlist):
    rtable = []
    temprouting2 = {"data":[]}
    if len(Revlinks) > 0 :
        tracker =0
        for element in Revlinks:
            if element[1] == []:
                tracker = tracker+1
        if tracker == len(Revlinks):
            pass
        else: 
            newconnectionlist =[]
            for element in Revlinks:
                for element2 in element[1]:
                    newconnectionlist.append((element[0],element2))

            for newlink in newconnectionlist:
                for index in routing['data']:
                    if int(index["pair1"]) == int(newlink[0]) and int(index["pair2"]) == int(newlink[1]):
                        fil_temprouting2(index,temprouting2)
                    elif int(index["pair1"]) == int(newlink[1]) and int(index["pair2"]) == int(newlink[0]):
                        fil_temprouting2(index,temprouting2)
                    else: 
                        print(newlink)
                        pass

            for element in temprouting2['data']:
                if element not in temprouting['data']:
                    fil_temprouting2(element,temprouting)
            currentlist = getcurrentlist(temprouting)
            for element in newconnectionlist:                
                    badconnectionlist.remove(element)
            if len(badconnectionlist) == 0:
                badconnectionlist = []

            rtable = []
            rtable = A.widest_path(temprouting,sorted(currentlist),badconnectionlist)


    return temprouting, rtable,badconnectionlist



def checkdeadlink(first, second):

    sharedKeys = set(first.keys()).intersection(second.keys())
    deadlist = []
    for key in sharedKeys:

        if first[key] != second[key]:

            deadlist.append((key, list(first[key].difference(second[key]))))

    return deadlist

def checkrevlink(first, second):
    sharedKeys = set(first.keys()).intersection(second.keys())
    revlist = []
    for key in sharedKeys:
        if first[key] != second[key]:
            revlist.append((key, list(second[key].difference(first[key]))))
    return revlist
