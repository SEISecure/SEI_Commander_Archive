import asyncio
import logging
import socket
import sys
import psycopg2
import time
import math
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
import loadNueralNetwork
import os


model = loadNueralNetwork.loadModel('trenchModel')
model.eval()
async def runner():

    continousMovement()




def distanceBetweenPoints(X1,Z1,X2,Z2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Z1- Z2, 2))
    return dis  

def percentBlueAlive():
    totalCount = database_connect_Arma.numOfAlive_v2Blue()
    soldiers = database_connect_Arma.getAllBlueForceUnits(totalCount)
    aliveCount = 0
    for soldier in soldiers:
        if(float(soldier[1]) > 7):
            aliveCount+=1
    if(aliveCount > 0):
        return aliveCount/totalCount
    return 0
    
def percentRedAlive():
    totalCount = database_connect_Arma.numOfAlive_v2()
    soldiers = database_connect_Arma.getAllOpForceUnits(totalCount)
    aliveCount = 0
    for soldier in soldiers:
        if(float(soldier[1]) > 7):
            aliveCount+=1
    if(aliveCount > 0):
        return aliveCount/totalCount    

def atFireLocation(unitName):
    trenchFireLocations = [ [983488.0, 1000164.5] , [983498.0, 1000163.0] , [983508.0, 1000161.0] , [983518.0, 1000160.0] , [983528.0, 1000158.5] , [983538.0, 1000157.5] ,
        [983548.0, 1000156.0] , [983558.0, 1000155.5] , [983568.0, 1000154.1] , [983578.0, 1000152.0] , [983588.0, 1000154.3] , [983598.0, 1000159.5], 
        [983608.0, 1000165.6] , [983618.0, 1000171.5], [983628.0, 1000179.3] ];
    atFireLocationCounter = 0
    atFireLoc = 0
    totalCount = database_connect_Arma.numOfAlive_v2()
    soldiers = database_connect_Arma.getAllOpForceUnits(totalCount)
    for soldier in soldiers:
        for trenchLoc in trenchFireLocations:
            if distanceBetweenPoints(trenchLoc[0], trenchLoc[1], float(soldier[2]), float(soldier[3])) <=3 and float(soldier[1]) < 0.93:
                atFireLocationCounter+=1
            if(unitName in soldier[0]):
                atFireLoc = 1
    
    return atFireLoc, atFireLocationCounter/totalCount

def minOpAllyDis(unitName, X, Z):
    totalCount = database_connect_Arma.numOfAlive_v2()
    soldiers = database_connect_Arma.getAllOpForceUnits(totalCount)
    #print(soldiers)
    minDisFromAlly = 10000
    deadSolCount = 0
    for soldier2 in soldiers:
        if unitName not in soldier2[0]:
            if(float(soldier2[1]) < 7):
                disFromAlly = distanceBetweenPoints(float(X), float(Z), float(soldier2[2]), float(soldier2[3]))
                if(disFromAlly < minDisFromAlly ):
                    minDisFromAlly = disFromAlly
            if(float(soldier2[1]) > 0.93 ):
                deadSolCount+=1
                
    if(deadSolCount == totalCount):
        return -1    
    return minDisFromAlly/50


def minDisFromOpEnemy(X, Z):
    totalCount = database_connect_Arma.numOfAlive_v2Blue()
    totalCountOP = database_connect_Arma.numOfAlive_v2()
    soldiers = database_connect_Arma.getAllOpForceUnits(totalCountOP)
    eSoldiers = database_connect_Arma.getAllBlueForceUnits(totalCount)
    minDisFromEnemy = 10000
    for eSoldier in eSoldiers:
        if(float(eSoldier[1]) < 7):
            disFromEnemy = distanceBetweenPoints(float(X), float(Z), float(eSoldier[2]), float(eSoldier[3]))
            if(disFromEnemy < minDisFromEnemy ):
                minDisFromEnemy = disFromEnemy
    if(minDisFromEnemy == 10000): 
        return -1

    return minDisFromEnemy/300

def continousMovement():
    while True:
        trenchMovement()
        time.sleep(20)


def trenchMovement():
    print("here")
    trenchFireLocations = [ [983488.0, 1000164.0] , [983498.0, 1000162.5] , [983508.0, 1000160.5] , [983518.0, 1000159.5] , [983528.0, 1000158.0] , [983538.0, 1000157.0] ,
        [983548.0, 1000155.0] , [983558.0, 1000154.2] , [983568.0, 1000153.1] , [983578.0, 1000151.0] , [983588.0, 1000153.3] , [983598.0, 1000158.5], 
        [983608.0, 1000164.6] , [983618.0, 1000170.5], [983628.0, 1000178.3] ]
   
    trenchSafeLocations = [ [983493.0, 0.0, 1000167.3] , [983503.0, 0.0, 1000166.0] , [983513.0, 0.0, 1000165.0] , [983523.0, 0.0, 1000163.2] , [983533.0, 0.0, 1000161.1] , [983543.0, 0.0, 1000161.1] ,
        [983553.0, 0.0, 1000159.5] , [983563.0, 0.0, 1000158.0] , [983573.0, 0.0, 1000156.4] , [983583.0, 0.0, 1000156.2] , [983593.0, 0.0, 1000161.0] , [983603.5, 0.0, 1000166.0] ,
        [983613.0, 0.0, 1000172.8] , [983623.0, 0.0, 1000178.8] , [983633.0, 0.0, 1000185.1] ]
    #15 positions each for safe and fire
    random.seed()
    trenchLocations = trenchFireLocations + trenchSafeLocations
    sentLocations =[]
    totalCount = database_connect_Arma.numOfAlive_v2()
    soldiers = database_connect_Arma.getAllOpForceUnits(totalCount)
    #print(soldiers)
    for sdata in soldiers:
        #print(sdata)
        #exit(0)
        nextPositions = []
        closeLocations = []   
        #print(float(sdata[1]))     
        if (float(sdata[1]) > 7):
            #search through the vectors for the closest location
            posData = getPosData(sdata[0], 1, sdata[2],sdata[3] )
            for v in trenchLocations:
                dis = distanceBetweenPoints(v[0],v[1],float(sdata[2]),float(sdata[3]))
                if dis < 20 and dis > 1:
                    closeLocations.append(v)
                    print("adding close loc")
            noAllyNearby = True
            if(len(closeLocations) > 0) :
                for chosenLocation in closeLocations:
                    noAllyNearby = True               
                    for allydata in soldiers:
                        if sdata[0] not in allydata[0]:
                            disFromAlly = distanceBetweenPoints(chosenLocation[0],chosenLocation[1],float(allydata[2]),float(allydata[3]))
                            if (disFromAlly < 4  and float(allydata[1]) > 7 ):
                                #nearby ally break out of loop
                                noAllyNearby = False
                                print("soldier nearby")
                                break

                    if noAllyNearby == True:
                        print("trying to add")
                        print(posData[0] , posData[1])
                        #no nearby ally move to location
                        nextPosData = getPosData(sdata[0], 0, chosenLocation[0],chosenLocation[1] )
                        print("next location", nextPosData[0] , nextPosData[1])
                        print("---------------------------")
                        if (nextPosData[0] + nextPosData[1])> (posData[0] + posData[1]) * 1.01 and [chosenLocation[0] , chosenLocation[1]] not in sentLocations :
                            nextPositions.append(nextPosData)
                            print("no soldier nearby add position")
            #move soldier to the best new location 
            print(len(nextPositions))
            print(sdata[0])

            if(len(nextPositions)> 0):
                bestmove = 0
                xpos = 0
                zpos = 0
                for pos in nextPositions:
                    tempValue = pos[0] + pos[1]
                    if(tempValue > bestmove):
                        bestmove = tempValue
                        xpos = pos[2]
                        zpos = pos[3]
                print("Moving", sdata[0])
                print(sentLocations)
                database_connect_Arma.moveUnit( xpos,zpos, 0, sdata[0])
                sentLocations.append([xpos, zpos])
                print(sentLocations)


def SoldierAlreadySent(sentLocations, newLoc):
    if (len(sentLocations) > 0):
        for v in sentLocations:
            if distanceBetweenPoints(v[0],v[1],newLoc[0],newLoc[1]):
                return True
            else:
                continue
    return False


def getPosData(unitName, sameLocFlag, X, Z):
    perBlueAlive = percentBlueAlive()
    perRedAlive = percentRedAlive()
    atFire , FireLocCount = atFireLocation(unitName)
    disFromEnemy = minDisFromOpEnemy(X,Z)
    disFromAlly = minOpAllyDis(unitName, X, Z) 
    print("pos", X, Z)           
    print("perBlueAlive", perBlueAlive)
    print("perRedAlive", perRedAlive)
    print("atFire",atFire)
    print("FireLocCount", FireLocCount)
    print("disFromEnemy", disFromEnemy)
    print("disFromAlly", disFromAlly)
    input = np.array([perRedAlive,perBlueAlive,disFromAlly,
                       disFromEnemy, atFire, FireLocCount, sameLocFlag])
    dtype = torch.float
    device = torch.device("cpu")
    inputNodes = torch.tensor(input,device=device, dtype=dtype)
    output = model(inputNodes)
    
    #print(output[0].item())
    return output[0].item(), output[1].item(), X, Z
async def main():
    #readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())