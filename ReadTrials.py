#reads the csv and creates data needed to train the ONR neural network modelt csv
import csv
import numpy
import math
import io
from bisect import bisect_left
terraindDict={}
terrainXSet ={}
terrainZSet ={}
def main():
    nameOfFolder = "ForestMovementBottomLeft"
    nameOfFile = "move3"
    header = True 
    starting = True
    cutOffTime = 0
    global terraindDict
    global terrainXSet
    global terrainZSet 
    ft1Position ={}
    ft2Position ={}
    ft3Position ={}
    mgPosition ={}
    SUGVPosition = {}
    UGVPosition={}
    UAVPosition={}
    enSoldierPosition ={}
    


    #variables 
    ft1Vars = {}
    ft2Vars = {}
    ft3Vars = {}
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
        
        #print(line)
    terrainFile.close()
    terrainXSet = sorted(set(terrainX))
    terrainZSet = sorted(set(terrainZ))


    step=0
    with open('C:/Users/Roy Hayes/Downloads/PositionData/'+nameOfFolder+'/'+nameOfFile+'.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if header:
                header = False
            else:
                #gets the x,z, and health of a unti 
                time = row[0].split(':')
                seconds = float(time[0])*60+float(time[1])
                unitName = row[1]
                X = float(row[2])
                Z= float(row[4])
                health = float(row[8])
                
                if starting:
                    cutOffTime = seconds+5
                    
                    starting=False
                elif seconds > cutOffTime:
                    ft1Vars[step] = ftvariables(ft1Position, ft2Position, ft3Position, UAVPosition, SUGVPosition, UGVPosition, mgPosition, enSoldierPosition)
                    ft2Vars[step] = ftvariables(ft2Position, ft3Position, ft1Position, UAVPosition, SUGVPosition, UGVPosition, mgPosition, enSoldierPosition)
                    ft3Vars[step] = ftvariables(ft3Position, ft1Position, ft2Position, UAVPosition, SUGVPosition, UGVPosition, mgPosition, enSoldierPosition)
                    step+=1
                    cutOffTime = cutOffTime+5
                    

            #update the position and health of unti     
                if 'ft1' in unitName:
                    ft1Position[unitName] =[X,Z,health]
                elif 'ft2' in unitName:
                    ft2Position[unitName] =[X,Z,health]
                elif 'ft3' in unitName:
                    ft3Position[unitName] =[X,Z,health]
                elif 'UAV' in unitName:
                    UAVPosition[unitName] =[X,Z,health]
                elif 'SUGV' in unitName:
                    SUGVPosition[unitName] =[X,Z,health]
                elif 'UGV' in unitName and 'SUGV' not in unitName:
                    UGVPosition[unitName] =[X,Z,health]
                elif 'mg' in unitName and 'gunner' not in unitName:
                    mgPosition[unitName] =[X,Z,health]
                else:
                    enSoldierPosition[unitName] =[X,Z,health]
    i = 0
    j = i+4
    f = open('C:/Users/Roy Hayes/Downloads/PositionData/'+nameOfFolder+'/'+nameOfFile+'CleanedData.csv', "w")
    f.write('')
    f.close()
    f = open('C:/Users/Roy Hayes/Downloads/PositionData/'+nameOfFolder+'/'+nameOfFile+'CleanedData.csv', "a")
    headerVars = ['percentFTAlive', 'atAlive', 'ftWoodedTeerain', 'numberUAV200M', 'closestDistanceUAV', 'psAngleUAV', 'ptAngleUAV', 'numberSUGV200M', 'closestDistanceSUGV', 'psAngleSUGV', 'ptAngleSUGV','numberUGV200M', 'closestDistanceUGV', 'psAngleUGV', 'ptAngleUGV', 'numberMG200M', 'closestDistanceMG', 'psAngleMG', 'ptAngleMG','numberSoldier200M', 'closestDistanceSoldier', 'psAngleSoldier', 'ptAngleSoldier']
    
    header = 'ft1AliveFuture, ft2AliveFuture, ft3AliveFuture,'
    header = addHeader(header,"ft1", headerVars) 
    header =addHeader(header,"ft2", headerVars)
    header =addHeader(header,"ft3", headerVars)
    header=header[:-1]
    header+='\n'
    f.write(header)
    while j<step:
        outPut=''
        ft1cuurentVars = ft1Vars[i]
        ft2cuurentVars = ft2Vars[i]
        ft3cuurentVars = ft3Vars[i]

        ft1PercentAlive = ft1Vars[j][0]
        ft2PercentAlive = ft2Vars[j][0]
        ft3PercentAlive = ft3Vars[j][0]
        outPut += str(ft1PercentAlive) + "," +str(ft2PercentAlive)+","+str(ft3PercentAlive)+","
        outPut= addToOutPutString(outPut, ft1cuurentVars)
        outPut= addToOutPutString(outPut, ft2cuurentVars)
        outPut= addToOutPutString(outPut, ft3cuurentVars)
        outPut+= "\n"
        i+=1
        j+=1
        
        f.write(outPut)
        
    
    f.close()

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



if __name__ == "__main__":
    main()
