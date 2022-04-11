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
    unitName = "ugv1"
    #getUnitBlueData(unitName)
    #getUnitDetections(unitName)

    displaceUnit(5, 10, unitName)
   

def displaceUnit(x_dis, z_dis, unitName):
    database_connect_Arma.setConnection("127.0.0.1")
    numberofUnits = database_connect_Arma.numOfAlive_v2Blue()
    print(numberofUnits)
    allunits = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
    print(allunits)
    for unit in allunits:
        print(unit[0])
        if unitName ==  unit[0]:
            database_connect_Arma.setConnection("127.0.0.1")
            #database_connect_Arma.setConnection("192.168.10.155")
            database_connect_Arma.moveUnit(unit[2]+x_dis, unit[3], unit[4]+z_dis, unitName)
            print("moving")
            


def moveUnit(x_dis, z_dis, unitName):
    database_connect_Arma.setConnection("127.0.0.1")
    numberofUnits = database_connect_Arma.numOfAlive_v2Blue()
    allunits = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
    for unit in allunits:
        if unitName ==  unit[0]:
            database_connect_Arma.setConnection("192.168.10.155")
            database_connect_Arma.moveUnit(x_dis, unit[3], z_dis, unitName)


        
async def main():
    #readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())