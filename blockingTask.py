import math
import numpy as np
import random as rand
import copy
import database_connect_Arma
import database_connect_ArmaRuns
import FileIO_Arma
import time
from datetime import datetime
import random
import CanyonRun






def initSoldierPos():
    soldierStats = {}
    numOfOpFor = 0
    while True:
        database_connect_Arma.Broadcast("red")
        time.sleep(4)
        numOfOpFor = database_connect_Arma.numOfAlive_v2()
        #print(numOfOpFor)
        if(numOfOpFor !=0):
            break     
    soldiers = database_connect_Arma.getAllOpForceUnitsASC(numOfOpFor)
    #print(soldiers)
    for soldier in soldiers:
        soldierStats[soldier[0]]= [soldier[1],soldier[2], soldier[3]]
    return soldierStats

def initialMove():
    pathPlanner = CanyonRun.Astar()
    path2 = 'C:/arma3/terrain/'
    goalLoc = pathPlanner.getGoalLocation()
    initUnits = initSoldierPos()
    #print(initUnits)
    goalLocationName = list(goalLoc.keys())
    #print(goalLocationName)
    traversedWaypoint = {}
    for i in range(0,30): 
        if i%10 == 0:
            print(i)         
        goalLocationValue = random.randint(0,len(goalLocationName)-1)
        locTuple = goalLoc[goalLocationName[goalLocationValue]]
        traveresedRoute = pathPlanner.getRandomPath(locTuple)
        if len(traveresedRoute) > 0:
            for t in range(1, len(traveresedRoute)-10):
                waypoint = traveresedRoute[t]
                if waypoint in traversedWaypoint:
                    traversedWaypoint[waypoint]+=1
                else:
                    traversedWaypoint[waypoint]=1
    
    mostTraveresedWaypoint = ()
    traversalCounter = 0
    for key,value in traversedWaypoint.items():
        if value > traversalCounter:
            traversalCounter = value
            mostTraveresedWaypoint = key
        
    
       
    ugv1RouteLength =[1000,1000, 1000]
    ugv2RouteLength =[1000,1000, 1000]
    ugv3RouteLength =[1000,1000, 1000]
    
    ugvList = list(initUnits.keys())
    for i in range(0,3):
        initalX = initUnits[ugvList[i]][1]
        initalY = initUnits[ugvList[i]][2]
        
        loc1 = goalLoc[goalLocationName[0]]
        loc2 = goalLoc[goalLocationName[1]]
        #print(loc1)
        #print(initUnits[ugvList[i]])
        route1 = pathPlanner.aStarPerform(int(initalX), int(initalY), int(loc1[0]),int(loc1[1]))
        route2 = pathPlanner.aStarPerform(int(initalX), int(initalY), int(loc2[0]),int(loc2[1]))
        route3 = pathPlanner.aStarPerform(int(initalX), int(initalY), int(mostTraveresedWaypoint[0]),int(mostTraveresedWaypoint[1]))
        if i == 0:
            if None != route1:
                ugv1RouteLength[0] = len(route1)
            if None != route2:
                ugv1RouteLength[1] = len(route2)
            if None != route3:
                ugv1RouteLength[2] = len(route3)
        elif i == 1:
            if None != route1:
                ugv2RouteLength[0] = len(route1)
            if None != route2:
                ugv2RouteLength[1] = len(route2)
            if None != route3:
                ugv2RouteLength[2] = len(route3)
        else:
            if None != route1:
                ugv3RouteLength[0] = len(route1)
            if None != route2:
                ugv3RouteLength[1] = len(route2)
            if None != route3:
                ugv3RouteLength[2] = len(route3)
                
    assignments = [[0,1,2],[2,0,1],[1,2,0],[0,2,1],[1,0,2]]
    lowestValue = 4000
    bestAssignment = 0
    for t in range(0, len(assignments)):
        goalAssigned = assignments[t]
        tempVal = ugv1RouteLength[goalAssigned[0]]+ugv2RouteLength[goalAssigned[1]]+ugv3RouteLength[goalAssigned[2]]
        if tempVal< lowestValue:
            lowestValue = tempVal
            bestAssignment  = t
            
    endLocAssignment = ()
    if assignments[bestAssignment][0]  < 2:
        endLocAssignment = goalLoc[goalLocationName[assignments[bestAssignment][0]]]
    else:
        endLocAssignment = mostTraveresedWaypoint
    database_connect_Arma.moveUnit( endLocAssignment[0],endLocAssignment[1], 2, ugvList[0])
    
    if assignments[bestAssignment][1]  < 2:
        endLocAssignment = goalLoc[goalLocationName[assignments[bestAssignment][1]]]
    else:
        endLocAssignment = mostTraveresedWaypoint
        
    database_connect_Arma.moveUnit( endLocAssignment[0],endLocAssignment[1], 2, ugvList[1])
    
    
    if assignments[bestAssignment][2]  < 2:
        endLocAssignment = goalLoc[goalLocationName[assignments[bestAssignment][2]]]
    else:
        endLocAssignment = mostTraveresedWaypoint
    database_connect_Arma.moveUnit( endLocAssignment[0],endLocAssignment[1], 2, ugvList[2])
    print("finished")

    '''
    database_connect_Arma.moveUnit( 0,0, 2, "rugv1")
    database_connect_Arma.moveUnit( 0,0, 2, "rugv2")
    database_connect_Arma.moveUnit( 0,0, 2, "rugv3")
    '''
  
    
