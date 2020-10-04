import socket
import sys
import os 
import json 
from pprint import pprint as pp
import itertools

graphtable = {"data":[]}
routegraphtable = {"data":[]}
masteredge = {"data":[]}


def fil_masteredge(**kwargs):
    user = {}
    user["pair1"]=kwargs["pair1"]
    user["pair2"]=kwargs["pair2"]
    user["BW"]=kwargs["BW"]
    user["Delay"]=kwargs["Delay"]
    user['Path'] = kwargs["Path"]
    masteredge["data"].append(user)

def fil_graphtable(**kwargs):
    user = {}
    user["pair1"]=kwargs["pair1"]
    user["pair2"]=kwargs["pair2"]
    user["BW"]=kwargs["BW"]
    user["Delay"]=kwargs["Delay"]
    user['Path'] = kwargs["Path"]
    graphtable["data"].append(user)

def fil_routegraphtable(**kwargs):
    user = {}
    user["pair1"]=kwargs["pair1"]
    user["pair2"]=kwargs["pair2"]
    user["BW"]=kwargs["BW"]
    user["Delay"]=kwargs["Delay"]
    user['Path'] = kwargs["Path"]
    routegraphtable["data"].append(user)

def graphoutline(registercounter,routinglength):
    pairs = []
    for subset in itertools.combinations(registercounter,2):
        pairs.append(subset)
    for elements in pairs: 
        fil_graphtable(pair1 = elements[0],pair2 =elements[1], BW=None, Delay=None, Path = None)
        for i in range(routinglength): 
            if (graphtable['data'][-1]['pair1'] == int(routegraphtable['data'][i]["pair1"])) and (graphtable['data'][-1]['pair2'] == int(routegraphtable['data'][i]["pair2"])):
                graphtable['data'][-1] = routegraphtable['data'][i]


def routegraphmaker(routing,registercounter,routinglength,badconnectionlist):
    pairs = []
    edges = []
    for subset in itertools.combinations(registercounter,2):
        pairs.append(subset)
    for elements in pairs: 
        for i in range(routinglength):            
            if (elements[0] == int(routing['data'][i]['pair1'])) and (elements[1] == int(routing['data'][i]['pair2'])):
                if badconnectionlist == []:
                    BW = int(routing['data'][i]['BW'])
                    pair1= int(routing['data'][i]["pair1"])
                    pair2= int(routing['data'][i]["pair2"])
                    Delay= int(routing['data'][i]["Delay"])
                    tempedge = (elements[0],elements[1], BW,Delay, []) 
                    edges.append(tempedge)
                    fil_masteredge(pair1 = tempedge[0], pair2 =tempedge[1], BW=tempedge[2], Delay=tempedge[3] , Path = tempedge[4]) 
                    Path = None 
                    fil_routegraphtable(pair1 = pair1,pair2 =pair2, BW=BW, Delay=Delay , Path = Path)
                    
                elif (elements[0], elements[1]) in badconnectionlist:
                    pass
                else: 
                    BW = int(routing['data'][i]['BW'])
                    pair1= int(routing['data'][i]["pair1"])
                    pair2= int(routing['data'][i]["pair2"])
                    Delay= int(routing['data'][i]["Delay"])
                    tempedge = (elements[0],elements[1], BW,Delay, []) 
                    edges.append(tempedge)
                    fil_masteredge(pair1 = tempedge[0], pair2 =tempedge[1], BW=tempedge[2], Delay=tempedge[3] , Path = tempedge[4]) 
                    Path = None 
                    fil_routegraphtable(pair1 = pair1,pair2 =pair2, BW=BW, Delay=Delay , Path = Path)
    return edges, pairs  

def graphalgo(edges,pairs):
    edgestemp =[]
    for i in range(len(edges)):
        source1, des1, BW1,Delay1,Path1 =  edges[i]
        temppair = (source1, des1)
        for k in pairs:
            if temppair == k:
                pairs.remove(temppair)
        if len(pairs) == 0:
            return edges,pairs
        for j in range(len(edges)):
            source2, des2, BW2, Delay2,Path2 =  edges[j]
            if (source2 == des1 or source1 == des2):
                Path = Path1 + Path2
                Path.append(source2)
                newedge = (source1, des2, min(BW1,BW2), Delay1+Delay2,Path)
                if newedge[0] == newedge[1]:
                    pass
                else:
                    fil_masteredge(pair1 = newedge[0],pair2 =newedge[1], BW=newedge[2], Delay=newedge[3] , Path = newedge[4])      
                    edgestemp.append(newedge) 
            elif (source1 == source2):
                Path = Path1 + Path2
                Path.append(source2)
                newedge = (min(des1,des2),max(des1, des2), min(BW1,BW2), Delay1+Delay2,Path)
                if newedge[0] == newedge[1]:
                    pass
                else:
                    fil_masteredge(pair1 = newedge[0],pair2 =newedge[1], BW=newedge[2], Delay=newedge[3] , Path = newedge[4]) 
                    edgestemp.append(newedge)
            elif (des1 == des2): 
                Path = Path1 + Path2
                Path.append(des2)
                newedge = (min(source1,source2),max(source1,source2), min(BW1,BW2), Delay1+Delay2,Path)
                if newedge[0] == newedge[1]:
                    pass
                else:
                    fil_masteredge(pair1 = newedge[0],pair2 =newedge[1], BW=newedge[2], Delay=newedge[3] , Path = newedge[4]) 
                    edgestemp.append(newedge)
    edges = edges + edgestemp
    edges,pairs = graphalgo(edges,pairs)
    return edges,pairs

def listsplit(i,j,edges, rtable):
    sublist = []
    for elements in edges:
        if (i == int(elements[0])) and (j == int(elements[1])):
            sublist.append(elements)
    sortedsublist = sorted(sublist, key = lambda x:len(x[4]))
    maxsublist = max(sortedsublist, key = lambda x:x[2])
    rtable.append(maxsublist)

def widest_path(routing,registercounter,badconnectionlist):
    rtable = []
    routinglength = len(routing['data']) 
    edges,pairs = routegraphmaker(routing, registercounter,routinglength,badconnectionlist)
    graphoutline(registercounter,routinglength)
    edges,pairs = graphalgo(edges,pairs)
    edges.sort()
    del pairs
    pairs = []
    for subset in itertools.combinations(registercounter,2):
        pairs.append(subset)

    for i in range(len(pairs)):
        listsplit(pairs[i][0],pairs[i][1],edges,rtable)
    return rtable
    del edges, pairs 
    graphtable = {"data":[]}
    routegraphtable = {"data":[]}
    masteredge = {"data":[]}
