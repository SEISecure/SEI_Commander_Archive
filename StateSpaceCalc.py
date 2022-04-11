import database_connect
import math
import csv
import ReadTerrainFile
import FileIO






def distanceBetweenEnemy(opFor, blueFor):
    opForPosition = database_connect.getOpforSoldierPos(opFor)
    blueForPosition = database_connect.getBlueforSoldierPos(blueFor)
    #print(blueForPosition)
    dis = distanceBetweenPoints(float(opForPosition[0]),float(opForPosition[1]), float(blueForPosition[0]),float(blueForPosition[1]))
    return dis

def distanceBetweenEnemywOpForPos(opForPos, blueFor):
    blueForPosition = database_connect.getBlueforSoldierPos(blueFor)
    dis = distanceBetweenPoints(float(opForPos[0]),float(opForPos[1]), float(blueForPosition[0]),float(blueForPosition[1]))
    return dis

def distanceBetweenBlueForceAlly(blueFor, blueForAlly):
    blueForAllyPosition = database_connect.getBlueforSoldierPos(blueForAlly)
    blueForPosition = database_connect.getBlueforSoldierPos(blueFor)
    dis = distanceBetweenPoints(float(blueForAllyPosition[0]),float(blueForAllyPosition[1]), float(blueForPosition[0]),float(blueForPosition[1]))
    return dis

def distanceBetweenOpForceAlly(opFor, opForAlly):
    opForAllyPosition = database_connect.getOpforSoldierPos(opForAlly)
    opForPosition = database_connect.getOpforSoldierPos(opFor)
    dis = distanceBetweenPoints(float(opForAllyPosition[0]),float(opForAllyPosition[1]), float(opForPosition[0]),float(opForPosition[1]))
    return dis

def distanceBetweenPoints(X1,Z1,X2, Z2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Z1- Z2, 2))
    return dis 

def distanceToNearestOpForAlly(opFor, opForSize):
    
    numbers =[]
    soldiers = database_connect.getAllOpForceUnits(opForSize)
    for soldier in soldiers:
        if opFor not in soldier[0] and float(soldier[1]) < 0.99:
            dis = distanceBetweenOpForceAlly(opFor, soldier[0])
            numbers.append(dis)
    if(len(numbers) == 0):
        return "No Allys Alive" 
    return min(numbers)   

def distanceToNearestBlueForAlly(blueFor, blueForSize):
    numbers =[]
    soldiers = database_connect.getAllBlueForceUnits(blueForSize)
    for soldier in soldiers:
        if blueFor not in soldier[0] and float(soldier[1]) < 0.99:
            dis = distanceBetweenBlueForceAlly(blueFor, soldier[0])
            numbers.append(dis)
                  
 
    if(len(numbers) == 0):
        return "No Allys Alive"    
    return min(numbers)    

def distanceBetweenNearestBlueForEnemyandType(blueFor, opForSize ):
    numbers =[]

    soldiers = database_connect.getAllOpForceUnits(opForSize)
    EnemyType = "Rifleman"
    for soldier in soldiers:
        if(float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemy(soldier[0], blueFor)
            numbers.append(distanceFromSol)       
    if(len(numbers) == 0):
        return -1, " "

    return min(numbers), EnemyType                     

def distanceBetweenNearestOpForEnemyandType(opForName,blueForSize):
    numbers =[]
    distanceDict = {}
    EnemyType = "Rifleman"
    soldiers = database_connect.getAllBlueForceUnits(blueForSize)
    visibleEnemies = database_connect.opForVision(opForName)
    for soldier in soldiers:
        if(soldier[0] in visibleEnemies and float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemy(opForName,soldier[0] )
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0]        
    if(len(numbers) == 0):
        return -1, " "
    nearestEnemy = min(numbers) 
    if "gunner" in distanceDict[nearestEnemy]:
        EnemyType = "MGunner"
    elif "grenadier" in distanceDict[nearestEnemy]:
        EnemyType = "Grenadier"
    return min(numbers), EnemyType

def distanceBetweenNearestOpForEnemyWPos(opForPos, opForName, blueForSize):
    numbers =[]
    distanceDict = {}
    EnemyType = "Rifleman"
    soldiers = database_connect.getAllBlueForceUnits(blueForSize)
    visibleEnemies = database_connect.opForVision(opForName)
    for soldier in soldiers:
        if(soldier[0] in visibleEnemies and float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemywOpForPos(opForPos,soldier[0] )
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0] 
    if(len(numbers) == 0):
        return -1
    return min(numbers) 

 
def getForestAtOpForPosLocation(opForPosition, forestDict):
    return forestDict[FileIO.roundup(float(opForPosition[0])), FileIO.roundup(float(opForPosition[1]))] 
 
def getForestAtOpForLocation(opFor, forestDict):
    opForPosition = database_connect.getOpforSoldierPos(opFor) 
    return forestDict[FileIO.roundup(float(opForPosition[0])), FileIO.roundup(float(opForPosition[1]))]

def getForestAtBlueForLocation(blueFor, forestDict):
    blueForPosition = database_connect.getBlueforSoldierPos(blueFor) 
    return forestDict[FileIO.roundup(float(blueForPosition[0])), FileIO.roundup(float(blueForPosition[1]))]

def getForestAtNearestBlueForEnemyLocation(blueForName, forestDict, opForSize):
    numbers =[]
    distanceDict = {}
    soldiers = database_connect.getAllOpForceUnits(opForSize)
    for soldier in soldiers:
        if(float(soldier[1]) < 0.94):

            distanceFromSol = distanceBetweenEnemy(soldier[0], blueForName )
            #print(blueForName)
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0]        
    if(len(numbers) == 0):
        return -1
    nearestEnemyDistance = min(numbers) 
    nearestEnemy = distanceDict[nearestEnemyDistance]
    
    opForPosition = database_connect.getOpforSoldierPos(nearestEnemy)
    return forestDict[FileIO.roundup(float(opForPosition[0])), FileIO.roundup(float(opForPosition[1]))]
 

def getForestAtNearestOpForEnemyLocation(opForName, forestDict, blueForSize):
    numbers =[]
    distanceDict = {}
    soldiers = database_connect.getAllBlueForceUnits(blueForSize)
    visibleEnemies = database_connect.opForVision(opForName)
    for soldier in soldiers:
        #print(visibleEnemies)
        if(soldier[0] in visibleEnemies and float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemy(opForName,soldier[0] )
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0]        
    if(len(numbers) == 0):
        return -1
    nearestEnemyDistance = min(numbers) 
    nearestEnemy = distanceDict[nearestEnemyDistance]
    blueforPosition = database_connect.getBlueforSoldierPos(nearestEnemy)
    return forestDict[FileIO.roundup(float(blueforPosition[0])), FileIO.roundup(float(blueforPosition[1]))]

    
def getForestAtNearestOpForPosEnemyLocation(opForPos, forestDict, blueForSize):
    numbers =[]
    distanceDict = {}
    soldiers = database_connect.getAllBlueForceUnits(blueForSize)
    for soldier in soldiers:

        if(float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemywOpForPos(opForPos, soldier[0] )
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0]        
    if(len(numbers) == 0):
        return -1
    nearestEnemyDistance = min(numbers) 
    nearestEnemy = distanceDict[nearestEnemyDistance]
    blueforPosition = database_connect.getBlueforSoldierPos(nearestEnemy)
    return forestDict[FileIO.roundup(float(blueforPosition[0])), FileIO.roundup(float(blueforPosition[1]))]
 
def getForestAtLocationFromTerrainFile(fileName, X, Z): 
    lethality = 0
    with open(fileName+'.csv', 'rt') as f:
        #header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        results = filter(lambda x: x[1]==str(ReadTerrainFile.roundup(float(X))) and x[3]==str(ReadTerrainFile.roundup(float(Z))), reader)
        #print(results)
        for line in results:
            return line[6]

def elevationDifFromNearestBlueForEnemy(blueForName, elevationDict, opForSize):
    numbers =[]
    distanceDict = {}
    soldiers = database_connect.getAllOpForceUnits(opForSize)
 
    for soldier in soldiers:
        if( float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemy(soldier[0], blueForName)
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0]        
    if(len(numbers) == 0):
        return -1
    nearestEnemyDistance = min(numbers) 
    nearestEnemy = distanceDict[nearestEnemyDistance]
    opForPosition = database_connect.getOpforSoldierPos(nearestEnemy)
    blueForPosition = database_connect.getBlueforSoldierPos(blueForName)
    return  ReadTerrainFile.elevationDifferenceBetweenPoints(FileIO.roundup(float(opForPosition[0])),FileIO.roundup(float(opForPosition[1])),
                                                             FileIO.roundup(float(blueForPosition[0])),FileIO.roundup(float(blueForPosition[1])), elevationDict) 
   



def elevationDifFromNearestOpForEnemy(opForName, elevationDict, blueForSize):
    
    numbers =[]
    distanceDict = {}
    soldiers = database_connect.getAllBlueForceUnits(blueForSize)
    visibleEnemies = database_connect.opForVision(opForName)
    for soldier in soldiers:
 
        if(soldier[0] in visibleEnemies and float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemy(opForName,soldier[0] )
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0]        
    if(len(numbers) == 0):
        return -1
    nearestEnemyDistance = min(numbers) 
    nearestEnemy = distanceDict[nearestEnemyDistance]
    opForPosition = database_connect.getOpforSoldierPos(opForName)
    blueForPosition = database_connect.getBlueforSoldierPos(nearestEnemy)
    return  ReadTerrainFile.elevationDifferenceBetweenPoints(FileIO.roundup(float(opForPosition[0])),FileIO.roundup(float(opForPosition[1])),
                                                             FileIO.roundup(float(blueForPosition[0])),FileIO.roundup(float(blueForPosition[1])), elevationDict) 


def elevationDifFromNearestOpForEnemyPos(opForPos, opForName, elevationDict, blueForSize):
    numbers =[]
    distanceDict = {}
    soldiers = database_connect.getAllBlueForceUnits(blueForSize)
    visibleEnemies = database_connect.opForVision(opForName)
    for soldier in soldiers:
        if(soldier[0] in visibleEnemies and float(soldier[1]) < 0.94):
            distanceFromSol = distanceBetweenEnemy(opForName,soldier[0] )
            numbers.append(distanceFromSol)
            distanceDict[distanceFromSol] = soldier[0]        
    if(len(numbers) == 0):
        return -1
    nearestEnemyDistance = min(numbers) 
    nearestEnemy = distanceDict[nearestEnemyDistance]
    blueForPosition = database_connect.getBlueforSoldierPos(nearestEnemy)
    return  ReadTerrainFile.elevationDifferenceBetweenPoints(FileIO.roundup(float(opForPos[0])),FileIO.roundup(float(opForPos[1])),
                                                             FileIO.roundup(float(blueForPosition[0])),FileIO.roundup(float(blueForPosition[1])), elevationDict) 
    return "No enemies"



def opForXPosition(opFor):
    Xpos = database_connect.getOpforSoldierPos(opFor)
    
    return Xpos[0]


def opForZPosition(opFor):
    Zpos = database_connect.getOpforSoldierPos(opFor)
    
    return Zpos[1]

def blueForXPosition(blueFor):
    Xpos = database_connect.getBlueforSoldierPos(blueFor)
    
    return Xpos[0]


def blueForZPosition(blueFor):
    Zpos = database_connect.getBlueforSoldierPos(blueFor)
    
    return Zpos[1]

def opForXVelocity(opFor):
    Xvelocity = database_connect.getOpforUnit(opFor)
    
    return Xvelocity[3] 

def opForZVelocity(opFor):
    Zvelocity = database_connect.getOpforUnit(opFor)
    
    return Zvelocity[3] 

def blueForXVelocity(blueFor):
    Xvelocity = database_connect.getOpforUnit(blueFor)
    
    return Xvelocity[3] 

def blueForZVelocity(blueFor):
    Zvelocity = database_connect.getOpforUnit(blueFor)
    
    return Zvelocity[3] 

def OpForAnglesOfAttack(opforPos, opforAllyPos, blueForceSize):
    
    soldiers = database_connect.getAllBlueForceUnits(blueForceSize)
    anglesOfAttack = []
    for soldier in soldiers:
        if(float(soldier[1]) < 0.94):
            blueSolAngle = angleOfAttack(soldier[2], soldier[3], opforPos[0], opforPos[1],opforAllyPos[0], opforAllyPos[1])
            anglesOfAttack.append(blueSolAngle) 
    if len(anglesOfAttack) != 0:
        return max(anglesOfAttack), min(anglesOfAttack)
    return -1, -1

def BlueForAnglesOfAttack(blueforPos, blueforAllyPos, opForceSize):
    
    soldiers = database_connect.getAllOpForceUnits(opForceSize)
    anglesOfAttack = []
    for soldier in soldiers:
        if(float(soldier[1]) < 0.94):
            opSolAngle = angleOfAttack(soldier[2], soldier[3],  blueforPos[0], blueforPos[1],blueforAllyPos[0], blueforAllyPos[1])
            anglesOfAttack.append(opSolAngle)     
    if len(anglesOfAttack) != 0:
        return max(anglesOfAttack), min(anglesOfAttack)
    return -1, -1


    


def angleOfAttack (enemyX, enemyY, alphaFTX, alphaFTY,bravoFTX, bravoFTy):
    numerator = (float(alphaFTX)-float(enemyX))*(float(bravoFTX)-float(enemyX))+(float(alphaFTY)-float(enemyY))*(float(bravoFTy)-float(enemyY))
    var1 = math.pow(float(alphaFTX)-float(enemyX),2)+math.pow(float(alphaFTY)-float(enemyY),2)
    var2 = math.pow(float(bravoFTX)-float(enemyX),2)+math.pow(float(bravoFTy)-float(enemyY),2)
    var3 = 0
    denominator = math.sqrt(var1) * math.sqrt(var2)
    if(denominator == 0):
        var3 = numerator
    else:
        var3 = numerator/denominator
    if(var3 < -1):
        var3 = -1
    if(var3 > 1):
        var3 = 1
    angle = math.acos(var3)
    return math.fabs(angle)















   
    