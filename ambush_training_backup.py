
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
from tempfile import NamedTemporaryFile
import shutil
import StateSpaceCalc
import FileIO
import loadNueralNetwork
import os



outputPathOp = ""
outputPathBlue = ""
xTeam = []
zTeam = []
soldierDict = {}
guy1position = 0
guy2position = 0
avgPosX = 0
avgPosZ = 0
xEnemy = []
zEnemy = []
forestDict = {}
elevationDict = {}
positionData = {}
terraindDict={}
terrainXSet ={}
terrainZSet ={}
nest_asyncio.apply()
enemyLocationTemp ={}
forestMap = True
SimulationStart= datetime.now()
D_in, H_one, H_two,  D_out = 17, 17, 17, 1
model = torch.nn.Sequential(
    torch.nn.Linear(D_in, H_one),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_one, H_two),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_two, D_out),
    torch.nn.Sigmoid(),

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

    #global elevationDict
    #elevationDict = FileIO.getElevationFromFile("elevation")
    #terrainVariablesToFile('ft1Ambush_Forest', 9600, 16130, 9200, 15930, "Forest")
    #print("Done")
    #terrainVariablesToFile('ft1Ambush_Open', 9100, 16470, 8900, 16070, "Open")
    #print("Done")
    #terrainVariablesToFile('ft2AmbushOnly', 9950, 16821, 9465, 16423)
    #print("Done")
    #ft1Lethality = calculateLethalityAtAmbushFromFile('ft1Ambush.csv', 9019,16020)
    #print(ft1Lethality)
    #saveLethalityPredicitionAtAmbushZoneToFile('ft1Ambush_Forest', 9600, 16130, 9200, 15930)
    #saveLethalityPredicitionAtAmbushZoneToFile('ft1Ambush_Open', 9100, 16470, 8900, 16070)
    #saveLethalityPredicitionAtAmbushZoneToFile('ft2AmbushOnly', 9950, 16821, 9465, 16423)
    #saveLethalityPredicitionAtAmbushZoneToFile('ft1Ambush', 9990, 16470, 8800, 15870)
    #exit(0)
    
    missionType = database_connect.getMissionType()
    opPath = 'C:/Downloads/opForceAgent/'
    count = len([name for name in os.listdir(opPath) if os.path.isfile(os.path.join(opPath, name))]) + 1
    global outputPathOp
    outputPathOp = opPath + 'opForceAgentData-'+str(count)
    bluePath = 'C:/Downloads/blueForceAgent/'
    count = len([name for name in os.listdir(bluePath) if os.path.isfile(os.path.join(bluePath, name))]) + 1
    global outputPathBlue
    outputPathBlue = bluePath + 'blueForceAgentData-'+str(count)
    if("Ft1" not in missionType and "Ft2" not in missionType):
        print("Launching Full")
        twoFireTeams()
    elif("Ft1" in missionType and "Forest" in missionType):
        #launch with ft1 forest
        print("Launching ft1 Forest")
        fireTeam1("Forest", 9600, 16130, 9200, 15930)
    elif("Ft1" in missionType and "Open"  in missionType):
        #launch with ft1 open area
        print("Launching ft1 Open")
        fireTeam1("Open", 9100, 16470, 8900, 16070)
    elif("Ft2" in missionType):
        print("Launching ft2")
        fireTeam2()
      
    #fireTeam2()
    
def fireTeam1(missionType, Xmax, Zmax, Xmin, Zmin):
    global model      
    random.seed()
    model = loadNueralNetwork.loadModel()
    ft1leastLethality, ft1LethalArray = 0, []
    if("Forest" in missionType):
        ft1leastLethality, ft1LethalArray = getPredictedLethalityFromFile('ft1Ambush_Forest')
    elif("Open" in missionType):
        ft1leastLethality, ft1LethalArray = getPredictedLethalityFromFile('ft1Ambush_Open')
    ft1AmbushSiteNumber = len(ft1LethalArray)/10
    #sorted array of lethalitys descending order
    #len/4
    ft1SentXLocation = 0
    ft1SentZLocation = 0
    ft1predictedLethality = random.randint(0,int(ft1AmbushSiteNumber))
    #ft1SentXLocation = 9060
    #ft1SentZLocation = 16270
    #commandFireTeam("ft1_lead", ft1SentXLocation, ft1SentZLocation)
    
    for X , Z in ft1leastLethality:
        #print(X,Z)
        if((X <= Xmax and X >= Xmin) and (Z <= Zmax and Z >= Xmin)):
            lethality = ft1leastLethality[X,Z]
            ft1SentXLocation = X
            ft1SentZLocation = Z
            #print(lethality)     
            if(ft1LethalArray[ft1predictedLethality] == lethality[0]):
                commandFireTeam("ft1_lead", X, Z)
                print("ft1 en route")
      
    global forestDict
    global elevationDict
    forestDict = FileIO.getForestFromTerrainFile('terrainType_db')
    elevationDict = FileIO.getElevationFromFile("elevation")
    Ft1KillPercentage = calculateKillPercentagesFt1(missionType)
    
    

    if("Forest" in missionType):
        openTerrain, closed, neighbors, DToPath, ElevationChanged = getPositionDataAtAmbushFromFile('ft1Ambush_Forest', ft1SentXLocation,ft1SentZLocation)
        saveToTrainingFile('ambushTraining', Ft1KillPercentage, openTerrain, closed, neighbors, DToPath, ElevationChanged)
        generateUpdatedLethality('ft1Ambush_Forest', Xmax, Zmax, Xmin, Zmin)
        print("Training Model Updated")
    
    elif("Open" in missionType):
        openTerrain, closed, neighbors, DToPath, ElevationChanged = getPositionDataAtAmbushFromFile('ft1Ambush_Open', ft1SentXLocation,ft1SentZLocation)
        saveToTrainingFile('ambushTraining', Ft1KillPercentage, openTerrain, closed, neighbors, DToPath, ElevationChanged)
        generateUpdatedLethality('ft1Ambush_Open', Xmax, Zmax, Xmin, Zmin)
        print("Training Model Updated")
    
def fireTeam2():
    #make max X
    global model     
    random.seed()
    commandNotIssued = True 
    model = loadNueralNetwork.loadModel()
    ft2leastLethality, ft2LethalArray = getPredictedLethalityFromFile('ft2AmbushOnly')
    
    
    ft2AmbushSiteNumber = len(ft2LethalArray)*.10
    
    #sorted array of lethalitys descending order
    #len/4
    xMove = 9700 # used to move ambush location. The location will happen east of the X
    ft2SentXLocation = 0
    ft2SentZLocation = 0
    ft2predictedLethality = 0
    if xMove < 9700: #changes the lethality search area depending on desired ambush location. 
        ft2predictedLethality = random.randint(0,int(ft2AmbushSiteNumber))
    else:
        ft2AmbushSiteNumber = len(ft2LethalArray)*.40
        index = int(round( len(ft2LethalArray)/20))
        ft2predictedLethality = random.randint(index,(index+int(ft2AmbushSiteNumber)))
    while commandNotIssued:
        for key in ft2leastLethality:
            
            X = int(key[0])
            Z = int(key[1])
            
            lethality = ft2leastLethality[X,Z]
            ft2SentXLocation = X
            ft2SentZLocation = Z
            #print(lethality)
         
            if(ft2LethalArray[ft2predictedLethality] == lethality[0]):
                print(X, Z)
                print(ft2LethalArray[ft2predictedLethality])
                if (X > xMove):
                    commandFireTeam("ft2_lead", X, Z)
                    X=X+5
                    Z=Z+5
                    commandFireTeam("ft1_lead", X, Z)
                    print("ft2 en route")
                    commandNotIssued =False
                    break
                else:
                    if xMove < 9700:
                        ft2predictedLethality = random.randint(0,int(ft2AmbushSiteNumber))
                    else:
                        print("here")
                        index = int(round( len(ft2LethalArray)/20))
                        print(index)
                        ft2predictedLethality = random.randint(index,(index+int(ft2AmbushSiteNumber)))
                        print(ft2predictedLethality)
                    break
                    
            

    global forestDict
    global elevationDict
    forestDict = FileIO.getForestFromTerrainFile('terrainType_db')
    elevationDict = FileIO.getElevationFromFile("elevation")
    Ft2KillPercentage = calculateKillPercentagesFt2()
    
   

    openTerrain2, closed2, neighbors2, DToPath2, ElevationChanged2 = getPositionDataAtAmbushFromFile('ft2AmbushOnly', ft2SentXLocation,ft2SentZLocation)
    saveToTrainingFile('ambushTraining_ft2', Ft2KillPercentage, openTerrain2, closed2, neighbors2, DToPath2, ElevationChanged2)
    print("Training Model Updated ft2")
    generateUpdatedLethality('ft2AmbushOnly', 9950, 16821, 9465, 16423)


def twoFireTeams():
    global model      
    global forestMap
    random.seed()
    commandNotIssued = True
    commandNotIssuedTWO = True
    model = loadNueralNetwork.loadModel()
    ft1leastLethality, ft1LethalArray = getPredictedLethalityFromFile('ft1Ambush')
    ft2leastLethality, ft2LethalArray = getPredictedLethalityFromFile('ft2Ambush')
    ft1AmbushSiteNumber=0
    if(forestMap):
        ft1AmbushSiteNumber = len(ft1LethalArray)*0.3
    else:
        ft1AmbushSiteNumber = len(ft1LethalArray)*.1
    #sorted array of lethalitys descending order
    #len/4
    ft1SentXLocation = 0
    ft1SentZLocation = 0
    ft2SentXLocation = 0
    ft2SentZLocation = 0
    ft1predictedLethality = random.randint(0,int(ft1AmbushSiteNumber))
    
    while  commandNotIssued and commandNotIssuedTWO:
        
        for X , Z in ft1leastLethality:
            lethality = ft1leastLethality[X,Z]
            ft1SentXLocation = X
            ft1SentZLocation = Z
            predLethal =0
            
            if forestMap:
                index = round(len(ft1LethalArray)/2)+ft1predictedLethality
                predLethal = ft1LethalArray[int(index)] 
            else:
                predLethal = ft1LethalArray[ft1predictedLethality]
            
            #print(str(X)+','+ str(Z)+','+str(round(lethality[0]))+','+ str(round(predLethal)))    
            
            #print(predLethal)
            if(predLethal== lethality[0]):
                print (str(X)+','+str(Z))
                if  forestMap == True and X > 9200 and X <9300 and Z <16174:
                    commandFireTeam("ft1_lead", X, Z)
                    print("ft1 en route")
                    commandNotIssued=False
                    
                    break
                  
                elif  forestMap == False and X < 9200 and X > 9000 and Z < 16372:
                    commandFireTeam("ft1_lead", X, Z)
                    commandFireTeam("ft2_lead", (X+5), Z)
                    print("ft1 en route")
                    commandNotIssued=False
                    break
                else: 
                    ft1predictedLethality = random.randint(0,int(ft1AmbushSiteNumber))
                    print(ft1predictedLethality)
                    break 
    while   commandNotIssuedTWO:
        ft1predictedLethality = random.randint(0,int(ft1AmbushSiteNumber))
        for X , Z in ft1leastLethality:
            lethality = ft1leastLethality[X,Z]
            ft1SentXLocation = X
            ft1SentZLocation = Z
            predLethal =0
            
            if forestMap:
                index = round(len(ft1LethalArray)/2)+ft1predictedLethality
                predLethal = ft1LethalArray[int(index)] 
            else:
                predLethal = ft1LethalArray[ft1predictedLethality]
            
            #print(str(X)+','+ str(Z)+','+str(round(lethality[0]))+','+ str(round(predLethal)))    
            
            #print(predLethal)
            if(predLethal== lethality[0]):
                print (str(X)+','+str(Z))
                if  forestMap == True and X > 9200 and X <9300 and Z <16174:
                    commandFireTeam("ft2_lead", (X+5), Z)
                    print("ft1 en route")
                    commandNotIssuedTWO=False
                    
                    break
                  
                elif  forestMap == False and X < 9200 and X > 9000 and Z < 16372:
                    commandFireTeam("ft1_lead", X, Z)
                    
                    print("ft1 en route")
                    commandNotIssuedTWO=False
                    break
                else: 
                    ft1predictedLethality = random.randint(0,int(ft1AmbushSiteNumber))
                    print(ft1predictedLethality)
                    break 
                
    ft2AmbushSiteNumber = len(ft2LethalArray)/10        
    ft2predictedLethality = random.randint(0,int(ft2AmbushSiteNumber))
    for X , Z in ft2leastLethality:
        lethality = ft2leastLethality[X,Z]
        ft2SentXLocation = X
        ft2SentZLocation = Z
        #print(lethality)
        if(ft2LethalArray[ft2predictedLethality] == lethality[0]):
            #commandFireTeam("ft2_lead", X, Z)
            print("ft2 en route")
    global forestDict
    global elevationDict
    forestDict = FileIO.getForestFromTerrainFile('terrainType_db')
    elevationDict = FileIO.getElevationFromFile("elevation")
    Ft1KillPercentage, Ft2KillPercentage = calculateKillPercentages()
    
    

    
    openTerrain, closed, neighbors, DToPath, ElevationChanged = getPositionDataAtAmbushFromFile('ft1Ambush', ft1SentXLocation,ft1SentZLocation)
    saveToTrainingFile('ambushTraining', Ft1KillPercentage, openTerrain, closed, neighbors, DToPath, ElevationChanged)
    print("Training Model Updated")
    generateUpdatedLethality('ft1Ambush', 9902, 16334, 9019, 16010)
    
    if(Ft2KillPercentage !=-1):
        openTerrain2, closed2, neighbors2, DToPath2, ElevationChanged2 = getPositionDataAtAmbushFromFile('ft2Ambush', ft2SentXLocation,ft2SentZLocation)
        saveToTrainingFile('ambushTraining', Ft2KillPercentage, openTerrain2, closed2, neighbors2, DToPath2, ElevationChanged2)
        print("Training Model Updated ft2")
        generateUpdatedLethality('ft2Ambush', 9950, 16821, 9465, 16423)

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10

def generateOpForceFt1Output():
    global forestDict
    global elevationDict
    global outputPathOp
    print("printing opfor data")
    opSol1 = database_connect.getOpforUnit("ft1_lead")
    opSol2 = database_connect.getOpforUnit("ft1_member")


    opfor = "ft1_lead"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_member") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
   
           

    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
       
       
    Elevation = elevationDict[roundup(float(opSol1[1])), roundup(float(opSol1[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol1[1], opSol1[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol1[1], opSol1[2]], [opSol2[1], opSol2[2]])


    saveToAgentDataFile(outputPathOp, opSol1[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType, 
                        greatestAngle, smallestAngle, opSol1[3], opSol1[4], opSol1[1], opSol1[2], ElevationDiff, Elevation, opSol1[0], 
                        PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])
       

    opfor = "ft1_member"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_lead") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  

           

    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
    
    
    Elevation = elevationDict[roundup(float(opSol2[1])), roundup(float(opSol2[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol2[1], opSol2[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol2[1], opSol2[2]], [opSol1[1], opSol1[2]])
    
    
    saveToAgentDataFile(outputPathOp, opSol2[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, opSol2[3], opSol2[4], opSol2[1], opSol2[2], ElevationDiff, Elevation, opSol2[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])


def generateOpForceFt2Output():  
    global forestDict
    global elevationDict
    global outputPathOp
    print("printing opfor data")

    opSol3 = database_connect.getOpforUnit("ft2_lead")
    opSol4 = database_connect.getOpforUnit("ft2_member")     
    
    
    opfor = "ft2_lead"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol4Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_member") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
    
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
    
    
    Elevation = elevationDict[roundup(float(opSol3[1])), roundup(float(opSol3[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol3[1], opSol3[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol3[1], opSol3[2]], [opSol4[1], opSol4[2]])
    
    
    saveToAgentDataFile(outputPathOp, opSol3[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, opSol3[3], opSol3[4], opSol3[1], opSol3[2], ElevationDiff, Elevation, opSol3[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])
    
    
    opfor = "ft2_member"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol4Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_lead") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
    
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
    
    
    Elevation = elevationDict[roundup(float(opSol4[1])), roundup(float(opSol4[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol4[1], opSol4[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol4[1], opSol4[2]], [opSol3[1], opSol3[2]])
    
    saveToAgentDataFile(outputPathOp, opSol4[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, opSol4[3], opSol4[4], opSol4[1], opSol4[2], ElevationDiff, Elevation, opSol4[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3] )
    
    
    

def generateOpForceOutput():
    global forestDict
    global elevationDict
    global outputPathOp
    print("printing opfor data")
    opSol1 = database_connect.getOpforUnit("ft1_lead")
    opSol2 = database_connect.getOpforUnit("ft1_member")
    opSol3 = database_connect.getOpforUnit("ft2_lead")
    opSol4 = database_connect.getOpforUnit("ft2_member")

    opfor = "ft1_lead"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_member") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_lead") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_member") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
           

    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
       
       
    Elevation = elevationDict[roundup(float(opSol1[1])), roundup(float(opSol1[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol1[1], opSol1[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol1[1], opSol1[2]], [opSol2[1], opSol2[2]])


    saveToAgentDataFile(outputPathOp, opSol1[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType, 
                        greatestAngle, smallestAngle, opSol1[3], opSol1[4], opSol1[1], opSol1[2], ElevationDiff, Elevation, opSol1[0], 
                        PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])
       

    opfor = "ft1_member"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_lead") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_lead") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_member") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
           

    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
    
    
    Elevation = elevationDict[roundup(float(opSol2[1])), roundup(float(opSol2[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol2[1], opSol2[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol2[1], opSol2[2]], [opSol1[1], opSol1[2]])
    
    
    saveToAgentDataFile(outputPathOp, opSol2[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, opSol2[3], opSol2[4], opSol2[1], opSol2[2], ElevationDiff, Elevation, opSol2[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])

       

    opfor = "ft2_lead"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_member") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_lead") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_member") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
    
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
    
    
    Elevation = elevationDict[roundup(float(opSol3[1])), roundup(float(opSol3[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol3[1], opSol3[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol3[1], opSol3[2]], [opSol4[1], opSol4[2]])
    
    
    saveToAgentDataFile(outputPathOp, opSol3[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, opSol3[3], opSol3[4], opSol3[1], opSol3[2], ElevationDiff, Elevation, opSol3[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])
    
    
    opfor = "ft2_member"   
    DNA = StateSpaceCalc.distanceToNearestOpForAlly(opfor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opfor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_member") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft1_lead") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfOpForAlly(opfor, "ft2_lead") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
    
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier1") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier2") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldier3") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemy(opfor, "Soldiergunner") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
    
    
    Elevation = elevationDict[roundup(float(opSol4[1])), roundup(float(opSol4[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestOpForEnemy(opfor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestOpForEnemyLocation(opfor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtOpForLocation(opfor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([opSol4[1], opSol4[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.OpForAnglesOfAttack([opSol4[1], opSol4[2]], [opSol3[1], opSol3[2]])
    
    saveToAgentDataFile(outputPathOp, opSol4[5], opfor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, opSol4[3], opSol4[4], opSol4[1], opSol4[2], ElevationDiff, Elevation, opSol4[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3] )
    
    
    




def generateBlueForceOutput():
    global forestDict
    global elevationDict
    global outputPathBlue
    blueSol1 = database_connect.getBlueforUnit("Soldier1")
    blueSol2 = database_connect.getBlueforUnit("Soldier2")
    blueSol3 = database_connect.getBlueforUnit("Soldier3")
    blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
    print("printing bluefor data")

    bluefor = "Soldier1"   
    DNA = StateSpaceCalc.distanceToNearestBlueForAlly(bluefor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestBlueForEnemyandType(bluefor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier2") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier3") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldiergunner") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
    
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_lead") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_member") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_lead") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_member") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)   
    
    
    Elevation = elevationDict[roundup(float(blueSol1[1])), roundup(float(blueSol1[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestBlueForEnemy(bluefor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestBlueForEnemyLocation(bluefor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtBlueForLocation(bluefor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([blueSol1[1], blueSol1[2]], forestDict)
    
    greatestAngle, smallestAngle = StateSpaceCalc.BlueForAnglesOfAttack([blueSol1[1], blueSol1[2]], [blueSol2[1], blueSol2[2]])
    
    
    saveToAgentDataFileBlue(outputPathBlue, blueSol1[5], bluefor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, blueSol1[3], blueSol1[4], blueSol1[1], blueSol1[2], ElevationDiff, Elevation, blueSol1[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3] )
    
    
    bluefor = "Soldier2"   
    DNA = StateSpaceCalc.distanceToNearestBlueForAlly(bluefor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestBlueForEnemyandType(bluefor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier1") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier3") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldiergunner") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
        
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_lead") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_member") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_lead") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_member") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)     
        
    Elevation = elevationDict[roundup(float(blueSol2[1])), roundup(float(blueSol2[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestBlueForEnemy(bluefor,elevationDict)
    
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestBlueForEnemyLocation(bluefor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtBlueForLocation(bluefor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([blueSol2[1], blueSol2[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.BlueForAnglesOfAttack([blueSol2[1], blueSol2[2]], [blueSol3[1], blueSol3[2]])
    
    saveToAgentDataFileBlue(outputPathBlue, blueSol2[5], bluefor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, blueSol2[3], blueSol2[4], blueSol2[1], blueSol2[2], ElevationDiff, Elevation, blueSol2[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])
    
    
    
    bluefor = "Soldier3"   
    DNA = StateSpaceCalc.distanceToNearestBlueForAlly(bluefor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestBlueForEnemyandType(bluefor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier1") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier2") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldiergunner") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
        
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_lead") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_member") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_lead") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_member") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector) 
        
    Elevation = elevationDict[roundup(float(blueSol3[1])), roundup(float(blueSol3[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestBlueForEnemy(bluefor,elevationDict)
    
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestBlueForEnemyLocation(bluefor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtBlueForLocation(bluefor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([blueSol3[1], blueSol3[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.BlueForAnglesOfAttack([blueSol3[1], blueSol3[2]], [blueSol1[1], blueSol1[2]])
    
    
    saveToAgentDataFileBlue(outputPathBlue, blueSol3[5], bluefor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, blueSol3[3], blueSol3[4], blueSol3[1], blueSol3[2], ElevationDiff, Elevation, blueSol3[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])
    
    
    
    bluefor = "Soldiergunner"   
    DNA = StateSpaceCalc.distanceToNearestBlueForAlly(bluefor)  
    DNE, NearestEType = StateSpaceCalc.distanceBetweenNearestBlueForEnemyandType(bluefor) 
    AllySectors = []
    Sol2Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier1") 
    if(Sol2Sector != -1):
        AllySectors.append(Sol2Sector)  
    Sol3Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier2") 
    if(Sol3Sector != -1):
        AllySectors.append(Sol3Sector) 
    Sol4Sector = ReadTerrainFile.sectorOfBlueForAlly(bluefor, "Soldier3") 
    if(Sol4Sector != -1):
        AllySectors.append(Sol4Sector)   
        
        
    EnemySectors = []
    Enemy1Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_lead") 
    if(Enemy1Sector != -1):
        EnemySectors.append(Enemy1Sector)  
    Enemy2Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft1_member") 
    if(Enemy2Sector != -1):
        EnemySectors.append(Enemy2Sector) 
    Enemy3Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_lead") 
    if(Enemy3Sector != -1):
        EnemySectors.append(Enemy3Sector)  
    Enemy4Sector = ReadTerrainFile.sectorOfBlueForEnemy(bluefor, "ft2_member") 
    if(Enemy4Sector != -1):
        EnemySectors.append(Enemy4Sector)               
    Elevation = elevationDict[roundup(float(blueSol4[1])), roundup(float(blueSol4[2]))]            
    ElevationDiff = StateSpaceCalc.elevationDifFromNearestBlueForEnemy(bluefor,elevationDict)
    PercentForestAtEnemy = StateSpaceCalc.getForestAtNearestBlueForEnemyLocation(bluefor, forestDict)
    PercentForestAtSol = StateSpaceCalc.getForestAtBlueForLocation(bluefor, forestDict)
    PercentForestAtSector = ReadTerrainFile.percentForestAtSector([blueSol4[1], blueSol4[2]], forestDict)
    greatestAngle, smallestAngle = StateSpaceCalc.BlueForAnglesOfAttack([blueSol4[1], blueSol4[2]], [blueSol2[1], blueSol2[2]])
    
    saveToAgentDataFileBlue(outputPathBlue, blueSol4[5], bluefor, DNA , DNE, AllySectors, EnemySectors, NearestEType,
                 greatestAngle, smallestAngle, blueSol4[3], blueSol4[4], blueSol4[1], blueSol4[2], ElevationDiff, Elevation, blueSol4[0],
                  PercentForestAtEnemy, PercentForestAtSol, PercentForestAtSector[0], PercentForestAtSector[1], PercentForestAtSector[2], PercentForestAtSector[3])





def randomMovement(input, offset):
    return round(random.uniform(-offset, offset) + input)


def ft1Move():
    global forestDict
    global elevationDict
    global model
    model.eval()
    dtype = torch.float
    device = torch.device("cpu")
    opSol1 = database_connect.getOpforUnit("ft1_lead")
    opSol2 = database_connect.getOpforUnit("ft1_member")

    opforlead = "ft1_lead"  
    opformember = "ft1_member"  

    DNEft_lead, NearestETypeft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opforlead)   
    DNEft_member, NearestETypeft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opformember) 
    ft_leadX, ft_leadZ = float(opSol1[1]), float(opSol1[2])
    ft_memberX, ft_memberZ = float(opSol2[1]), float(opSol2[2])
    ft_leadHP, ft_memberHP = float(opSol1[0]), float(opSol2[0])
    
    if(DNEft_lead <= 150 or DNEft_member <= 150):
        ft_leadXZ = {}
        ft_memberXZ ={}
        for i in range(0,30):
            newft_leadX = randomMovement(ft_leadX, 5)
            newft_leadZ = randomMovement(ft_leadZ, 5)
            newft_memberX = randomMovement(ft_memberX, 5)
            newft_memberZ = randomMovement(ft_memberZ, 5)
            if(ft_leadHP <= 0.99):
                DNAft_lead = -1
                AllySectorft_lead = -1
                greatestAngleft_lead, smallestAngleft_lead = -1, -1
                
                if(ft_memberHP <= 0.99):
                    DNAft_lead = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_lead = ReadTerrainFile.sectorOfOpForAllyPos([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])     
                    greatestAngleft_lead, smallestAngleft_lead = StateSpaceCalc.OpForAnglesOfAttack([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])
                
                EnemySectorft_lead = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_lead.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_lead.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_lead.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_lead.append(Enemy4Sector)   
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_lead:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
                
                
                
                ftEnemyType = 0
                if(NearestETypeft_lead != "Rifleman"):
                    ftEnemyType = 1
                newDNEft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_leadX, newft_leadZ],opforlead)  
                DNEft_lead =  newDNEft_lead
                Elevationft_lead = elevationDict[roundup(newft_leadX), roundup(newft_leadZ)]            
                ElevationDiff_ft_lead = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_leadX, newft_leadZ],elevationDict)
                PercentForestAtEnemyft_lead = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSolft_lead = StateSpaceCalc.getForestAtOpForPosLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSectorft_lead = ReadTerrainFile.percentForestAtSector([newft_leadX, newft_leadZ], forestDict)
                #predict outcome 
                ftlead_input = np.array([[round(DNAft_lead), round(DNEft_lead),
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_lead,1), round(smallestAngleft_lead,1), round(ElevationDiff_ft_lead,1), round(Elevationft_lead),
                                 round(PercentForestAtEnemyft_lead[0],1), round(PercentForestAtSolft_lead[0],1), 
                                 round(PercentForestAtSectorft_lead[0],2), round(PercentForestAtSectorft_lead[1],2),
                                 round(PercentForestAtSectorft_lead[2],2), round(PercentForestAtSectorft_lead[3],2)]])
                inputNodes = torch.tensor(ftlead_input,device=device, dtype=dtype)
                outputPrediction = model(inputNodes)
                if(newft_leadX, newft_leadZ) in ft_leadXZ:
                    temp=ft_leadXZ[(newft_leadX, newft_leadZ) ]
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                    ft_leadXZ[(newft_leadX, newft_leadZ) ]=temp
                else:
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[float(str(outputPrediction[0].item()))]
                    else:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[-1]
                
            if(ft_memberHP <= 0.99):
                DNAft_member = -1
                AllySectorft_member = -1
                greatestAngleft_member, smallestAngleft_member = -1, -1
                
                if(ft_leadHP <= 0.99):
                    DNAft_member = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_member = ReadTerrainFile.sectorOfOpForAllyPos([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])     
                    greatestAngleft_member, smallestAngleft_member = StateSpaceCalc.OpForAnglesOfAttack([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])
                
                EnemySectorft_member = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_member.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_member.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_member.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_member.append(Enemy4Sector)  
                ftEnemyType = 0
                if(NearestETypeft_member != "Rifleman"):
                    ftEnemyType = 1 
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_member:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
       
                newDNEft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_memberX, newft_memberZ], opformember)  
                DNEft_member =  newDNEft_member
                Elevationft_member = elevationDict[roundup(newft_memberX), roundup(newft_memberZ)]            
                ElevationDiff_ft_member = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_memberX, newft_memberZ],elevationDict)
                PercentForestAtEnemyft_member = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSolft_member = StateSpaceCalc.getForestAtOpForPosLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSectorft_member = ReadTerrainFile.percentForestAtSector([newft_memberX, newft_memberZ], forestDict)
                #predict outcome 
                #predict outcome 
                ftmember_input = np.array([[round(DNAft_member), round(DNEft_member),
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_member,1), round(smallestAngleft_member,1), round(ElevationDiff_ft_member,1), round(Elevationft_member),
                                 round(PercentForestAtEnemyft_member[0],1), round(PercentForestAtSolft_member[0],1), 
                                 round(PercentForestAtSectorft_member[0],2), round(PercentForestAtSectorft_member[1],2),
                                 round(PercentForestAtSectorft_member[2],2), round(PercentForestAtSectorft_member[3],2)]])
                inputNodes = torch.tensor(ftmember_input,device=device, dtype=dtype)
                outputPrediction = model(inputNodes)
                if(newft_memberX, newft_memberZ) in ft_memberXZ:
                    temp=ft_memberXZ[(newft_memberX, newft_memberZ) ]
                    if  DNEft_member <=150:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=temp
                    #print(DNEft_member)
                else:
                    if  DNEft_member <=150:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[float(str(outputPrediction[0].item()))]
                        #print(ft_leadXZ)
                    else:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[-1]
                
        ft_leadBestXZ =""
        ft_memberBestXZ =""
        leadBest =-1
        memberBest=-1
        for key,value in ft_leadXZ.items():
            if(len(ft_leadXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    leadBest = avgBest
                    ft_leadBestXZ = key
                
        for key,value in ft_memberXZ.items():
            if(len(ft_memberXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    memberBest = avgBest
                    ft_memberBestXZ = key
            #using the ft_BestXZ give command to move
        if(len(ft_leadBestXZ) > 1):
            leadMoveString = "'" + str(ft_leadBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_leadBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opforlead, leadMoveString)
            print("Repositioning Opfor")
        if(len(ft_memberBestXZ) > 1):
            memberMoveString = "'" + str(ft_memberBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_memberBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opformember, memberMoveString)
            print("Repositioning Opfor")

def ft2Move():
    global forestDict
    global elevationDict
    global model
    model.eval()
    dtype = torch.float
    device = torch.device("cpu")
    opSol3 = database_connect.getOpforUnit("ft2_lead")
    opSol4 = database_connect.getOpforUnit("ft2_member")
    
    opforlead = "ft2_lead"  
    opformember = "ft2_member"  

    DNEft_lead, NearestETypeft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opforlead)   
    DNEft_member, NearestETypeft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opformember) 
    ft_leadX, ft_leadZ = float(opSol3[1]), float(opSol3[2])
    ft_memberX, ft_memberZ = float(opSol4[1]), float(opSol4[2])
    ft_leadHP, ft_memberHP = float(opSol3[0]), float(opSol4[0])
    
    if(DNEft_lead <= 150 or DNEft_member <= 150):
        ft_leadXZ = {}
        ft_memberXZ ={}
        for i in range(0,30):
            newft_leadX = randomMovement(ft_leadX, 5)
            newft_leadZ = randomMovement(ft_leadZ, 5)
            newft_memberX = randomMovement(ft_memberX, 5)
            newft_memberZ = randomMovement(ft_memberZ, 5)
            #print(newft_leadX, newft_leadZ)
            #print(newft_memberX, newft_memberZ)
            if(ft_leadHP <= 0.99):
                DNAft_lead = -1
                AllySectorft_lead = -1
                greatestAngleft_lead, smallestAngleft_lead = -1, -1
                
                if(ft_memberHP <= 0.99):
                    DNAft_lead = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_lead = ReadTerrainFile.sectorOfOpForAllyPos([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])     
                    greatestAngleft_lead, smallestAngleft_lead = StateSpaceCalc.OpForAnglesOfAttack([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])
                
                EnemySectorft_lead = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_lead.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_lead.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_lead.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_lead.append(Enemy4Sector)   
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_lead:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
       
                ftEnemyType = 0
                if(NearestETypeft_lead != "Rifleman"):
                    ftEnemyType = 1
                
                newDNEft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_leadX, newft_leadZ], opforlead)  
                DNEft_lead =  newDNEft_lead
                Elevationft_lead = elevationDict[roundup(newft_leadX), roundup(newft_leadZ)]            
                ElevationDiff_ft_lead = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_leadX, newft_leadZ],elevationDict)
                PercentForestAtEnemyft_lead = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSolft_lead = StateSpaceCalc.getForestAtOpForPosLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSectorft_lead = ReadTerrainFile.percentForestAtSector([newft_leadX, newft_leadZ], forestDict)
                #predict outcome 
                ftlead_input = np.array([[round(DNAft_lead), round(DNEft_lead),
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_lead,1), round(smallestAngleft_lead,1), round(ElevationDiff_ft_lead,1), round(Elevationft_lead),
                                 round(PercentForestAtEnemyft_lead[0],1), round(PercentForestAtSolft_lead[0],1), 
                                 round(PercentForestAtSectorft_lead[0],2), round(PercentForestAtSectorft_lead[1],2),
                                 round(PercentForestAtSectorft_lead[2],2), round(PercentForestAtSectorft_lead[3],2)]])
                inputNodes = torch.tensor(ftlead_input,device=device, dtype=dtype)
                outputPrediction = model(inputNodes)
                if(newft_leadX, newft_leadZ) in ft_leadXZ:
                    temp=ft_leadXZ[(newft_leadX, newft_leadZ)]
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                    ft_leadXZ[(newft_leadX, newft_leadZ) ]=temp
                else:
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[float(str(outputPrediction[0].item()))]
                    else:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[-1]
                
            if(ft_memberHP <= 0.99):
                DNAft_member = -1
                AllySectorft_member = -1
                greatestAngleft_member, smallestAngleft_member = -1, -1
                
                if(ft_leadHP <= 0.99):
                    DNAft_member = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_member = ReadTerrainFile.sectorOfOpForAllyPos([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])     
                    greatestAngleft_member, smallestAngleft_member = StateSpaceCalc.OpForAnglesOfAttack([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])
                
                EnemySectorft_member = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_member.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_member.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_member.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_member.append(Enemy4Sector)  
                ftEnemyType = 0
                if(NearestETypeft_member != "Rifleman"):
                    ftEnemyType = 1 
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_member:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
       
                newDNEft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_memberX, newft_memberZ], opformember)  
                DNEft_member =  newDNEft_member
                Elevationft_member = elevationDict[roundup(newft_memberX), roundup(newft_memberZ)]            
                ElevationDiff_ft_member = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_memberX, newft_memberZ],elevationDict)
                PercentForestAtEnemyft_member = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSolft_member = StateSpaceCalc.getForestAtOpForPosLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSectorft_member = ReadTerrainFile.percentForestAtSector([newft_memberX, newft_memberZ], forestDict)
                #predict outcome 
                #predict outcome 
                ftmember_input = np.array([[round(DNAft_member), round(DNEft_member), 
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_member,1), round(smallestAngleft_member,1), round(ElevationDiff_ft_member,1), round(Elevationft_member),
                                 round(PercentForestAtEnemyft_member[0],1), round(PercentForestAtSolft_member[0],1), 
                                 round(PercentForestAtSectorft_member[0],2), round(PercentForestAtSectorft_member[1],2),
                                 round(PercentForestAtSectorft_member[2],2), round(PercentForestAtSectorft_member[3],2)]])
                inputNodes = torch.tensor(ftmember_input,device=device, dtype=dtype)
                #print(inputNodes.size())
                #print(model)
                outputPrediction = model(inputNodes)
                if(newft_memberX, newft_memberZ) in ft_memberXZ:
                    temp=ft_memberXZ[(newft_memberX, newft_memberZ) ]
                    if  DNEft_member <=150  and DNEft_member >=0:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                    ft_memberXZ[(newft_memberX, newft_memberZ) ]=temp
                else:
                    if  DNEft_member <=150 and DNEft_member >=0:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[float(str(outputPrediction[0].item()))]
                    else:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[-1]
    
    
    
        ft_leadBestXZ =""
        ft_memberBestXZ =""
        leadBest =-1
        memberBest=-1
        for key,value in ft_leadXZ.items():
            if(len(ft_leadXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    leadBest = avgBest
                    ft_leadBestXZ = key
                
        for key,value in ft_memberXZ.items():
            if(len(ft_memberXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    memberBest = avgBest
                    ft_memberBestXZ = key
            #using the ft_BestXZ give command to move
        if(len(ft_leadBestXZ) > 1):
            leadMoveString = "'" + str(ft_leadBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_leadBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opforlead, leadMoveString)
            print("Repositioning Opfor")
        if(len(ft_memberBestXZ) > 1):
            memberMoveString = "'" + str(ft_memberBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_memberBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opformember, memberMoveString)
            print("Repositioning Opfor")
    
def opforMove():
    global forestDict
    global elevationDict
    global model
    model.eval()
    dtype = torch.float
    device = torch.device("cpu")
    opSol1 = database_connect.getOpforUnit("ft1_lead")
    opSol2 = database_connect.getOpforUnit("ft1_member")
    opSol3 = database_connect.getOpforUnit("ft2_lead")
    opSol4 = database_connect.getOpforUnit("ft2_member")

    opforlead = "ft1_lead"  
    opformember = "ft1_member"  

    DNEft_lead, NearestETypeft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opforlead)   
    DNEft_member, NearestETypeft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opformember) 
    ft_leadX, ft_leadZ = float(opSol1[1]), float(opSol1[2])
    ft_memberX, ft_memberZ = float(opSol2[1]), float(opSol2[2])
    ft_leadHP, ft_memberHP = float(opSol1[0]), float(opSol2[0])
    
    if(DNEft_lead <= 150 or DNEft_member <= 150):
        ft_leadXZ = {}
        ft_memberXZ ={}
        for i in range(0,30):
            newft_leadX = randomMovement(ft_leadX, 5)
            newft_leadZ = randomMovement(ft_leadZ, 5)
            newft_memberX = randomMovement(ft_memberX, 5)
            newft_memberZ = randomMovement(ft_memberZ, 5)
            if(ft_leadHP <= 0.99):
                DNAft_lead = -1
                AllySectorft_lead = -1
                greatestAngleft_lead, smallestAngleft_lead = -1, -1
                
                if(ft_memberHP <= 0.99):
                    DNAft_lead = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_lead = ReadTerrainFile.sectorOfOpForAllyPos([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])     
                    greatestAngleft_lead, smallestAngleft_lead = StateSpaceCalc.OpForAnglesOfAttack([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])
                
                EnemySectorft_lead = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_lead.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_lead.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_lead.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_lead.append(Enemy4Sector)   
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_lead:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
                
                
                
                ftEnemyType = 0
                if(NearestETypeft_lead != "Rifleman"):
                    ftEnemyType = 1
                newDNEft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_leadX, newft_leadZ],opforlead)  
                DNEft_lead =  newDNEft_lead
                Elevationft_lead = elevationDict[roundup(newft_leadX), roundup(newft_leadZ)]            
                ElevationDiff_ft_lead = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_leadX, newft_leadZ],elevationDict)
                PercentForestAtEnemyft_lead = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSolft_lead = StateSpaceCalc.getForestAtOpForPosLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSectorft_lead = ReadTerrainFile.percentForestAtSector([newft_leadX, newft_leadZ], forestDict)
                #predict outcome 
                ftlead_input = np.array([[round(DNAft_lead), round(DNEft_lead),
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_lead,1), round(smallestAngleft_lead,1), round(ElevationDiff_ft_lead,1), round(Elevationft_lead),
                                 round(PercentForestAtEnemyft_lead[0],1), round(PercentForestAtSolft_lead[0],1), 
                                 round(PercentForestAtSectorft_lead[0],2), round(PercentForestAtSectorft_lead[1],2),
                                 round(PercentForestAtSectorft_lead[2],2), round(PercentForestAtSectorft_lead[3],2)]])
                inputNodes = torch.tensor(ftlead_input,device=device, dtype=dtype)
                outputPrediction = model(inputNodes)
                if(newft_leadX, newft_leadZ) in ft_leadXZ:
                    temp=ft_leadXZ[(newft_leadX, newft_leadZ) ]
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                    ft_leadXZ[(newft_leadX, newft_leadZ) ]=temp
                else:
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[float(str(outputPrediction[0].item()))]
                    else:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[-1]
                
            if(ft_memberHP <= 0.99):
                DNAft_member = -1
                AllySectorft_member = -1
                greatestAngleft_member, smallestAngleft_member = -1, -1
                
                if(ft_leadHP <= 0.99):
                    DNAft_member = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_member = ReadTerrainFile.sectorOfOpForAllyPos([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])     
                    greatestAngleft_member, smallestAngleft_member = StateSpaceCalc.OpForAnglesOfAttack([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])
                
                EnemySectorft_member = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_member.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_member.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_member.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_member.append(Enemy4Sector)  
                ftEnemyType = 0
                if(NearestETypeft_member != "Rifleman"):
                    ftEnemyType = 1 
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_member:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
       
                newDNEft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_memberX, newft_memberZ], opformember)  
                DNEft_member =  newDNEft_member
                Elevationft_member = elevationDict[roundup(newft_memberX), roundup(newft_memberZ)]            
                ElevationDiff_ft_member = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_memberX, newft_memberZ],elevationDict)
                PercentForestAtEnemyft_member = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSolft_member = StateSpaceCalc.getForestAtOpForPosLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSectorft_member = ReadTerrainFile.percentForestAtSector([newft_memberX, newft_memberZ], forestDict)
                #predict outcome 
                #predict outcome 
                ftmember_input = np.array([[round(DNAft_member), round(DNEft_member),
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_member,1), round(smallestAngleft_member,1), round(ElevationDiff_ft_member,1), round(Elevationft_member),
                                 round(PercentForestAtEnemyft_member[0],1), round(PercentForestAtSolft_member[0],1), 
                                 round(PercentForestAtSectorft_member[0],2), round(PercentForestAtSectorft_member[1],2),
                                 round(PercentForestAtSectorft_member[2],2), round(PercentForestAtSectorft_member[3],2)]])
                inputNodes = torch.tensor(ftmember_input,device=device, dtype=dtype)
                outputPrediction = model(inputNodes)
                if(newft_memberX, newft_memberZ) in ft_memberXZ:
                    temp=ft_memberXZ[(newft_memberX, newft_memberZ) ]
                    if  DNEft_member <=150  and DNEft_member >=0:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                    ft_memberXZ[(newft_memberX, newft_memberZ) ]=temp
                else:
                    if  DNEft_member <=150 and DNEft_member >=0:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[float(str(outputPrediction[0].item()))]
                    else:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[-1]
                
        ft_leadBestXZ =""
        ft_memberBestXZ =""
        leadBest =-1
        memberBest=-1
        for key,value in ft_leadXZ.items():
            if(len(ft_leadXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    leadBest = avgBest
                    ft_leadBestXZ = key
                
        for key,value in ft_memberXZ.items():
            if(len(ft_memberXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    memberBest = avgBest
                    ft_memberBestXZ = key
            #using the ft_BestXZ give command to move
        if(len(ft_leadBestXZ) > 1):
            leadMoveString = "'" + str(ft_leadBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_leadBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opforlead, leadMoveString)
            print("Repositioning Opfor")
        if(len(ft_memberBestXZ) > 1):
            memberMoveString = "'" + str(ft_memberBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_memberBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opformember, memberMoveString)
            print("Repositioning Opfor")
    opforlead = "ft2_lead"  
    opformember = "ft2_member"  

    DNEft_lead, NearestETypeft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opforlead)   
    DNEft_member, NearestETypeft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyandType(opformember) 
    ft_leadX, ft_leadZ = float(opSol3[1]), float(opSol3[2])
    ft_memberX, ft_memberZ = float(opSol4[1]), float(opSol4[2])
    ft_leadHP, ft_memberHP = float(opSol3[0]), float(opSol4[0])
    
    if(DNEft_lead <= 150 or DNEft_member <= 150):
        ft_leadXZ = {}
        ft_memberXZ ={}
        for i in range(0,30):
            newft_leadX = randomMovement(ft_leadX, 5)
            newft_leadZ = randomMovement(ft_leadZ, 5)
            newft_memberX = randomMovement(ft_memberX, 5)
            newft_memberZ = randomMovement(ft_memberZ, 5)
            if(ft_leadHP <= 0.99):
                DNAft_lead = -1
                AllySectorft_lead = -1
                greatestAngleft_lead, smallestAngleft_lead = -1, -1
                
                if(ft_memberHP <= 0.99):
                    DNAft_lead = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_lead = ReadTerrainFile.sectorOfOpForAllyPos([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])     
                    greatestAngleft_lead, smallestAngleft_lead = StateSpaceCalc.OpForAnglesOfAttack([newft_leadX, newft_leadZ], [newft_memberX, newft_memberZ])
                
                EnemySectorft_lead = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_lead.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_lead.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_lead.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_leadX, newft_leadZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_lead.append(Enemy4Sector)   
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_lead:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
       
                ftEnemyType = 0
                if(NearestETypeft_lead != "Rifleman"):
                    ftEnemyType = 1
                
                newDNEft_lead = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_leadX, newft_leadZ], opforlead)  
                DNEft_lead =  newDNEft_lead
                Elevationft_lead = elevationDict[roundup(newft_leadX), roundup(newft_leadZ)]            
                ElevationDiff_ft_lead = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_leadX, newft_leadZ],elevationDict)
                PercentForestAtEnemyft_lead = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSolft_lead = StateSpaceCalc.getForestAtOpForPosLocation([newft_leadX, newft_leadZ], forestDict)
                PercentForestAtSectorft_lead = ReadTerrainFile.percentForestAtSector([newft_leadX, newft_leadZ], forestDict)
                #predict outcome 
                ftlead_input = np.array([[round(DNAft_lead), round(DNEft_lead),
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_lead,1), round(smallestAngleft_lead,1), round(ElevationDiff_ft_lead,1), round(Elevationft_lead),
                                 round(PercentForestAtEnemyft_lead[0],1), round(PercentForestAtSolft_lead[0],1), 
                                 round(PercentForestAtSectorft_lead[0],2), round(PercentForestAtSectorft_lead[1],2),
                                 round(PercentForestAtSectorft_lead[2],2), round(PercentForestAtSectorft_lead[3],2)]])
                inputNodes = torch.tensor(ftlead_input,device=device, dtype=dtype)
                #print(inputNodes.size())
                outputPrediction = model(inputNodes)
                if(newft_leadX, newft_leadZ) in ft_leadXZ:
                    temp=ft_leadXZ[(newft_leadX, newft_leadZ) ]
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                    ft_leadXZ[(newft_leadX, newft_leadZ) ]=temp
                else:
                    if  DNEft_lead <=150 and DNEft_lead >=0:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[float(str(outputPrediction[0].item()))]
                    else:
                        ft_leadXZ[(newft_leadX, newft_leadZ) ]=[-1]
                
            if(ft_memberHP <= 0.99):
                DNAft_member = -1
                AllySectorft_member = -1
                greatestAngleft_member, smallestAngleft_member = -1, -1
                
                if(ft_leadHP <= 0.99):
                    DNAft_member = StateSpaceCalc.distanceBetweenPoints(newft_leadX,newft_leadZ, newft_memberX, newft_memberZ) 
                    AllySectorft_member = ReadTerrainFile.sectorOfOpForAllyPos([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])     
                    greatestAngleft_member, smallestAngleft_member = StateSpaceCalc.OpForAnglesOfAttack([newft_memberX, newft_memberZ], [newft_leadX, newft_leadZ])
                
                EnemySectorft_member = []
                Enemy1Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier1") 
                if(Enemy1Sector != -1):
                    EnemySectorft_member.append(Enemy1Sector)  
                Enemy2Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier2") 
                if(Enemy2Sector != -1):
                    EnemySectorft_member.append(Enemy2Sector) 
                Enemy3Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldier3") 
                if(Enemy3Sector != -1):
                    EnemySectorft_member.append(Enemy3Sector)  
                Enemy4Sector = ReadTerrainFile.sectorOfOpForEnemyPos([newft_memberX, newft_memberZ], "Soldiergunner") 
                if(Enemy4Sector != -1):
                    EnemySectorft_member.append(Enemy4Sector)  
                ftEnemyType = 0
                if(NearestETypeft_member != "Rifleman"):
                    ftEnemyType = 1 
    
                numEnmSectNorth =0
                numEnmSectEast =0
                numEnmSectSouth =0
                numEnmSectWest =0
                for sect in EnemySectorft_member:
                    if sect =='1':
                        numEnmSectNorth+=1
                    elif sect =='2':
                        numEnmSectEast+=1
                    elif sect =='3':
                        numEnmSectSouth+=1
                    elif sect =='4':
                        numEnmSectWest+=1
       
                newDNEft_member = StateSpaceCalc.distanceBetweenNearestOpForEnemyWPos([newft_memberX, newft_memberZ], opformember)  
                DNEft_member =  newDNEft_member
                Elevationft_member = elevationDict[roundup(newft_memberX), roundup(newft_memberZ)]            
                ElevationDiff_ft_member = StateSpaceCalc.elevationDifFromNearestOpForEnemyPos([newft_memberX, newft_memberZ],elevationDict)
                PercentForestAtEnemyft_member = StateSpaceCalc.getForestAtNearestOpForPosEnemyLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSolft_member = StateSpaceCalc.getForestAtOpForPosLocation([newft_memberX, newft_memberZ], forestDict)
                PercentForestAtSectorft_member = ReadTerrainFile.percentForestAtSector([newft_memberX, newft_memberZ], forestDict)
                #predict outcome 
                #predict outcome 
                ftmember_input = np.array([[round(DNAft_member), round(DNEft_member), 
                                 numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest, ftEnemyType, 
                                 round(greatestAngleft_member,1), round(smallestAngleft_member,1), round(ElevationDiff_ft_member,1), round(Elevationft_member),
                                 round(PercentForestAtEnemyft_member[0],1), round(PercentForestAtSolft_member[0],1), 
                                 round(PercentForestAtSectorft_member[0],2), round(PercentForestAtSectorft_member[1],2),
                                 round(PercentForestAtSectorft_member[2],2), round(PercentForestAtSectorft_member[3],2)]])
                inputNodes = torch.tensor(ftmember_input,device=device, dtype=dtype)
                #print(inputNodes.size())
                #print(model)
                outputPrediction = model(inputNodes)
                if(newft_memberX, newft_memberZ) in ft_memberXZ:
                    temp=ft_memberXZ[(newft_memberX, newft_memberZ) ]
                    if  DNEft_member <=150  and DNEft_member >=0:
                        temp.append(float(str(outputPrediction[0].item())))
                    else:
                        temp.append(-1)
                    ft_memberXZ[(newft_memberX, newft_memberZ) ]=temp
                else:
                    if  DNEft_member <=150 and DNEft_member >=0:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[float(str(outputPrediction[0].item()))]
                    else:
                        ft_memberXZ[(newft_memberX, newft_memberZ) ]=[-1]
    
    
    
        ft_leadBestXZ =""
        ft_memberBestXZ =""
        leadBest =-1
        memberBest=-1
        for key,value in ft_leadXZ.items():
            if(len(ft_leadXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    leadBest = avgBest
                    ft_leadBestXZ = key
                
        for key,value in ft_memberXZ.items():
            if(len(ft_memberXZ) > 0):
                avgBest = sum(value) / len(value)
                if(avgBest > leadBest):
                    memberBest = avgBest
                    ft_memberBestXZ = key
            #using the ft_BestXZ give command to move
        if(len(ft_leadBestXZ) > 1):
            leadMoveString = "'" + str(ft_leadBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_leadBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opforlead, leadMoveString)
            print("Repositioning Opfor")
        if(len(ft_memberBestXZ) > 1):
            memberMoveString = "'" + str(ft_memberBestXZ[0]) +  ";" + "3.9" + ";" + str(ft_memberBestXZ[1]) + "'"
            database_connect.soldierMoveCommand(opformember, memberMoveString)
            print("Repositioning Opfor")
       
def calculateKillPercentagesFt2():    
    Count = 0 
    ft2kills = []  
    BlueForceRemaining = 4
    Ft2Killed = 0
    Ft2KillPercentage = 0
    while(True):
        Count +=1
        #read blueforceposition table and opforposition table 
        #check if blueforce is close to ft1  
        # if close check if any blueforce units are dead
        # amount of killed/4 
        #if ft1 is dead 
        #check if blueforce is close to ft2   
        # if close check if any blueforce units are dead
        # amount of killed/amount remaining  
        sol1Killed = False      
        sol2Killed = False  
        sol3Killed = False  
        sol4Killed = False     
        EnemyUnit = ""     
        ft2lead = database_connect.getOpforUnit("ft2_lead")
        ft2member = database_connect.getOpforUnit("ft2_member")
        if(float(ft2lead[0]) < 1 or float(ft2member[0]) < 1):
            distanceFromFt2 = distanceBetweenUnits("ft2_lead", "Soldier1")
            if(distanceFromFt2 <= 200):
                blueSol1 = database_connect.getBlueforUnit("Soldier1")            
                if(float(blueSol1[0]) > 0.99 and 1 not in ft2kills):
                    Ft2Killed+=1
                    ft2kills.append(1)
                    sol1Killed = True
                blueSol2 = database_connect.getBlueforUnit("Soldier2")
                if(float(blueSol2[0]) > 0.99 and 2 not in ft2kills):
                    Ft2Killed+=1
                    ft2kills.append(2)
                    sol2Killed = True
                blueSol3 = database_connect.getBlueforUnit("Soldier3")
                if(float(blueSol3[0]) > 0.99 and 3 not in ft2kills):
                    Ft2Killed+=1
                    ft2kills.append(3)
                    sol3Killed = True
                blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
                if(float(blueSol4[0]) > 0.99  and 4 not in ft2kills):
                    Ft2Killed+=1 
                    ft2kills.append(4)
                    sol4Killed = True     
        
        if(sol1Killed):
            BlueForceRemaining -= 1  
            Ft2KillPercentage = Ft2Killed / 4
        if(sol2Killed):
            BlueForceRemaining -= 1  
            Ft2KillPercentage = Ft2Killed / 4
        if(sol3Killed):
            BlueForceRemaining -= 1  
            Ft2KillPercentage = Ft2Killed / 4
        if(sol4Killed):
            BlueForceRemaining -= 1  
            Ft2KillPercentage = Ft2Killed / 4
            
        if(Count%10000 == 0):
            Count = 0
            print(Ft2KillPercentage)
        generateOpForceFt2Output()    
        generateBlueForceOutput()
        ft2Move()
    
        blueSol1 = database_connect.getBlueforUnit("Soldier1")
        blueSol2 = database_connect.getBlueforUnit("Soldier2")
        blueSol3 = database_connect.getBlueforUnit("Soldier3")
        blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
        if((float(ft2lead[0]) > 0.99 and float(ft2member[0]) > 0.99) 
           or (float(blueSol1[0]) > 0.99 and float(blueSol2[0]) > 0.99 and float(blueSol3[0]) > 0.99 and float(blueSol4[0]) > 0.99) 
           or (distanceBetweenPoints(float(blueSol1[1]), float(blueSol1[2]), 10017,16418) <=20) 
           or (distanceBetweenPoints(float(blueSol2[1]), float(blueSol2[2]), 10017,16418) <=20)
           or (distanceBetweenPoints(float(blueSol3[1]), float(blueSol3[2]), 10017,16418) <=20) 
           or (distanceBetweenPoints(float(blueSol4[1]), float(blueSol4[2]), 10017,16418) <=20)):
            break
        time.sleep(5)
    return Ft2KillPercentage  
        
def calculateKillPercentagesFt1(missionType):  
    
    Count = 0 
    ft1kills = []
    BlueForceRemaining = 4
    Ft1Killed = 0
    Ft1KillPercentage = 0     
    while(True):
        Count +=1
        #read blueforceposition table and opforposition table 
        #check if blueforce is close to ft1  
        # if close check if any blueforce units are dead
        # amount of killed/4 
        #if ft1 is dead 
        #check if blueforce is close to ft2   
        # if close check if any blueforce units are dead
        # amount of killed/amount remaining  
        sol1Killed = False      
        sol2Killed = False  
        sol3Killed = False  
        sol4Killed = False     
        EnemyUnit = ""     
        ft1lead = database_connect.getOpforUnit("ft1_lead")
        ft1member = database_connect.getOpforUnit("ft1_member")
        if(float(ft1lead[0]) < 1 or float(ft1member[0]) < 1):
            distanceFromFt1 = distanceBetweenUnits("ft1_lead", "Soldier1")
            if(distanceFromFt1 <= 200):
                blueSol1 = database_connect.getBlueforUnit("Soldier1")            
                if(float(blueSol1[0]) > 0.99 and 1 not in ft1kills):
                    Ft1Killed+=1
                    ft1kills.append(1)
                    sol1Killed = True
                blueSol2 = database_connect.getBlueforUnit("Soldier2")
                if(float(blueSol2[0]) > 0.99 and 2 not in ft1kills):
                    Ft1Killed+=1
                    ft1kills.append(2)
                    sol2Killed = True
                blueSol3 = database_connect.getBlueforUnit("Soldier3")
                if(float(blueSol3[0]) > 0.99 and 3 not in ft1kills):
                    Ft1Killed+=1
                    ft1kills.append(3)
                    sol3Killed = True
                blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
                if(float(blueSol4[0]) > 0.99  and 4 not in ft1kills):
                    Ft1Killed+=1 
                    ft1kills.append(4)
                    sol4Killed = True     
        
        if(sol1Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
        if(sol2Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
        if(sol3Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
        if(sol4Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
            
        if(Count%10000 == 0):
            Count = 0
            print(Ft1KillPercentage)
        generateOpForceFt1Output()    
        generateBlueForceOutput()
        ft1Move()
    
        blueSol1 = database_connect.getBlueforUnit("Soldier1")
        blueSol2 = database_connect.getBlueforUnit("Soldier2")
        blueSol3 = database_connect.getBlueforUnit("Soldier3")
        blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
        if("Forest" in missionType):
            if((float(ft1lead[0]) > 0.99 and float(ft1member[0]) > 0.99) 
               or (float(blueSol1[0]) > 0.99 and float(blueSol2[0]) > 0.99 and float(blueSol3[0]) > 0.99 and float(blueSol4[0]) > 0.99) 
               or (distanceBetweenPoints(float(blueSol1[1]), float(blueSol1[2]), 9140,16000) <=20) 
               or (distanceBetweenPoints(float(blueSol2[1]), float(blueSol2[2]), 9140,16000 ) <=20)
               or (distanceBetweenPoints(float(blueSol3[1]), float(blueSol3[2]), 9140,16000) <=20) 
               or (distanceBetweenPoints(float(blueSol4[1]), float(blueSol4[2]), 9140,16000) <=20)):
                break
        if("Open" in missionType):
            if((float(ft1lead[0]) > 0.99 and float(ft1member[0]) > 0.99) 
               or (float(blueSol1[0]) > 0.99 and float(blueSol2[0]) > 0.99 and float(blueSol3[0]) > 0.99 and float(blueSol4[0]) > 0.99) 
               or (distanceBetweenPoints(float(blueSol1[1]), float(blueSol1[2]), 9030,16340) <=20) 
               or (distanceBetweenPoints(float(blueSol2[1]), float(blueSol2[2]), 9030,16340 ) <=20)
               or (distanceBetweenPoints(float(blueSol3[1]), float(blueSol3[2]), 9030,16340) <=20) 
               or (distanceBetweenPoints(float(blueSol4[1]), float(blueSol4[2]), 9030,16340) <=20)):
                break
        
        time.sleep(5)
    return Ft1KillPercentage  


def calculateKillPercentages():
    Count = 0 
    ft1kills = []
    ft2kills = []  
    BlueForceRemaining = 4
    Ft1Killed = 0
    Ft2Killed = 0
    Ft1KillPercentage = 0     
    Ft2KillPercentage = -1
    while(True):
        Count +=1
        #read blueforceposition table and opforposition table 
        #check if blueforce is close to ft1  
        # if close check if any blueforce units are dead
        # amount of killed/4 
        #if ft1 is dead 
        #check if blueforce is close to ft2   
        # if close check if any blueforce units are dead
        # amount of killed/amount remaining  
        sol1Killed = False      
        sol2Killed = False  
        sol3Killed = False  
        sol4Killed = False     
        EnemyUnit = ""     
        ft1lead = database_connect.getOpforUnit("ft1_lead")
        ft1member = database_connect.getOpforUnit("ft1_member")
        if(float(ft1lead[0]) < 1 or float(ft1member[0]) < 1):
            distanceFromFt1 = distanceBetweenUnits("ft1_lead", "Soldier1")
            if(distanceFromFt1 <= 200):
                blueSol1 = database_connect.getBlueforUnit("Soldier1")            
                if(float(blueSol1[0]) > 0.99 and 1 not in ft1kills):
                    Ft1Killed+=1
                    ft1kills.append(1)
                    sol1Killed = True
                blueSol2 = database_connect.getBlueforUnit("Soldier2")
                if(float(blueSol2[0]) > 0.99 and 2 not in ft1kills):
                    Ft1Killed+=1
                    ft1kills.append(2)
                    sol2Killed = True
                blueSol3 = database_connect.getBlueforUnit("Soldier3")
                if(float(blueSol3[0]) > 0.99 and 3 not in ft1kills):
                    Ft1Killed+=1
                    ft1kills.append(3)
                    sol3Killed = True
                blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
                if(float(blueSol4[0]) > 0.99  and 4 not in ft1kills):
                    Ft1Killed+=1 
                    ft1kills.append(4)
                    sol4Killed = True     
        
        if(sol1Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
        if(sol2Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
        if(sol3Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
        if(sol4Killed):
            BlueForceRemaining -= 1  
            Ft1KillPercentage = Ft1Killed / 4
            
        if(1 not in ft1kills):
            EnemyUnit = "Soldier1" 
        
        elif(2 not in ft1kills):
            EnemyUnit = "Soldier2"  
            
        elif(3 not in ft1kills):
            EnemyUnit = "Soldier3" 
        
        elif(4 not in ft1kills):
            EnemyUnit = "Soldiergunner"
        
        if(EnemyUnit != ""):
            distanceFromFt2 = distanceBetweenUnits("ft2_lead", EnemyUnit)
            if(distanceFromFt2 <= 200):
                blueSol1 = database_connect.getBlueforUnit("Soldier1")
                if(float(blueSol1[0]) > 0.99 not in ft1kills and 1 not in ft2kills):
                    Ft2Killed+=1
                    ft2kills.append(1)
                blueSol2 = database_connect.getBlueforUnit("Soldier2")
                if(float(blueSol2[0]) > 0.99 and 2 not in ft1kills and 2 not in ft2kills):
                    Ft2Killed+=1
                    ft2kills.append(2)
                blueSol3 = database_connect.getBlueforUnit("Soldier3")
                if(float(blueSol3[0]) > 0.99 and 3 not in ft1kills and 3 not in ft2kills):
                    Ft2Killed+=1
                    ft2kills.append(3)
                blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
                if(float(blueSol4[0]) > 0.99 and 4 not in ft1kills and 4 not in ft2kills):
                    Ft2Killed+=1
                    ft2kills.append(4)
                
        if(BlueForceRemaining > 0):
            Ft2KillPercentage = Ft2Killed / BlueForceRemaining
        if(Count%10000 == 0):
            Count = 0
            print(Ft1KillPercentage)
            print(Ft2KillPercentage)
        generateOpForceOutput()    
        generateBlueForceOutput()
        opforMove()
        ft2lead = database_connect.getOpforUnit("ft2_lead")
        ft2member = database_connect.getOpforUnit("ft2_member")    
        blueSol1 = database_connect.getBlueforUnit("Soldier1")
        blueSol2 = database_connect.getBlueforUnit("Soldier2")
        blueSol3 = database_connect.getBlueforUnit("Soldier3")
        blueSol4 = database_connect.getBlueforUnit("Soldiergunner")
        # and float(ft2lead[0]) > 0.99 and float(ft2member[0]) > 0.99
        
        global forestMap
        tX =9019.81
        tZ = 16333.23
        if forestMap:
            tX =9132.97
            tZ=16009.21
        print(blueSol1[0] + ',' + blueSol2[0] + ',' + blueSol3[0] + ',' + blueSol4[0])
        if((float(ft1lead[0]) > 0.92 and float(ft1member[0]) > 0.92) 
           or (float(blueSol1[0]) > 0.92 and float(blueSol2[0]) > 0.92 and float(blueSol3[0]) > 0.92 and float(blueSol4[0]) > 0.92) 
           or (distanceBetweenPoints(float(blueSol1[1]), float(blueSol1[2]), tX,tZ) <=20) 
           or (distanceBetweenPoints(float(blueSol2[1]), float(blueSol2[2]), tX,tZ ) <=20)
           or (distanceBetweenPoints(float(blueSol3[1]), float(blueSol3[2]), tX,tZ) <=20) 
           or (distanceBetweenPoints(float(blueSol4[1]), float(blueSol4[2]), tX,tZ) <=20)):
            break
        time.sleep(5)
    return Ft1KillPercentage, Ft2KillPercentage
    


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

 
def distanceBetweenUnits(opFor, blueFor):
    opForPosition = database_connect.getOpforSoldierPos(opFor)
    blueForPosition = database_connect.getBlueforSoldierPos(blueFor)
    dis = distanceBetweenPoints(float(opForPosition[0]),float(opForPosition[1]), float(blueForPosition[0]),float(blueForPosition[1]))
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
        
def saveToFile(fileName, x, z, openTerrain, closed, neighbors, DToPath, ElevationChanged):
    with open(fileName+'.csv', mode ='a', newline='') as csv_file:   
        headers = ['X', 'Z', 'open', 'closed', 'neighbors', 'DToPath', 'ElevationChange']
        writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n',fieldnames=headers)
        if csv_file.tell() == 0:
            writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow({ 'X': x, 'Z' : z, 'open' : openTerrain, 'closed' : closed, 'neighbors' : neighbors, 'DToPath' : DToPath, 'ElevationChange' : ElevationChanged})

def saveToTrainingFile(fileName, killing, openTerrain, closed, neighbors, DToPath, ElevationChanged):
    with open(fileName+'.csv', mode ='a', newline='') as csv_file:   
        headers = ['killing', 'open', 'closed', 'neighbors', 'DToPath', 'ElevationChange']
        writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n',fieldnames=headers)
        if csv_file.tell() == 0:
            writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow({ 'killing': killing, 'open' : openTerrain, 'closed' : closed, 'neighbors' : neighbors, 'DToPath' : DToPath, 'ElevationChange' : ElevationChanged})


def saveToAgentDataFile(fileName, timestamp, UnitName, DNA , DNE, AllySector, EnemySector, NearestEType,
                         GreatestAngle, SmallestAngle, Vx, Vz, Px, Pz , ElevationDiff, Elevation, Health,
                          PercentForestAtEnemy, PercentForestAtSol, PercentForestNorthSector, PercentForestSouthSector, PercentForestEastSector, PercentForestWestSector ):
    with open(fileName+'.csv', mode ='a', newline='') as csv_file:   
        headers = ['Timestamp','UnitName', 'DNA' , 'DNE', 'AllySector', 'EnemySector', 'NearestEType',
                   'GreatestAngle', 'SmallestAngle', 'Vx', 'Vz', 'Px', 'Pz' , 'ElevationDiff', 'Elevation', 'Health',
                   'PercentForestAtEnemy', 'PercentForestAtSol', 'PercentForestNorthSector', 'PercentForestSouthSector', 'PercentForestEastSector', 'PercentForestWestSector']
        writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n',fieldnames=headers)
        if csv_file.tell() == 0:
            writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow({ 'Timestamp' : timestamp , 'UnitName' : UnitName, 'DNA' : DNA, 'DNE' : DNE,
                          'AllySector' : AllySector, 'EnemySector' : EnemySector, 'NearestEType' : NearestEType, 
                           'GreatestAngle' : GreatestAngle, 'SmallestAngle' : SmallestAngle, 'Vx' : Vx, 'Vz' : Vz, 'Px' : Px, 'Pz' : Pz,
                            'ElevationDiff' : ElevationDiff, 'Elevation' : Elevation, 'Health' : Health,
                            'PercentForestAtEnemy' : PercentForestAtEnemy, 'PercentForestAtSol' : PercentForestAtSol,
                             'PercentForestNorthSector' : PercentForestNorthSector, 'PercentForestSouthSector' : PercentForestSouthSector,
                              'PercentForestEastSector' : PercentForestEastSector, 'PercentForestWestSector' : PercentForestWestSector})

def saveToAgentDataFileBlue(fileName, timestamp, UnitName, DNA , DNE, AllySector, EnemySector, NearestEType,
                         GreatestAngle, SmallestAngle, Vx, Vz, Px, Pz , ElevationDiff, Elevation, Health,
                          PercentForestAtEnemy, PercentForestAtSol, PercentForestNorthSector, PercentForestSouthSector, PercentForestEastSector, PercentForestWestSector ):
    with open(fileName+'.csv', mode ='a', newline='') as csv_file:   
        headers = ['Timestamp','UnitName', 'DNA' , 'DNE', 'AllySector', 'EnemySector', 'NearestEType',
                   'GreatestAngle', 'SmallestAngle', 'Vx', 'Vz', 'Px', 'Pz' , 'ElevationDiff', 'Elevation', 'Health',
                   'PercentForestAtEnemy', 'PercentForestAtSol', 'PercentForestNorthSector', 'PercentForestSouthSector', 'PercentForestEastSector', 'PercentForestWestSector']
        writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n',fieldnames=headers)
        if csv_file.tell() == 0:
            writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow({ 'Timestamp' : timestamp , 'UnitName' : UnitName, 'DNA' : DNA, 'DNE' : DNE,
                          'AllySector' : AllySector, 'EnemySector' : EnemySector, 'NearestEType' : NearestEType, 
                           'GreatestAngle' : GreatestAngle, 'SmallestAngle' : SmallestAngle, 'Vx' : Vx, 'Vz' : Vz, 'Px' : Px, 'Pz' : Pz,
                            'ElevationDiff' : ElevationDiff, 'Elevation' : Elevation, 'Health' : Health,
                            'PercentForestAtEnemy' : PercentForestAtEnemy, 'PercentForestAtSol' : PercentForestAtSol,
                             'PercentForestNorthSector' : PercentForestNorthSector, 'PercentForestSouthSector' : PercentForestSouthSector,
                              'PercentForestEastSector' : PercentForestEastSector, 'PercentForestWestSector' : PercentForestWestSector})



def terrainVariablesToFile(fileName, Xmax, Zmax, Xmin, Zmin, missionType):
    global TDict
    global elevationDict
    #global missionType
    XSet,ZSet, TDict = ReadTerrainFile.readTerrainFile()
    ReadTerrainFile.setTerrainValues(XSet, ZSet, TDict)
    for x in range(roundup(Xmin), roundup(Xmax), 10):
        for z in range(roundup(Zmin), roundup(Zmax), 10):
            #print(x,z)
            DToPath , ElevationChanged = ReadTerrainFile.findDistanceAndElevationToPath(x,z, elevationDict, missionType)
            urban, open , closed =  ReadTerrainFile.getTerrainAtLocation(x,z)
            neighbors = ReadTerrainFile.closedNeighbors(x,z)
            saveToFile(fileName, x, z, open, closed, neighbors, DToPath, ElevationChanged)
            print("Row Written")

def saveLethalityToFile(fileName, x,z, preditcedLethality):
    with open(fileName+'.csv', mode ='a', newline='') as csv_file:   
        headers = ['X', 'Z', 'preditcedLethality']
        writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n',fieldnames=headers)
        if csv_file.tell() == 0:
            writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow({ 'X': x, 'Z' : z, 'preditcedLethality' : preditcedLethality})

def updateLethalityToFile(fileName, x, z, lethality):
    tempfile = NamedTemporaryFile(mode='w', delete=False)
 
    with open(fileName+'.csv', 'r') as csvfile, tempfile:
        headers = ['X', 'Z', 'preditcedLethality']
        reader = csv.DictReader(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)
        writer = csv.DictWriter(tempfile, delimiter=',', lineterminator='\n',fieldnames=headers)
        for row in reader:
            if row['X'] == str(x) and row['Z'] == str(z):
                print("Updating Row", row['X'], row['Z'])
                row['preditcedLethality'] = lethality
            row = {'X': row['X'], 'Z' :row['Z'], 'preditcedLethality' : row['preditcedLethality']}
            writer.writerow(row)
    shutil.move(tempfile.name, fileName)

def generateUpdatedLethality(fileName, Xmax, Zmax, Xmin, Zmin):
    for x in range(roundup(Xmin), roundup(Xmax), 10):
        for z in range(roundup(Zmin), roundup(Zmax), 10):
            #print(x,z)
            Lethality = calculateLethalityAtAmbushFromFile(fileName, x,z)
            updateLethalityToFile(fileName+'_Lethality', x,z, Lethality)
            print("Lethality Writen To File " + str(Lethality))

def generateUpdatedLethalityFull(fileName, Xmax, Zmax, Xmin, Zmin):
    for x in range(Xmin, Xmax, 10):
        for z in range(Zmin, Zmax, 10):
            #print(x,z)
            Lethality = calculateLethalityAtAmbushFromFile(fileName, x,z)
            updateLethalityToFile(fileName+'_Lethality', x,z, Lethality)
            print("Lethality Writen To File " + str(Lethality))            

        
def saveLethalityPredicitionAtAmbushZoneToFile(fileName, Xmax, Zmax, Xmin, Zmin):
    for x in range(roundup(Xmin), Xmax, 10):
        for z in range(roundup(Zmin), Zmax, 10):
            Lethality = calculateLethalityAtAmbushFromFile(fileName, x,z)
            saveLethalityToFile(fileName+'_Lethality', x,z, Lethality)
            print("Lethality Writen To File " + str(Lethality))
    #readTerrainVariableFromFile('ft2Ambush.csv')
    
    



                   
def getPredictedLethalityFromFile(fileName):
    '''
    1. read file 
    1.a add [x,z] = leatality 
    1.b lethalArray.append(lethality)
    sort(lethalityarray, reverse = True)
    quartile = len(lethalarray)/4
    iterate through lethalDictonary{}
    randLethal = lethalityArray[rand(0,quartile)
    iterate through lethal dictionary:  if value = randlethal: return key
    key = [key for key, value in dict_obj.items() if value == 'value'][0]
    '''
    leastLethality = {}
    lethalArray =[]
    lethalityCount = 0
    with open(fileName+'_Lethality.csv', 'rt') as f:
        header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        
        #print(results)
        for row in reader:           
            leastLethality[float(row[0]),float(row[1])] = [float(row[2])]
            
            lethalityCount+=1
            lethalArray.append(float(row[2]))
    #print(leastLethality)        
    #print(sorted(set(lethalArray),reverse = True))
    #exit(0)
    return leastLethality, sorted(set(lethalArray),reverse = True)

def getPredictedLethalityFromFileFt2(fileName):
    '''
    1. read file 
    1.a add [x,z] = leatality 
    1.b lethalArray.append(lethality)
    sort(lethalityarray, reverse = True)
    quartile = len(lethalarray)/4
    iterate through lethalDictonary{}
    randLethal = lethalityArray[rand(0,quartile)
    iterate through lethal dictionary:  if value = randlethal: return key
    key = [key for key, value in dict_obj.items() if value == 'value'][0]
    '''
    leastLethality = {}
    lethalArray =[]
    lethalityCount = 0
    with open(fileName+'_ft2Lethality.csv', 'rt') as f:
        header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        
        #print(results)
        for row in reader:           
            leastLethality[float(row[0]),float(row[1])] = [float(row[2])]
            lethalityCount+=1
            lethalArray.append(float(row[2]))
    return leastLethality, sorted(set(lethalArray),reverse = True)
 
def getPositionDataAtAmbushFromFile(fileName, X, Z): 
    DToPath = 0
    ElevationChanged = 0                                              
    openTerrain = 0
    closed =  0
    neighbors =0
    with open(fileName+'.csv', 'rt') as f:
        #header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        #print(X, Z)
        results = filter(lambda x: x[0]==str(int(X)) and x[1]==str(int(Z)), reader)
        #print(results)
        for line in results:
            DToPath = float(line[5])
            ElevationChanged = float(line[6])  
            openTerrain = float(line[2])
            closed =  float(line[3])
            neighbors = float(line[4])

    return  openTerrain, closed, neighbors, DToPath, ElevationChanged             

def calculateLethalityAtAmbushFromFileFt2(fileName, X, Z): 
    lethality = 0
    with open(fileName+'.csv', 'rt') as f:
        #header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        results = filter(lambda x: x[0]==str(int(X)) and x[1]==str(int(Z)), reader)
        #print(results)
        for line in results:
            #print(line)
            lethality = linearRegression.predictLethalityFT2Pos(float(line[2]),float(line[3]), float(line[4]), float(line[5]), float(line[6]))[0,0]
       
    return lethality
def calculateLethalityAtAmbushFromFile(fileName, X, Z): 
    #print(fileName)
    #exit(0)
    lethality = 0
    with open(fileName+'.csv', 'rt') as f:
        #header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        results = filter(lambda x: x[0]==str(int(X)) and x[1]==str(int(Z)), reader)
        #print(results)
        for line in results:
            #print(line)
            lethality = linearRegression.predictLethalityAtPosition2(float(line[2]),float(line[3]), float(line[4]), float(line[5]), float(line[6]))[0,0]
     
    return lethality




    
async def main():
    #readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())
