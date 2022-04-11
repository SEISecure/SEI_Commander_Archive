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
import database_connect_Arma
import bisect
from tempfile import NamedTemporaryFile
import shutil
import os
import pandas as pd
import MCTS
import blockingTask
import vehicleCommander
import threading
import AthenaSenderTask
import AthenaReceiverLocalization
import AthenaReceiverStatus
import AthenaReceiverDetection

from Arthemis.NewCodePy import ArthemisSender as Art

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
terrainDict = {}
visDict = {}
positionData = {}
coverDict = {}
concealmentDict = {}
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


 
status = -1
#declaration of global variables 

#database connection information currently on localhost
'''
connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")
'''
#class that will handle database actions

def vehicleCRunner():
    vC = vehicleCommander.vehicleCommander()
    config = helper.read_config()
    simPlatform = config['vc']['simPlatform'] 
    vC.simPlatform = simPlatform
    side = config['vc']['side'] 
    vC.side = side
    unitName = config['vc']['unitName'] 
    fUnitName = unitName + vC.generateUUID()
    vC.setUnitName(fUnitName)
    waypointType = config['vc']['waypointType'] 
    vC.waypointType = waypointType
    indexVal = 0
    while True: 
        if indexVal % 10 ==0:
            print("++++++++++Running+++++++++++++++++")
            indexVal =0
        vC.processSquadCommand()
        vC.moveToRandoLocInZone()
        vC.findVisibleEnemy()
        indexVal+=1
        time.sleep(1)
        
   
def AthenaSender():       
    AthenaSenderTask.AthenaRunner()
    
def ArthemisSender():  
    print("Called Arthemis")     
    Art.ArthemisSender()
        
def AthenaReceiverLocal():       
    AthenaReceiverLocalization.AthenaReceiverRunner()       
    
def AthenaStatus():
    AthenaReceiverStatus.AthenaStatus()
    
    
def AthenaDetections():
    AthenaReceiverDetection.AthenaDetections()
    
async def runner(runflag):
    #runflag = 0
    #database_connect_Arma.setConnection("127.0.0.1")
    #velocity = database_connect_Arma.getUnitVelocity("ugv1", "VBS4")
    #print(velocity)
    database_connect_Arma.setConnection("127.0.0.1")
    database_connect_Arma.resetDB()  
    
    t2 = threading.Thread(target=AthenaSender)
    t2.daemon = True
    t2.start()  
        
    t1 = threading.Thread(target=vehicleCRunner)
    t1.daemon = True
    t1.start()
    
    t3 = threading.Thread(target=AthenaReceiverLocal)
    t3.daemon = True
    t3.start()

    t4 = threading.Thread(target=AthenaStatus)
    t4.daemon = True
    t4.start()
     
    #AthenaDetections()
    
     
    t5 = threading.Thread(target=AthenaDetections)
    t5.daemon = True
    t5.start() 
    
    t6 = threading.Thread(target=ArthemisSender)
    t6.daemon = True
    t6.start()  

    while True:
        time.sleep(1)
    '''
    if runflag == 0:
        MCTS.recon()
    else:
        #call terrain scan 
        database_connect_Arma.setConnection("127.0.0.1")
        path2 = 'C:/arma3/terrain/'
        database_connect_Arma.getObjects(path2)
        blockingTask.initialMove()
    '''
    
    #array = np.load('terrain.npy')
    #array = ([[1, 2], [3, 4, 5, 6]])
    #arrReshape = array.reshape(array.shape[0],-1)
    #np.set_printoptions(threshold=sys.maxsize)
    #np.savetxt('./terrain.csv', arrReshape, delimiter=',', newline='\n')
    #np.savetxt("data3.csv", a, delimiter = ",")   
    #print(np.array2string(array).replace('[[',' [').replace(']]',']'))
    #pd.DataFrame(arrReshape).to_csv('terrain.csv')
    '''
    for index in range(0,len(array),1):
        row = array[index]
        np.set_printoptions(threshold=sys.maxsize)
        print(row)
        file = open(r'./terrain.csv', 'a', newline = '\n')
        with file:
            write = csv.writer(file, delimiter = ',')
            write.writerows(row)

    
    
    #generateConcealmentFromFile('terrain')
    #generateCoverFromFile('terrain')
    global coverDict
    global concealmentDict
    coverDict = getCoverOrConcealmentFromFile('terrain_Cover')
    print("covers", coverDict[(1800,10000)])
    concealmentDict = getCoverOrConcealmentFromFile('terrain_Concealment')
    print("concealments", concealmentDict[(1800,10000)])    
    global visDict
    visDict = getVisFromFile("DB\AllblueforVisibility")
    print("vis", visDict[(1800, 10080, 1800, 10120)])
    
    exit(0)
    
    
    
    Xpositions = [2071.61, 1929.17, 2036.17, 2001.92, 2000]  
    Ypositions = [10523.2, 10499.8, 10373.9, 10128.7, 10072]  
    Zpositions = [7.695, 9.3, 9.69, 5.26] 
    #numOfOpFor = database_connect_Arma.getNumberofOpForceUnits()
    #database_connect_Arma.Broadcast("blue") 
    #time.sleep(4)
    database_connect_Arma.Broadcast("red")
    time.sleep(4)
    #numOfBlueFor = database_connect_Arma.getNumberofBlueForceUnits()     
    numOfOpFor = database_connect_Arma.getNumberofOpForceUnits()
    #blueForSoldiers = database_connect_Arma.getAllBlueForceUnits(numOfBlueFor)
    opForSoldiers = database_connect_Arma.getAllOpForceUnits(numOfOpFor)
    #print(numOfBlueFor)
    runNumber = 0
    
    while True: 
        print("yo") 
        index = 0  
        i = 0  
        print("Run Number", runNumber)
        while True:
            database_connect_Arma.Broadcast("red")
            time.sleep(4)
            print("lo") 
            numOfOpFor = database_connect_Arma.getNumberofOpForceUnits()
            print(numOfOpFor)
            if(numOfOpFor !=0):
                break     
        while(i < len(Xpositions)): 
        
            if(isMissionEnd()):
                i = 0
                index = 0
                runNumber+=1
                break
            
            if(i > 0):
                database_connect_Arma.Broadcast("red")
                time.sleep(4)   
                numOfOpFor = database_connect_Arma.getNumberofOpForceUnits()
                opForSoldiers = database_connect_Arma.getAllOpForceUnits(numOfOpFor)
                print("Hi")
                #disRed = []
                
                for opFor in opForSoldiers:
                    if(opFor[1]>0):
                        disRed = opFor
                        break
                
                opFor = opForSoldiers[0]
                #print(i)
                #print("opFor location", opFor[2], opFor[3], Xpositions[i-1],Ypositions[i-1])
                dis = distanceBetweenPoints(opFor[2], opFor[3], Xpositions[i-1],Ypositions[i-1]) 
                print("position sent to", Xpositions[i-1],Ypositions[i-1])
                #print(dis)
                print("The distance is", dis)
                if(dis <=20):
                    while(index <numOfOpFor):
                        opFor = opForSoldiers[index]
                        print("close enough")
                        if(opFor[1] > 0):
                            print(opFor[0], Xpositions[i]+index, Ypositions[i]+index, Zpositions[i]) 
                            database_connect_Arma.moveUnit("opfor", (Xpositions[i] +index), (Ypositions[i]+index), Zpositions[i], index) 
                            print("waypoint index", i)
                            time.sleep(2)
                            index +=1
                        else:
                            index +=1
                            opFor = opForSoldiers[index]
   
                if(index >= numOfOpFor):
                    i+=1  
                    index = 0
            elif(i==0):            
                database_connect_Arma.Broadcast("red") 
                time.sleep(5)  
                opForSoldiers = database_connect_Arma.getAllOpForceUnits(numOfOpFor)
                while(index <numOfOpFor):   
                    #print(opForSoldiers)
                    print(index, " place1")     
                    opFor = opForSoldiers[index]
                    if(opFor[1] > 0):
                        database_connect_Arma.moveUnit("opfor", (Xpositions[i] +index), (Ypositions[i]+index), Zpositions[i], index) 
                        print(opFor[0], Xpositions[i]+index, Ypositions[i]+index, Zpositions[i]) 
                        print("waypoint index", i)
                        time.sleep(2)
                        index +=1
                    else:
                        index +=1
                        opFor = opForSoldiers[index]
                i+=1
                index = 0 
            
            if(isMissionEnd()):
                i = 0
                index = 0
                database_connect_Arma.Broadcast("blue")
                time.sleep(4)
                numOfOpFor = database_connect_Arma.getNumberofOpForceUnits()
                print(numOfOpFor)
                runNumber+=1
                break
        '''
    #getDetections(2200,1800, 10225, 10080, 2200,1800, 10900, 10000 )       
    
          
    #fireTeam2()
#x: 1800  - 2200
#y: 10000  - 10900





def distanceBetweenPoints(X1,Y1,X2, Y2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Y1- Y2, 2))
    return dis  
    
    
def getDetections(Xmax,Xmin,Ymax,Ymin, XmaxOP,XminOP,YmaxOP,YminOP ):
    '''
    global terrainDict 
    terrainDict = getTerrainFromFile("terrain")
    print(terrainDict[1800, 10000])
    terrain = terrainDict[1800, 10000]
    print(terrain[0])
    global visDict 
    visDict = getTerrainFromFile("terrain")
    print(visDict[1800, 10000])
    vis = visDict[1800, 10000]
    print(vis[0])
    
    '''
    #print(terrainDict)
    previousTime = 0
    Xrange = Xmax - Xmin
    Yrange = Ymax - Ymin
    XrangeOP = XmaxOP - XminOP
    YrangeOP = YmaxOP - YminOP
    database_connect_Arma.Broadcast("blue")
    database_connect_Arma.Broadcast("red")
    numOfOpFor = database_connect_Arma.getNumberofOpForceUnits()
    numOfBlueFor = database_connect_Arma.getNumberofBlueForceUnits()
    blueForSoldiers = database_connect_Arma.getAllBlueForceUnits(numOfBlueFor)
    opForSoldiers = database_connect_Arma.getAllOpForceUnits(numOfOpFor)
    blueForSoldier = blueForSoldiers[0]
    opForSoldier = opForSoldiers[0]

    for Xblue in range(0,Xrange,20):
        XBluePosition = Xmin + Xblue
        YBlueStart = 0
        if Xblue == 0:
            continue
        if Xblue == 20:
            YBlueStart = 10695 - Ymin
            #Yrange = Ymax-YBlueStart
        for Yblue in range(YBlueStart, Yrange,20):
            YBluePosition = Ymin + Yblue
            terrain = terrainDict[XBluePosition, YBluePosition]
            if(terrain[0] <= 0):
                continue   
            database_connect_Arma.soldierSetPosCommand(blueForSoldier[0], XBluePosition,YBluePosition, blueForSoldier[4])
            XOpStart = 0
            YOpStart = 0
            if Xblue == 20 and Yblue == YBlueStart:
                XOpStart = 2140-XminOP
                #XrangeOP = XmaxOP - XOpStart
            else:
                XOpStart = Xblue
                #XrangeOP = XmaxOP - XOpStart
            for Xop in range(XOpStart ,XrangeOP,20):
                XOpPosition = XminOP + Xop
                if Xblue == 20 and Xop == XOpStart:
                    YOpStart = 10120 -YminOP
                    #YrangeOP = YmaxOP - YOpStart
                else:
                    YOpStart = Yblue
                    #YrangeOP = YmaxOP - YOpStart
                for Yop in range(YOpStart,YrangeOP,20):
                    YOpPosition = YminOP + Yop
                    print(YOpPosition)
                    while True:
                        currentTime = database_connect_Arma.getTimestamp()
                        if currentTime > previousTime:
                            previousTime = currentTime
                            print(XOpPosition,YOpPosition)
                            terrain = terrainDict[XOpPosition, YOpPosition]                            
                            if(terrain[0] <= 0):
                                break
                            database_connect_Arma.soldierSetPosCommand(opForSoldier[0], XOpPosition,YOpPosition, opForSoldier[4])
                            database_connect_Arma.soldierSetPosCommand(blueForSoldier[0], XBluePosition,YBluePosition, blueForSoldier[4])
                            break
                        else:
                            time.sleep(1)

async def main():
    #readTerrain()
    task = asyncio.create_task(runner(1))
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())