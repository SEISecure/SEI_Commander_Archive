import psycopg2
import numpy as np
import datetime
import database_connect_Arma
import random
import asyncio
import math
import sys
import csv
import time
import threading

#from connnection.connnection import database_connect


w_disToGoal = random.uniform(0.1, 1)
w_disToConceal = random.uniform(0.1, 1)
w_disToVehicle = random.uniform(0.1, 1)


async def runner():
    #set the location of the database
    t = time.localtime()
    database_connect_Arma.setConnection("127.0.0.1")
    #weights randomly generated
    global w_disToGoal
    global w_disToConceal
    global w_disToVehicle
    database_connect_Arma.HoldFire("ugv1")
    #create Array of squares use createSquaredMap to generate
    squareArray = []
    createSquaredMap(10, 1000580, 1000080, 999796, 999400, squareArray)
    #Debug! print(squareArray)
    #given an area with given radius go to random location within area and return x,z
    x,z = ugvZoneRecon("ugv1", [1000221,999550], 50)
    #goal is the final destination of the enemy, returned after car is given random route to go
    goal = opforCarRandoRoute()
    #given the squareArray and the location of the vehicle and angle create array of viewable squares
    
    #riskDict = {}   
    concealArray = getObjectLocFileVBS4("Dhalgram_Containers")
    print("populating inital risks")
    for square in squareArray:
        d_toGoal = distanceBetweenPoints(square[0],square[1], goal[0], goal[1]) 
        conceal = getClosestConcealLoc(square[0],square[1], concealArray)
        d_toVehicle = distanceBetweenPoints(square[0],square[1], x, z) 
        risk = (w_disToGoal * d_toGoal) + (w_disToConceal * conceal[2]) + (w_disToVehicle * d_toVehicle)
        #save to hash table 
        #riskDict[square[0], square[1]] = [risk,d_toGoal,conceal[2]]
        database_connect_Arma.insertRiskAtLocation(square[0],square[1],risk,d_toGoal,conceal[2])
    print("Done")  
    atLocFlag = False
    '''   
    while True: 
        start = time.localtime()   
        ang = random.uniform(0, 360) 
        viewableSquares = getVisibleSquares(squareArray, ang,  x,z)  
        print("update risk")
        #hash table put risk data in hashtable
        for square in squareArray:
            d_toGoal = distanceBetweenPoints(square[0],square[1], goal[0], goal[1]) 
            conceal = getClosestConcealLoc(square[0],square[1], concealArray)
            d_toVehicle = distanceBetweenPoints(square[0],square[1], x, z) 
            #riskData = riskDict[square[0],square[1]]
            riskData = database_connect_Arma.getRiskDataAtLocation(square[0],square[1])
            #print(riskData[0])
            risk = riskData[0] + (w_disToGoal * d_toGoal) + (w_disToConceal * conceal[2]) + (w_disToVehicle * d_toVehicle)
            newRisk = {}
            newRisk[square[0], square[1]] = [risk,d_toGoal,conceal[2]]
            #riskDict.update(newRisk)
            database_connect_Arma.updateRiskAtLocation(square[0],square[1],risk,d_toGoal,conceal[2])
            #update hash table with risk and other data update db every 5 min 
        print("Done") 
        stop = time.localtime() 
        print(start-stop)
        sys.exit(0)
    '''
    t1 = threading.Thread(target=updateRiskSquares, args=(x,z, squareArray, goal, concealArray))
    t1.start()
    while True:   
        ang = random.uniform(0, 360) 
        viewableSquares = getVisibleSquares(squareArray, ang,  x,z)  
        print("updating viewable squares")     
        for vsquare in viewableSquares:
            risk = 0
            riskData = database_connect_Arma.getRiskDataAtLocation(vsquare[0],vsquare[1])
            database_connect_Arma.updateRiskAtLocation(vsquare[0],vsquare[1],risk,riskData[1], riskData[2])
        print("Done, ViewableSquares Updated")
    #t2 = threading.Thread(target=updateViewableSquares, args=(viewableSquares))
    # starting thread 1

    # starting thread 2
    #t2.start()
            #update risk at vsquare loc
    
    #Debug 
        '''   
        for square in viewableSquares:
        print("\n", square)
        '''
        carX = 0
        carZ = 0
    
        numOfOpFor = database_connect_Arma.numOfAlive_v2()
        opforUnits = database_connect_Arma.getAllOpForceUnits(numOfOpFor)
        for unit in opforUnits:
            if "car" in unit[0]:
                carX = unit[2]
                carZ = unit[4]
                if unit[1] < 15 or (carX - goal[0] < 5 and carZ - goal[1] < 5):
                    currentTime = time.localtime()
                    runTime = t - currentTime
                    print("Run Time: ", runTime)
                    print("Weights: ", w_disToGoal,w_disToConceal,w_disToVehicle)
       
              
        while True:     
            numOfBluFor = database_connect_Arma.numOfAlive_v2Blue()
            BluforUnits = database_connect_Arma.getAllBlueForceUnits(numOfBluFor) 
            for unit in BluforUnits:  
                if "ugv1" in unit[0]: 
                    if not (unit[2] - x < 5 and unit[4] - z < 5):
                        time.sleep(5)
                    else:
                        atLocFlag = True
            if atLocFlag == True:
                print("At Loc")
                database_connect_Arma.OpenFire("ugv1")
                break
                        
        time.sleep(10)
                    #output run
                    #time of run, weights
                #for square in viewableSquares:
                #    if square[0] - carX <=10 and square[1] - carZ <=10:
                #        print("Enemy Found")
                #        database_connect_Arma.moveUnitVBS(square[0], square[1], "ugv1")
                #        print("Engaging")
            #check for enemys then update
            #squareArray.remove(square)
            #squareArray.append([squareX,squareZ,0])
    #inTriangle = PointInTriangle([1000177.97, 999548.33], [1000213,999584], [1000163.05, 999586.18], [1000177.97, 999548.33])
    #inTriangle = isInside(1000213,999584, 1000177.97, 999548.33, 1000163.05, 999586.18, 1000200,999583)
    #inTriangle = isInside(0,1, 1, 1, 0, 0, .5, .5)
    #print(inTriangle)
    #database_connect_Arma.setConnection("127.0.0.1")
    #ugvZoneRecon("ugv1", [1000221,999550], 50)
    #opforCarRandoMove("car",[1000480, 999598], 100)
    #opforCarRandoMove("car",[1000380, 999695], 100)
    #opforCarRandoMove("car",[1000280, 999700], 100)
    #opforCarRandoMove("car",[1000180, 999596], 100)
    #opforCarRandoMove("car",[1000280, 999500], 100)
    #database_connect_Arma.addWaypointViaSQF("car", 1000394,999487)
    #database_connect_Arma.addWaypointViaSQF("car", 1000508,999588)
    #database_connect_Arma.addWaypointViaSQF("car", 1000306,999682)
    #database_connect_Arma.addWaypointViaSQF("car", 1000159,999528)
    
    #opforCarRandoRoute()


#create func to read container data

def updateViewableSquares(viewableSquares):
    while True:  
        print("updating viewable squares")     
        for vsquare in viewableSquares:
            risk = 0
            riskData = database_connect_Arma.getRiskDataAtLocation(vsquare[0],vsquare[1])
            database_connect_Arma.updateRiskAtLocation(vsquare[0],vsquare[1],risk,riskData[1], riskData[2])
    time.sleep(10)

def updateRiskSquares(x,z, squareArray, goal, concealArray):
    global w_disToGoal
    global w_disToConceal
    global w_disToVehicle
    while True:  
        print("update risk")
        #hash table put risk data in hashtable
        for square in squareArray:
            d_toGoal = distanceBetweenPoints(square[0],square[1], goal[0], goal[1]) 
            conceal = getClosestConcealLoc(square[0],square[1], concealArray)
            d_toVehicle = distanceBetweenPoints(square[0],square[1], x, z) 
            #riskData = riskDict[square[0],square[1]]
            riskData = database_connect_Arma.getRiskDataAtLocation(square[0],square[1])
            #print(riskData[0])
            risk = riskData[0] + (w_disToGoal * d_toGoal) + (w_disToConceal * conceal[2]) + (w_disToVehicle * d_toVehicle)
            newRisk = {}
            newRisk[square[0], square[1]] = [risk,d_toGoal,conceal[2]]
            #riskDict.update(newRisk)
            database_connect_Arma.updateRiskAtLocation(square[0],square[1],risk,d_toGoal,conceal[2])
            #update hash table with risk and other data update db every 5 min 
        print("Done, Risk Updated") 
        time.sleep(10)

def getVisibleSquares(squareArray, ang, x,z):
    viewableSquares = []
    for square in squareArray:
        squareX = square[0]
        squareZ = square[1]
        #print(squareX, squareZ )
        checkedFlag = square[2] 
        result = checkIfSquareWithinDistance([1000160,999587], [squareX, squareZ], ang)
        #print(result, squareX, squareZ )
        if result == True:
            #print("Can See:",[squareX,squareZ])
            viewableSquares.append([squareX,squareZ,0])
    return viewableSquares

def opforCarRandoRoute():
    random.seed()
    randoPos1 = [1000480, 999598]
    randoPos2 = [1000380, 999695]
    randoPos3 = [1000280, 999700]
    randoPos4 = [1000280, 999500]
    #chose 2 zones lower radius to 20 m for final
    randoSteps = 2 #random.randint(1, 5)
    posArray = [randoPos1, randoPos2, randoPos3, randoPos4]
    
    finalPos = [1000180, 999596]
    
    if randoSteps == 1:
        opforCarRandoMove("car",finalPos, 20)
        print("Final Route",finalPos)
    else:
        i = 0
        sentLoc = []
        while i < randoSteps:
            while True:
                randoPosIndex = random.randint(0,3)   
                print("Chosen Index", randoPosIndex)         
                if(randoPosIndex not in sentLoc):
                    break
            sentLoc.append(randoPosIndex)
            opforCarRandoMove("car",posArray[randoPosIndex], 100)
            print("Route",randoPosIndex, "pos=", posArray[randoPosIndex])
            i +=1
        opforCarRandoMove("car",finalPos, 20)
    return finalPos
 #p[x,y]

def distanceBetweenPoints(X1,Z1,X2,Z2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Z1- Z2, 2))
    return dis  

def createSquaredMap(SquareSize, X_maxRange, X_minRange, Z_maxRange, Z_minRange, squareArray):
    #
    for x in range(X_minRange, X_maxRange, 10):
        for z in range(Z_minRange, Z_maxRange, 10):
            squareArray.append([x,z,-1])
            
def checkIfSquareWithinDistance(currentSquare, testSquare, ang):
    if(currentSquare[0]==testSquare[0] and currentSquare[1] == testSquare[1]):
        #print("Same Square")
        return True
    else:
        random.seed()
        alphacheck = 0
        #ang = random.uniform(0, 360)
        #ang = 0
        altcompare = False 
        altcompare2 = False 
        alpha1 = (ang - 22.5)
        
        if alpha1 < 0:
            alpha1 = 360 + alpha1
            altcompare = True
        #print(alpha1)        
        alpha2 = (ang + 22.5)
        
        if alpha2 > 360:
            alpha2 =  alpha2 -360
            altcompare2 = True  
        #print(alpha2)  
        #print(alpha1, alpha2)
        #sys.exit(0)
        #print("alpha1", alpha1, "alpha2", alpha2)
        alpha1 = alpha1  * math.pi/180 
        alpha2 = alpha2  * math.pi/180 
        testx = 0
        testz = 0
        
        dis = distanceBetweenPoints(currentSquare[0],currentSquare[1],testSquare[0],testSquare[1])
        
        if distanceBetweenPoints(currentSquare[0],currentSquare[1],testSquare[0],testSquare[1]) < 50:
            #print(dis)
            testx = testSquare[0] - currentSquare[0]
            testz = testSquare[1] - currentSquare[1]  
            #print(testSquare[0],testSquare[1])
            #print(testx, testz)
            #sys.exit(0)
            if testx == 0:
                testx = 0.0001     
            angletest = math.atan(testz/testx)
            #print(angletest * 180/math.pi )
            if(testx < 0 and testz > 0) or (testx < 0  and testz < 0):
                alphacheck = math.pi + angletest 
            elif testx > 0 and testz <= 0:
                alphacheck = 2 * math.pi + angletest
            else:
                #print(angletest)
                alphacheck = angletest                
            if altcompare == False and altcompare2 == False:                
                #print("alphas", alpha1, alpha2)
                if alpha1 <= alphacheck and alpha2 >= alphacheck:
                    #print("Success")
                    return True
            if altcompare2 == True:
                if alpha1 <= alphacheck or alpha2 >= alphacheck:
                    return True
            if altcompare == True:
                if alpha1 <= alphacheck or alpha2 >= alphacheck:
                    return True
    return False   


def getClosestConcealLoc(x,z, concealArray):
    disToConceal = 10000
    concealx = -1
    concealz = -1
    for conceal in concealArray:
        if(conceal[2] == 1):
            dis = distanceBetweenPoints(x,z,conceal[0],conceal[1])
            if(disToConceal > dis):
                disToConceal = dis
                concealx = x
                concealz = z 
    #print(concealx,concealz, disToConceal)           
    return concealx,concealz, disToConceal       
def getObjectLocFileVBS4(fileName):
    containers = []
    with open(fileName+'.csv', 'rt') as f:
        #header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        print("Reading Container Data")
        for row in reader:
            #X,Z, container value 
            containers.append([float(row[0]),float(row[1]),float(row[2])])

    return containers

def area(x1, y1, x2, y2, x3, y3):
 
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1)
                + x3 * (y1 - y2)) / 2.0)
 
 
    
def triangle(p1, p2, p3): 
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1]);



    

def opforCarRandoMove(unitName,center, radius):
    randoXPos = random.uniform(center[0]-radius, center[0] + radius)
    randoZPos = random.uniform(center[1] -radius, center[1] + radius)
    database_connect_Arma.addWaypointViaSQF("car", randoXPos,randoZPos)

 
def ugvZoneRecon(unitName, center, radius):
    #move to zone given center and radius and destroy any enemy nearby
    #center is array of [x,z] for VBS4
    randoXPos = random.uniform(center[0]-radius, center[0] + radius)
    randoZPos = random.uniform(center[1] -radius, center[1] + radius)
    
    database_connect_Arma.moveUnitVBS(randoXPos, randoZPos, unitName)
    return randoXPos,randoZPos
    
async def main():
    
    task = asyncio.create_task(runner())
    await task



asyncio.run(main())