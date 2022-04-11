
## this function provides the flanking position for a fix and flank
#once we decide to perform a flank we need to find and X,Z location that is the flank location
# to do this we first find the line of best fit that goes through the visible enemies
# We then find the closest X,Z location that will give use the line of best fit
# we then move a unit to perform the flank.
 
import asyncio
import logging
import socket
import sys
import psycopg2
import time
import math
from distutils import command
import torch
import csv
import numpy as np
from torch import nn
import nest_asyncio
import random
from datetime import datetime
from bisect import bisect_left
import copy
import io
import database_connect
import bisect
import ReadTerrainFile
import linearRegression



xTeam = []
zTeam = []
soldierDict = {}
guy1position = 0
guy2position = 0
avgPosX = 0
avgPosZ = 0
xEnemy = []
zEnemy = []
terraindDict={}
terrainXSet ={}
terrainZSet ={}
nest_asyncio.apply()
enemyLocationTemp ={}
SimulationStart= datetime.now()
D_in, H_one, H_two, H_three, D_out = 69, 69, 69, 69, 3
model = torch.nn.Sequential(
    torch.nn.Linear(D_in, H_one),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_one, H_two),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_two, H_three),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_three, D_out),
    torch.nn.Sigmoid()

    )


 

#declaration of global variables 

#database connection information currently on localhost
connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")
#class that will handle database actions
class ServerProtocol:
    
    def data_received(self, data):
        message = data.decode()
        print('Data received: {}'.format(message))

        print('Send: {}'.format(message))
        
        #print('Close the client socket')
        #self.transport.close()

async def runner():
    #get the current running loop and sets up the server connection to the database
    loop= asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: ServerProtocol(),
        '127.0.0.1', 10000)
    initialized = True
    soldierid = 0
    loadNueralNetwork()
    ft1Position ={}
    ft2Position ={}
    enSoldierPosition ={}
            
    ft1Size = 0.0
    ft1_avgX = 0.0
    ft1_avgZ = 0.0
    ft2Size = 0.0
    ft2_avgX = 0.0
    ft2_avgZ = 0.0
    ft1Position = updateFireTeam("ft1", ft1Position, 5)
    ft2Position = updateFireTeam("ft2", ft2Position, 4)

    
    ft1Size, ft1_avgX, ft1_avgZ = fireTeamAvgXZ(ft1Position)
    ft2Size, ft2_avgX, ft2_avgZ = fireTeamAvgXZ(ft2Position)
    
    ft1LocationData, ft1LethalitySet = ftAmbushLocationData(9902, 16334, 9019, 16010)
    ft2LocationData, ft2LethalitySet = ftAmbushLocationData(9950, 16821, 9465, 16423)
    ft1AmbushSiteNumber = len(ft1LethalitySet)/4
    ft1predictedLethality = ft1LethalitySet[random.randint(0,int(ft1AmbushSiteNumber))]
    for X , Z in ft1LocationData:
        lrate = ft1LocationData[X,Z]
        if(ft1predictedLethality == lrate):
            commandFireTeam("ft1_lead", X, Z)
            print("ft1 en route")
    
    ft2AmbushSiteNumber = len(ft2LethalitySet)/4
    ft2predictedLethality = ft2LethalitySet[random.randint(0,ft2AmbushSiteNumber)]
    for X , Z in ft2LocationData:
        lrate = ft2LocationData[X,Z]
        if(ft2predictedLethality == lrate):
            commandFireTeam("ft2_lead", X, Z)
            print("ft2 en route")
                


def commandFireTeam(ftLead, X, Z):
    soldierpositionString = "'" + str(round(X)) + ";" + "3.9" + ";" + str(round(Z))  + "'"
    database_connect.soldierTeamMoveCommand(ftLead, soldierpositionString)
    
def ftRandomMovement(ftposition, randomX, randomZ):
    for soldier in ftposition:
        tempVar = ftposition[soldier]
        if(float(tempVar[2]) < 1):
            X = float(tempVar[0]) + randomX
            Z = float(tempVar[1]) + randomZ
            ftposition[soldier] = [X,Z,float(tempVar[2])]
    return ftposition
 
def enemyFTVariables (pX,pZ,sX,sZ, tX,tZ, enemies):
    numberWitin200M = 0
    closestDistance = 100000
    psAngle =0.0
    ptAngle = 0.0
    for enemy in enemies:
        vars = enemies[enemy]
        if float(vars[2]) < 1:
            varX = vars[0]
            varZ = vars[1]
            tempDistance = math.sqrt(math.pow(pX-varX,2)+math.pow(pZ-varZ,2))
            if tempDistance < 200:
                numberWitin200M +=1
                
                if tempDistance < closestDistance:
                    closestDistance=tempDistance
                    psAngle = angleOfAttack(varX,varZ,pX,pZ,sX,sZ)
                    ptAngle = angleOfAttack(varX,varZ,pX,pZ,tX,tZ)
    return [numberWitin200M,closestDistance,psAngle,ptAngle]
 
def ftvariables (primary, secondary, tartary, UAV, SUGV, UGV, mg, eSoldier):
    temp = basicPositionandHealth(primary)
    primaryX = temp[0]
    primaryZ  = temp[1]
    percentFTAlive = temp[2]
    atAlive = temp[3]
    ftWoodedTeerain = temp[4]

    temp = basicPositionandHealth(secondary)
    secondaryX = temp[0]
    secondaryZ = temp[1]

    temp = basicPositionandHealth(secondary)
    tartaryX   = temp[0]
    tartaryZ   = temp[1]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, UAV)
    numberUAV200M  = temp[0]
    closestDistanceUAV     = temp[1]
    psAngleUAV     = temp[2]
    ptAngleUAV     = temp[3]
    
    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, SUGV)
    numberSUGV200M = temp[0]
    closestDistanceSUGV    = temp[1]
    psAngleSUGV    = temp[2]
    ptAngleSUGV    = temp[3]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, UGV)
    numberUGV200M  = temp[0]
    closestDistanceUGV     = temp[1]
    psAngleUGV     = temp[2]
    ptAngleUGV     = temp[3]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, mg)
    numberMG200M       = temp[0]
    closestDistanceMG  = temp[1]
    psAngleMG      = temp[2]
    ptAngleMG      = temp[3]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, eSoldier)
    numberSoldier200M = temp[0]
    closestDistanceSoldier = temp[1]
    psAngleSoldier = temp[2]
    ptAngleSoldier = temp[3]
    return [percentFTAlive, atAlive, ftWoodedTeerain, numberUAV200M, closestDistanceUAV, psAngleUAV, ptAngleUAV, numberSUGV200M, closestDistanceSUGV, psAngleSUGV, ptAngleSUGV,numberUGV200M, closestDistanceUGV, psAngleUGV, ptAngleUGV, numberMG200M, closestDistanceMG, psAngleMG, ptAngleMG,numberSoldier200M, closestDistanceSoldier, psAngleSoldier, ptAngleSoldier ]

def fireTeamAvgXZ(ftPosition):
    i = 0
    x = 0
    z = 0
    for soldier in ftPosition:
        tempVar = ftPosition[soldier]
        if(float(tempVar[2]) < 1):
            i+=1 
            x+=float(tempVar[0])
            z+=float(tempVar[1])
    if(i>0):
        x = x / i
        z = z / i
    return i, x, z
                
def updateFireTeam(ft, ftPosition, ftSize):
    
    global soldierDict
    soldiers = database_connect.getOpforFireTeam(ft, ftSize)
    for i in soldiers:
        ftPosition[i[0]] = [i[2],i[3],i[1]]   
        if(float(i[1]) < 1):
            if(i[0] not in soldierDict):
                soldierDict[i[0]] = [0,0,i[2],i[3],i[2],i[3],i[2],i[3]]
            else:
                tempState = soldierDict[i[0]]
                tempState[2] = i[2]
                tempState[3] = i[3]
                soldierDict[i[0]] = tempState
        else:
            if(i[0] in soldierDict):
                del soldierDict[i[0]]
    return ftPosition
      
def updateEnemy(enemyPosition):
    UAVPosition = {}
    SUGVPosition = {}
    UGVPosition = {}
    mgPosition = {}
    enSoldierPosition = {}
    for enemy in enemyPosition:
        e = database_connect.getBlueforUnit(enemy)
        if 'UAV' in enemy:
            #                     positon x, position z, health, velocity x, velocity z
            UAVPosition[enemy] = [e[1], e[2], e[0], e[3], e[4]]
        elif 'SUGV' in enemy:
            SUGVPosition[enemy] = [e[1], e[2], e[0], e[3], e[4]]
        elif 'UGV' in enemy and 'SUGV' not in enemy:
            UGVPosition[enemy] = [e[1], e[2], e[0], e[3], e[4]]
        elif 'mg' in enemy and 'gunner' not in enemy:
            mgPosition[enemy] = [e[1], e[2], e[0], e[3], e[4]]
        elif e is not None:
            enSoldierPosition[enemy] =[e[1], e[2], e[0], e[3], e[4]]
    
    return UAVPosition, SUGVPosition, UGVPosition, mgPosition, enSoldierPosition
              
def basicPositionandHealth (ft):
    ftX = 0.0
    ftZ =0.0
    percentFTAlive = 0.0
    atAlive =0
    percentWoods=0
    for unit in ft:
        vars = ft[unit]
        if (float(vars[2]) < 1):
            ftX+=vars[0]
            ftZ+=vars[1]
            percentFTAlive+=1.0
            if 'rpg' in unit:
                atAlive = 1
    if percentFTAlive>0:
        ftX = ftX/percentFTAlive
        ftZ = ftZ/percentFTAlive
        percentFTAlive = percentFTAlive/len(ft)
        global terraindDict
        percentWoods = float(terraindDict[closestXZTerrain(ftX, ftZ)][2])
    return [ftX,ftZ, percentFTAlive, atAlive, percentWoods]

            
def distanceToFOB(X,Z):
    dis = math.sqrt(math.pow(X-1179.88, 2) + math.pow(Z- 1479.86, 2))
    return dis
          
#function provides oreintation line if taking contact or begining assault
def orientOnline (xEnemy, zEnemy, xTeam, zTeam):
    if(len(xEnemy)>1):
        #gets the average X and y of enemy
        averageX = 0.0
        averageX = sum(xEnemy)/len(xEnemy)
        averageZ = 0.0
        averageZ = sum(zEnemy)/len(zEnemy)        
        #finds the slope of the line of best fit
        slope = 0.0
        squared=0.0
        for i in range(len(xEnemy)):
            slope+= (xEnemy[i]-averageX) * (zEnemy[i]-averageZ)
            squared+=(xEnemy[i]-averageX) * (xEnemy[i]-averageX)
        slope = slope/squared
        del squared

        b = averageZ - slope*averageX
        #finds the closest unit to the line of best fit
        closestUnit = -1
        closetsfriendlyDistance = 10000
        for i in range(len(xTeam)):
            tempD = abs(slope*xTeam[i] - zTeam[i]+b)/math.sqrt(math.pow(slope,2)+1)
            if tempD < closetsfriendlyDistance:
                closetsfriendlyDistance = tempD
                closestUnit = i
        
        #find orientation line
        friendlyB = zTeam[closestUnit] - slope * xTeam[closestUnit]
        return [slope, friendlyB]
    else:
        eX = xEnemy[0]
        eZ = zEnemy[0]

        #find the closet friendly unit to the enemy
        closestUnit = -1
        closetsfriendlyDistance = 10000
        for i in range(len(xTeam)):
            tempD = math.sqrt(math.pow(xTeam[i]-eX,2)+math.pow(zTeam[i]-eZ,2))
            if tempD < closetsfriendlyDistance:
                closetsfriendlyDistance = tempD
                closestUnit = i
        
        #find slope between enemy and closest friend unit
        slope = (zTeam[closestUnit] - eZ)/ (xTeam[closestUnit]-eX)
        #Oreintation slope is negative reciprocal
        orientationSlope = -1/slope
        #gets orientationB
        orientationB = zTeam[closestUnit]-oreintationSlope*xTeam[closestUnit]  
        return [orientationSlope, orientationB]



#functions finds point to move to on Oreintation line
#line = [slope, b]
def orientationPoint (line, unitX, unitz):
    #find perpendicuular line
    #currentB = unitz - (-1/line[0])* unitX
    #print (curre)
    #solve for set of equation
    #X = currentB - line[1]  /(line[0] +1/line[0])
    #Z = (-1/line[0])*X + currentB
    Z = line[0]* unitX +line[1]
    return [unitX, Z]

def continueAssault (fireteam, targetX, targetZ, soldierid):
    
    global soldierDict
    # Check if every soldier is at the target location = selectedSoldArray[4],selectedSoldArray[5] if true all soldiers weapons free
    filtered_dict = {k:v for (k,v) in soldierDict.items() if fireteam in k}
    allMoving = 0
    soldiers = []
    randomUnit =0
    cursor = connection.cursor()
    if len(filtered_dict)>0:
        selectedSoldier = []
        occupyingSoldier = []
        print("$$$$$$$$$$$$$$$")
        print(soldierDict)
        for key in filtered_dict:
            if(filtered_dict[key][1] == 1):
                allMoving = 1 
        
        for key in filtered_dict:
            soldiers.append(key)
        #randomly assign to move or cover
        print(soldiers)
        if len(soldiers) == 5:
            randomUnit =random.randint(0, len(soldiers)-1)
            selectedSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            selectedSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
        elif len(soldiers) == 4:
            randomUnit =random.randint(0, len(soldiers)-1)
            selectedSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            selectedSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
        elif len(soldiers) == 3:
            randomUnit =random.randint(0, len(soldiers)-1)
            selectedSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
        elif len(soldiers) == 2:
            randomUnit =random.randint(0, len(soldiers)-1)
            selectedSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
            randomUnit =random.randint(0, len(soldiers)-1)
            occupyingSoldier.append(soldiers[randomUnit])
            soldiers.remove(soldiers[randomUnit])
        elif len(soldiers) == 1:
            selectedSoldier.append(soldiers[0])

        if(allMoving == 0):
            #gets current positoin of soldiers
            xzPos=[]
            for sol in selectedSoldier:            
                positionList = database_connect.getOpforSoldierPos(sol)
                xzPos.append(positionList)
            for sol in occupyingSoldier:
                positionList = database_connect.getOpforSoldierPos(sol)
                xzPos.append(positionList)
        
           
            #soldiers move and occupy
            i = 0
            newsoldierDict={}
            for sol in selectedSoldier:
                selectedSoldArray = soldierDict.get(sol)
                newPosition1 = newAssaultPoint(targetX,targetZ, float(xzPos[i][0]), float(xzPos[i][1]))
                soldier1positionString = "'" + str(round(targetX) + np.random.uniform(-5,5)) + ";" + "3.9" + ";" + str(round(targetZ) + np.random.uniform(-5,5)) + "'"
                database_connect.soldierMoveCommand(sol, soldier1positionString)                
                database_connect.soldierChangeROE(sol)
                soldierDict[sol] = [0,1,xzPos[i][0],xzPos[i][1],targetX,targetZ,targetX,targetZ]
                i+=1

            for sol in occupyingSoldier:
                soldier3positionString = "'" + xzPos[i][0] + ";" + "3.9" + ";" + xzPos[i][1] + "'"
                database_connect.soldierMoveCommand(sol, soldier3positionString)            
                database_connect.soldierChangeROE(sol)
                soldierDict[sol] = [0,0,xzPos[i][0],xzPos[i][1],targetX,targetZ,xzPos[i][0],xzPos[i][1]]
                i+=1
            #update soldierDict with the new dictionary
            #soldierDict.update(newsoldierDict)
            print(soldierDict)
            print("$$$$$$$$$$$")
        
        else:
            for key in filtered_dict:
                soldiers.append(key)
            print("WEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            occupyingSoldier =[]
            selectedSoldier =[]
            print(soldiers)
            for sol in soldiers:
                tempSoldierValue = filtered_dict.get(sol)
                moveOrOccupy = tempSoldierValue[1]
                print("$&$#&*^%*(&$^&*#%^*#$&")
                print(tempSoldierValue, sol)
                #print(moveOrOccupy)
                if(float(moveOrOccupy) < 1):
                    occupyingSoldier.append(sol)
                else:
                    selectedSoldier.append(sol)


            
            #if the soldiers are not all holding
            #call newassaultpoint
            #make the soldiers that were holding move and the soldiers that were moving hold
            xzPos =[]
            #newsoldierDict={}
            #print("$&$#&*^%*(&$^&*#%^*#$&")
            print(occupyingSoldier)
            print(selectedSoldier)
            for sol in occupyingSoldier:
                positionList = database_connect.getOpforSoldierPos(sol)
                soldier1position = newAssaultPoint(targetX, targetZ, float(positionList[0]), float(positionList[1]))
                soldier1positionString = "'" + str(round(targetX) + np.random.uniform(-5,5)) + ";" + "3.9" + ";" + str(round(targetZ) + + np.random.uniform(-5,5)) + "'"
                database_connect.soldierMoveCommand(sol, soldier1positionString)                  
                database_connect.soldierChangeROE(sol)
                soldierDict[sol]= [0,1,positionList[0],positionList[1],targetX,targetZ,targetX,targetZ]
                
            for sol in selectedSoldier:
                positionList = database_connect.getOpforSoldierPos(sol)
                soldier3positionString = "'" + positionList[0] + ";" + "3.9" + ";" + positionList[1] + "'"
                database_connect.soldierMoveCommand(sol, soldier3positionString)  
                database_connect.soldierChangeROE(sol)
                soldierDict[sol]= [0,0,positionList[0],positionList[1],targetX,targetZ,positionList[0],positionList[1]]
                
                
            #soldierDict.update(newsoldierDict)
          
    return soldierid



def newAssaultPoint (targetX, targetZ, currentX , currentZ):
    #calculate the new assaultpoint to take
    slope = (currentZ-targetZ)/ (currentX - targetX +.00001)
    B = currentZ - currentX * slope
    x1 = currentX - 10 / math.sqrt(1 + pow(slope,2))
    x2 = currentX + 10 / math.sqrt(1 + pow(slope,2))
    if targetX < currentX:
        z = slope*x1 + B
        return [x1, z]
    else:
        z = slope*x2 + B
        return [x2, z]

def  futureLocationRandomize(enemyLocationTemp, time):
    for enemy in enemyLocationTemp:        
        tempPositionVar = enemyLocationTemp[enemy]
        if(float(tempPositionVar[2]) < 1):
            vxRandom=random.random()
            if random.random() <.5:
                vxRandom=vxRandom*-1     
            vzRandom = random.random()
            if random.random() <.5:
                vzRandom=vzRandom*-1 
    
            newPx = float(tempPositionVar[0]) + float(tempPositionVar[3])*time*vxRandom
            newPz = float(tempPositionVar[1]) + float(tempPositionVar[4])*time*vzRandom
            enemyLocationTemp[enemy] = [newPx, newPz, float(tempPositionVar[2]), float(tempPositionVar[3])*vxRandom,  float(tempPositionVar[4])*vzRandom]

    #returns new estimated position
    return enemyLocationTemp



def  futureLocationInital(enemy, time):
    cursor = connection.cursor()
    #get the data of the seen enemy position and velocity
    getEnemyData = "select px, py, pz, vx, vy, vz from blueforpositiondata where unit_name='" + enemy + "';"
    cursor.execute(getEnemyData)
    getEnemyPositions = cursor.fetchone()
    connection.commit()
    
    #randomizes movements
    vxRandom=random.random()
    if random.random() <.5:
        vxRandom=vxRandom*-1
    
    vyRandom = random.random()
    if random.random() <.5:
        vyRandom=vyRandom*-1
    
    vzRandom = random.random()
    if random.random() <.5:
        vzRandom=vzRandom*-1
    
    #calculate the new positions 
    newPx = float(getEnemyPositions[0]) + float(getEnemyPositions[3])*time*vxRandom
    newPy = float(getEnemyPositions[1]) + float(getEnemyPositions[4])*time*vyRandom
    newPz = float(getEnemyPositions[2]) + float(getEnemyPositions[5])*time*vzRandom
    return [newPx,newPy, newPz, float(getEnemyPositions[3])*vxRandom, float(getEnemyPositions[4])*vyRandom, float(getEnemyPositions[5])*vzRandom]
    
    
def flankPosition (xEnemy, zEnemy, xTeam, zTeam):
    #gets the average X and y of enemy
    averageX = 0.0
    averageX = sum(xEnemy)/len(xEnemy)
    averageZ = 0.0
    averageZ = sum(zEnemy)/len(zEnemy)
 

 

    #finds the slope of the line of best fit
    slope = 0.0
    squared=0.0
    for i in range(len(xEnemy)):
        slope+= (xEnemy[i]-averageX) * (zEnemy[i]-averageZ)
        squared+=(xEnemy[i]-averageX) * (xEnemy[i]-averageX)
    slope = slope/squared
    del squared
 

    b = averageZ - slope*averageX
 

 

    #calcualate average X and Z of the friendly fireteam
    friendlyAvgX = sum(xTeam)/len(xTeam)
    friendlyAvgZ = sum(zTeam)/len(zTeam)
 

    slopeIntesectingLine = -1*1/slope
    bIntersectingLine = friendlyAvgZ - slopeIntesectingLine * friendlyAvgX
 

    flankingX = (bIntersectingLine - b)/(slope - slopeIntesectingLine)
    flankingZ = slopeIntesectingLine*flankingX + bIntersectingLine
    return [flankingX,flankingZ]


#reads the terrain file and creates a dictionary of terrain types and sets
def readTerrain():
    terrainFile = open('C:\\Downloads\\terrainType_db.csv','r')
    count = 0
    terrainX =[]
    terrainZ =[]
    global terraindDict
    while True:
        
        line = terrainFile.readline()
        if not line:
            break
        if count > 0 :
            line = line.replace('\n','')
            values = line.split(',')
            xz = values[1] +','  +values[3]
            terrainX.append(float(values[1]))
            terrainZ.append(float(values[3]))
            uoc = [float(values[4]),float(values[5]),float(values[6])] 
            terraindDict[xz] = uoc
        else:
            count =1
    terrainFile.close()
    global terrainXSet
    terrainXSet = sorted(set(terrainX))
    global terrainZSet
    terrainZSet = sorted(set(terrainZ))
    
def getTerrainAtLocation(X,Z):
    global terraindDict
    global terrainXSet
    global terrainZSet
    newXpos = bisect_left(terrainXSet, X)
    newZpos = bisect_left(terrainZSet, Z)
    xz = newXpos + ',' + newZpos
    return terraindDict[xz]

def distanceBetweenUnits(opFor, blueFor):
    opForPosition = database_connect.getOpforSoldierPos(opFor)
    blueForPosition = database_connect.getBlueforSoldierPos(blueFor)
    dis = distanceBetweenPoints(opForPosition[0],opForPosition[1], blueForPosition[0],blueForPosition[1])
    return dis

def distanceBetweenPoints(X1,Z1,X2, Z2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Z1- Z2, 2))
    return dis        

def seenEnemy(soldier):
    while True:
        seenEnemies = database_connect.opForVision(soldier)
        if(seenEnemies > 0):
            soldierPos = database_connect.getOpForSoldierPos(soldier)
            soldierPositionString = "'" + soldierPos[0] + str(np.random.uniform(-15,15)) + ";" + "3.9" + ";" + soldierPos[1] + str(np.random.uniform(-15,15)) + "'"
            database_connect.soldierMoveCommand(soldier, soldierPositionString)
        if(seenEnemies <= 0):
            break;
def saveToFile():
    with open('filename.csv', mode ='w') as csv_file:
        fieldnames = ['X', 'Z', 'open', 'closed', 'neighbors', 'DToPath', 'ElevationChanged']     
        
def terrainVariablesToFile(Xmax, Zmax, Xmin, Zmin):
    XSet,ZSet, TDict = ReadTerrainFile.readTerrainFile()
    ReadTerrainFile.setTerrainValues(XSet, ZSet, TDict)
    XSet,ZSet, EDict = ReadTerrainFile.readElevationFile()
    ReadTerrainFile.setElevationValues(XSet, ZSet, EDict)
    for x in range(Xmin, Xmax, 10):
        for z in range(Zmin, Zmax, 10):
            print(x,z)
            DToPath , ElevationChanged = ReadTerrainFile.findDistanceAndElevationToPath(x,z)
            urban, open , closed =  ReadTerrainFile.getTerrainAtLocation(x,z)
            neighbors = ReadTerrainFile.closedNeighbors(x,z)
            #write variables to file 

def readTerrainVariableFromFile(fileName): 
    #read terrain file 
    #add to global dictionary[x,z] = open, closed, neighbors, DToPath, ElevationChanged
    positionData = {}
    lethalityset = []
    lethality = linearRegression.predictLethalityAtPosition2(open, closed, neighbors, DToPath, ElevationChanged)[0,0]
    positionData[x,z] = lethality
    lethalityset.append(lethality)
       
    return positionData, sorted(set(lethalityset),reverse = True)


'''
def ftAmbushLocationData(Xmax, Zmax, Xmin, Zmin):
    positionData = {}
    XSet,ZSet, TDict = ReadTerrainFile.readTerrainFile()
    ReadTerrainFile.setTerrainValues(XSet, ZSet, TDict)
    XSet,ZSet, EDict = ReadTerrainFile.readElevationFile()
    ReadTerrainFile.setElevationValues(XSet, ZSet, EDict)
    lethalityset = []
    for x in range(Xmin, Xmax, 50):
        for z in range(Zmin, Zmax, 50):
            print(x,z)
            DToPath , ElevationChanged = ReadTerrainFile.findDistanceAndElevationToPath(x,z)
            urban, open , closed =  ReadTerrainFile.getTerrainAtLocation(x,z)
            neighbors = ReadTerrainFile.closedNeighbors(x,z)
            
            lethality = linearRegression.predictLethalityAtPosition2(open, closed, neighbors, DToPath, ElevationChanged)[0,0]
            positionData[x,z] = lethality
            lethalityset.append(lethality)
            #positionData[x,z]= [ReadTerrainFile.getTerrainAtLocation(x,z),ReadTerrainFile.getElevationAtLocation(x,z)]    
            
    return positionData, sorted(set(lethalityset),reverse = True)
'''

    #for each location get the values open closed neighbor    
def futureOutComes (EPosition, FT1X, FT1Z, FT1_size, FT2X, FT2Z, FT2_size,FT3X, FT3Z, FT3_size ):
    ft1LargeUGVwithin300M =0
    ft1SamllUGVWithin300M =0
    ft1UAVWithin300M =0
    ft1TurretWithin300M =0
    ft1SoldierWithin300M =0
    ft1ClosestLargeUGV = 1000
    ft1ClosestSmallUGV = 1000
    ft1ClosestUAV = 1000
    ft1ClosestTurret = 1000
    ft1ClosestSoldier = 1000

    ft2LargeUGVwithin300M =0
    ft2SamllUGVWithin300M =0
    ft2UAVWithin300M =0
    ft2TurretWithin300M =0
    ft2SoldierWithin300M =0
    ft2ClosestLargeUGV = 1000
    ft2ClosestSmallUGV = 1000
    ft2ClosestUAV = 1000
    ft2ClosestTurret = 1000
    ft2ClosestSoldier = 1000

    ft3LargeUGVwithin300M =0
    ft3SamllUGVWithin300M =0
    ft3UAVWithin300M =0
    ft3TurretWithin300M =0
    ft3SoldierWithin300M =0
    ft3ClosestLargeUGV = 1000
    ft3ClosestSmallUGV = 1000
    ft3ClosestUAV = 1000
    ft3ClosestTurret = 1000
    ft3ClosestSoldier = 1000

    angleFireLargeUGVFT1FT2 = 0
    angleFireLargeUGVFT2FT1 = 0
    angleFireLargeUGVFT1FT3 = 0
    angleFireLargeUGVFT3FT2 = 0
    angleFireLargeUGVFT3FT2 = 0
    angleFireLargeUGVFT2FT3 = 0

    angleFireSmallUGVFT1FT2 = 0
    angleFireSmallUGVFT2FT1 = 0
    angleFireSmallUGVFT1FT3 = 0
    angleFireSmallUGVFT3FT1 = 0
    angleFireSmallUGVFT3FT2 = 0
    angleFireSmallUGVFT2FT3 = 0

    angleFireUAVFT1FT2 = 0
    angleFireUAVFT2FT1 = 0
    angleFireUAVFT1FT3 = 0
    angleFireUAVFT3FT2 = 0
    angleFireUAVFT3FT2 = 0
    angleFireUAVFT2FT3 = 0

    angleFireTurretFT1FT2 = 0
    angleFireTurretFT2FT1 = 0
    angleFireTurretFT1FT3 = 0
    angleFireTurretFT3FT2 = 0
    angleFireTurretFT3FT2 = 0
    angleFireTurretFT2FT3 = 0

    angleFireSoldierFT1FT2 = 0
    angleFireSoldierFT2FT1 = 0
    angleFireSoldierFT1FT3 = 0
    angleFireSoldierFT3FT2 = 0
    angleFireSoldierFT3FT2 = 0
    angleFireSoldierFT2FT3 = 0

    for enemy in EPosition:
        getEnemyData = EPosition[enemy]
        if 'SUGV' in enemy:
            if FT1_size >0:
                if ft1ClosestSmallUGV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z):
                    ft1ClosestSmallUGV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z)
                    angleFireSmallUGVFT1FT2 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireSmallUGVFT1FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT3X, FT3Z)
                    if ft1ClosestSmallUGV <=300:
                        ft1SamllUGVWithin300M += 1
            
            if  FT2_size >0:
                if ft2ClosestSmallUGV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z):
                    ft2ClosestSmallUGV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z)
                    angleFireSmallUGVFT2FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireSmallUGVFT2FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft2ClosestSmallUGV <=300:
                        ft2SamllUGVWithin300M += 1   

            if  FT3_size >0:
                if ft3ClosestSmallUGV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z):
                    ft3ClosestSmallUGV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z)
                    angleFireSmallUGVFT3FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z,FT2X, FT2Z)
                    angleFireSmallUGVFT3FT2= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft3ClosestSmallUGV <=300:
                        ft3SamllUGVWithin300M += 1         
            pass
        elif 'UGV' in enemy:
            if FT1_size >0:
                if ft1ClosestLargeUGV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z):
                    ft1ClosestLargeUGV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z)
                    angleFireLargeUGVFT1FT2 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireLargeUGVFT1FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT3X, FT3Z)
                    if ft1ClosestLargeUGV <=300:
                        ft1LargeUGVwithin300M += 1
            
            if  FT2_size >0:
                if ft2ClosestLargeUGV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z):
                    ft2ClosestLargeUGV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z)
                    angleFireLargeUGVFT2FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireLargeUGVFT2FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft2ClosestLargeUGV <=300:
                        ft2LargeUGVwithin300M += 1   

            if  FT3_size >0:
                if ft3ClosestLargeUGV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z):
                    ft3ClosestLargeUGV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z)
                    angleFireLargeUGVFT3FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z,FT2X, FT2Z)
                    angleFireLargeUGVFT3FT2= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft3ClosestLargeUGV <=300:
                        ft3LargeUGVwithin300M += 1  
            pass
        elif 'UAV' in enemy or 'UCAV' in enemy:
            if FT1_size >0:
                if ft1ClosestUAV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z):
                    ft1ClosestUAV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z)
                    angleFireUAVFT1FT2 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireUAVFT1FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT3X, FT3Z)
                    if ft1ClosestUAV <=300:
                        ft1UAVWithin300M += 1
            
            if  FT2_size >0:
                if ft2ClosestUAV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z):
                    ft2ClosestUAV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z)
                    angleFireUAVFT2FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireUAVFT2FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft2ClosestUAV <=300:
                        ft2UAVWithin300M += 1   

            if  FT3_size >0:
                if ft3ClosestUAV > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z):
                    ft3ClosestUAV = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z)
                    angleFireUAVFT3FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z,FT2X, FT2Z)
                    angleFireUAVFT3FT2= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft3ClosestUAV <=300:
                        ft3UAVWithin300M += 1
            pass
        elif 'mg' in enemy and 'mgunner' not in enemy:
            if FT1_size >0:
                if ft1ClosestTurret > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z):
                    ft1ClosestTurret = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z)
                    angleFireTurretFT1FT2 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireTurretFT1FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT3X, FT3Z)
                    if ft1ClosestTurret <=300:
                        ft1TurretWithin300M += 1
            
            if  FT2_size >0:
                if ft2ClosestTurret > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z):
                    ft2ClosestTurret = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z)
                    angleFireTurretFT2FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireTurretFT2FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft2ClosestTurret <=300:
                        ft2TurretWithin300M += 1   

            if  FT3_size >0:
                if ft3ClosestTurret > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z):
                    ft3ClosestTurret = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z)
                    angleFireTurretFT3FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z,FT2X, FT2Z)
                    angleFireTurretFT3FT2= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft3ClosestTurret <=300:
                        ft3TurretWithin300M += 1
        else:
            if FT1_size >0:
                if ft1ClosestSoldier > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z):
                    ft1ClosestSoldier = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z)
                    angleFireSoldierFT1FT2 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireSoldierFT1FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT3X, FT3Z)
                    if ft1ClosestSoldier <=300:
                        ft1ClosestSoldier += 1
            
            if FT2_size >0:
                if ft2ClosestSoldier > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z):
                    ft2ClosestSoldier = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z)
                    angleFireSoldierFT2FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT1X,FT1Z,FT2X, FT2Z)
                    angleFireSoldierFT2FT3= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft2ClosestSoldier <=300:
                        ft2ClosestSoldier += 1   

            if  FT3_size >0:
                if ft3ClosestSoldier > distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z):
                    ft3ClosestSoldier = distanceBetweenPoints(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z)
                    angleFireSoldierFT3FT1 = angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT3X,FT3Z,FT2X, FT2Z)
                    angleFireSoldierFT3FT2= angleOfAttack(float(getEnemyData[0]),float(getEnemyData[2]), FT2X,FT2Z,FT3X, FT3Z)
                    if ft3ClosestSoldier <=300:
                        ft3ClosestSoldier += 1
    
    FT1Woods = terraindDict[closestXZTerrain(FT1X, FT2X)][2]
    FT2Woods = terraindDict[closestXZTerrain(FT1X, FT2X)][2]
    FT3Woods = terraindDict[closestXZTerrain(FT1X, FT2X)][2]
    #check to see if enemy within 300m
    enemyIndicator = ft1LargeUGVwithin300M +   ft1SamllUGVWithin300M +    ft1UAVWithin300M +    ft1TurretWithin300M +   ft1SoldierWithin300M +ft2LargeUGVwithin300M +   ft2SamllUGVWithin300M +    ft2UAVWithin300M +    ft2TurretWithin300M +   ft2SoldierWithin300M + ft3LargeUGVwithin300M +   ft3SamllUGVWithin300M +    ft3UAVWithin300M +    ft3TurretWithin300M +   ft3SoldierWithin300M
    #check to see if enemy is within 300 m and check to see if mostly in woods
    deleteLargeUGV = False
    deleteSmallUGV= False
    deleteUAV= False
    deletTurret= False
    deleteSoldier = False
    if(enemyIndicator==0 or(FT1Woods>0.5 and FT2Woods >0.5 and FT3Woods>0.5)):
        #Engage
        if ft1LargeUGVwithin300M > 0:
            if FT1_size ==4:
                FT1_size-=2
                deleteLargeUGV = True
            
            elif FT1_size ==3:
                FT1_size-=3
                deleteLargeUGV = True
            else:
                FT1_size = 0
        if ft1SamllUGVWithin300M > 0:
            if FT1_size >1:
                FT1_size-=1
                deleteSmallUGV = True
            else:
                FT1_size = 0
        if ft1UAVWithin300M > 0:
            if FT1_size ==4:
                FT1_size-=3
                deleteUAV = True
        if ft1TurretWithin300M:
            if FT1_size ==4:
                FT1_size-=2
                deletTurret = True
            
            elif FT1_size ==3:
                FT1_size-=3
                deletTurret = True
            else:
                FT1_size = 0
        if ft1SoldierWithin300M:
            if FT1_size >1:
                FT1_size-=1
                deleteSoldier = True
            else:
                FT1_size = 0
        #FT2 enage 
        if ft2LargeUGVwithin300M > 0:
            if FT2_size ==4:
                FT2_size-=2
                deleteLargeUGV = True
            
            elif FT2_size ==3:
                FT2_size-=3
                deleteLargeUGV = True
            else:
                FT2_size = 0
        if ft2SamllUGVWithin300M > 0:
            if FT2_size >1:
                FT2_size-=1
                deleteSmallUGV = True
            else:
                FT2_size = 0
        if ft2UAVWithin300M > 0:
            if FT2_size ==4:
                FT2_size-=3
                deleteUAV = True
        if ft2TurretWithin300M:
            if FT2_size ==4:
                FT2_size-=2
                deletTurret = True
            
            elif FT2_size ==3:
                FT2_size-=3
                deletTurret = True
            else:
                FT2_size = 0
        if ft2SoldierWithin300M:
            if FT2_size >1:
                FT2_size-=1
                deleteSoldier = True
            else:
                FT2_size = 0
        #FT3 engages
        if ft3LargeUGVwithin300M > 0:
            if FT3_size ==4:
                FT3_size-=2
                deleteLargeUGV = True
            
            elif FT3_size ==3:
                FT3_size-=3
                deleteLargeUGV = True
            else:
                FT3_size = 0
        if ft3SamllUGVWithin300M > 0:
            if FT3_size >1:
                FT3_size-=1
                deleteSmallUGV = True
            else:
                FT3_size = 0
        if ft3UAVWithin300M > 0:
            if FT3_size ==4:
                FT3_size-=3
                deleteUAV = True
        if ft3TurretWithin300M:
            if FT3_size ==4:
                FT3_size-=2
                deletTurret = True
            
            elif FT3_size ==3:
                FT3_size-=3
                deletTurret = True
            else:
                FT3_size = 0
        if ft3SoldierWithin300M:
            if FT3_size >1:
                FT3_size-=1
                deleteSoldier = True
            else:
                FT3_size = 0
    
    tempListEnemies = copy.deepcopy(list(EPosition.keys()))
    for enemy in tempListEnemies:
        if  'SUGV' in enemy and deleteSmallUGV:
            del EPosition[enemy]
            deleteSmallUGV = False
        elif 'UGV' in enemy and deleteLargeUGV:
            del EPosition[enemy]
            deleteLargeUGV = False
        elif ('UAV' in enemy or 'UCAV' in enemy) and deleteUAV:
            del EPosition[enemy]
            deleteUAV = False
        elif 'mg' in enemy and 'mgunner' not in enemy and deletTurret:
            del EPosition[enemy]
            deletTurret = False
        elif deleteSoldier:
            del EPosition[enemy]
            deleteSoldier = False
    
    return [EPosition, FT1_size, FT2_size, FT3_size]
           








#return angle of attack 
def angleOfAttack (enemyX, enemyY, alphaFTX, alphaFTY,bravoFTX, bravoFTy):
    numerator = (alphaFTX-enemyX)*(bravoFTX-enemyX)+(alphaFTY-enemyY)*(bravoFTy-enemyY)
    var1 = math.pow(alphaFTX-enemyX,2)+math.pow(alphaFTY-enemyY,2)
    var2 = math.pow(bravoFTX-enemyX,2)+math.pow(bravoFTy-enemyY,2)
    
    denominator = math.sqrt(var1) * math.sqrt(var2)
    var3 = numerator/denominator
    if(var3 < -1):
        var3 = -1
    if(var3 > 1):
        var3 = 1
    angle = math.acos(var3)
    return angle
def nueralNetwork(inputNodes):
    global model
    model.eval()
    #print(inputNodes)
  
    dtype = torch.float
    device = torch.device("cpu")
    input = torch.tensor(inputNodes,device=device, dtype=dtype)
    out_pred = model(input)
    return out_pred
def loadNueralNetwork():
    global model
    model.load_state_dict(torch.load('C:/Users/Mo/Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/Quantico2.pth'))
    


#returns the closest X and Z value that is in the terrain set
def closestXZTerrain(currentX, currentZ):
    global terrainXSet
    global terrainZSet
    closeX = '0'
    closeZ = '0'
    #finds the closest X value in the terrain set
    pos = bisect_left(terrainXSet, currentX)
    if pos == 0:
        closeX = str(int(terrainXSet[0]))
    if pos == len(terrainXSet):
        closeX = str(int(terrainXSet[-1]))
    before = terrainXSet[pos -1]
    if(pos>=len(terrainZSet)):
        after = terrainXSet[pos-1]
    else:
        after = terrainXSet[pos]
    if after - currentX < currentX - before:
        closeX = str(int(after))
    else:
        closeX = str(int(before))
    
    #finds the closest Z value in the terrain set
    pos = bisect_left(terrainZSet, currentZ)
    if pos == 0:
        closeZ = str(int(terrainZSet[0]))
    if pos == len(terrainZSet):
        closeZ = str(int(terrainZSet[-1]))
    
    before = terrainZSet[pos -1]

    if(pos>=len(terrainZSet)):
        after = terrainZSet[pos-1]
    else:
        after = terrainZSet[pos]
    if after - currentZ < currentZ - before:
        closeZ = str(int(after))
    else:
        closeZ = str(int(before))
    
    return closeX+","+closeZ
    
async def main():
    readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())
