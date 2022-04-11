import random
import asyncio
import database_connect_Arma

mars1 = "mars1" 
mars2 = "mars2" 
initPosMars1 = (34.4032283, -116.2697004,0)
initPosMars2 = (34.4034283, -116.2699004,0)
marsList = {mars1,mars2}
async def runner():
    if(len(marsList)>0):
        #call detections
        #call functionInitateFlank
        targetLoc = database_connect_Arma.getAllDetection()
        marsToMove, coordsList = functionInitateFlank(targetLoc)
        print(marsToMove)
        if(marsToMove != ""):
            if(marsToMove in marsList):
                #send to athena the coordinate with move call
                database_connect_Arma.moveUnitW(coordsList, marsToMove)
                print(marsToMove + " sent to " + str(coordsList))
                marsList.discard(marsToMove)
def functionInitateFlank(latLongList):
    print(latLongList)
    for latlong in latLongList:
        lat = float(latlong[0])
        long = float(latlong[1])
    route = []
    test1= (34.4022283, -116.2695004,0)
    test2= (34.4024328, -116.2687524,0)
    test3= (34.4019616, -116.2685888,0)
    route.append(test1)
    route.append(test2)
    route.append(test3)
    randValue = random.random()
    if randValue <0.33:
        return 'mars1',route

    elif randValue<.66:
        return 'mars2',route
    else:
        return '',[]

async def main():
    task = asyncio.create_task(runner())
    await task

asyncio.run(main())

