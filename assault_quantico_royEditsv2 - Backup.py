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
import copy


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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_lead' order by timestamp desc limit 1;")
            ft1_lead = cursor.fetchone()
            if(float(ft1_lead[1]) < 1):
                if(initialized):
                    soldierDict[ft1_lead[0]] = [0,0,ft1_lead[2],ft1_lead[3],ft1_lead[2],ft1_lead[3],ft1_lead[2],ft1_lead[3]]
                else:
                    tempState = soldierDict[ft1_lead[0]]
                    tempState[2] = ft1_lead[2]
                    tempState[3] = ft1_lead[3]
                    soldierDict[ft1_lead[0]] = tempState
                ft1_avgX += float(ft1_lead[2])
                ft1_avgZ += float(ft1_lead[3])
                ft1_team.append(ft1_lead)
            else:
                if(ft1_lead[0] in soldierDict):
                    del soldierDict[ft1_lead[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_rifleman' order by timestamp desc limit 1;")
            ft1_rifleman = cursor.fetchone()
            if(float(ft1_rifleman[1]) < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_mgunner' order by timestamp desc limit 1;")
            ft1_mgunner = cursor.fetchone()
            if(float(ft1_mgunner[1]) < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_grenadier' order by timestamp desc limit 1;")
            ft1_grenadier = cursor.fetchone()
            if(float(ft1_grenadier[1]) < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft1_rpg' order by timestamp desc limit 1;")
            ft1_rpg = cursor.fetchone()
            if(float(ft1_rpg[1]) < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_rifleman' order by timestamp desc limit 1;")
            ft2_rifleman = cursor.fetchone()
            if(float(ft2_rifleman[1]) < 1):
                if(initialized):
                    soldierDict[ft2_rifleman[0]] = [0,0,ft2_rifleman[2],ft2_rifleman[3],ft2_rifleman[2],ft2_rifleman[3],ft2_rifleman[2],ft2_rifleman[3]]
                else:
                    tempState = soldierDict[ft2_rifleman[0]]
                    tempState[2] = ft2_rifleman[2]
                    tempState[3] = ft2_rifleman[3]
                ft2_avgX += float(ft2_rifleman[2])
                ft2_avgZ += float(ft2_rifleman[3])
                ft2_team.append(ft2_rifleman)
            else:
                if(ft2_rifleman[0] in soldierDict):
                    del soldierDict[ft2_rifleman[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_mgunner' order by timestamp desc limit 1;")
            ft2_mgunner = cursor.fetchone()
            if(float(ft2_mgunner[1])  < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_grenadier' order by timestamp desc limit 1;")
            ft2_grenadier = cursor.fetchone()
            if(float(ft2_grenadier[1]) < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft2_rpg' order by timestamp desc limit 1;")
            ft2_rpg = cursor.fetchone()
            if(float(ft2_rpg[1]) < 1):
                if(initialized):
                    soldierDict[ft2_rpg[0]] = [0,0,ft2_rpg[2],ft2_rpg[3],ft2_rpg[2],ft2_rpg[3],ft2_rpg[2],ft2_rpg[3]]
                else:
                    tempState = soldierDict[ft2_rpg[0]]
                    tempState[2] = ft2_rpg[2]
                    tempState[3] = ft2_rpg[3]
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_rifleman' order by timestamp desc limit 1;")
            ft3_rifleman = cursor.fetchone()
            if(float(ft3_rifleman[1]) < 1):
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
                if(ft3_rifleman[0] in soldierDict):
                    del soldierDict[ft3_rifleman[0]]
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_mgunner' order by timestamp desc limit 1;")
            ft3_mgunner = cursor.fetchone()
            if(float(ft3_mgunner[1]) < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_grenadier' order by timestamp desc limit 1;")
            ft3_grenadier = cursor.fetchone()
            if(float(ft3_grenadier[1]) < 1):
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
            cursor.execute("select unit_name, health, px, pz from opforpositiondata where unit_name='ft3_rpg' order by timestamp desc limit 1;")
            ft3_rpg = cursor.fetchone()
            if(float(ft3_rpg[1]) < 1):
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
                team_size = len(ft3_team)
                ft3_avgX = ft3_avgX / team_size
                ft3_avgZ = ft3_avgZ / team_size
            
            allSeenEnemies = []
            initialized = False
            #get all the enemies that the ft1 team sees
            for soldier in ft1_team:
                cursor.execute("select seenblufor from enemyVisibility where opfor='"+ str(soldier[0]) + "';")
                seenEnemies = cursor.fetchall()
                for i in seenEnemies:
                    en = i[0]
                    if en not in allSeenEnemies:
                        allSeenEnemies.append(en)
                
                
            for soldier in ft2_team:
                cursor.execute("select seenblufor from enemyVisibility where opfor='"+ str(soldier[0]) + "';")
                seenEnemies = cursor.fetchall()
                for i in seenEnemies:
                    en = i[0]
                    if en not in allSeenEnemies:
                        allSeenEnemies.append(en)
                        
            for soldier in ft3_team:
                cursor.execute("select seenblufor from enemyVisibility where opfor='"+ str(soldier[0]) + "';")
                seenEnemies = cursor.fetchall()
                for i in seenEnemies:
                    en = i[0]
                    if en not in allSeenEnemies:
                        allSeenEnemies.append(en)
            
            ft1nextPosReward = {}
            ft2nextPosReward = {}
            ft3nextPosReward = {}
            ft1Size = len(ft1_team)
            ft2Size = len(ft2_team)
            ft3Size = len(ft3_team)
            monteCarloStart= datetime.now()
            global terraindDict
            daCount = 0
            '''
            soldierid = continueAssault(soldierDict, "ft2", 1233, 1004, soldierid)
            soldierid = continueAssault(soldierDict, "ft1", 1327, 954, soldierid)
            soldierid = continueAssault(soldierDict, "ft3", 15201, 1004, soldierid)
            time.sleep(30)
            soldierid = continueAssault(soldierDict, "ft2", 1128, 1046, soldierid)
            soldierid = continueAssault(soldierDict, "ft1", 1233, 1004, soldierid)
            soldierid = continueAssault(soldierDict, "ft3", 15201, 1046, soldierid)
            '''
            while(True):
                daCount+=1
                ft1nextX = round(ft1_avgX + np.random.uniform(-40,40), 0)
                ft1nextZ = round(ft1_avgZ + np.random.uniform(-40,40), 0)
                ft2nextX = round(ft2_avgX + np.random.uniform(-40,40), 0)
                ft2nextZ = round(ft2_avgZ + np.random.uniform(-40,40), 0)
                ft3nextX = round(ft3_avgX + np.random.uniform(-40,40), 0)
                ft3nextZ = round(ft3_avgZ + np.random.uniform(-40,40), 0)
                #print("@$$%@%@%%$%")
                #print(ft1nextX, ft1nextZ)
                tempft1X = ft1nextX
                tempft1Z = ft1nextZ
                tempft2X = ft2nextX
                tempft2Z = ft2nextZ
                tempft3X = ft3nextX
                tempft3Z = ft3nextZ              
                nextPosReward = 0.0
                nextPosRewardft1 = 0.0
                nextPosRewardft2 = 0.0
                nextPosRewardft3 = 0.0
                enemyLocation = {}
                for enemy in allSeenEnemies:
                    enemyLocation[enemy] = futureLocationInital(enemy, 5)
                
                
                for t in range(1,2):
                    initalSeenEnemy = len(enemyLocation)
                    preditedFuture = futureOutComes(enemyLocation,tempft1X,tempft1Z,ft1Size,tempft2X,tempft2Z,ft2Size,tempft3X,tempft3Z,ft3Size)
                    enemyLocation =preditedFuture[0]
                    
                    ft1Size=preditedFuture[1]
                    ft2Size=preditedFuture[2]
                    ft3Size = preditedFuture[3]
                    killedEnemy = initalSeenEnemy - len(enemyLocation)
                    for enemy in enemyLocation:
                        enemyLocation[enemy] = futureLocationRandomize(enemy, enemyLocation, 5) 
                    
                    nextPosReward -= (1- (ft1Size+ft2Size+ft3Size)/13)
                    #print(ft1Size+ft2Size+ft3Size)
                    nextPosReward += killedEnemy
                    nextPosRewardft1 += 1.1-(distanceToFOB(tempft1X, tempft1Z))/780 
                    nextPosRewardft2 += 1.1-(distanceToFOB(tempft2X, tempft2Z))/780 
                    nextPosRewardft3 += 1.1-(distanceToFOB(tempft3X, tempft3Z))/780 
                    #print(killedEnemy)
                    tempft1X = tempft1X + np.random.uniform(-40,40)
                    tempft1Z = tempft1Z + np.random.uniform(-40,40)
                    tempft2X = tempft2X + np.random.uniform(-40,40)
                    tempft2Z = tempft2Z + np.random.uniform(-40,40)
                    tempft3X = tempft3X + np.random.uniform(-40,40)
                    tempft3Z = tempft3Z + np.random.uniform(-40,40)
                ft1p = str(round(ft1nextX,0)) + "," + str(round(ft1nextZ, 0))
                ft2p = str(round(ft2nextX, 0)) + "," + str(round(ft2nextZ, 0))
                ft3p = str(round(ft3nextX, 0)) + "," + str(round(ft3nextZ, 0))
                if(ft1p in ft1nextPosReward):
                    tempR = ft1nextPosReward[ft1p]
                    tempR.append(nextPosRewardft1)
                    ft1nextPosReward[ft1p] = tempR
                else:
                    ft1nextPosReward[ft1p] = [nextPosRewardft1]
                
                if(ft2p in ft2nextPosReward):
                    tempR = ft2nextPosReward[ft2p]
                    tempR.append(nextPosRewardft2)
                    ft2nextPosReward[ft2p] = tempR
                else:
                    ft2nextPosReward[ft2p] = [nextPosRewardft2]
                
                if(ft3p in ft3nextPosReward):
                    tempR = ft3nextPosReward[ft3p]
                    tempR.append(nextPosRewardft3)
                    ft3nextPosReward[ft3p] = tempR
                else:
                    ft3nextPosReward[ft3p] = [nextPosRewardft3]
                   
                monteCarloStop = datetime.now()
                delta = monteCarloStop - monteCarloStart 
                currentRunTime = delta.seconds + delta.microseconds/1E6
                if(currentRunTime > 5):
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
                print("*******************************************************")
                print(str(ft3_avgX)+","+str(ft3_avgZ))
                print(tempBestPos)
                print(str(1.1-(distanceToFOB(float(newXZ[0]), float(newXZ[1]))/4)/780 ))
                print(tempBestReward)
                print("*******************************************************")
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
            if(filtered_dict[key][1] == 1):
                allMoving = 1 
        
        for key in filtered_dict:
            soldiers.append(key)
        #randomly assign to move or cover
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
            print(soldiers)
            occupyingSoldier.append(soldiers[0])
        else:
            return
        if(allMoving == 0):
            #gets current positoin of soldiers
            xzPos=[]
           
            for sol in selectedSoldier:
                
                getPos = "select px,pz from opforpositiondata where unit_name='" + sol + "' order by timestamp desc limit 1;"
                cursor.execute(getPos)
                positionList = cursor.fetchone()
                xzPos.append(positionList)
            for sol in occupyingSoldier:
                cursor = connection.cursor()
                getPos = "select px,pz from opforpositiondata where unit_name='" + sol + "' order by timestamp desc limit 1;"
                cursor.execute(getPos)
                positionList = cursor.fetchone()
                xzPos.append(positionList)
        
           
            #soldiers move and occupy
            i = 0
            newsoldierDict={}
            for sol in selectedSoldier:
                selectedSoldArray = soldierDict.get(sol)
                newPosition1 = newAssaultPoint(targetX,targetZ, float(xzPos[i][0]), float(xzPos[i][1]))
                soldier1positionString = "'" + str(round(targetX) + np.random.uniform(-5,5)) + ";" + "3.9" + ";" + str(round(targetZ) + np.random.uniform(-5,5)) + "'"
                soldier1Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + sol + "', 'move'," + soldier1positionString + ");"
                soldierid+=1
                print(soldier1Move)
                cursor.execute(soldier1Move)
                soldier1Fire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'change_roe', '2');"
                soldierid+=1
                cursor.execute(soldier1Fire)
                connection.commit()
                newsoldierDict[sol] = [0,1,xzPos[i][0],xzPos[i][1],targetX,targetZ,targetX,targetZ]
                i+=1

            for sol in occupyingSoldier:
                soldier3positionString = "'" + xzPos[i][0] + ";" + "3.9" + ";" + xzPos[i][1] + "'"
                soldier3Fire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('"  + str(soldierid) + "','" + sol + "', 'change_roe', '0');"
                soldierid+=1
                soldier3Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('"  + str(soldierid) + "','" + sol + "', 'move'," + soldier3positionString + ");"
                soldierid+=1
                cursor.execute(soldier3Fire)
                print(soldier3Move)
                cursor.execute(soldier3Move)
                connection.commit()
                newsoldierDict[sol] = [0,0,xzPos[i][0],xzPos[i][1],targetX,targetZ,xzPos[i][0],xzPos[i][1]]
                i+=1
            #update soldierDict with the new dictionary
            
            soldierDict.update(newsoldierDict)
        
        else:
            for key in filtered_dict:
                soldiers.append(key)

            occupyingSoldier =[]
            selectedSoldier =[]
            for sol in soldiers:
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
                soldier1positionString = "'" + str(round(targetX) + np.random.uniform(-5,5)) + ";" + "3.9" + ";" + str(round(targetZ) + + np.random.uniform(-5,5)) + "'"
                soldier1Fire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'change_roe', '2');"
                soldierid+=1
                soldier1Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'move'," + soldier1positionString + ");"
                soldierid+=1
                cursor.execute(soldier1Fire)
                connection.commit()
                print(soldier1Move)
                cursor.execute(soldier1Move)
                connection.commit()
                newsoldierDict[sol]= [0,1,positionList[0],positionList[1],targetX,targetZ,targetX,targetZ]
            for sol in selectedSoldier:
                getPos1 = "select px,pz from opforpositiondata where unit_name='" + sol + "';"
                cursor.execute(getPos1)
                positionList = cursor.fetchone()
                soldier3positionString = "'" + positionList[0] + ";" + "3.9" + ";" + positionList[1] + "'"
                soldier3Fire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'change_roe', '0');"
                soldierid+=1
                cursor.execute(soldier3Fire)
                connection.commit()
                newsoldierDict[sol]= [0,0,positionList[0],positionList[1],targetX,targetZ,positionList[0],positionList[1]]
                
            soldierDict.update(newsoldierDict)
          
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

def  futureLocationRandomize(enemy, enemyLocationTemp, time):
    tempPositionVar = enemyLocationTemp[enemy]

    vxRandom=random.random()
    if random.random() <.5:
        vxRandom=vxRandom*-1
    
    vyRandom = random.random()
    if random.random() <.5:
        vyRandom=vyRandom*-1
    
    vzRandom = random.random()
    if random.random() <.5:
        vzRandom=vzRandom*-1 

    newPx = float(tempPositionVar[0]) + float(tempPositionVar[3])*time*vxRandom
    newPy = float(tempPositionVar[1]) + float(tempPositionVar[4])*time*vyRandom
    newPz = float(tempPositionVar[2]) + float(tempPositionVar[5])*time*vzRandom

    #returns new estimated position
    return [newPx,newPy, newPz, float(tempPositionVar[3])*vxRandom, float(tempPositionVar[4])*vyRandom, float(tempPositionVar[5])*vzRandom]



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
    
def distanceBetweenPoints(X1,Z1,X2, Z2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Z1- Z2, 2))
    return dis        

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
    if(var1 < 0 or var2 < 0 ):
        print("##############################")
        print (str(var1) +","+str(var2))
        print("##############################")
    denominator = math.sqrt(var1) * math.sqrt(var2)
    var3 = numerator/denominator
    if(var3 < -1):
        var3 = -1
    if(var3 > 1):
        var3 = 1
    angle = math.acos(var3)
    return angle

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
