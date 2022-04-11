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

startTime = 0
elapsedTime = 0
blueRemaining = 0
opforRemaining = 0
runNumber = 0
coverRadius = 10
coverIncrement = 1
concealmentRadius = 10
concealmentIncrement = 1
buddyTeamLocation = {} #dictionary buddy team and their location
buddyTeamPreviousLocation ={} # list of all previous locations a buddy team has been
previouslyObservedSite ={} #previously viewed sites
minX = 1800
minY = 10100
maxX = 2200
maxY = 10900
#soldierStats = {} #name = health,px,py
coverDict = {}
concealmentDict = {}
visDict = {}
terrainDict = {}
blue_sent_x = 0
blue_sent_y = 0
XgridLocation =[]
YgridLcoatoin =[]
Cover ={} # value of cover at each location
Concealment ={}# value of concealment at each location

weight_percentBuddyTeamVisibleRange = 0
weight_minCover = 0
weight_minConcealment = 0
weight_averageCover = 0
weight_averageConcealment = 0 
weight_averageVisibleArea = 0
weight_percentBuddyTeamNotMoving = 0 
weight_largestNumberBuddyTeam30Meters = 0 
weight_areaLeftUnsearched = 0
weight_distanceMoved = 0

#percentBuddyTeamVisibleRange, #minCover, #minConcealment, #averageCover, 
#averageConcealment, #averageVisibleArea, #percentBuddyTeamNotMoving, 
#largestNumberBuddyTeam30Meters, #areaLeftUnsearched, #Distance
#weights =[0.7, 0.5, 0.7, 0.4, 0.8, 0.4, 0.1, 0.7, 0.7, 0.7]
#weights =[]
# Cautious 
#weights = [0.97935904, 0.16486296, 0.97977294, 0.60549313, 0.12059349,
# 0.59641712, 0.39970657, 0.54875692, 0.88235823, 0.92450549] 
# Lethal
weights = [0.10773285, 0.59071208, 0.80467096, 0.76942688, 0.99905881, 0.00432602, 0.63006018, 0.08615641, 0.60961342, 0.0332233 ]


#deprecated moved to weightGenerator
def randomizeWeights():
    global weights
    global weight_percentBuddyTeamVisibleRange
    global weight_minCover
    global weight_minConcealment
    global weight_averageCover
    global weight_averageConcealment
    global weight_averageVisibleArea 
    global weight_percentBuddyTeamNotMoving 
    global weight_largestNumberBuddyTeam30Meters 
    global weight_areaLeftUnsearched
    global weight_distanceMoved
    weight_percentBuddyTeamVisibleRange = random.random()
    weight_minCover = random.random()
    weight_minConcealment = random.random()
    weight_averageCover = random.random()
    weight_averageConcealment = random.random()
    weight_averageVisibleArea = random.random()
    weight_percentBuddyTeamNotMoving = random.random()
    weight_largestNumberBuddyTeam30Meters = random.random()
    weight_areaLeftUnsearched = random.random()
    weight_distanceMoved = random.random()
    
    weights = [ weight_percentBuddyTeamVisibleRange,
    weight_minCover, 
    weight_minConcealment, 
    weight_averageCover,
    weight_averageConcealment, 
    weight_averageVisibleArea, 
    weight_percentBuddyTeamNotMoving, 
    weight_largestNumberBuddyTeam30Meters, 
    weight_areaLeftUnsearched,
    weight_distanceMoved ]


def initSoldierPos():
    soldierStats = {}
    numOfOpFor = 0
    while True:
        database_connect_Arma.Broadcast("red")
        time.sleep(4)
        numOfOpFor = database_connect_Arma.numOfAlive_v2()
        print(numOfOpFor)
        if(numOfOpFor !=0):
            break     
    soldiers = database_connect_Arma.getAllOpForceUnitsASC(numOfOpFor)
    #print(soldiers)
    for soldier in soldiers:
        soldierStats[soldier[0]]= [soldier[1],soldier[2], soldier[3]]
    return soldierStats

def currentSoldierPos():
    soldierStats = {}
    numOfOpFor = 0
    while True:
        database_connect_Arma.Broadcast("red")
        numOfOpFor = database_connect_Arma.numOfAlive_v2()
        print(numOfOpFor)
        if(numOfOpFor !=0):
            break     
    soldiers = database_connect_Arma.getAllOpForceUnits(numOfOpFor)
    #print(soldiers)
    for soldier in soldiers:
        soldierStats[soldier[0]]= [soldier[1],soldier[2], soldier[3]]
    return soldierStats

def getOpForceAvgLoc():
    numOfOpFor = 0
    avgX = 0
    avgY = 0
    while True:
        database_connect_Arma.Broadcast("red")
        time.sleep(4)
        numOfOpFor = database_connect_Arma.numOfAlive_v2()
        print(numOfOpFor)
        if(numOfOpFor !=0):
            break     
    soldiers = database_connect_Arma.getAllOpForceUnits(numOfOpFor)
    #print(soldiers)
    for soldier in soldiers:
        avgX += soldier[2]
        avgY += soldier[3]
    
    return avgX/numOfOpFor, avgY/numOfOpFor

def currentSoldierPosBlu():
    soldierStats = {}
    numOfOpFor = 0
    while True:
        database_connect_Arma.Broadcast("blue")
        time.sleep(4)
        numOfBluFor = database_connect_Arma.numOfAlive_v2Blue()
        if(numOfBluFor !=0):
            break     
    soldiers = database_connect_Arma.getAllBlueForceUnits(numOfBluFor)
    #print(soldiers)
    for soldier in soldiers:
        soldierStats[soldier[0]]= [soldier[1],soldier[2], soldier[3]]
    return soldierStats


def updateSoldierPos():
    updatedSoldierStats = {}
    timestamp = database_connect_Arma.getTimestampOpfor()
    soldiers = database_connect_Arma.getOpForceUnitsByTimestamp(timestamp)
    for soldier in soldiers:
        updatedSoldierStats[soldier[0]]= [soldier[1],soldier[2], soldier[3]]
    return updatedSoldierStats
            
        
        


#updates buddy team location and add to previous locations
def setBuddyTeams(Buddy, x, y): 
    global buddyTeamLocation # gets currnet buddy team location
    if Buddy in buddyTeamPreviousLocation: # checks to see if buddy team already has a previous location set
        previousLocations = buddyTeamPreviousLocation[Buddy] # gets the list of previous location
        previousLocations.append([x,y])# should be center of grid square that we are located in
        buddyTeamPreviousLocation[Buddy] = previousLocations # adds back to previous lcoation
    else:
        buddyTeamPreviousLocation[Buddy] = [[x,y]]# should be center of grid square that we are located in
    buddyTeamLocation[Buddy] = [x,y]# should be center of grid square that we are located in
    
#Identify Line of site of terrain. Read this in from DB or File
# we will need to 


def closestGrid(xLoc,yLoc): #gives you the closests grid cell based on where you are currently located
    global previouslyObservedSite
    minDis = 100000
    closestX = xLoc
    closestY = yLoc
    for site in previouslyObservedSite:
        tempDistance = distanceBetweenPoints(site[0], site[1], xLoc, yLoc)
        if(tempDistance< minDis):
            minDis = tempDistance
            closestX = site[0] #finds the closets observed X
            closestY = site[1] # finds the closets observed Y
    return (closestX,closestY)


#gives the percentage of cover 
def percentageCover(radius, increment, x, y): #looks across your neighbors 
    global coverDict
    percentCover = 0
    totalCoverTested =0
    i=radius*-1
    while i <= radius:#x
        j = radius*-1
        while j <=radius:#y
            testX = int(x) +i # increment X location
            testY = int(y) + j # increment Y location
            #print("test location",testX, testY)
            if (testX,testY) in coverDict: #checks to see if x,y in cover
                #print("In Cover Dict", testX,testY)
                percentCover +=coverDict[(testX,testY)] #adds cover to percent cover
                totalCoverTested+=1.0
            j+=increment
        i+=increment
    #print("percentCover", percentCover)
    #print("totalCoverTested", totalCoverTested)
    if totalCoverTested == 0:
        return percentCover
    return(percentCover/totalCoverTested) # returns percent coverage 
            
#gives the percentage concealment 
def percentageConcealment(radius, increment, x, y):
    global concealmentDict
    percentConcealment = 0
    totalConcealmentTested =0
    i=radius*-1
    #print("i", i)
    #print("radius", radius)
    while i <= radius:#x
        j = radius*-1
        while j <=radius:#y
            testX = int(x) +i # increment X
            testY = int(y) + j # increment Y
            #print("test location",testX, testY)
            if (testX,testY) in concealmentDict: # checks to see if concealment location exist
                percentConcealment +=concealmentDict[(testX,testY)] #gets percent concealement 
                totalConcealmentTested+=1.0
                #print("In Concealment Dict", testX,testY)
            j+=increment
        i+=increment
    #print("percentConcealment", percentConcealment)
    #print("totalConcealmentTested", totalConcealmentTested)
    if totalConcealmentTested == 0:
        return percentConcealment
    else:
        return percentConcealment/totalConcealmentTested # returns the concealment 


##################
#Need to initalize the buddy team location from actual data
###########
#moves the units to new location based on movement criteria 

def distanceBetweenPoints(X1,Y1,X2,Y2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Y1- Y2, 2))
    return dis  

def moveRnSUnits(TSoldierLocation, TpreviouslyObsereved):
    global minX
    global minY
    global maxX
    global maxY
    global terrainDict
    global startTime
    random.seed()
    count = 0
    #printSoldier =[]
    averageDistanceIncreased = 0
    for TSoldier in TSoldierLocation:
        initPosSold = database_connect_Arma.getInitOpForceUnit(TSoldier)
        count+=1
        #print(initPosSold)
        initialX = initPosSold[2]
        #print(initialX)
        initialY = initPosSold[3] 
        loc = TSoldierLocation[TSoldier]
      
        
        initalDistance = math.sqrt(math.pow(loc[1]-initialX,2)+math.pow(loc[2]-initialY,2))
        newXMove = random.randint(-1,1)*20
        newYMove = random.randint(-1,0)*20
        gridLocation = closestGrid(newXMove, newYMove)
        newLOC = [loc[1]+newXMove,loc[2]+newYMove]
        newDistance = math.sqrt(math.pow(newLOC[0]-initialX,2)+math.pow(newLOC[1]-initialY,2))
        
        counter = 0
        #incrementer = 0;
        terrainGrid = closestGrid(newLOC[0] , newLOC[1])
        terrain = terrainDict[terrainGrid[0] , terrainGrid[1]]
        #print("Terrain Elevation", terrain)
        averageDistanceIncreased += newDistance/(initalDistance+1)
        while newLOC[0] < initialX or newLOC[1] > initialY or newLOC[0] >maxX or newLOC[1] < minY  or terrain[0] <= 0.7:
            endTime = time.time()
            elapsedTime = endTime - startTime
            if(elapsedTime > 2700):
                #resetMission()
                break
            #needs to include check to see if position is not in water
            if(counter >= 5):
                #print("new loc", newLOC[0] , newLOC[1])
                #incrementer += 20
                newXMove = random.randint(-1,1)*40
                newYMove = random.randint(-1,1)*40
            else:
                newXMove = random.randint(-1,1)*20
                newYMove = random.randint(-1,1)*20
            counter+=1
            gridLocation = closestGrid(newXMove, newYMove)
            #if(TSoldier in printSoldier):
                #print(printSoldier)
                #print("loc[1]", loc[1])
                #print("loc[1] + move", loc[1]+newXMove)
                #print("loc[2]", loc[2])
                #print("loc[2] + move", loc[2]+newXMove)
            newLOC = [loc[1]+newXMove,loc[2]+newYMove]
            terrainGrid = closestGrid(newLOC[0] , newLOC[1])
            terrain = terrainDict[terrainGrid[0] , terrainGrid[1]]
            #print("newX: ",newLOC[0], "initX: ", initialX, "newY: ", newLOC[1], "initY: ", initialY, "maxX: ", maxX, "maxY: ", maxY, "minY: ", minY, "newDistance", newDistance, "init distance",initalDistance)
            #print("In Loop")
            newDistance = math.sqrt(math.pow(newLOC[0]-initialX,2)+math.pow(newLOC[1]-initialY,2))
            averageDistanceIncreased += newDistance/(initalDistance+1)
            
                
        
        #print("newLoc, initialx, initialy",newLOC, initialX, initialY)      
        TpreviouslyObsereved[gridLocation[0], gridLocation[1]] = 1
        TSoldierLocation[TSoldier]=[loc[0], newLOC[0], newLOC[1]] #health, newX, newY
        #future work predict hp
    averageDistanceIncreased = averageDistanceIncreased/(len(TSoldierLocation)+1)
    return TSoldierLocation, averageDistanceIncreased



'''
def calculateVisuals(TSoldierLocation, TpreviouslyObservedSite):
    searchGrid = 25*len(TSoldierLocation)
    visibilitySearched = 0
    global visDict
    for soldier in TSoldierLocation:
        loc = TSoldierLocation[soldier]
        newLoc = closestGrid(loc[1],loc[2])
        visibilitySearched+=1
        TpreviouslyObservedSite[newLoc]=1
        for i in range (-40, 40, 20): 
            for j in range (-40, 40, 20):
                if( (newLoc[0],newLoc[1], newLoc[0] + i, newLoc[1] + j) in visDict and visDict[(newLoc[0],newLoc[1], newLoc[0] + i, newLoc[1] + j)] == 1):
                    visibilitySearched+=1
                    TpreviouslyObservedSite[(newLoc[0] + i, newLoc[1] + j)]=1
                    TpreviouslyObservedSite[(newLoc[0] - i, newLoc[1] + j)]=1
                    TpreviouslyObservedSite[(newLoc[0] + i, newLoc[1] - j)]=1
                    TpreviouslyObservedSite[(newLoc[0] - i, newLoc[1] - j)]=1
                elif( ( newLoc[0] + i, newLoc[1] + j,newLoc[0],newLoc[1]) in visDict and visDict[( newLoc[0] + i, newLoc[1] + j,newLoc[0],newLoc[1])] == 1):
                    visibilitySearched+=1
                    TpreviouslyObservedSite[(newLoc[0] + i, newLoc[1] + j)]=1
                    TpreviouslyObservedSite[(newLoc[0] - i, newLoc[1] + j)]=1
                    TpreviouslyObservedSite[(newLoc[0] + i, newLoc[1] - j)]=1
                    TpreviouslyObservedSite[(newLoc[0] - i, newLoc[1] - j)]=1
    
    if float(len(TpreviouslyObservedSite)) == 0:
        #print("Visuals: ", sum(TpreviouslyObservedSite.values()),(visibilitySearched/searchGrid))
        return sum(TpreviouslyObservedSite.values()),(visibilitySearched/searchGrid),TpreviouslyObservedSite
    elif searchGrid == 0:
        #print("Visuals: ", sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched))
        return sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched),TpreviouslyObservedSite
    elif float(len(TpreviouslyObservedSite)) == 0 and searchGrid == 0:
        #print("Visuals: ", sum(TpreviouslyObservedSite.values()),(visibilitySearched))
        return sum(TpreviouslyObservedSite.values()),(visibilitySearched),TpreviouslyObservedSite
    else:      
        #print("Visuals: ", sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched/searchGrid))         
        return sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched/searchGrid),TpreviouslyObservedSite

'''
    
def calculateVisuals(TSoldierLocation, TpreviouslyObservedSite):
    searchGrid = 25*len(TSoldierLocation)
    visibilitySearched = 0
    global visDict
    for soldier in TSoldierLocation:
        loc = TSoldierLocation[soldier]
        newLoc = closestGrid(loc[1],loc[2])
        visibilitySearched+=1
        TpreviouslyObservedSite[newLoc]=1
        for i in range (-40, 40, 20): 
            for j in range (-40, 40, 20):
                if( (newLoc[0],newLoc[1], newLoc[0] + i, newLoc[1] + j) in visDict and visDict[(newLoc[0],newLoc[1], newLoc[0] + i, newLoc[1] + j)] == 1):
                    visibilitySearched+=1
                    TpreviouslyObservedSite[(newLoc[0] + i, newLoc[1] + j)]=1
                elif( ( newLoc[0] + i, newLoc[1] + j,newLoc[0],newLoc[1]) in visDict and visDict[( newLoc[0] + i, newLoc[1] + j,newLoc[0],newLoc[1])] == 1):
                    visibilitySearched+=1
                    TpreviouslyObservedSite[(newLoc[0] + i, newLoc[1] + j)]=1
    
    if float(len(TpreviouslyObservedSite)) == 0:
        #print("Visuals: ", sum(TpreviouslyObservedSite.values()),(visibilitySearched/searchGrid))
        return sum(TpreviouslyObservedSite.values()),(visibilitySearched/searchGrid),TpreviouslyObservedSite
    elif searchGrid == 0:
        #print("Visuals: ", sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched))
        return sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched),TpreviouslyObservedSite
    elif float(len(TpreviouslyObservedSite)) == 0 and searchGrid == 0:
        #print("Visuals: ", sum(TpreviouslyObservedSite.values()),(visibilitySearched))
        return sum(TpreviouslyObservedSite.values()),(visibilitySearched),TpreviouslyObservedSite
    else:      
        #print("Visuals: ", sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched/searchGrid))         
        return sum(TpreviouslyObservedSite.values())/float(len(TpreviouslyObservedSite)),(visibilitySearched/searchGrid),TpreviouslyObservedSite



def isMissionEnd():
    #call broadcast command
    global minY
    global blueRemaining
    global opforRemaining
    global startTime
    global elapsedTime
    database_connect_Arma.Broadcast("blue")
    database_connect_Arma.Broadcast("red")
    time.sleep(3)
    aliveBlue = database_connect_Arma.numOfAlive_v2Blue()
    print(aliveBlue)
    aliveRed = database_connect_Arma.numOfAlive_v2()
    print(aliveRed)
    soldierStats = currentSoldierPos()
    endTime = time.time()
    elapsedTime = endTime - startTime
    if aliveBlue == 0 or aliveRed == 0 or elapsedTime > 2700:
        blueRemaining = aliveBlue
        opforRemaining = aliveRed
        resetMission()
        return True
    for key in soldierStats:
        soldier = soldierStats[key]
        if(abs(soldier[2] - minY) <= 20 ):
            resetMission()
            return True
    return False         
    

def resetMission():
    global startTime
    global elapsedTime
    global runNumber
    global blueRemaining
    global opforRemaining
    global blue_sent_x 
    global blue_sent_y
    global visDict
    global previouslyObservedSite
    global weights
    visDict, previouslyObservedSite = FileIO_Arma.getVisFromFile("DB\AllblueforVisibility")
    print("resetting")
    time.sleep(30)
    database_connect_Arma.Broadcast("blue")
    time.sleep(4)
    database_connect_Arma.Broadcast("red")
    time.sleep(4)
    numOfOpFor = database_connect_Arma.getNumberofOpForceUnits()
    numOfBlueFor = database_connect_Arma.getNumberofBlueForceUnits()
    print(numOfOpFor)
    print(numOfBlueFor)
    aliveBlue = database_connect_Arma.numOfAlive_v2Blue()
    print(aliveBlue)
    aliveRed = database_connect_Arma.numOfAlive_v2()
    print(aliveRed)
    allblueForSoldiers = database_connect_Arma.getAllBlueForceUnitsASC(numOfBlueFor)
    print(allblueForSoldiers)
    allopForSoldiers = database_connect_Arma.getAllOpForceUnitsASC(numOfOpFor)
    #reCreatedBlue = 0 
    #reCreatedRed = 0 
    #print("Removing remaining units")
    database_connect_ArmaRuns.armaRunData(runNumber, elapsedTime, opforRemaining, blueRemaining, blue_sent_x, blue_sent_y,
weights[0], weights[1], weights[2], weights[3], weights[4], weights[5], weights[6], weights[7], weights[8], weights[9]) 
    
    #numOfOpFor-=aliveRed-1
    if(aliveBlue >0):
        counter = 0
        print("Removing blue units remaining")
        while True:
            for index in range(0, aliveBlue):
                database_connect_Arma.resetHP(index, "blufor")
                print(allblueForSoldiers[index][0], index)
                counter+=1
                time.sleep(2)
                #reCreatedBlue+=1
                #px, py, pz = database_connect_Arma.initPosBlue(allblueForSoldiers[index][0])           
                #print(allblueForSoldiers[index][0])
                #database_connect_Arma.createUnit(allblueForSoldiers[index][6],
                #     px, py, pz, "west")
                #time.sleep(2)
            database_connect_Arma.Broadcast("blue")
            time.sleep(4)
            aliveBlue = database_connect_Arma.numOfAlive_v2Blue()
            print(aliveBlue)
            if(aliveBlue <= 0):
                break
        print("Remaining units removed: ", counter)
        
    if(aliveRed >0): 
        counter = 0
        print("Removing red units remaining")
        while True:
            for index in range(0, aliveRed):
                database_connect_Arma.resetHP(index, "opfor")
                print(allopForSoldiers[index][0], index)
                counter+=1
                time.sleep(2)
                #reCreatedRed+=1        
                #px, py, pz = database_connect_Arma.initPosBlue(allopForSoldiers[index][0])           
                #print(allopForSoldiers[index][0])
                #database_connect_Arma.createUnit(allopForSoldiers[index][6],
                #     px, py, pz, "east")
                #time.sleep(2)
            database_connect_Arma.Broadcast("red")
            time.sleep(4)
            aliveRed = database_connect_Arma.numOfAlive_v2()
            print(aliveRed)
            if(aliveRed <= 0):
                break
                
        print("Remaining units removed: ", counter)
    #numOfBlueFor-=aliveBlue-1 
    time.sleep(40)
    print("Creating new units")
    print("Total Blue Units", numOfBlueFor)
    for index in range(0,numOfBlueFor):
        #fIndex = index + reCreatedBlue
        #print(fIndex)
        px, py, pz = database_connect_Arma.initPosBlue(allblueForSoldiers[index][0])
        database_connect_Arma.createUnit(allblueForSoldiers[index][6],
             px, py, pz, "west") 
    print("Total Red Units", numOfOpFor)
    for index in range(0,numOfOpFor):
        #fIndex = index + reCreatedRed
        #print(fIndex)
        px, py, pz = database_connect_Arma.initPosRed(allopForSoldiers[index][0]) 
        database_connect_Arma.createUnit(allopForSoldiers[index][6],
             px, py, pz, "east")  
    runNumber = database_connect_ArmaRuns.getNumberofRuns()  
    runNumber+=1  
    print(elapsedTime)
 
    #randomizeWeights()   
    #weights = database_connect_ArmaRuns.getWeights()
    database_connect_Arma.resetDB()
    database_connect_Arma.Broadcast("red")
    time.sleep(4)
    aliveRed = database_connect_Arma.numOfAlive_v2()
    print(aliveRed)
    randomBlueMove(1860, 2080, 10100, 10400)
    time.sleep(5)
    startTime = time.time()
    print("Done")    
    

def randomBlueMove(Xmin, Xmax, Ymin, Ymax):
    random.seed()
    global blue_sent_x 
    global blue_sent_y
    newXMove = random.randint(Xmin,Xmax)
    newYMove = random.randint(Ymin,Ymax)
    blue_sent_x = newXMove
    blue_sent_y = newYMove
    soldiers = currentSoldierPosBlu()
    for key in soldiers:                      
        database_connect_Arma.moveUnit(newXMove, newYMove, 2, key)


#efficent method for identifying tree cover (average of sorrounding tiles)
#efficent method for identifying concealment (average of sorrounding tiles)
#iterate through tree
    #select next location for Buddy team (team should not move into a cell they went to)
    #Team cannot move backwards
    #calculate new reward
    #test if line is bad
    
# def generateDangerArea(Xmin, Xmax, Ymin, Ymax):
    # random.seed()
    # dangerArea_X = random.randint(Xmin,Xmax)
    # dangerArea_Y = random.randint(Ymin,Ymax)
    
    # return dangerArea_X,dangerArea_Y

def isAtDangerArea(dangerArea_X,dangerArea_Y, assaultedArea):
    soldierStats = currentSoldierPos()

    for soldier in soldierStats:
        soldierLoc = soldierStats[soldier]
        if (distanceBetweenPoints(dangerArea_X,dangerArea_Y,soldierLoc[1], soldierLoc[2]) <= 20 and assaultedArea == False):
        #trigger assault
            assaultedArea = assaultDangerAreaSmartL(dangerArea_X,dangerArea_Y)
    return assaultedArea     

def assaultDangerAreaSmartL(dangerArea_X,dangerArea_Y):
    print("beginning assault of danger area", dangerArea_X,dangerArea_Y)
    soldiers = currentSoldierPos()
    topAssault_x, topAssault_y = dangerArea_X, (dangerArea_Y + 20)
    eastAssault_x, eastAssault_y = (dangerArea_X + 20), dangerArea_Y 
    westAssault_x, westAssault_y = (dangerArea_X - 20), dangerArea_Y
    soldiersByEast = {}
    soldiersByWest = {}
    for key in soldiers:
        soldierLoc = soldiers[key]
        if(distanceBetweenPoints(eastAssault_x, eastAssault_y,soldierLoc[1], soldierLoc[2]) < distanceBetweenPoints(westAssault_x, westAssault_y,soldierLoc[1], soldierLoc[2])):
            soldiersByEast[key] = soldierLoc
        else:
            soldiersByWest[key] = soldierLoc
    if(len(soldiersByEast) > len(soldiersByWest)):
        print("East assault")
        counter = 0
        for key in soldiers:
            if counter == 0:              
                database_connect_Arma.moveUnit(topAssault_x, topAssault_y , 2, key)
            elif counter < 4 and counter > 0:              
                database_connect_Arma.moveUnit( topAssault_x - (5*counter), topAssault_y , 2, key)
            elif counter < 6 and counter >= 4:              
                database_connect_Arma.moveUnit(topAssault_x + (5*(counter-3)), topAssault_y , 2, key)
            elif counter < 8 and counter >=6 :
                database_connect_Arma.moveUnit(eastAssault_x, eastAssault_y + (5*(counter-5))  , 2, key)
            elif counter == 8: 
                database_connect_Arma.moveUnit(eastAssault_x, eastAssault_y, 2, key)
            else:
                database_connect_Arma.moveUnit( eastAssault_x, eastAssault_y - (5*(counter-8))  , 2, key)
            counter+=1
    else:
        print("West assault")
        counter = 0
        for key in soldiers:
            if counter == 0:              
                database_connect_Arma.moveUnit(topAssault_x, topAssault_y , 2, key)
            elif counter < 4 and counter > 0:              
                database_connect_Arma.moveUnit(topAssault_x - (5*counter), topAssault_y , 2, key)
            elif counter < 6 and counter >= 4:              
                database_connect_Arma.moveUnit(topAssault_x + (5*(counter-3)), topAssault_y , 2, key)
            elif counter < 8 and counter >=6 :
                database_connect_Arma.moveUnit(westAssault_x, westAssault_y + (5*(counter-5))  , 2, key)
            elif counter == 8: 
                database_connect_Arma.moveUnit( westAssault_x, westAssault_y, 2, key)
            else:
                database_connect_Arma.moveUnit(westAssault_x, westAssault_y - (5*(counter-8))  , 2, key)
            counter+=1
    time.sleep(30)
    counter = 0
    print("Moving in")
    for key in soldiers:
        if counter == 0:              
            database_connect_Arma.moveUnit( dangerArea_X, dangerArea_Y , 2, key)
        elif counter < 4 and counter > 0:              
            database_connect_Arma.moveUnit(dangerArea_X + (5*counter), dangerArea_Y , 2, key)
        elif counter < 6 and counter >= 4:              
            database_connect_Arma.moveUnit(  dangerArea_X - (5*(counter-3)), dangerArea_Y , 2, key)
        elif counter < 8 and counter >=6 :
            database_connect_Arma.moveUnit( dangerArea_X, dangerArea_Y + (5*(counter-5))  , 2, key)
        elif counter == 8: 
            database_connect_Arma.moveUnit( dangerArea_X, dangerArea_Y, 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X, dangerArea_Y - (5*(counter-8))  , 2, key)
        counter+=1
    return True

def assaultDangerArea(dangerArea_X,dangerArea_Y):
    print("beginning assault of danger area", dangerArea_X,dangerArea_Y)
    soldiers = currentSoldierPos()
    counter = 0
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 40 , 2, key)
        counter+=1
    print("opfor in position")
    time.sleep(30)
    counter = 0
    print("Moving in to clear 1")
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 20 , 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 2")
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 10 , 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 3")
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y, 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 4")
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y - 10, 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 5")
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y - 20, 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 6")
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y - 30, 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 7")
    for key in soldiers:
        soldierMove = soldiers[key]              
        database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y - 40, 2, key)
        counter+=1
    time.sleep(20)
    #print string to check if enemy detected
    return True
    
def assaultLShapedDangerArea(dangerArea_X,dangerArea_Y):
    print("beginning assault of danger area", dangerArea_X,dangerArea_Y)
    soldiers = currentSoldierPos()
    counter = 0
    for key in soldiers:
        if counter < 6:              
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 50 , 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X + 60, dangerArea_Y - (20 + counter)  , 2, key)
        counter+=1
    print("opfor in position")
    time.sleep(50)
    counter = 0
    print("Moving in to clear 1")
    for key in soldiers:    
        if counter < 6:         
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 40 , 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X + 50, dangerArea_Y - (20 + counter)  , 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 2")
    for key in soldiers:      
        if counter < 6:       
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 30 , 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X + 40, dangerArea_Y - (20 + counter), 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 3")
    for key in soldiers:
        if counter < 6:        
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 20, 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X + 30, dangerArea_Y - (20 + counter)  , 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 4")
    for key in soldiers:     
        if counter < 6:        
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y + 10, 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X + 20, dangerArea_Y - (20 + counter) , 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 5")
    for key in soldiers:
        if counter < 6:             
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y , 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X + 10, dangerArea_Y - (20 + counter)  , 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 6")
    for key in soldiers:            
        if counter < 6:  
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y - 10, 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X, dangerArea_Y - (20 + counter)  , 2, key)
        counter+=1
    time.sleep(20)
    counter = 0
    print("Moving in to clear 7")
    for key in soldiers:  
        if counter < 6:           
            database_connect_Arma.moveUnit( dangerArea_X + counter, dangerArea_Y - 10, 2, key)
        else:
            database_connect_Arma.moveUnit( dangerArea_X - 10, dangerArea_Y - (20 + counter)  , 2, key)
        counter+=1
    time.sleep(20)
    #print string to check if enemy detected
    return True
    
    
    
def checkDetection():
    soldierStats = currentSoldierPos()
    for key in soldierStats:
        targetFound = database_connect_Arma.getRecentDetection(key)
        if targetFound != -1:
            print("Enemy Found")
            assaultDangerAreaSmartL(targetFound[0],targetFound[1])
            exit(0)
    
def recon():
    #FileIO_Arma.addToVisFile('DB\AllblueforVisibility', 1800, 2200, 10100, 10900)
    #print("Done")
    global startTime
    global coverDict
    global concealmentDict
    coverDict = FileIO_Arma.getCoverOrConcealmentFromFile('terrain_Cover')
    concealmentDict = FileIO_Arma. getCoverOrConcealmentFromFile('terrain_Concealment')
    global visDict
    global previouslyObservedSite
    visDict, previouslyObservedSite = FileIO_Arma.getVisFromFile("DB\AllblueforVisibility")
    global terrainDict
    terrainDict = FileIO_Arma.getTerrainFromFile("terrain")
    #print(percentageConcealment(3,0.5,4,5))

    global concealmentRadius
    global coverRadius
    global coverIncrement
    global concealmentIncrement
    global weights
    global dangerArea  
    dangerArea = {}
    global assaultedArea
    assaultedArea = []
    dangerArea, assaultedArea = FileIO_Arma.getDangerAreaFromFile("Prediction-100")  

    soldierStats = initSoldierPos()

    #weights = database_connect_ArmaRuns.getWeights()
    #1) select buddy team
    #    a) make sure buddy team alive
    #2) randomly select a location 1 cell away that meets the criteria
    #    a) Distance must move away from starting location 
    #    b) Cannot stand on previous location
    #3) calculate total value of weights
    
    #randomizeWeights()
    #randomBlueMove(1860, 2080, 10100, 10400)
    startTime = time.time()
    avgX = 0
    avgY = 0
    while True:        
        #isMissionEnd()
        bestSoldierMove ={}
        bestReward = -1
        initalTeamMove ={}
        test = 0
        atLoc = True
        #for test in range(0,5):
        soldierStats = currentSoldierPos()
        #print(soldierStats)
        tempPreviouslyObservedSite={}
        while (test < 120): #or atLoc== False):
            print("test",test)
            tempSoldierLoc =  copy.deepcopy(soldierStats)
            tempPreviouslyObservedSite = copy.deepcopy(previouslyObservedSite)
            tempSoldierLoc, tempDistanceMoved   = moveRnSUnits(tempSoldierLoc, tempPreviouslyObservedSite)
            
            areaLeftUnsearched,averageViewArea, tempPreviouslyObservedSite = calculateVisuals(tempSoldierLoc, tempPreviouslyObservedSite)
            initalTeamMove= copy.deepcopy(tempSoldierLoc)
            
            reward =0
            for k in range (0,1):
                soldierName = list(tempSoldierLoc.keys())
                #print(soldierName)
                soldierThatAreVisible = []
                #checks to see if the teams are visible to one another
                for i in range(0, len(soldierName)):
                    for j in range(i+1, len(soldierName)):
                        if soldierName[i] == soldierName[j]:
                            continue
                        else:
                            firstSoldier = tempSoldierLoc[soldierName[i]]
                            secondSoldier = tempSoldierLoc[soldierName[j]]
                            tempSol1x, tempSol1y =closestGrid(firstSoldier[1],firstSoldier[2])
                            tempSol2x, tempSol2y =closestGrid(secondSoldier[1],secondSoldier[2])                        
                            if tempSol1x == tempSol2x and tempSol1y == tempSol2y:
                                #print("soldier  1 name", soldierName[i], "soldier  2 name", soldierName[j])
                                soldierThatAreVisible.append(i)
                                soldierThatAreVisible.append(j) 
                                #print("soldier can see each other")
                                #time.sleep(2)
                            else:
            
                                #will need to update to find which location was the start and which was the destination
                                if (tempSol1x, tempSol1y , tempSol2x, tempSol2y) in visDict:
                                    #print("visual location check", tempSol1x, tempSol1y , tempSol2x, tempSol2y)
                                    #print("soldier  1 name", soldierName[i])
                                    #print("soldier  2 name", soldierName[j])
                                    if (visDict[(tempSol1x, tempSol1y,tempSol2x, tempSol2y)] ) == 1:
                                            soldierThatAreVisible.append(i)
                                            soldierThatAreVisible.append(j)
                                            #print("soldier can see each other")
                                            #time.sleep(2)
                                    #else:
                                        #print("soldiers cant see each other")
                                        #time.sleep(2)
                                elif (tempSol2x, tempSol2y , tempSol1x, tempSol1y) in visDict:
                                    #print("visual location check", tempSol2x, tempSol2y , tempSol1x, tempSol1y)
                                    #print("soldier  1 name", soldierName[j])
                                    #print("soldier  2 name", soldierName[i])
                                    if (visDict[(tempSol2x, tempSol2y, tempSol1x, tempSol1y)]) == 1:
                                            soldierThatAreVisible.append(i)
                                            soldierThatAreVisible.append(j)
                                            #print("soldier can see each other")
                                            #time.sleep(2)
                                    #else:
                                        #print("soldiers cant see each other")
                                        #time.sleep(2)
                                #else:
                                    #print("Not in visDict, soldier  1 name", soldierName[i], "soldier  2 name", soldierName[j])
                                    #print("soldiers cant see each other not in visDict")
                                    #time.sleep(2)
                            
                soldierThatAreVisible = set(soldierThatAreVisible)
                percentTeamsVisible = 0
                if(len(soldierName) !=0):
                    percentTeamsVisible = len(soldierThatAreVisible)/len(soldierName)
                    #print("percent Visible ppls: ", percentTeamsVisible)
                    #time.sleep(2)
                
                #Checks to see distance grouping
                distance = {}
                buddyDistance = {}
                sortedDistance =[]
                for l in range(0, len(soldierName)-1):
                    for m in range(l+1, len(soldierName)):
                        firstSoldier = tempSoldierLoc[soldierName[l]]
                        secondSoldier = tempSoldierLoc[soldierName[m]]
                        dis = math.sqrt(math.pow(firstSoldier[1]-secondSoldier[1],2)+math.pow(firstSoldier[2]-secondSoldier[2],2))
                        buddyDistance[(soldierName[l],soldierName[m])] = dis
                        if dis not in distance:
                            distance[dis] = [(soldierName[l],soldierName[m])]
                        else:
                            grouping = distance[dis] 
                            grouping.append((soldierName[l],soldierName[m]))
                            distance[dis]  = grouping
                        sortedDistance.append(dis)
                sortedDistance = sorted(set(sortedDistance))
                #print(distance)
                maxDistance = 1.2
        
        
                #checks max cluster size 
                clusters ={}
                t = 0
                for currentDistance in sortedDistance:
                    if currentDistance < maxDistance:
                        groups = distance[currentDistance]
                        for pair in groups:
                            team1 = pair[0]
                            team2 = pair[1]
                            addedMatch = False
                            for clusterNumber,sNames in clusters.items():
                                if team1 in sNames and team2 not in sNames:
                                    withinDistance = True
                                    for soldier in sNames:
                                        if (soldier,team2) in buddyDistance and float(buddyDistance[(soldier,team2)])>maxDistance:
                                            withinDistance = False
                                        elif (team2,soldier) in buddyDistance  and float(buddyDistance[(team2,soldier)])>maxDistance:
                                            withinDistance = False
                                    if withinDistance:
                                        sNames.append(team2)
                                        clusters[clusterNumber] = sNames
                                        addedMatch = True
                                            
                                elif team1 not in sNames and team2 in sNames:
                                    withinDistance = True
                                    for soldier in sNames:
                                        if (soldier,team1) in buddyDistance and float(buddyDistance[(soldier,team1)])>maxDistance:
                                            withinDistance = False
                                        elif (team1,soldier) in buddyDistance  and float(buddyDistance[(team1,soldier)])>maxDistance:
                                            withinDistance = False
                                    if withinDistance:
                                        sNames.append(team1)
                                        clusters[clusterNumber] = sNames
                                        addedMatch = True
                                elif team1  in sNames and team2 in sNames:
                                    addedMatch = True # already added into the cluster
                                if addedMatch:
                                    break
                            if addedMatch == False:
                                clusters[t] = [team1,team2]
                                t+=1
                            
                    else:
                        break
        
                #print(clusters)
                maxClusterSize = 0
                for key, value in clusters.items():
                    size = len(value) 
                    if size> maxClusterSize:
                        maxClusterSize = size
        
                percentageWithinDistance =  maxClusterSize/len(soldierName)
                #print (percentageWithinDistance)
                minConcealment =100
                averageConcealment = 0
        
                minCover=100
                averageCover=0
               
                for location in tempSoldierLoc.values():
                    tempCover = percentageCover(coverRadius, coverIncrement, location[1], location[2])
                    tempConcealment = percentageConcealment(concealmentRadius, concealmentIncrement, location[1], location[2])
                    if tempCover <minCover:
                        minCover = tempCover
                    averageCover+=tempCover
                    if tempConcealment < minConcealment:
                        minConcealment = tempConcealment
                    averageConcealment+=tempConcealment
                averageCover = averageCover/len(tempSoldierLoc.values())
                averageConcealment= averageConcealment/len( tempSoldierLoc.values())
                print("Info", percentTeamsVisible, minCover, minConcealment, averageCover, averageConcealment, averageViewArea,  percentageWithinDistance, areaLeftUnsearched, tempDistanceMoved)
                #percentBuddyTeamVisibleRange, #minCover, #minConcealment, #averageCover, #averageConcealment, #averageVisibleArea,  #largestNumberBuddyTeam30Meters, #areaLeftUnsearched
                
                reward+= percentTeamsVisible*weights[0] + minCover*weights[1]+ minConcealment*weights[2] + averageCover*weights[3]+averageConcealment*weights[4]+ averageViewArea*weights[5]
                +percentageWithinDistance*weights[7]+areaLeftUnsearched*weights[8]+ tempDistanceMoved*weights[9]
                tempSoldierLoc,tempDistanceMoved = moveRnSUnits(tempSoldierLoc,tempPreviouslyObservedSite)
                areaLeftUnsearched,averageViewArea,tempPreviouslyObservedSite = calculateVisuals(tempSoldierLoc, tempPreviouslyObservedSite)
            if reward > bestReward:
                bestReward =reward

                bestSoldierMove = copy.deepcopy(initalTeamMove)
            test+=1
            
            
            '''
            #check to see if soldiers are at desired location
            if notFirstPass:
                tempCurrentSoldierLoc =  updateSoldierPos()
                atLocCounter = 0
                for key in tempCurrentSoldierLoc:
                    tempCurrentLoc = tempCurrentSoldierLoc[key]
                    soldierMove = tempSoldierLoc[key]
                    if(abs(tempCurrentLoc[1] -soldierMove[1]) < 10 and abs(tempCurrentLoc[2] -soldierMove[2]) < 10):
                        atLocCounter+=1
                if(atLocCounter == len(tempCurrentSoldierLoc)):
                    atLoc = True
            
            '''
        #print (bestReward)
        #print(bestSoldierMove)
        solIndex = 0
        soldierMoveArray = []
        '''
        for key in bestSoldierMove:
            soldierMove = bestSoldierMove[key]
            moveItem = soldierMove[1],soldierMove[2],2
            #moveString =  str(soldierMove[0]) + "," +  str(soldierMove[1])  + ", 2" 
            #new_string = moveString.replace("'", "")
            soldierMoveArray.append(moveItem)
            
                #print("first soldier", printSoldier)
        
        aliveRed = database_connect_Arma.numOfAlive_v2()    
        database_connect_Arma.moveAllUnits("opfor", soldierMoveArray, aliveRed)

        '''
        for key in bestSoldierMove:
            soldierMove = bestSoldierMove[key]
            #if solIndex == 0:
                #printSoldier = soldierMove
                #print("first soldier", printSoldier)
            print(key)
            database_connect_Arma.moveUnit(soldierMove[1], soldierMove[2], 2, key)
            #solIndex+=1
        #soldierStats = copy.deepcopy(bestSoldierMove)
        #notFirstPass = True
        #atLoc = False
        
        previouslyObservedSite = copy.deepcopy(tempPreviouslyObservedSite)
        time.sleep(8)
        #avgX, avgY =getOpForceAvgLoc()
        print("starting danger area check")
        x = [a_tuple[0] for a_tuple in dangerArea]
        y = [a_tuple[1] for a_tuple in dangerArea]
        i = 0
        while i <  len(dangerArea):
            #print(i, assaultedArea[i])
            assaultedArea[i] = isAtDangerArea(x[i],y[i], assaultedArea[i])
            #print(i, assaultedArea[i])
            i = i + 1
        print("finished ckeck")
        
        checkDetection()
        
      # '''
      #  soldierStats = currentSoldierPos()
      #  for soldier in soldierStats:
      #      soldierLoc = soldierStats[soldier]
      #      if (distanceBetweenPoints(dangerArea_X,dangerArea_Y,soldierLoc[1], soldierLoc[2]) <= 30 and assaultedArea == False):
      #      #trigger assault
      #          assaultedArea = assaultDangerArea(dangerArea_X,dangerArea_Y)
      #          break
      #  '''
