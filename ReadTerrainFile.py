#reads the csv and creates data needed to train the ONR neural network modelt csv
import csv
import numpy
import math
import io
from bisect import bisect_left
import StateSpaceCalc
import database_connect
import FileIO

terraindDict={}
terrainXSet ={}
terrainZSet ={}
elevationDict={}
elevationXSet = {}
elevationZSet ={}

path = 'C:/Users/Mo/Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/'
#terrainFileCSV = "terrainType_db.csv"
elevationFileCSV = "elevation.csv"

xCenter =0

yCenter = 0

radius = 30

def withinRadius(xCenter, zCenter, x, z, radius):

    distance = math.sqrt(math.pow(xCenter-x,2)+ math.pow(zCenter-z,2))
    if(distance <= radius):
        return 1
    else:
        return -1

def percentForestAtSector(ForPos, forestDict):
    Zmax = roundup(float(ForPos[1]) + 40)
    Zmin = roundup(float(ForPos[1]) - 40)
    Xmin = roundup(float(ForPos[0]) - 40)
    Xmax = roundup(float(ForPos[0]) + 40)
    
    northForestPercentages =[]
    southForestPercentages =[]
    eastForestPercentages =[]
    westForestPercentages =[]
    for z in range(Zmin, Zmax, 10):
        for x in range(Xmin, Xmax, 10): 
            if(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 1):
                forest = forestDict[x,z]
                northForestPercentages.append(forest[0])
            elif(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 3):
                forest = forestDict[x,z]
                southForestPercentages.append(forest[0])
            elif(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 2):
                forest = forestDict[x,z]
                eastForestPercentages.append(forest[0])
            elif(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 4):
                forest = forestDict[x,z]
                westForestPercentages.append(forest[0])
    '''
    for z in range(roundup(float(ForPos[1])), Zmax, 10):
        for x in range(Xmin, Xmax, 10): 
            if(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 1):
                forest = StateSpaceCalc.getForestAtLocationFromTerrainFile('terrainType_db', x, z)
                forestPercentages.append(float(forest))
    '''
    NPercentages = 0  
    SPercentages = 0
    WPercentages = 0
    EPercentages = 0          
    if(len(northForestPercentages) > 0):
        NPercentages = sum(northForestPercentages) / len(northForestPercentages)
    if(len(southForestPercentages) > 0):
        SPercentages = sum(southForestPercentages) / len(southForestPercentages)
    if(len(westForestPercentages) > 0):
        WPercentages = sum(westForestPercentages) / len(westForestPercentages)
    if(len(eastForestPercentages) > 0):
        EPercentages = sum(eastForestPercentages) / len(eastForestPercentages)
    return NPercentages, SPercentages, EPercentages, WPercentages

def percentForestAtSouthSector(ForPos, forestDict):
    Zmin = roundup(float(ForPos[1]) - 40)
    Xmin = roundup(float(ForPos[0]) - 20)
    Xmax = roundup(float(ForPos[0]) + 20)
    forestPercentages = []

    for z in range(Zmin, roundup(float(ForPos[1])), 10):
        for x in range(Xmin, Xmax, 10): 
            if(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 3):
                forest = forestDict[x,z]
                forestPercentages.append(forest[0])
                #forest = StateSpaceCalc.getForestAtLocationFromTerrainFile('terrainType_db', x, z)
                #forestPercentages.append(float(forest))

    if(len(forestPercentages) > 0):
        return sum(forestPercentages) / len(forestPercentages)
    return  -1

def percentForestAtWestSector(ForPos, forestDict):
    Xmin = roundup(float(ForPos[0]) - 40)
    Zmin = roundup(float(ForPos[1]) - 20)
    Zmax = roundup(float(ForPos[1]) + 20)
    forestPercentages =[]

    for x in range(Xmin, roundup(float(ForPos[0])), 10):
        for z in range(Zmin, Zmax, 10): 
            if(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 4):
                forest = forestDict[x,z]
                forestPercentages.append(forest[0])
                #forest = StateSpaceCalc.getForestAtLocationFromTerrainFile('terrainType_db', x, z)
                #forestPercentages.append(float(forest))

    if(len(forestPercentages) > 0):
        return sum(forestPercentages) / len(forestPercentages)
    return  -1

def percentForestAtEastSector(ForPos, forestDict):
    Xmax = roundup(float(ForPos[0]) + 40)
    Zmin = roundup(float(ForPos[1]) - 20)
    Zmax = roundup(float(ForPos[1]) + 20)
    forestPercentages =[]

    for x in range(roundup(float(ForPos[0])), Xmax, 10):
        for z in range(Zmin, Zmax, 10): 
            if(sectorOfCircle(roundup(float(ForPos[0])), roundup(float(ForPos[1])), x, z, 40) == 2):
                forest = forestDict[x,z]
                forestPercentages.append(forest[0])
                #forest = StateSpaceCalc.getForestAtLocationFromTerrainFile('terrainType_db', x, z)
                #forestPercentages.append(float(forest))
                
    if(len(forestPercentages) > 0):
        return sum(forestPercentages) / len(forestPercentages)
    return  -1

def sectorOfOpForAlly(opfor, opforAlly):
    #use getopforunit for opforAlly and getopforpos for opforpos
    opforpos = database_connect.getOpforSoldierPos(opfor)
    opforAllydata = database_connect.getOpforUnit(opforAlly)
    if(float(opforAllydata[0]) < 0.99):
        return sectorOfCircle(roundup(float(opforpos[0])), roundup(float(opforpos[1])), roundup(float(opforAllydata[1])), roundup(float(opforAllydata[2])), 40)
    else: 
        return -1

def sectorOfOpForAllyPos(opforpos, opforAllypos):
    return sectorOfCircle(roundup(float(opforpos[0])), roundup(float(opforpos[1])), roundup(float(opforAllypos[0])), roundup(float(opforAllypos[1])), 40)


   
def sectorOfOpForEnemy(opfor, blueforEnemy):
    #use getblueforunit for blueforEnemy and getopforpos for opforpos
    #print(opfor, blueforEnemy)
    opforpos = database_connect.getOpforSoldierPos(opfor)
    blueforEnemydata = database_connect.getBlueforUnit(blueforEnemy)
    if(float(blueforEnemydata[0]) < 0.99):
        return sectorOfCircle(roundup(float(opforpos[0])), roundup(float(opforpos[1])), roundup(float(blueforEnemydata[1])), roundup(float(blueforEnemydata[2])), 600)
    else: 
        return -1

def sectorOfOpForEnemyPos(opforpos, blueforEnemy):
    #use getblueforunit for blueforEnemy and getopforpos for opforpos
    blueforEnemydata = database_connect.getBlueforUnit(blueforEnemy)
    if(float(blueforEnemydata[0]) < 0.99):
        return sectorOfCircle(roundup(float(opforpos[0])), roundup(float(opforpos[1])), roundup(float(blueforEnemydata[1])), roundup(float(blueforEnemydata[2])), 600)
    else: 
        return -1

def sectorOfBlueForAlly(bluefor, blueforAlly):
    #use getopforunit for opforAlly and getopforpos for opforpos
    blueforpos = database_connect.getBlueforSoldierPos(bluefor)
    blueforAllydata = database_connect.getBlueforUnit(blueforAlly)
    if(float(blueforAllydata[0]) < 0.99):
        return sectorOfCircle(roundup(float(blueforpos[0])), roundup(float(blueforpos[1])), roundup(float(blueforAllydata[1])), roundup(float(blueforAllydata[2])), 40)
    else: 
        return -1
    

    
def sectorOfBlueForEnemy(bluefor, opforEnemy):
    #use getblueforunit for blueforEnemy and getopforpos for opforpos
    blueforpos = database_connect.getBlueforSoldierPos(bluefor)
    opforEnemydata = database_connect.getOpforUnit(opforEnemy)
    if(float(opforEnemydata[0]) < 0.99):
        return sectorOfCircle(roundup(float(blueforpos[0])), roundup(float(blueforpos[1])), roundup(float(opforEnemydata[1])), roundup(float(opforEnemydata[2])), 600)
    else: 
        return -1



def sectorOfCircle (xCenter, zCenter, x, z, radius):

    inRadius = withinRadius(xCenter, zCenter, x, z, radius)
    #North = 1 South = 3 East = 2 West = 3
    if inRadius > 0:
        testX = x- xCenter
        testZ = z-zCenter

        if (testX)>0:
            #must be sector 1, 2, 3
            if(testZ > 0):
                if(abs(testX)> abs(testZ)) :
                    #sector 2
                    return 2
                else:
                    #sector 1
                    return 1
            else:
                if(abs(testX)> abs(testZ)) :
                    #sector 2
                    return 2
                else:
                    #sector 3
                    return 3
                #must be sector 2 or 3
        else:  
            #must be sector 2, 4, 3
            if(testZ > 0):
                if(abs(testX)> abs(testZ)):
                    #sector 4
                    return 4
                else:
                    #sector 1
                    return 1
            else:
                if abs(testX)> abs(testZ):
                    #sector 4
                    return 4
                else:
                    #sector 3
                    return 3
    else:
        return inRadius
    #print(sectorOfCircle(0,0,-1.2,-.4,1))

def closedNeighbors(x,z):
    #readTerrainFile()
    global terraindDict
    closedNeighbors = 0.0
    for t in range (-1,2,1):
        for u in range(-1,2,1):
            if t !=0 or u != 0:
                xoffSet = 50*t+x
                zoffSet = 50*u+z
                xzpoint = closestXZTerrain(xoffSet,zoffSet)
                uoc = terraindDict[xzpoint]
                closedNeighbors += float(uoc[2])
    return closedNeighbors

def readElevationFile():
    global elevationDict
    global elevationXSet
    global elevationZSet
    global elevationFileCSV
    global path 
    #reads elevation file
    elevationFile = open(path+elevationFileCSV,'r')
    elevationX=[]
    elevationZ =[]
    count=0
    while True:
        
        line = elevationFile.readline()
        if not line:
            break
        if count > 0 :
            line = line.replace('\n','')
            if line != '':
                values = line.split(',')
                elevationZ.append(float(values[0])) #sets Z for elevation
                for i in range (1, len(values)):
                    elev = float(values[i])
                    xz = str(int(elevationX[i-1]))+','+  str(int(values[0]))
                    elevationDict[str(xz)] = elev
        else:
            line = line.replace('\n','')
            values = line.split(',')
            for val in values:
                if val !='':
                    elevationX.append(float(val))
            count =1
        
        #print(line)
    elevationXSet = sorted(set(elevationX))
    elevationZSet =sorted(set(elevationZ))
    elevationFile.close()
    
    return elevationXSet, elevationZSet, elevationDict

def setElevationValues(XSet, ZSet, elevDict):
    global elevationDict
    global elevationXSet
    global elevationZSet
    elevationDict = elevDict
    elevationXSet = XSet
    elevationZSet = ZSet
    
def readTerrainFile(terrainFileCSV):
    global terraindDict
    global terrainXSet
    global terrainZSet 
    global path 


    #variables 
  
    terrainFile = open(path+terrainFileCSV+".csv",'r')
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
        
        #print(line)
        
    terrainFile.close()
    
    terrainXSet = sorted(set(terrainX))
    terrainZSet = sorted(set(terrainZ))
    
    return terrainXSet, terrainZSet, terraindDict

def setTerrainValues(XSet, ZSet, terrDict):
    global terraindDict
    global terrainXSet
    global terrainZSet 
    terraindDict = terrDict
    terrainXSet = XSet
    terrainZSet = ZSet
        
def readFiles():
    global terraindDict
    global terrainXSet
    global terrainZSet 
    global elevationDict
    global elevationXSet
    global elevationZSet
    global path 
    global terrainFileCSV
    global elevationFileCSV
    


    #variables 
  
    terrainFile = open(path+terrainFileCSV,'r')
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
        
        #print(line)
        
    terrainFile.close()
    
    terrainXSet = sorted(set(terrainX))
    terrainZSet = sorted(set(terrainZ))
    
    #reads elevation file
    elevationFile = open(path+elevationFileCSV,'r')
    elevationX=[]
    elevationZ =[]
    count=0
    while True:
        
        line = elevationFile.readline()
        if not line:
            break
        if count > 0 :
            line = line.replace('\n','')
            if line != '':
                values = line.split(',')
                elevationZ.append(float(values[0])) #sets Z for elevation
                for i in range (1, len(values)):
                    elev = float(values[i])
                    xz = str(int(elevationX[i-1]))+','+  str(int(values[0]))
                    elevationDict[str(xz)] = elev
        else:
            line = line.replace('\n','')
            values = line.split(',')
            for val in values:
                if val !='':
                    elevationX.append(float(val))
            count =1
        
        #print(line)
    elevationXSet = sorted(set(elevationX))
    elevationZSet =sorted(set(elevationZ))
    elevationFile.close()


def findDistanceAndElevationToPath(x,z, elevationDict, missionType):
    lineSegment = findClosestTwoWaypointXZ(float(x),float(z), missionType)
    x1 = lineSegment[0]
    z1 = lineSegment[1]
    x2 = lineSegment[2]
    z2 = lineSegment[3]
    denominator = x2-x1
    if denominator == 0:
        denominator = 1
    #first find the equation of a line for patrol route
    m = (z2-z1)/(denominator)
    b = z1 - x1*m

    #now find perpendicular slope and line of perpendicular line 
    gradient = 1/m * -1
    c = z - x*gradient

    #solve simulatneous equation
    intesectionX = (c-b)/ (m-gradient)
    intersectionY = m*intesectionX + b
    
    #distance to line 
    distance = math.sqrt(pow(intesectionX-float(x),2)+pow(intersectionY-float(z),2))
    elvChange = elevationDifferenceBetweenPoints(roundup(x),roundup(z),roundup(intesectionX),roundup(intersectionY), elevationDict)
    return distance,elvChange
    
def getTerrainAtLocation(X,Z):
    #readTerrainFile()
    global terraindDict
    global terrainXSet
    global terrainZSet
    newXpos = bisect_left(terrainXSet, X)
    newZpos = bisect_left(terrainZSet, Z)
    xz = str(int(terrainXSet[newXpos])) + ',' + str(int(terrainZSet[newZpos]))
    return terraindDict[xz]

def getElevationAtLocation(X,Z):
    #readElevationFile()
    global elevationDict
    global elevationXSet
    global elevationZSet
    newXpos = bisect_left(elevationXSet, X)
    newZpos = bisect_left(elevationZSet, Z)
    xz = str(int(elevationXSet[newXpos])) + ',' + str(int(elevationZSet[newZpos]))
    return elevationDict[xz]

def findClosestTwoWaypointXZ(x, z, missionType):
    if("Forest" in missionType):
        waypointX = [9800, 9600, 9400,9300]
        waypointZ = [16135,16070, 16016,15980]
    elif("Open" in missionType):
        waypointX = [9400, 9300, 9200,9100, 9060, 9040]
        waypointZ = [15885,15940, 15990,16045,16150, 16260]
    elif("Ft2" in missionType):
        waypointX = [9340, 9400, 9470,9600, 9700, 9800]
        waypointZ = [16470,16515, 16570,16670,16750, 16820]
    elif("Village" in missionType):
        waypointX = [1000110,1000110,1000070,1000050,1000050,1000040,1000000,999990,
                     1000000,1000040,1000070,1000100,1000140,1000150,1000100]
        waypointZ = [1004220,1004170,1004140,1004130,1004070,1004030,1004020,1003980,
                     1003950, 1003900, 1003870,1003820,1003780,1003700,1003680]

        
    '''
    else:
        waypointX = [10284.6,10135.73,9901.62,9132.97,9019.81,9467.22,9918.99,9950.4,10635.28]
        waypointZ = [16132.96,16014.41,16174.41,16009.21,16333.23,16523.04,16820.76,16422.23,16191.95]
    '''

    closest = 10000
    firstBestX = 0
    firstBestZ = 0
    secondClosest = 100000
    secondBestX = 0
    secondBestZ = 0
    for i in range(0,len(waypointX)):
        currentx = waypointX[i]
        currentz = waypointZ[i]
        dis = math.sqrt(pow(currentx-x,2)+pow(currentz-z,2))
        if dis <closest:
            secondClosest = closest
            secondBestX = firstBestX
            secondBestZ = firstBestZ
            firstBestX = currentx
            firstBestZ = currentz
            closest = dis
        elif dis < secondClosest:
            secondBestX = currentx
            secondBestZ = currentz
            secondClosest = dis
    return [firstBestX,firstBestZ,secondBestX,secondBestZ]





def addHeader (headerString, ft, headerCol):
    for val in headerCol:
        headerString+= ft+val+","
    
    return headerString

#helps buid output string   
def addToOutPutString(output, ftValues):
    for value in ftValues:
        output+= str(value)+","
    output[:-1]
    return output          
            
def ftvariables (primary, secondary, tartary, UAV, SUGV, UGV, mg, eSoldier):
    temp = basicPositionandHealth(primary)
    primaryX = temp[0]
    primaryZ  = temp[1]
    percentFTAlive = temp[2]
    atAlive = temp[3]
    ftWoodedTeerain = temp[4]

    temp = basicPositionandHealth(secondary)
    secondaryX = temp[0]
    secondaryZ = temp[1]

    temp = basicPositionandHealth(secondary)
    tartaryX   = temp[0]
    tartaryZ   = temp[1]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, UAV)
    numberUAV200M  = temp[0]
    closestDistanceUAV     = temp[1]
    psAngleUAV     = temp[2]
    ptAngleUAV     = temp[3]
    
    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, SUGV)
    numberSUGV200M = temp[0]
    closestDistanceSUGV    = temp[1]
    psAngleSUGV    = temp[2]
    ptAngleSUGV    = temp[3]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, UGV)
    numberUGV200M  = temp[0]
    closestDistanceUGV     = temp[1]
    psAngleUGV     = temp[2]
    ptAngleUGV     = temp[3]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, mg)
    numberMG200M       = temp[0]
    closestDistanceMG  = temp[1]
    psAngleMG      = temp[2]
    ptAngleMG      = temp[3]

    temp = enemyFTVariables(primaryX, primaryZ, secondaryX, secondaryZ, tartaryX, tartaryZ, eSoldier)
    numberSoldier200M = temp[0]
    closestDistanceSoldier = temp[1]
    psAngleSoldier = temp[2]
    ptAngleSoldier = temp[3]
    return [percentFTAlive, atAlive, ftWoodedTeerain, numberUAV200M, closestDistanceUAV, psAngleUAV, ptAngleUAV, numberSUGV200M, closestDistanceSUGV, psAngleSUGV, ptAngleSUGV,numberUGV200M, closestDistanceUGV, psAngleUGV, ptAngleUGV, numberMG200M, closestDistanceMG, psAngleMG, ptAngleMG,numberSoldier200M, closestDistanceSoldier, psAngleSoldier, ptAngleSoldier ]


#add Terrain to this function 
def basicPositionandHealth (ft):
    ftX = 0.0
    ftZ =0.0
    percentFTAlive = 0.0
    atAlive =0
    percentWoods=0
    for unit in ft:
        vars = ft[unit]
        if vars[2] < 1:
            ftX+=vars[0]
            ftZ+=vars[1]
            percentFTAlive+=1.0
            if 'rpg' in unit:
                atAlive = 1
    if percentFTAlive>0:
        ftX = ftX/percentFTAlive
        ftZ = ftZ/percentFTAlive
        percentFTAlive = percentFTAlive/len(ft)
        global terraindDict
        percentWoods = float(terraindDict[closestXZTerrain(ftX, ftZ)][2])
    return [ftX,ftZ, percentFTAlive, atAlive, percentWoods]


#gets the variables needed for enemyFT relationship
def enemyFTVariables (pX,pZ,sX,sZ, tX,tZ, enemies):
    numberWitin200M = 0
    closestDistance = 100000
    psAngle =0.0
    ptAngle = 0.0
    for enemy in enemies:
        vars = enemies[enemy]
        if vars[2] < 1:
            varX = vars[0]
            varZ = vars[1]
            tempDistance = math.sqrt(math.pow(pX-varX,2)+math.pow(pZ-varZ,2))
            if tempDistance < 200:
                numberWitin200M +=1
                
                if tempDistance < closestDistance:
                    closestDistance=tempDistance
                    psAngle = angleOfAttack(varX,varZ,pX,pZ,sX,sZ)
                    ptAngle = angleOfAttack(varX,varZ,pX,pZ,tX,tZ)
    return [numberWitin200M,closestDistance,psAngle,ptAngle]


def angleOfAttack (enemyX, enemyY, alphaFTX, alphaFTY,bravoFTX, bravoFTy):
    numerator = (alphaFTX-enemyX)*(bravoFTX-enemyX)+(alphaFTY-enemyY)*(bravoFTy-enemyY)
    var1 = math.pow(alphaFTX-enemyX,2)+math.pow(alphaFTY-enemyY,2)
    var2 = math.pow(bravoFTX-enemyX,2)+math.pow(bravoFTy-enemyY,2)
    denominator = math.sqrt(var1) * math.sqrt(var2)
    angle = numerator/denominator
    if angle > 1:
        angle = 1
    elif angle < -1:
        angle = -1
    angle = math.acos(angle)
    return angle

def elevationDifferenceBetweenPoints (ambushX,ambushZ,pathX,pathZ, elevationDict):
    opforElevation = elevationDict[ambushX, ambushZ]
    blueforElevation = elevationDict[pathX,pathZ]
    #print(elevationDict)
    if opforElevation < 0  and blueforElevation > 0 :
        opforElevation = 0.1
        blueforElevation = 0.1
    
    if opforElevation > 0  and blueforElevation < 0 :
        opforElevation = 0.1
        blueforElevation = 0.1

    return math.log(opforElevation/blueforElevation)

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


def closestXZElevation(currentX, currentZ):
    global elevationXSet
    global elevationZSet
    closeX = '0'
    closeZ = '0'
    #finds the closest X value in the terrain set
    pos = bisect_left(elevationXSet, currentX)
    if pos == 0:
        closeX = str(int(elevationXSet[0]))
    if pos == len(elevationXSet):
        closeX = str(int(elevationXSet[-1]))
    before = elevationXSet[pos -1]
    after = elevationXSet[pos]
    if after - currentX < currentX - before:
        closeX = str(int(after))
    else:
        closeX = str(int(before))
    
    #finds the closest Z value in the terrain set
    pos = bisect_left(elevationZSet, currentZ)
    if pos == 0:
        closeZ = str(int(elevationZSet[0]))
    if pos == len(elevationZSet):
        closeZ = str(int(elevationZSet[-1]))
    before = elevationZSet[pos -1]
    after = elevationZSet[pos]
    if after - currentZ < currentZ - before:
        closeZ = str(int(after))
    else:
        closeZ = str(int(before))
    
    return closeX+","+closeZ



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



