import psycopg2
import numpy as np
import asyncio
import database_connect_Arma
import time

'''
connection2 = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "192.168.10.158",
                                  port = "5432",
                                  database = "units")

connection3 = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "192.168.10.151",
                                  port = "5432",
                                  database = "units")
'''
async def runner():
    #getVBS4detection("uav_nike_233")
    #set the unit name for the machine
    unitName = "UGV_mars_123"
    #getUnitBlueData(unitName)
    #getUnitDetections(unitName)
    
    while True:
        getUnitBlueData(unitName)
        getUnitDetections(unitName)
        time.sleep(5)

def displaceUnit(x_dis, z_dis, unitName):
    database_connect_Arma.setConnection("127.0.0.1")
    numberofUnits = database_connect_Arma.numOfAlive_v2()
    allunits = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
    detections = database_connect_Arma.getRecentDetectionData(unitName)
    for unit in allunits:
        if unitName ==  unit[0]:
            database_connect_Arma.setConnection("192.168.10.155")
            database_connect_Arma.moveUnit(unit[2]+x_dis,  unit[4]+z_dis, unit[3], unitName)




def sendDataToAllyUnits(unitName):
    database_connect_Arma.setConnection("127.0.0.1")
    numberofUnits = database_connect_Arma.numOfAlive_v2Blue()
    allunits = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
    database_connect_Arma.setConnection("192.168.10.158")
    for unit in allunits:
        if unitName ==  unit[0]:
            database_connect_Arma.insertPos(unit, "blufor")
            print("Reporting position to 192.168.10.158")


def sendDetectionToAllyUnits(unitName):
    database_connect_Arma.setConnection("127.0.0.1")
    allunits = database_connect_Arma.getRecentDetectionData(unitName)
    #print(allunits)
    if(allunits !=-1):
        #store to detections of unit on that machine 
        database_connect_Arma.setConnection("192.168.10.158")
        database_connect_Arma.insertDetections(allunits[0], unitName, [allunits[2], allunits[3], allunits[4]], allunits[1])
        print("Detected Enemy")
        
def getUnitDetections(unitName):
    database_connect_Arma.setConnection("192.168.10.155")
    allunits = database_connect_Arma.getRecentDetectionData(unitName)
    #print(allunits)
    if(allunits !=-1):
    #store to detections of unit on that machine 
        database_connect_Arma.setConnection("127.0.0.1")
        database_connect_Arma.insertDetections(allunits[0], unitName, [allunits[2], allunits[3], allunits[4]], allunits[1])
        print("Detected Enemy")
    
def getUnitOpData(unitName):
    database_connect_Arma.setConnection("192.168.10.155")
    numberofUnits = database_connect_Arma.numOfAlive_v2()
    allunits = database_connect_Arma.getAllOpForceUnits(numberofUnits)
    for unit in allunits:
        if unitName ==  unit[0]:
            #add to positiondata table of unit on that machine
            database_connect_Arma.setConnection("127.0.0.1")
            database_connect_Arma.insertPos(unit, "opfor")
            print("Getting position")
                
def getUnitBlueData(unitName):
    database_connect_Arma.setConnection("192.168.10.155")
    numberofUnits = database_connect_Arma.numOfAlive_v2Blue()
    allunits = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
    for unit in allunits:
        if unitName ==  unit[0]:
            #add to positiondata table of unit on that machine
            #print(unit) 
            database_connect_Arma.setConnection("127.0.0.1")
            database_connect_Arma.insertPos(unit, "blufor")
            print("Getting position")


        
async def main():
    #readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())