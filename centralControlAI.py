import psycopg2
import numpy as np
import asyncio
import database_connect_Arma
import time


async def runner():
    database_connect_Arma.setConnection("127.0.0.1")
    while True:
        print("Sending Detections")  
        numberofUnits = database_connect_Arma.numOfAlive_v2Blue()
        allunits = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
        #print(allunits)
        for unit in allunits:
            getVBS4detection(unit[0])
         
        print("Sleeping")    
        time.sleep(20)

def sendDataToAllyUnits():
    print("TODO")

def getUnitDetections(unitName):
    allunits = database_connect_Arma.getRecentDetectionData(unitName)
    print(allunits)
    #store to detections of unit on that machine 
    
def getUnitData(unitName):
    numberofUnits = database_connect_Arma.numOfAlive_v2Blue()
    allunits = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
    for unit in allunits:
        if unitName ==  unit[0]:
            #add to positiondata table of unit on that machine
            print(unit) 

def getVBS4detection(unit_name):
    
    if "uav" in unit_name or "ucav" in unit_name:
        uavthreats = database_connect_Arma.getVBS4UAVthreats(unit_name)
        if uavthreats is not None:
            if "," in uavthreats[1]:
                print("TODO")
                #uavthreats[1].split(",",1)[1]
                exit(0)
            enemy = database_connect_Arma.getOpForceUnitByTimestamp(uavthreats[1], uavthreats[0])
            print("Enemy pos", enemy)
            #insert into detections
            #timestamp, unit_name, enemyPos, enemyName
            database_connect_Arma.insertDetectionData(uavthreats[0], unit_name, enemy, uavthreats[1])
    else:
        #insert threat data into detections
        threats = database_connect_Arma.getVBS4threats(unit_name)
        if threats is not None:
            if "," in threats[1]:
                print("TODO")
                #threats[1].split(",",1)[1]
                exit(0)
            enemy = database_connect_Arma.getOpForceUnitByTimestamp(threats[1], threats[0])
            print(enemy)
            #insert into detections
            #timestamp, unit_name, enemyPos, enemyName
            database_connect_Arma.insertDetectionData(threats[0], unit_name, enemy, threats[1])

async def main():
    #readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task



asyncio.run(main())