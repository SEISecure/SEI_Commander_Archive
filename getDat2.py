import psycopg2
import numpy as np
import asyncio
import database_connect_Arma
import random
import math
import getDatScientist
import time





async def runner():
    while True:
        database_connect_Arma.setConnection("127.0.0.1")
        getDatScientist.assignPathToFireTeam("ft2")


async def main():
    #readTerrain()
    task  = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())