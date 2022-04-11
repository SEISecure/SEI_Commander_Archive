import psycopg2
import numpy as np
import asyncio
import database_connect_Arma



async def runner():

    while True:
        database_connect_Arma.setConnection("127.0.0.1")
        #database_connect_Arma.sendToFileMisssionStatus()
        missionStatus = database_connect_Arma.missionStat()
        print(missionStatus)
        if ("End" in missionStatus):
            database_connect_Arma.sendToFileMisssionStatus()
            database_connect_Arma.sendToFileUAVThreats()
            print("Data Outputed")
            database_connect_Arma.resetMisDB()


async def main():
    #readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())