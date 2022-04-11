import math
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
enemyLocationTemp ={}
nest_asyncio.apply()



 

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
    while(True):
        
            '''
            Step 0 - Read in terrain file
            Step 1 - Find all Red Force that are alive
                1.a Create a list of soldiers names that are alive on ft1
                1.b Create a list of soldiers names that are alive on ft2
                1.c Create a list of soldiers names that are alive on ft3
    
            Step 2 - Find the current x and z positon for each team member 
                2.a ft1XPosition ft1ZPosition
                2.b ft2XPosition ft2ZPosition
                2.c ft3XPosition ft3ZPosition
            
            Step 3 - Find all enemies that are visible from any team members
               3.a pull all visible enemies for the database
               3.b create a list with all visible enemies (make sure no names are repeated)
            
            Step 4 - Simulate future states to see ideal next move
                4.a var StartTime = getCurrentTime 
                4.b create dictionary fireTeamsNextPos key = "x,z" value = [Reward (0.0)]
                4.c while CurrentTime - StartTime < 4 Seconds perfom the following tasks
                    4.d create a temp variable for current X,Z for each fireteam and visible enemy
                    4.e create a temp variable nextXZ =[x,z] for each fireteam
                    4.f newStateReward =0.0
                    4.g for i in range (1:7)
                        4.g.1 randomly select a new average X and Z of each fire team that is no more than 20 meters away from current x,z
                        4.g.2 update current with the new X and Z location
                        4.g.3 if this is the first time through iteration update nextXZ with the randonly selected x,z
                        4.g.4 run futureLocationRandomize (enemy, 20* i) for all enemeys and record their location
                        4.g.5 calculate state reward:
                            4.g.5.1 newStateReward += 1.5 - ft1 distance to FOB/500
                            4.g.5.2 newStateReward += 1.5 - ft2 distance to FOB/500
                            4.g.5.3 newStateReward += 1.5 - ft3 distance to FOB/500
                            4.g.5.4 newStateReward += 1 * ft1 Closed Terrain Percentage
                            4.g.5.5 newStateReward += 1 * ft2 Closed Terrain Percentage
                            4.g.5.6 newStateReward += 1 * ft3 Closed Terrain Percentage
                            4.g.5.7 newStateReward -= 1 * ft1 urban Terrain Percentage
                            4.g.5.8 newStateReward -= 1 * ft2 urban Terrain Percentage
                            4.g.5.9 newStateReward -= 1 * ft3 urban Terrain Percentage
                            4.g.5.10 If enemy are within 300 M
                                if ugv newStateReward -= 0.33
                                if uav newStateReward -= 0.2
                                if turret newStateReward -= 0.2
                    add new reward to dictionary fireTeamsNextPos = [newStateReward1, newStateReward2]
                Sort through all positions in fireTeamsNextPos and select the x,z with the highest average newStateReward
            
            Step 5 move soldiers to next state
                if soldiers within 300 meters of visible enemy use continueAssault2 with target X and Z being the new location
                else: move soldiers to new target X and Z and set them not to engage target.
            
            Step 6 simulation ends 
                if all blue force are killed
                if all red force are killed
                if red force reaches the fence (i.e., 20 meters from center of FOB)
            '''
            
    
    
            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print ( connection.get_dsn_parameters(),"\n")
            
            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record,"\n")
            ft1_team =[]
            ft1_avgX = 0.0
            ft1_avgZ = 0.0
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_rifleman';")
            ft1_rifleman = cursor.fetchone()
            if(ft1_rifleman[1] !=1):
                if(initialized):
                    soldierDict[ft1_rifleman[0]] = [0,0,ft1_rifleman[2],ft1_rifleman[3],ft1_rifleman[2],ft1_rifleman[3],ft1_rifleman[2],ft1_rifleman[3]]
                else:
                    tempState = soldierDict[ft1_rifleman[0]]
                    tempState[2] = ft1_rifleman[2]
                    tempState[3] = ft1_rifleman[3]
                    soldierDict[ft1_rifleman[0]] = tempState
                ft1_avgX += float(ft1_rifleman[2])
                ft1_avgZ += float(ft1_rifleman[3])
                ft1_team.append(ft1_rifleman)
            else:
                if(ft1_rifleman[0] in soldierDict):
                    del soldierDict[ft1_rifleman[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_mgunner';")
            ft1_mgunner = cursor.fetchone()
            if(ft1_mgunner[1] !=1):
                if(initialized):
                    soldierDict[ft1_mgunner[0]] = [0,0,ft1_mgunner[2],ft1_mgunner[3],ft1_mgunner[2],ft1_mgunner[3],ft1_mgunner[2],ft1_mgunner[3]]
                else:
                    tempState = soldierDict[ft1_mgunner[0]]
                    tempState[2] = ft1_mgunner[2]
                    tempState[3] = ft1_mgunner[3]
                    soldierDict[ft1_mgunner[0]] = tempState
                ft1_avgX += float(ft1_mgunner[2])
                ft1_avgZ += float(ft1_mgunner[3])
                ft1_team.append(ft1_mgunner)
            else:
                if(ft1_mgunner[0] in soldierDict):
                    del soldierDict[ft1_mgunner[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_grenadier';")
            ft1_grenadier = cursor.fetchone()
            if(ft1_grenadier[1] !=1):
                if(initialized):
                    soldierDict[ft1_grenadier[0]] = [0,0,ft1_grenadier[2],ft1_grenadier[3],ft1_grenadier[2],ft1_grenadier[3],ft1_grenadier[2],ft1_grenadier[3]]
                else:
                    tempState = soldierDict[ft1_grenadier[0]]
                    tempState[2] = ft1_grenadier[2]
                    tempState[3] = ft1_grenadier[3]
                    soldierDict[ft1_grenadier[0]] = tempState
                ft1_avgX += float(ft1_grenadier[2])
                ft1_avgZ += float(ft1_grenadier[3])
                ft1_team.append(ft1_grenadier)
            else:
                if(ft1_grenadier[0] in soldierDict):
                    del soldierDict[ft1_grenadier[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_rpg';")
            ft1_rpg = cursor.fetchone()
            if(ft1_rpg[1] !=1):
                if(initialized):
                    soldierDict[ft1_rpg[0]] = [0,0,ft1_rpg[2],ft1_rpg[3],ft1_rpg[2],ft1_rpg[3],ft1_rpg[2],ft1_rpg[3]]
                else:
                    tempState = soldierDict[ft1_rpg[0]]
                    tempState[2] = ft1_rpg[2]
                    tempState[3] = ft1_rpg[3]
                    soldierDict[ft1_rpg[0]] = tempState
                ft1_avgX += float(ft1_rpg[2])
                ft1_avgZ += float(ft1_rpg[3])
                ft1_team.append(ft1_rpg)
            else:
                if(ft1_rpg[0] in soldierDict):
                    del soldierDict[ft1_rpg[0]]
            
            if(len(ft1_team) >0):
                team_size = len(ft1_team)
                ft1_avgX = ft1_avgX / team_size
                ft1_avgZ = ft1_avgZ / team_size
                
            ft2_team =[]
            ft2_avgX = 0.0
            ft2_avgZ = 0.0
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_rifleman';")
            ft2_rifleman = cursor.fetchone()
            if(ft2_rifleman[1] !=1):
                if(initialized):
                    soldierDict[ft2_rifleman[0]] = [0,0,ft2_rifleman[2],ft2_rifleman[3],ft2_rifleman[2],ft2_rifleman[3],ft2_rifleman[2],ft2_rifleman[3]]
                else:
                    tempState = soldierDict[ft1_rifleman[0]]
                    tempState[2] = ft2_rifleman[2]
                    tempState[3] = ft2_rifleman[3]
                ft2_avgX += float(ft2_rifleman[2])
                ft2_avgZ += float(ft2_rifleman[3])
                ft2_team.append(ft2_rifleman)
            else:
                if(ft2_rifleman[0] in soldierDict):
                    del soldierDict[ft2_rifleman[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_mgunner';")
            ft2_mgunner = cursor.fetchone()
            if(ft2_mgunner[1] !=1):
                if(initialized):
                    soldierDict[ft2_mgunner[0]] = [0,0,ft2_mgunner[2],ft2_rifleman[3],ft2_rifleman[2],ft2_rifleman[3],ft2_rifleman[2],ft2_rifleman[3]]
                else:
                    tempState = soldierDict[ft2_mgunner[0]]
                    tempState[2] = ft2_mgunner[2]
                    tempState[3] = ft2_mgunner[3]
                ft2_avgX += float(ft2_mgunner[2])
                ft2_avgZ += float(ft2_mgunner[3])
                ft2_team.append(ft2_mgunner)
            else:
                if(ft2_mgunner[0] in soldierDict):
                    del soldierDict[ft2_mgunner[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_grenadier';")
            ft2_grenadier = cursor.fetchone()
            if(ft2_grenadier[1] !=1):
                if(initialized):
                    soldierDict[ft2_grenadier[0]] = [0,0,ft2_grenadier[2],ft2_grenadier[3],ft2_grenadier[2],ft2_grenadier[3],ft2_grenadier[2],ft2_grenadier[3]]
                else:
                    tempState = soldierDict[ft2_grenadier[0]]
                    tempState[2] = ft2_grenadier[2]
                    tempState[3] = ft2_grenadier[3]
                ft2_avgX += float(ft2_grenadier[2])
                ft2_avgZ += float(ft2_grenadier[3])
                ft2_team.append(ft2_grenadier)
            else:
                if(ft2_grenadier[0] in soldierDict):
                    del soldierDict[ft2_grenadier[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_rpg';")
            ft2_rpg = cursor.fetchone()
            if(ft2_rpg[1] !=1):
                if(initialized):
                    soldierDict[ft2_rpg[0]] = [0,0,ft2_rpg[2],ft2_rpg[3],ft2_rpg[2],ft2_rpg[3],ft2_rpg[2],ft2_rpg[3]]
                else:
                    tempState = soldierDict[ft2_grenadier[0]]
                    tempState[2] = ft2_grenadier[2]
                    tempState[3] = ft2_grenadier[3]
                ft2_avgX += float(ft2_rpg[2])
                ft2_avgZ += float(ft2_rpg[3])
                ft2_team.append(ft2_rpg)
            else:
                if(ft2_rpg[0] in soldierDict):
                    del soldierDict[ft2_rpg[0]]
            if(len(ft2_team) >0):
                team_size = len(ft2_team)
                ft2_avgX = ft2_avgX / team_size
                ft2_avgZ = ft2_avgZ / team_size
            
            ft3_team =[]
            ft3_avgX = 0.0
            ft3_avgZ = 0.0
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_rifleman';")
            ft3_rifleman = cursor.fetchone()
            if(ft3_rifleman[1] !=1):
                if(initialized):
                    soldierDict[ft3_rifleman[0]] = [0,0,ft3_rifleman[2],ft3_rifleman[3],ft3_rifleman[2],ft3_rifleman[3],ft3_rifleman[2],ft3_rifleman[3]]
                else:
                    tempState = soldierDict[ft3_rifleman[0]]
                    tempState[2] = ft3_rifleman[2]
                    tempState[3] = ft3_rifleman[3]
                ft3_avgX += float(ft3_rifleman[2])
                ft3_avgZ += float(ft3_rifleman[3])
                ft3_team.append(ft3_rifleman)
            else:
                del soldierDict[ft3_rifleman[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_mgunner';")
            ft3_mgunner = cursor.fetchone()
            if(ft3_mgunner[1] !=1):
                if(initialized):
                    soldierDict[ft3_mgunner[0]] = [0,0,ft3_mgunner[2],ft3_mgunner[3],ft3_mgunner[2],ft3_mgunner[3],ft3_mgunner[2],ft3_mgunner[3]]
                else:
                    tempState = soldierDict[ft3_mgunner[0]]
                    tempState[2] = ft3_mgunner[2]
                    tempState[3] = ft3_mgunner[3]
                ft3_avgX += float(ft3_mgunner[2])
                ft3_avgZ += float(ft3_mgunner[3])
                ft3_team.append(ft3_mgunner)
            else:
                if(ft3_mgunner[0] in soldierDict):
                    del soldierDict[ft3_mgunner[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_grenadier';")
            ft3_grenadier = cursor.fetchone()
            if(ft3_grenadier[1] !=1):
                if(initialized):
                    soldierDict[ft3_grenadier[0]] = [0,0,ft3_grenadier[2],ft3_grenadier[3],ft3_grenadier[2],ft3_grenadier[3],ft3_grenadier[2],ft3_grenadier[3]]
                else:
                    tempState = soldierDict[ft3_grenadier[0]]
                    tempState[2] = ft3_grenadier[2]
                    tempState[3] = ft3_grenadier[3]
                ft3_avgX += float(ft3_grenadier[2])
                ft3_avgZ += float(ft3_grenadier[3])
                ft3_team.append(ft3_grenadier)
            else:
                if(ft3_grenadier[0] in soldierDict):
                    del soldierDict[ft3_grenadier[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_rpg';")
            ft3_rpg = cursor.fetchone()
            if(ft3_rpg[1] !=1):
                if(initialized):
                    soldierDict[ft3_rpg[0]] = [0,0,ft3_rpg[2],ft3_rpg[3],ft3_rpg[2],ft3_rpg[3],ft3_rpg[2],ft3_rpg[3]]
                else:
                    tempState = soldierDict[ft3_rpg[0]]
                    tempState[2] = ft3_rpg[2]
                    tempState[3] = ft3_rpg[3]
                ft3_avgX += float(ft3_rpg[2])
                ft3_avgZ += float(ft3_rpg[3])
                ft3_team.append(ft3_rpg)
            else:
                if(ft3_rpg[0] in soldierDict):
                    del soldierDict[ft3_rpg[0]]
                    
            if(len(ft3_team) >0):
                team_size = len(ft2_team)
                ft3_avgX = ft3_avgX / team_size
                ft3_avgZ = ft3_avgZ / team_size
            
            allSeenEnemies = []
            initialized = False
            #get all the enemies that the ft1 team sees
            for soldier in ft1_team:
                cursor.execute("select seenblufor from enemyVisibility where opfor='"+ str(soldier[0]) + " ';")
                seenEnemies = cursor.fetchall()
                for i in seenEnemies:
                    if i not in allSeenEnemies:
                        allSeenEnemies.append(i)
                
                
            for soldier in ft2_team:
                cursor.execute("select seenblufor from enemyVisibility where opfor='"+ str(soldier[0]) + " ';")
                seenEnemies = cursor.fetchall()
                for i in seenEnemies:
                    if i not in allSeenEnemies:
                        allSeenEnemies.append(i)
                        
            for soldier in ft3_team:
                cursor.execute("select seenblufor from enemyVisibility where opfor='"+ str(soldier[0]) + " ';")
                seenEnemies = cursor.fetchall()
                for i in seenEnemies:
                    if i not in allSeenEnemies:
                        allSeenEnemies.append(i)
            
            ft1nextPosReward = {}
            ft2nextPosReward = {}
            ft3nextPosReward = {}
            monteCarloStart= datetime.now()
            global terraindDict
            while(True):
                ft1nextX = ft1_avgX + np.random.uniform(-30,30)
                ft1nextZ = ft1_avgZ + np.random.uniform(-30,30)
                ft2nextX = ft2_avgX + np.random.uniform(-30,30)
                ft2nextZ = ft2_avgZ + np.random.uniform(-30,30)
                ft3nextX = ft3_avgX + np.random.uniform(-30,30)
                ft3nextZ = ft3_avgZ + np.random.uniform(-30,30)
                tempft1X = ft1nextX
                tempft1Z = ft1nextZ
                tempft2X = ft2nextX
                tempft2Z = ft2nextZ
                tempft3X = ft3nextX
                tempft3Z = ft3nextZ
                nextPosReward = 0.0
                enemyLocation = {}
                for t in range(1,5):
                    for enemy in allSeenEnemies:
                        enemyLocation[enemy] = futureLocationRandomize(enemy, 35*(t)) 
                    if(ft1_avgX > 1):
                        nextPosReward += 1*terraindDict[closestXZTerrain(tempft1X,tempft1Z)][2]
                        nextPosReward -= 1*terraindDict[closestXZTerrain(tempft1X,tempft1Z)][0]
                        nextPosReward += 1.1-distanceToFOB(tempft1X, tempft1Z)/780
                    if(ft2_avgX > 1):
                        nextPosReward += 1*terraindDict[closestXZTerrain(tempft2X,tempft2Z)][2]
                        nextPosReward -= 1*terraindDict[closestXZTerrain(tempft2X,tempft2Z)][0]
                        nextPosReward += 1.1-distanceToFOB(tempft2X, tempft2Z)/780
                    if(ft3_avgX > 1):
                        nextPosReward += 1*terraindDict[closestXZTerrain(tempft3X,tempft3Z)][2]
                        nextPosReward -= 1*terraindDict[closestXZTerrain(tempft3X,tempft3Z)][0]
                        nextPosReward += 1.1-distanceToFOB(tempft3X, tempft3Z)/780
                    tempft1X = tempft1X + np.random.uniform(-30,30)
                    tempft1Z = tempft1Z + np.random.uniform(-30,30)
                    tempft2X = tempft2X + np.random.uniform(-30,30)
                    tempft2Z = tempft2Z + np.random.uniform(-30,30)
                    tempft3X = tempft3X + np.random.uniform(-30,30)
                    tempft3Z = tempft3Z + np.random.uniform(-30,30)
                ft1p = str(ft1nextX) + "," + str(ft1nextZ)
                ft2p = str(ft2nextX) + "," + str(ft2nextZ)
                ft3p = str(ft3nextX) + "," + str(ft3nextZ)
                if(ft1p in ft1nextPosReward):
                    tempR = ft1nextPosReward[ft1p]
                    tempR.append(nextPosReward)
                    ft1nextPosReward[ft1p] = tempR
                else:
                    ft1nextPosReward[ft1p] = [nextPosReward]
                
                if(ft2p in ft2nextPosReward):
                    tempR = ft2nextPosReward[ft1p]
                    tempR.append(nextPosReward)
                    ft2nextPosReward[ft2p] = tempR
                else:
                    ft2nextPosReward[ft2p] = [nextPosReward]
                
                if(ft3p in ft3nextPosReward):
                    tempR = ft3nextPosReward[ft3p]
                    tempR.append(nextPosReward)
                    ft3nextPosReward[ft3p] = tempR
                else:
                    ft3nextPosReward[ft3p] = [nextPosReward]
                    
                monteCarloStop = datetime.now()
                delta = monteCarloStop - monteCarloStart 
                currentRunTime = delta.seconds + delta.microseconds/1E6
                if(currentRunTime > 31):
                    break
            #time.sleep(35)
            if(len(ft1nextPosReward) > 0):
                tempBestReward = -100
                tempBestPos = ""
                for pos in ft1nextPosReward:
                    avgReward = sum(ft1nextPosReward[pos])*1.0/len(ft1nextPosReward[pos])
                    if(avgReward > tempBestReward):
                        tempBestReward = avgReward
                        tempBestPos = pos
                newXZ = tempBestPos.split(",")
                soldierid = continueAssault(soldierDict, "ft1", float(newXZ[0]), float(newXZ[1]), soldierid)
                
            if(len(ft2nextPosReward) > 0):
                tempBestReward = -100
                tempBestPos = ""
                for pos in ft2nextPosReward:
                    avgReward = sum(ft2nextPosReward[pos])*1.0/len(ft2nextPosReward[pos])
                    if(avgReward > tempBestReward):
                        tempBestReward = avgReward
                        tempBestPos = pos
                newXZ = tempBestPos.split(",")
                soldierid = continueAssault(soldierDict, "ft2", float(newXZ[0]), float(newXZ[1]), soldierid)
                
            if(len(ft3nextPosReward) > 0):
                tempBestReward = -100
                tempBestPos = ""
                for pos in ft3nextPosReward:
                    avgReward = sum(ft3nextPosReward[pos])*1.0/len(ft3nextPosReward[pos])
                    if(avgReward > tempBestReward):
                        tempBestReward = avgReward
                        tempBestPos = pos
                newXZ = tempBestPos.split(",")
                soldierid = continueAssault(soldierDict, "ft3", float(newXZ[0]), float(newXZ[1]), soldierid)
            
            
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
        print("hi")
        print(xEnemy)
        print(zEnemy)
        print(xTeam)
        print(zTeam)
        
        #finds the slope of the line of best fit
        slope = 0.0
        squared=0.0
        for i in range(len(xEnemy)):
            slope+= (xEnemy[i]-averageX) * (zEnemy[i]-averageZ)
            squared+=(xEnemy[i]-averageX) * (xEnemy[i]-averageX)
        slope = slope/squared
        del squared

        b = averageZ - slope*averageX
        print(slope)
        print(b)
        print("hi")
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
        print(friendlyB)
        print("hi")
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
 
def continueAssault (soldierDict, fireteam, targetX, targetZ, soldierid):
    
    
    # Check if every soldier is at the target location = selectedSoldArray[4],selectedSoldArray[5] if true all soldiers weapons free
    filtered_dict = {k:v for (k,v) in soldierDict.items() if fireteam in k}
    allMoving = 0
    soldiers = []
    randomUnit =0
    cursor = connection.cursor()
    if len(filtered_dict)>0:
        selectedSoldier = []
        occupyingSoldier = []
        
        for key in filtered_dict:
            print(filtered_dict[key][1])
            if(filtered_dict[key][1] == 1):
                allMoving = 1 
        
        for key in filtered_dict:
            soldiers.append(key)
        #randomly assign to move or cover
        if len(soldiers) == 4:
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
        else:
            occupyingSoldier.append[soldiers[0]]
        if(allMoving == 0):
            #gets current positoin of soldiers
            xzPos=[]
            for sol in selectedSoldier:
                
                getPos = "select px,pz from opforpositiondata where unit_name='" + sol + "';"
                cursor.execute(getPos)
                positionList = cursor.fetchone()
                xzPos.append(positionList)
            for sol in occupyingSoldier:
                cursor = connection.cursor()
                getPos = "select px,pz from opforpositiondata where unit_name='" + sol + "';"
                cursor.execute(getPos)
                positionList = cursor.fetchone()
                xzPos.append(positionList)
        
           
            #soldiers move and occupy
            i = 0
            newsoldierDict={}
            for sol in selectedSoldier:
                selectedSoldArray = soldierDict.get(sol)
                newPosition1 = newAssaultPoint(targetX,targetZ, float(xzPos[i][0]), float(xzPos[i][1]))
                soldier1positionString = "'" + str(round(newPosition1[0])) + ";" + "3.9" + ";" + str(round(newPosition1[1])) + "'"
                soldier1Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + sol + "', 'move'," + soldier1positionString + ");"
                soldierid+=1
                cursor.execute(soldier1Move)
                soldier1HoldFire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'change_roe', '2');"
                soldierid+=1
                cursor.execute(soldier1HoldFire)
                connection.commit()
                newsoldierDict[sol] = [0,1,xzPos[i][0],xzPos[i][1],targetX,targetZ,newPosition1[0],newPosition1[1]]
                i+=1

            for sol in occupyingSoldier:
                soldier3positionString = "'" + xzPos[i][0] + ";" + "3.9" + ";" + xzPos[i][1] + "'"
                soldier3Fire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('"  + str(soldierid) + "','" + sol + "', 'change_roe', '0');"
                soldierid+=1
                soldier3Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('"  + str(soldierid) + "','" + sol + "', 'move'," + soldier3positionString + ");"
                soldierid+=1
                cursor.execute(soldier3Fire)
                cursor.execute(soldier3Move)
                connection.commit()
                newsoldierDict[sol] = [0,0,xzPos[i][0],xzPos[i][1],targetX,targetZ,xzPos[i][0],xzPos[i][1]]
                i+=1
             #update soldierDict with the new dictionary
            
            soldierDict.update(newsoldierDict)
        
        else:
            for key in filtered_dict:
                soldiers.append(key)

            print(filtered_dict)
            occupyingSoldier =[]
            selectedSoldier =[]
            for sol in soldiers:
                print("**********************")
                tempSoldierValue = filtered_dict.get(sol)
                moveOrOccupy = tempSoldierValue[1]
                if(moveOrOccupy == 0):
                    occupyingSoldier.append(sol)
                else:
                    selectedSoldier.append(sol)

                    
            #if the soldiers are not all holding
            #call newassaultpoint
            #make the soldiers that were holding move and the soldiers that were moving hold
            xzPos =[]
            newsoldierDict={}
            for sol in occupyingSoldier:
                getPos1 = "select px,pz from opforpositiondata where unit_name='" + sol + "';"
                cursor.execute(getPos1)
                positionList = cursor.fetchone()
                soldier1position = newAssaultPoint(targetX, targetZ, float(positionList[0]), float(positionList[1]))
                soldier1positionString = "'" + str(round(soldier1position[0])) + ";" + "3.9" + ";" + str(round(soldier1position[1])) + "'"
                soldier1HoldFire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'change_roe', '2');"
                soldierid+=1
                soldier1Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'move'," + soldier1positionString + ");"
                soldierid+=1
                cursor.execute(soldier1HoldFire)
                connection.commit()
                cursor.execute(soldier1Move)
                connection.commit()
                newsoldierDict[sol]= [0,0,positionList[0],positionList[1],targetX,targetZ,soldier1position[0],soldier1position[1]]

            for sol in selectedSoldier:
                getPos1 = "select px,pz from opforpositiondata where unit_name='" + sol + "';"
                cursor.execute(getPos1)
                positionList = cursor.fetchone()
                soldier3positionString = "'" + positionList[0] + ";" + "3.9" + ";" + positionList[1] + "'"
                soldier3Fire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'change_roe', '0');"
                soldierid+=1
                cursor.execute(soldier3Fire)
                connection.commit()
                newsoldierDict[sol]= [0,1,positionList[0],positionList[1],targetX,targetZ,positionList[0],positionList[1]]
        
            soldierDict.update(newsoldierDict)
    return soldierid

def continueAssault2 (soldierDict, fireteam, targetX, targetZ):
    
    
    # Check if every soldier is at the target location = targetX, targetZ if true all soldiers weapons free
    #filter the dicitonary by fireteam
    filtered_dict = {k:v for (k,v) in soldierDict.items() if fireteam in k}
    allMoving = 0
    soldiers = []
    randomUnit =0
    print("&&&&&&&&&&&&&&&&&&")
    print(soldierDict)
    print("&&&&&&&&&&&&&&&&&&")
    selectedSoldier1 = ""
    selectedSoldier2 = ""
    occupyingSoldier1 = ""
    occupyingSoldier2 = ""
    #check to see the action of each soldier and assign soldier based on it
    for key in filtered_dict:
        print(filtered_dict[key][1])
        if(filtered_dict[key][1] == 1):
            allMoving = 1 
    if(allMoving == 0):
        print("yo")
        for key in filtered_dict:
            soldiers.append(key)
        randomUnit =random.randint(0, len(soldiers)-1)
        selectedSoldier1 = soldiers[randomUnit]
        soldiers.remove(selectedSoldier1)
        randomUnit =random.randint(0, len(soldiers)-1)
        selectedSoldier2 = soldiers[randomUnit]
        soldiers.remove(selectedSoldier2)
        randomUnit =random.randint(0, len(soldiers)-1)
        occupyingSoldier1 = soldiers[randomUnit]
        soldiers.remove(occupyingSoldier1)
        randomUnit =random.randint(0, len(soldiers)-1)
        occupyingSoldier2 = soldiers[randomUnit]
        soldiers.remove(occupyingSoldier2)
    else:
        print("&&&&&&&&&&&&&&&&&&")
        for key in filtered_dict:
            soldiers.append(key)
        numbOccupiedSoldiers = 0
        numbMovingSoldiers = 0
        print(filtered_dict)
        for i in range(4):
            print("**********************")
            tempSoldier = soldiers[i]
            tempSoldierValue = filtered_dict.get(tempSoldier)
            moveOrOccupy = tempSoldierValue[1]
            if(moveOrOccupy == 0):
                print("@@@@@@@@@@@@@")
                if(numbOccupiedSoldiers == 0 ):
                    occupyingSoldier1 = tempSoldier
                    numbOccupiedSoldiers+=1
                else:
                    occupyingSoldier2 = tempSoldier
            else:
                print("!!!!!!!!!!!!!!")
                if(numbMovingSoldiers == 0):
                    selectedSoldier1 = tempSoldier
                    #print("selected")
                    numbMovingSoldiers+=1
                else:
                    selectedSoldier2 = tempSoldier
    #print("@@@@@@@@@@@@@")
    #print(selectedSoldier1)
    #print(selectedSoldier2)
    #print(occupyingSoldier1)
    #print(occupyingSoldier2)
    #print("@@@@@@@@@@@@@")
    #get the most current positions of the soldiers 
    cursor = connection.cursor()
    getPos1 = "select px,pz from opforpositiondata where unit_name='" + selectedSoldier1 + "' order by timestamp desc limit 1;"
    cursor.execute(getPos1)
    soldier1position = cursor.fetchone()
    getPos2 = "select px,pz from opforpositiondata where unit_name='" + selectedSoldier2 + "' order by timestamp desc limit 1;"
    cursor.execute(getPos2)
    soldier2position = cursor.fetchone()
    getPos3 = "select px,pz from opforpositiondata where unit_name='" + occupyingSoldier1 + "' order by timestamp desc limit 1;"
    cursor.execute(getPos3)
    soldier3position = cursor.fetchone()
    getPos4 = "select px,pz from opforpositiondata where unit_name='" + occupyingSoldier2 + "' order by timestamp desc limit 1;"
    cursor.execute(getPos4)
    soldier4position = cursor.fetchone()

    
    """
    if((abs(float(soldier1position[0]) - targetX) <=15   and abs(float(soldier2position[0]) - targetX) <=15 and abs(float(soldier3position[0]) - targetX) <=15 and abs(float(soldier4position[0]) - targetX) <=15)
  and (abs(float(soldier1position[1]) - targetZ) <=15 and abs(float(soldier2position[1]) - targetZ) <=15 and abs(float(soldier3position[1]) - targetZ) <=15 and abs(float(soldier4position[1]) - targetZ) <=15)):
        soldier1Fire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (0, '" + occupyingSoldier1 + "', 'change_roe', '0');"
        soldier2Fire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (1, '" + occupyingSoldier2 + "', 'change_roe', '0');"
        soldier3Fire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (2, '" + selectedSoldier1 + "', 'change_roe', '0');"
        soldier4Fire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (3, '" + selectedSoldier2 + "', 'change_roe', '0');"
        cursor.execute(soldier1Fire)
        connection.commit()
        cursor.execute(soldier2Fire)
        connection.commit()
        cursor.execute(soldier3Fire)
        connection.commit()
        cursor.execute(soldier4Fire)
        connection.commit()
        return
    """
    print(getPos4)
    print(soldier3position)
    #get the data of selected soldier 
    selectedSoldArray = soldierDict.get(selectedSoldier1)
    selectedSoldArray2 = soldierDict.get(selectedSoldier2)
    #calculate their new position
    newPosition1 = newAssaultPoint(targetX, targetZ, float(soldier1position[0]), float(soldier1position[1]))
    newPosition2 = newAssaultPoint(targetX, targetZ, float(soldier2position[0]), float(soldier2position[1]))
    print(soldier3position)   
    #create their position strings to be inserted
    soldier1positionString = "'" + str(round(newPosition1[0])) + ";" + "3.9" + ";" + str(round(newPosition1[1])) + "'"
    print(soldier2position)
    soldier2positionString = "'" + str(round(newPosition2[0])) + ";" + "3.9" + ";" + str(round(newPosition2[1])) + "'"
    print(soldier3position)
    soldier3positionString = "'" + soldier3position[0] + ";" + "3.9" + ";" + soldier3position[1] + "'"
    print(soldier4position)
    soldier4positionString = "'" + soldier4position[0] + ";" + "3.9" + ";" + soldier4position[1] + "'"
    if(allMoving == 0):
        #soldiers move 2 at a time if the are all still, create soldier commands strings to be insereted into soldiercommand 
        soldier1Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (4, '" + selectedSoldier1 + "', 'move'," + soldier1positionString + ");"
        soldier2Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (5, '" + selectedSoldier2 + "', 'move'," + soldier2positionString + ");"
        soldier3HoldFire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (6, '" + occupyingSoldier1 + "', 'change_roe', '2');"
        soldier3Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (7, '" + occupyingSoldier1 + "', 'move'," + soldier3positionString + ");"
        soldier4HoldFire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (8, '" + occupyingSoldier2 + "', 'change_roe', '2');"
        soldier4Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (9, '" + occupyingSoldier2 + "', 'move'," + soldier4positionString + ");"
        #execute the strings created earlier on the database
        cursor.execute(soldier1Move)
        connection.commit()
        cursor.execute(soldier2Move)
        connection.commit()
        cursor.execute(soldier3HoldFire)
        cursor.execute(soldier3Move)
        connection.commit()
        cursor.execute(soldier4HoldFire)
        connection.commit()
        cursor.execute(soldier4Move)
        connection.commit()
        print(avgPosX, avgPosZ)
        #create a dict with the new soldier data actions and positions
        newsoldierDict = { selectedSoldier1 : [0,1,soldier1position[0],soldier1position[1],selectedSoldArray[4],selectedSoldArray[5],newPosition1[0],newPosition1[1]],
                       selectedSoldier2 : [0,1,soldier2position[0],soldier2position[1],selectedSoldArray[4],selectedSoldArray[5],newPosition2[0],newPosition2[1]],
                       occupyingSoldier1 : [0,0,soldier3position[0],soldier3position[1],selectedSoldArray[4],selectedSoldArray[5],soldier3position[0],soldier3position[1]],
                       occupyingSoldier2 : [0,0,soldier4position[0],soldier4position[1],selectedSoldArray[4],selectedSoldArray[5],soldier4position[0],soldier4position[1]]}  
        #update soldierDict with the new dictionary
        soldierDict.update(newsoldierDict)
        print("yolodololololol")
        print (soldierDict)
        print("yolodololololol")
        #soldierDict = newsoldierDict
        #print(newsoldierDict)
    else:
        #if the soldiers are not all holding
        #call newassaultpoint
        #make the soldiers that were holding move and the soldiers that were moving hold
        getPos1 = "select px,pz from opforpositiondata where unit_name='" + occupyingSoldier1 + "' order by timestamp desc limit 1;"
        cursor.execute(getPos1)
        soldier1position = cursor.fetchone()
        getPos2 = "select px,pz from opforpositiondata where unit_name='" + occupyingSoldier2 + "' order by timestamp desc limit 1;"
        cursor.execute(getPos2)
        soldier2position = cursor.fetchone()
        #call newassaultpoint
        soldier1position = newAssaultPoint(targetX, targetZ, float(soldier1position[0]), float(soldier1position[1]))
        soldier2position = newAssaultPoint(targetX, targetZ, float(soldier2position[0]), float(soldier2position[1]))
        '''
        getPos3 = "select px,pz from opforpositiondata where unit_name='" + selectedSoldier1 + "' order by timestamp desc limit 1;"
        cursor.execute(getPos3)
        soldier3position = cursor.fetchone()
        getPos4 = "select px,pz from opforpositiondata where unit_name='" + selectedSoldier2 + "' order by timestamp desc limit 1;"
        cursor.execute(getPos4)
        soldier4position = cursor.fetchone()
        
        '''
        
        selectedSoldArray = soldierDict.get(occupyingSoldier1)
        selectedSoldArray2 = soldierDict.get(occupyingSoldier2)
        
        newPosition1 = newAssaultPoint(selectedSoldArray[4],selectedSoldArray[5], float(soldier1position[0]), float(soldier1position[1]))
        newPosition2 = newAssaultPoint(selectedSoldArray2[4],selectedSoldArray2[5], float(soldier2position[0]), float(soldier2position[1]))
           
        soldier1positionString = "'" + str(round(newPosition1[0])) + ";" + "3.9" + ";" + str(round(newPosition1[1])) + "'"
        soldier2positionString = "'" + str(round(newPosition2[0])) + ";" + "3.9" + ";" + str(round(newPosition2[1])) + "'"
        soldier3positionString = "'" + soldier3position[0] + ";" + "3.9" + ";" + soldier3position[1] + "'"
        soldier4positionString = "'" + soldier4position[0] + ";" + "3.9" + ";" + soldier4position[1] + "'"
        
        soldier1Fire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (10, '" + occupyingSoldier1 + "', 'change_roe', '0');"
        soldier2Fire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (11, '" + occupyingSoldier2 + "', 'change_roe', '0');"
        soldier1Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (12, '" + occupyingSoldier1 + "', 'move'," + soldier1positionString + ");"
        soldier2Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (13, '" + occupyingSoldier2 + "', 'move'," + soldier2positionString + ");"
        soldier3HoldFire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (14, '" + selectedSoldier1 + "', 'change_roe', '2');"
        #soldier3Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (15, '" + selectedSoldier1 + "', 'move'," + soldier3positionString + ");"
        soldier4HoldFire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (16, '" + selectedSoldier2 + "', 'change_roe', '2');"
        #soldier4Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (17, '" + selectedSoldier2 + "', 'move'," + soldier4positionString + ");"
        cursor.execute(soldier1Fire)
        connection.commit()
        cursor.execute(soldier2Fire)
        connection.commit()
        cursor.execute(soldier1Move)
        connection.commit()
        cursor.execute(soldier2Move)
        connection.commit()
        cursor.execute(soldier3HoldFire)
        #cursor.execute(soldier3Move)
        connection.commit()
        cursor.execute(soldier4HoldFire)
        connection.commit()
        #cursor.execute(soldier4Move)
        connection.commit()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(soldier1Move)
        print(soldier2Move)
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(avgPosX, avgPosZ)
        newsoldierDict = { occupyingSoldier1 : [0,1,soldier1position[0],soldier1position[1],selectedSoldArray[4],selectedSoldArray[5],newPosition1[0],newPosition1[1]],
                       occupyingSoldier2 : [0,1,soldier2position[0],soldier2position[1],selectedSoldArray[4],selectedSoldArray[5],newPosition2[0],newPosition2[1]],
                       selectedSoldier1 : [0,0,soldier3position[0],soldier3position[1],selectedSoldArray[4],selectedSoldArray[5],soldier3position[0],soldier3position[1]],
                       selectedSoldier2 : [0,0,soldier4position[0],soldier4position[1],selectedSoldArray[4],selectedSoldArray[5],soldier4position[0],soldier4position[1]]}  
        soldierDict.update(newsoldierDict)
        print("yolodololololol")
        print (soldierDict)
        print("yolodolololo.lol")
        #soldierDict.update(newsoldierDict)
        #soldierDict = newsoldierDict
    return soldierDict

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

def  futureLocationRandomize(enemy, time):
    cursor = connection.cursor()
    #get the data of the seen enemy position and velocity
    getEnemyData = "select px, py, pz, vx, vy, vz from blueforpositiondata where unit_name='" + enemy + "' order by timestamp desc limit 1;"
    cursor.execute(getEnemyData)
    getEnemyPositions = cursor.fetchone()
    connection.commit()
    print(getEnemyData)
    print(getEnemyPositions)
    
    #randomizes movements
    vxRandom = random.random()
    if random.random() <.5:
        vxRandom=vxRandom*-1
    
    vyRandom = random.random()
    if random.random() <.5:
        vyRandom=vyRandom*-1
    
    vzRandom = random.random()
    vzRandom=vzRandom*-1

    #calculate the new positions 
    newPx = float(getEnemyPositions[0]) + float(getEnemyPositions[3])*time*vxRandom
    newPy = getEnemyPositions[1] + getEnemyPositions[4]*time*vyRandom
    newPz = getEnemyPositions[2] + getEnemyPositions[5]*time*vzRandom
    
    newPosition = [newPx,newPy, newPz]
    return newPosition  

def futureLocation(enemy, time): 
    cursor = connection.cursor()
    #get the data of the seen enemy position and velocity
    getEnemyData = "select px, py, pz, vx, vy, vz from blueforpositiondata where unit_name='" + enemy[2] + "' order by timestamp desc limit 1;"
    cursor.execute(getEnemyData)
    getEnemyPositions = cursor.fetchone()
    connection.commit()
    print(getEnemyData)
    print(getEnemyPositions)
    #calculate the new positions 
    newPx = float(getEnemyPositions[0]) + float(getEnemyPositions[3])*time
    newPy = getEnemyPositions[1] + getEnemyPositions[4]*time
    newPz = getEnemyPositions[2] + getEnemyPositions[5]*time
    #create dictionary with the new predicted positions 
    newPosition = { enemy[2] : [newPx,newPy, newPz]}
    return newPosition   
  
    
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
