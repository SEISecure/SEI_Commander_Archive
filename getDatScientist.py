import psycopg2
import numpy as np
import asyncio
import database_connect_Arma
import random
import math



_0  =  [999856.359009,96.221260,999886.830676]
_1 =  [999910.432839,97.517708,999862.968756]
_2 =  [999953.374869,98.342293,999845.724716]
_3 =  [1000012.524979,100.935463,999821.103426]
_4 =  [1000081.194409,102.111061,999802.616106]
_5 =  [1000156.024519,103.022148,999767.085316]
_6 =  [999842.701699,96.446587,999841.291186]
_7 =  [999902.470509,96.048286,999842.177246]
_8 =  [999946.759609,97.687683,999823.111706]
_9 =  [1000090.718029,103.692177,999771.412466]
_10 =  [1000126.190319,105.747803,999749.289946]
_11 =  [999820.895779,97.572746,999806.858536]
_12 =  [999846.053879,98.177528,999811.374096]
_13 =  [999867.126469,98.192413,999809.653876]
_14 =  [999955.502289,99.312180,999797.182346]
_15 =  [999973.134449,101.291924,999769.228926]
_16 =  [1000001.732949,101.501961,999783.850716]
_17 =  [1000037.157619,102.031738,999764.920336]
_18 =  [1000080.442359,103.058632,999740.216216]
_19 =  [1000124.823709,104.145416,999718.950166]
_20 =  [1000146.291999,104.050911,999719.347296]
_21 =  [999837.427599,98.758614,999792.866706]
_22 =  [999871.641719,99.168503,999788.592036]
_23 =  [999895.484729,96.832077,999782.760466]
_24 =  [999918.922619,97.466347,999769.858876]
_25 =  [999942.790549,99.036308,999755.667146]
_26 =  [999973.341749,101.546783,999748.817006]
_27 =  [999995.001829,102.292023,999747.865576]
_28 =  [1000026.739769,102.764870,999739.769406]
_29 =  [1000054.937309,103.053146,999732.706266]
_30 =  [1000085.346329,104.193871,999704.905796]
_31 =  [1000105.988859,105.124962,999702.110446]
_32 =  [1000121.470749,105.360161,999689.208866]
_33 =  [1000147.703989,103.573334,999688.348776]
_34 =  [999805.881529,97.484894,999782.394436]
_35 =  [999841.964019,99.596893,999761.619696]
_36 =  [999871.212689,99.929237,999752.052356]
_37 =  [999929.710049,99.563843,999731.277616]
_38 =  [999964.403089,101.926697,999722.882386]
_39 =  [999989.386269,102.712143,999717.733186]
_40 =  [1000011.657259,103.297768,999709.813316]
_41 =  [1000079.807249,104.401154,999686.135456]
_42 =  [1000124.281719,104.936081,999674.311356]
_43 =  [1000140.110759,103.397827,999668.590016]
_44 =  [999825.011859,98.896721,999748.687866]
_45 =  [999842.710099,99.960709,999735.596006]
_46 =  [999873.257749,100.844719,999725.655896]
_47 =  [999907.199569,100.760628,999714.503606]
_48 =  [999929.746619,101.231247,999710.382086]
_49 =  [999954.735149,102.317017,999704.514256]
_50 =  [999977.039779,102.656982,999699.180546]
_51 =  [1000008.799629,103.615311,999686.816006]
_52 =  [1000056.736769,104.533974,999665.498196]
_53 =  [1000082.435589,104.820023,999667.922606]
_54 =  [1000103.770439,105.617973,999665.983076]
_55 =  [1000122.195999,104.670540,999660.164476]
_56 =  [999789.323699,96.638924,999745.457506]
_57 =  [999822.295759,99.469940,999727.516846]
_58 =  [999840.236449,100.491676,999716.122086]
_59 =  [999869.814309,101.120934,999706.909306]
_60 =  [999904.483459,101.578201,999693.817446]
_61 =  [999925.772179,101.936256,999690.889746]
_62 =  [999954.970069,102.549797,999685.856536]
_63 =  [1000010.106729,103.533524,999664.406416]
_64 =  [1000043.152449,104.722481,999652.999196]
_65 =  [1000070.548369,105.307213,999642.574206]
_66 =  [1000115.400039,104.621513,999631.906786]
_67 =  [1000135.280289,103.437332,999625.360856]
_68 =  [999818.255699,97.030670,999683.070486]
_69 =  [999872.320179,98.612190,999662.220486]
_70 =  [999929.778839,98.895508,999643.067616]
_71 =  [1000017.875479,102.497398,999643.693966]
_72 =  [1000034.451779,103.705994,999622.889056]
_73 =  [1000066.781809,105.875610,999612.126116]
_74 =  [1000113.012489,105.134468,999611.481036]
_75 =  [999981.201309,100.491257,999628.683156]
_76 =  [1000012.285709,102.095207,999606.475006]
_77 =  [1000040.763619,105.209763,999595.569076]
_78 =  [1000065.705889,106.134117,999594.731556]
_79 =  [1000109.572029,105.967850,999591.483566]
_80 =  [1000138.815659,105.442253,999590.193406]
_81 =  [999971.525119,100.945824,999578.366956]
_82 =  [1000015.820549,103.392838,999569.765916]
_83 =  [1000046.569319,106.054443,999569.550886]
_84 =  [1000110.862209,106.938820,999564.605276]
_85 =  [1000009.473,102.73,999740.30]

route_1  = [_83,_77,_76,_71,_64,_52,_51,_50,_38,_26,_27,_85]
route_2  = [_83,_77,_72,_64,_65,_53,_41,_40,_28,_17,_16,_85]
route_3  = [_83,_82,_81,_70,_69,_68,_56,_34,_11,_21,_22,_25,_26,_27,_85]
route_4 = [_83, _82, _81, _75, _63, _62, _61, _60, _59, _58, _57, _56, _34, _11, _6, _0, _1, _2, _3, _4, _17, _28,_85]
route_5 = [_83, _77, _72, _64, _65, _53, _41, _40, _27, _17, _4, _3, _2, _1, _0, _6, _13, _25, _15, _27,_85]
route_6 = [_83, _77, _73, _74, _67, _43, _42, _41, _40, _28, _17,_85]
route_7 = [_83, _77, _72, _64, _65, _53, _41, _40, _51, _50, _38, _37, _25, _15, _27,_85]
route_8 = [_83, _77, _72, _64, _65, _53, _41, _40, _28, _17, _4, _3, _8, _23, _25, _15, _27,_85]
route_9 = [_83, _82, _81, _75, _71, _64, _52, _51, _50, _49, _62, _61, _60, _59, _58, _57, _56, _34, _11, _21, _22, _25, _26, _27, _85]
route_10 = [_83, _82, _81, _70, _69, _68, _56, _34, _11, _6, _0, _1, _2, _3, _4, _17, _28, _85]
route_11 = [_83, _82, _81, _75, _63, _62, _61, _60, _59, _58, _57, _56, _34, _11, _6, _0, _1, _2, _3, _16, _85]
route_12 = [_83, _77, _73, _74, _67, _43, _33, _32, _31, _41, _40, _28, _85]


pos1 = [999986.943,0,1000063.711]
pos2 = [999991.513,0,1000169.419]
pos3 = [999668.241,0,1000123.199]
t_route = [pos1,pos2,pos3]

async def runner():

    #assignPathToFireTeam("ft1")
    #assignPathToFireTeam("ft2")
    #assignPathToFireTeam("ft3")

    '''
    while True:
        missionStatus  = database_connect_Arma.missionStat()
        print(missionStatus)
        if missionStatus ! = 0:
            if ("End" in missionStatus ):
                database_connect_Arma.sendToFileMisssionStatus()
                database_connect_Arma.sendToFileUAVThreats()
                print("Data Outputed")
                database_connect_Arma.resetMisDB()
    '''

def assignPathToFireTeam(fireTeam):
    global route_1 
    global route_2  
    global route_3  
    global route_4 
    global route_5
    global route_6
    global route_7 
    global route_8
    global route_9 
    global route_10 
    global route_11 
    global route_12 
    global t_route
    print(fireTeam)
    print("Do route test")
    #moveFireTeamByWaypoint(t_route, fireTeam)
    while True:
        missionStatus = database_connect_Arma.missionStat()
        print(missionStatus)
        if missionStatus != 0:
            if ("End" in missionStatus or missionStatus == "" ):
                break
        n  = random.randint(0,100)
        if(n<31):
            print("Do route 1")  
            processRoutePath(route_1, fireTeam)
        elif(n<53):
            print("Do route 2")
            processRoutePath(route_2, fireTeam)
        elif(n<65):
            print("Do route 3")
            processRoutePath(route_3, fireTeam)
        elif(n<72):
            print("Do route 4")
            processRoutePath(route_4, fireTeam)
        elif(n<77):
            print("Do route 5")
            processRoutePath(route_5, fireTeam)
        elif(n<82):
            print("Do route 6")
            processRoutePath(route_6, fireTeam)
        elif(n<86):
            print("Do route 7")
            processRoutePath(route_7, fireTeam)
        elif(n<90):
            print("Do route 8")
            processRoutePath(route_8, fireTeam)
        elif(n<93):
            print("Do route 9")
            processRoutePath(route_9, fireTeam)
        elif(n<96):
            print("Do route 10")
            processRoutePath(route_10, fireTeam)
        elif(n<98):
            print("Do route 11")
            processRoutePath(route_11, fireTeam)
        else:
            print("Do route 12")
            processRoutePath(route_12, fireTeam)
    

def processRoutePath(route, fireTeam):
    newPos = None
    prevPos = None
    flag = False
    for x in range(0, len(route)):
        missionStatus = database_connect_Arma.missionStat()
        if missionStatus == "" or missionStatus == "End":
            print("mission ended")
            break
        if x == 0:
            while True:
                newPos = route[0]
                print("base condition")
                flag = moveFireTeamByPos(newPos,prevPos, fireTeam)
                if flag == True:
                    break
        else:
            while True:
                missionStatus = database_connect_Arma.missionStat()
                if missionStatus == "" or missionStatus == "End":
                    print("mission ended")
                    break
                newPos = route[x]
                prevPos = route[x-1]
                print("loopin", x)
                flag = moveFireTeamByPos(newPos,prevPos, fireTeam)
                if flag == True:
                    break
                
        
    

def distanceBetweenPoints(X1,Y1,X2,Y2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Y1- Y2, 2))
    return dis 

def moveFireTeamByPos(newPos,prevPos, fireTeam):
    database_connect_Arma.setConnection("127.0.0.1")
    flag = False
    #while True:
    #numberofUnits  = database_connect_Arma.numOfAlive_v2()
    #numberofUnits  = database_connect_Arma.numOfAlive_v2()
    #allunits  = database_connect_Arma.getAllOpForceUnits(numberofUnits)
    allunits = database_connect_Arma.getOpForceFireTeam(4,fireTeam)
    if prevPos != None:
        fireTeamMinDis = 100
        for unit in allunits:
            if fireTeam in  unit[0] and float(unit[1]) > 5 :
                dis = distanceBetweenPoints(float(unit[2]),float(unit[4]),prevPos[0],prevPos[2])
                if fireTeamMinDis> dis:
                    fireTeamMinDis=dis
                    
        if fireTeamMinDis<=10:
            for unit in allunits:
                    if fireTeam in  unit[0] and float(unit[1]) > 5 :
                        #fireTeamLeader = unit
                        #print("unit pos :", float(unit[1]),float(unit[3]))
                        #print("prevPos :", prevPos[0],prevPos[2])
                        #dis = distanceBetweenPoints(float(unit[2]),float(unit[4]),prevPos[0],prevPos[2])
                        #if dis < 10:                         
                        flag = True
                        print("Going To Next Route Point", unit[0])
                        database_connect_Arma.moveUnit(newPos[0],newPos[1], newPos[2], unit[0])
                        '''
                            for unit in allunits:
                                if fireTeam in unit[0] and fireTeamLeader[0] != unit[0]:
                                    database_connect_Arma.followUnit(unit[0], fireTeamLeader[0])
                            '''
                    else:
                        print("found none")
    else:  
        for unit in allunits:
                if fireTeam in  unit[0]:
                    #fireTeamLeader = unit
                    database_connect_Arma.moveUnit(newPos[0],newPos[1], newPos[2], unit[0])
                    flag = True
                    '''
                    for unit in allunits:
                        if fireTeam in unit[0] and fireTeamLeader[0] != unit[0]:
                            database_connect_Arma.followUnit(unit[0], fireTeamLeader[0])
                    '''
                    print("Going to First Route Point")
                    
                    
        #if flag == True:
        #   break
    
    return flag                    
        


def moveFireTeamByWaypoint(coordsList, fireTeam):
    database_connect_Arma.setConnection("127.0.0.1")
    #numberofUnits  = database_connect_Arma.numOfAlive_v2()
    numberofUnits  = database_connect_Arma.numOfAlive_v2Blue()
    allunits  = database_connect_Arma.getAllBlueForceUnits(numberofUnits)
    for unit in allunits:
        if fireTeam in  unit[0]:
            database_connect_Arma.moveUnitW(coordsList, unit[0])

async def main():
    #readTerrain()
    task  = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())