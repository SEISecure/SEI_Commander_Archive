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
import numpy
from torch import nn
import nest_asyncio
import random

nest_asyncio.apply()



 

#declaration of global variables 
initalize = True
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
    
    try:
        '''
        Step 0 - Read in terrain file
        Step 1 - Find all Red Force that are alive
            1.a Create a list of soldiers names that are alive on ft1
            1.b Create a list of soldiers names that are alive on ft2
            1.c Create a list of soldiers names that are alive om ft3

        Step 2 - Find the current x and z positon for each team member 
            2.a ft1XPosition ft1ZPosition
            2.b ft2XPosition ft2ZPosition
            2.c ft3XPosition ft3ZPosition
        
        Step 3 - Find all enemies that are visible from any team members
           3.a pull all visible enemies for the database
           3.b create a list with all visible enemies (make sure no names are repeated)
        
        Step 4 - Simulate future states to see ideal next move
            4.a var StartTime = getCurrentTime 
            4.b create dictionary fireTeamsNextPosReward key = "x,z" value = [Reward (0.0)]
                4.b.1 ft1NextPOSReward
                4.b.2 ft2NextPOSReward
                4.b.3 ft3NextPOSReward
            4.c while CurrentTime - StartTime < 4 Seconds perfom the following tasks
                4.d create a temp variable for current X,Z for each fireteam and visible enemy
                4.e create a temp variable nextXZ ="x,z" for each fireteam
                    ft1nextXZ =''
                    ft2nextXZ=''
                    ft3nextXZ=''
                4.f newStateReward =0.0
                4.g for i in range (1:7)
                    4.g.1 randomly select a new average X and Z of each fire team that is no more than 20 meters away from current x,z
                    4.g.2 update current with the new X and Z location
                    4.g.3 if i = 1 then set 
                        4.g.3.A ft1nextXZ = randonly selected ft1 x,z
                        4.g.3.B ft2nextXZ = randonly selected ft2 x,z
                        4.g.3.C ft3nextXZ = randonly selected ft3 x,z
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
                        4.g.5.10 for each enemy  within 300 M
                            if largeUGV newStateReward -= 0.33
                            if smallugv newStateReward -= 0.2
                            if uav newStateReward -= 0.2
                            if turret newStateReward -= 0.2
                            if Blueforce -= 0.1
                4.h check to see if nextXZ is in fireTeamsNextPosReward
                    4.h.1 if ft1nextXZ is in ft1NextPOSReward
                    4.h.2 if ft2nextXZ is in ft2NextPOSReward
                    4.5.3 if ft3nextXZ is in ft3NextPOSReward
                    If the key is in the dictionary
                        tempReward = fireTeamsNextPosReward[ftnextXZ]
                        tempReward.append(newStateReward)
                        fireTeamsNextPosReward[ftnextXZ] = tempReward
                    else
                        fireTeamsNextPosReward[ftnextXZ] = [newStateReward]
                
            4.i iterate through all positions in fireTeamsNextPosRw and select the x,z with the highest average newStateReward
        
        Step 5 move soldiers to next state
            if soldiers within 300 meters of visible enemy use continueAssault2 with target X and Z being the new location
            else: move soldiers to new target X and Z and set them not to engage target.
        
        Step 6 simulation ends 
            if all blue force are killed
            if all red force are killed
            if red force reaches the fence (i.e., 20 meters from center of FOB)
        '''




    #create a dictionary that defines each soldier and their position and what action they last performed
    #Actions 0 = Assault 1 = Move Sneaky 2 = Move Engage 3 = Retreat
    #Low lvl Actions 0 = Holding 1 = Moving 
    #soldierDict = { "soldier_name" : Action, Low lvl Action, Current X, Current Z, Target X, Target Z, Low Level X, Low Level Z }
    if initalize:
        # for each soldier set
        soldierDict['soldier'] =  [0,0,soldier[0],soldier[1],soldier[1], soldier[1],soldier[1],soldier[1]]
        initalize = False
    else:
        #check if soldiers are still alive 
        #if soldier dead delete from soldier dict
        del soldierDict['del']


        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")
        
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
        #get the position data of the blueforce soldiers
        cursor.execute("select px,pz from blueforpositiondata where unit_name='guy1' order by timestamp desc limit 1;")
        guy1position = cursor.fetchone()
        cursor.execute("select px,pz from blueforpositiondata where unit_name='guy2'order by timestamp desc limit 1;")
        guy2position = cursor.fetchone()
        #assign the position data to the global xEnemy, zEnemy after converting to float numbers 
        xEnemy =[float(guy1position[0]), float(guy2position[0])]
        zEnemy =[float(guy1position[1]), float(guy2position[1])]
        #get the avg position x and z of the blueforce soldiers
        avgPosX = (xEnemy[0] + xEnemy[1])/2
        avgPosZ = (zEnemy[0] + zEnemy[1])/2
        print(avgPosX, avgPosZ)
        #get the position data of the opforce soldiers
        cursor.execute("select px,pz from opforpositiondata where unit_name='ft2_rifleman' order by timestamp desc limit 1;")
        ft2_riflemanposition = cursor.fetchone()
        cursor.execute("select px,pz from opforpositiondata where unit_name='ft2_mgunner' order by timestamp desc limit 1;")
        ft2_mgunnerposition = cursor.fetchone()
        cursor.execute("select px,pz from opforpositiondata where unit_name='ft2_grenadier' order by timestamp desc limit 1;")
        ft2_grenadier = cursor.fetchone()
        cursor.execute("select px,pz from opforpositiondata where unit_name='ft2_rpg' order by timestamp desc limit 1;")
        ft2_rpg = cursor.fetchone()
        #put the opfor position data into the global xteam and zteam
        xTeam =[float(ft2_riflemanposition[0]), float(ft2_mgunnerposition[0]), float(ft2_grenadier[0]), float(ft2_rpg[0])]
        zTeam =[float(ft2_riflemanposition[1]), float(ft2_mgunnerposition[1]), float(ft2_grenadier[1]), float(ft2_rpg[1])]

        
        print("Enemy Positions:")
        print(xEnemy)
        print("\n")
        print(zEnemy)
        print("\n")
        print("Team Positions:")
        print(xTeam)
        print("\n")
        print(zTeam)
        
        
        
        
    
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)  
    #call oline function  to find the path for the soldiers to take  given the avg enemy team position and the team position 
    oline = orientOnline(xEnemy, zEnemy, xTeam, zTeam)
    print("hilo")
    print(avgPosX, avgPosZ)
    #using the oline calculate the point on the line  for each unit and then create a position string per unit that will be inserted into the soldiercommand table 
    newUnitPos1 = orientationPoint (oline, float(ft2_riflemanposition[0]), float(ft2_riflemanposition[1]))
    newUnitPos1X = str(round(newUnitPos1[0], 5))
    newUnitPos1Z = str(round(newUnitPos1[1], 5))
    newUnitPos1String = "'" + newUnitPos1X + ";" + "3.9" + ";" + newUnitPos1Z + "'"
    newUnitPos2 = orientationPoint (oline, float(ft2_mgunnerposition[0]), float(ft2_mgunnerposition[1]))
    newUnitPos2X = str(round(newUnitPos2[0], 5))
    newUnitPos2Z = str(round(newUnitPos2[1] , 5))
    newUnitPos2String = "'" + newUnitPos2X + ";" + "3.9" + ";" + newUnitPos2Z + "'"
    newUnitPos3 = orientationPoint (oline, float(ft2_grenadier[0]), float(ft2_grenadier[1]))
    newUnitPos3X = str(round(newUnitPos3[0], 5))
    newUnitPos3Z = str(round(newUnitPos3[1], 5))
    newUnitPos3String = "'" + newUnitPos3X + ";" + "3.9" + ";" + newUnitPos3Z + "'"
    newUnitPos4 = orientationPoint (oline, float(ft2_rpg[0]), float(ft2_rpg[1]))
    newUnitPos4X = str(round(newUnitPos4[0], 5))
    newUnitPos4Z = str(round(newUnitPos4[1], 5))
    newUnitPos4String = "'" + newUnitPos4X + ";" + "3.9" + ";" + newUnitPos4Z + "'"
    
    
    print(soldierDict)
    #give the command to move the soldiers to the new positions given the position strings
    unit1Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (0, 'ft2_rifleman', 'move'," + newUnitPos1String + ");"
    #cursor.execute("insert into soldiercommand (soldierID, soldier_name, command, params)  values (0, 'ft2_rifleman', 'move', %s);",( newUnitPos1String))
    cursor.execute(unit1Move)
    connection.commit()
    print("Rifleman moving into position")
    print(newUnitPos1)
    #cursor.execute("insert into soldiercommand (soldierID, soldier_name, command, params)  values (0, 'ft2_mgunne', 'move', %s);",( newUnitPos2String))
    unit2Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (1, 'ft2_mgunner', 'move'," + newUnitPos2String + ");"
    cursor.execute(unit2Move)
    connection.commit()
    print("Gunner moving into position")
    print(newUnitPos2)
    #cursor.execute("insert into soldiercommand (soldierID, soldier_name, command, params)  values (0, 'ft2_grenadier', 'move', %s);",(newUnitPos3String))
    unit3Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (2, 'ft2_grenadier', 'move'," + newUnitPos3String + ");"
    cursor.execute(unit3Move)
    connection.commit()
    print("Grenadier moving into position")
    print(newUnitPos3)
    #cursor.execute("insert into soldiercommand (soldierID, soldier_name, command, params)  values (0, 'ft2_rpg', 'move', %s);",(newUnitPos4String))
    unit4Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (3, 'ft2_rpg', 'move'," + newUnitPos4String + ");"
    cursor.execute(unit4Move)
    connection.commit()
    print("Rpg moving into position")
    print(newUnitPos4)
    
    #find all the enemies that a unit sees in this case ft2_rifleman
    cursor.execute("select * from enemyVisibility where opfor='ft2_rifleman';")
    seenEnemies = cursor.fetchall()
    #dictionary that will store the future positions of the enemies seen
    futurePos = {}
    print(seenEnemies)
    #for each seen enemy calculate the future position in the allotted time 20 in this case
    for i in seenEnemies:
        #update the dictionary with the seen enemy
        futurePos.update(futureLocation(i, 20))
    print(futurePos)
     
        
    '''
    while(True):
        soldierDict.update(continueAssault2 (soldierDict, "ft2", avgPosX, avgPosZ))
        print("yolo@@@@@@@@@@@@@")
        print (soldierDict)
        print("yolo@@@@@@@@@@@@@@@@@@@@@@@@@@")
        time.sleep(5)
    '''
    
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
 
def continueAssault (soldierDict, fireteam, targetX, targetZ):
    
    
    # Check if every soldier is at the target location = selectedSoldArray[4],selectedSoldArray[5] if true all soldiers weapons free
    
    filtered_dict = {k:v for (k,v) in soldierDict.items() if fireteam in k}
    allMoving = 0
    soldiers = []
    randomUnit =0
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
                cursor = connection.cursor()
                getPos = "select px,pz from opforpositiondata where unit_name='" + sol + "' order by timestamp desc limit 1;"
                cursor.execute(getPos)
                positionList = cursor.fetchone()
                xzPos.append(positionList)
            for sol in occupyingSoldier:
                cursor = connection.cursor()
                getPos = "select px,pz from opforpositiondata where unit_name='" + sol + "' order by timestamp desc limit 1;"
                positionList = cursor.fetchone()
                xzPos.append(positionList)
        
           
            #soldiers move and occupy
            i = 0
            newsoldierDict={}
            for sol in selectedSoldier:
                selectedSoldArray = soldierDict.get(sol)
                newPosition1 = newAssaultPoint(targetX,targetZ, float(xzPos[i][0]), float(xzPos[i][1]))
                i+=1
                soldier1positionString = "'" + str(round(newPosition1[0])) + ";" + "3.9" + ";" + str(round(newPosition1[1])) + "'"
                soldier1Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (4, '" + selectedSoldier1 + "', 'move'," + soldier1positionString + ");"
                cursor.execute(soldier1Move)
                connection.commit()
                newsoldierDict[sol] = [0,1,xzPos[i]s[0],xzPos[i][1],targetX,targetZ,newPosition1[0],newPosition1[1]]
                i+=1

            for sol in occupyingSoldier:
                soldier3positionString = "'" + xzPos[i][0] + ";" + "3.9" + ";" + xzPos[i][1] + "'"
                soldier3HoldFire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (6, '" + sol + "', 'change_roe', '2');"
                soldier3Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (7, '" + sol + "', 'move'," + soldier3positionString + ");"
                cursor.execute(soldier3HoldFire)
                cursor.execute(soldier3Move)
                connection.commit()
                newsoldierDict[sol] = [0,0,xzPos[i][0],xzPos[i][1],targetX,targetZ,xzPos[i][0],xzPos[i][1]]
                i+=1
             #update soldierDict with the new dictionary
            
            soldierDict.update(newsoldierDict)
        
        else:
            for key in filtered_dict:
            soldiers.append(key)
            numbOccupiedSoldiers = 0
            numbMovingSoldiers = 0
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
                getPos1 = "select px,pz from opforpositiondata where unit_name='" + sol + "' order by timestamp desc limit 1;"
                cursor.execute(getPos1)
                positionList = cursor.fetchone()
                soldier1position = newAssaultPoint(targetX, targetZ, float(positionList[0]), float(positionList[1]))
                soldier1positionString = "'" + str(round(soldier1position[0])) + ";" + "3.9" + ";" + str(round(soldier1position[1])) + "'"
                soldier1Fire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (10, '" + sol + "', 'change_roe', '0');"
                soldier1Move = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (12, '" + sol + "', 'move'," + soldier1positionString + ");"
                cursor.execute(soldier1Fire)
                connection.commit()
                cursor.execute(soldier1Move)
                connection.commit()
                newsoldierDict[sol]= [0,0,positionList[0],positionList[1],targeX,targetZ,soldier1position[0],soldier1position[1]]

            for sol in selectedSoldier:
                getPos1 = "select px,pz from opforpositiondata where unit_name='" + sol + "' order by timestamp desc limit 1;"
                cursor.execute(getPos1)
                positionList = cursor.fetchone()
                soldier3positionString = "'" + positionList[0] + ";" + "3.9" + ";" + positionList[1] + "'"
                soldier3HoldFire = "insert into soldiercommand (soldierID, soldier_name, command, params)  values (14, '" + sol + "', 'change_roe', '2');"
                cursor.execute(soldier3HoldFire)
                connection.commit()
                newsoldierDict[sol]= [0,1,positionList[0],positionList[1],targeX,targetZ,positionList[0],positionList[1]]
        
            soldierDict.update(newsoldierDict)
        

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
    getEnemyData = "select px, py, pz, vx, vy, vz from blueforpositiondata where unit_name='" + enemy[2] + "' order by timestamp desc limit 1;"
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
    #create dictionary with the new predicted positions 
    newPosition = { enemy[2] : [newPx,newPy, newPz]}
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
    terrainFile = open('C:/Users/Roy Hayes/Downloads/terrainType_db.csv','r')
    count = 0
    terrainX =[]
    terrainZ =[]
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
    terrainXSet = sorted(set(terrainX))
    terrainZSet = sorted(set(terrainZ))

#returns the closest X and Z value that is in the terrain set
def closestXZTerrain(currentX, currentZ):
    closeX = '0'
    closeZ = '0'
    #finds the closest X value in the terrain set
    pos = bisect_left(terrainXSet, currentX)
    if pos == 0:
        closeX = str(terrainXSet[0])
    if pos == len(terrainXSet):
        closeX = str(terrainXSet[-1])
    before = terrainXSet[pos -1]
    after = terrainXSet[pos]
    if after - currentX < currentX - before:
        closeX = str(after)
    else:
        closeX = str(before)
    
    #finds the closest Z value in the terrain set
    pos = bisect_left(terrainZSet, currentZ)
    if pos == 0:
        closeZ = str(terrainZSet[0])
    if pos == len(terrainZSet):
        closeZ = str(terrainZSet[-1])
    before = terrainZSet[pos -1]
    after = terrainZSet[pos]
    if after - currentZ < currentZ - before:
        closeZ = str(after)
    else:
        closeZ = str(before)
    
    return closeX+","+closeZ
    
async def main():
    
    readTerrain()
    task = asyncio.create_task(runner())
    
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())
