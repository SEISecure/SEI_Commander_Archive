import psycopg2
import numpy as np



#database connection information currently on localhost
connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")

soldierid = 0
def getOpforBuddyTeam(ft, ftSize):
    cursor = connection.cursor()
    cursor.execute("select unit_name, health, px, pz, vx, vz, timestamp from opforpositiondataarma where unit_name like '" + ft + "%' order by timestamp desc limit "+ str(ftSize) + ";")
    soldiers = cursor.fetchall()
    return soldiers
def getNumberofBlueForceUnits():
    cursor = connection.cursor()
    cursor.execute("select count(distinct unit_name) from blueforpositiondataArma order by timestamp desc limit 1;")
    count = cursor.fetchone()
    return int(count[0])

def getNumberofOpForceUnits():
    cursor = connection.cursor()
    cursor.execute("select count(distinct unit_name) from opforpositiondataArma  order by timestamp desc limit 1;")
    count = cursor.fetchone()
    return int(count[0])

def getTimestampBlue():
    cursor = connection.cursor()
    cursor.execute("select timestamp from blueforpositiondataArma  order by timestamp desc limit 1;")
    time = cursor.fetchone()
    return time[0]
def getTimestampOpfor():
    cursor = connection.cursor()
    cursor.execute("select timestamp from opforpositiondataArma  order by timestamp asc limit 1;")
    time = cursor.fetchone()
    return time[0]

def getAllBlueForceUnits(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("select unit_name, health, px, py, pz, timestamp from positiondata  order by timestamp desc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getAllOpForceUnits(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("select unit_name, health, px, py, pz, timestamp from positiondata  order by timestamp desc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getOpForceUnitsByTimestamp(timestamp):

    cursor = connection.cursor()
    cursor.execute("select unit_name, health, px, py, pz, timestamp from positiondata  where timestamp =" + str(timestamp) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getAllBlueForceUnitsASC(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp from positiondata  where side = 'blufor'  order by timestamp asc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getAllOpForceUnitsASC(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp from positiondata where side = 'opfor'  order by timestamp asc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getInitOpForceUnit(unit_name):

    cursor = connection.cursor()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp from positiondata where unit_name = '" + unit_name + "' order by timestamp asc limit 1;")
    soldiers = cursor.fetchone()
    return soldiers

def soldierMoveCommand(sol, X, Y, Z):
    global soldierid
    soldierpositionString = "'" + str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z))  + "'"
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + sol + "', 'move'," + soldierpositionString + ");"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def soldierSetPosCommand(sol, X, Y, Z):
    global soldierid
    soldierpositionString = "'" + str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z))  + "'"
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + sol + "', 'setPos'," + soldierpositionString + ");"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()
    
def Broadcast(side):
    global soldierid
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, command)  values ('" + str(soldierid) + "', 'broadcast " + side + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()    
    
#two new functions to get initial pos

def initPosBlue(blueforUnit):
    cursor = connection.cursor()
    cursor.execute("select px, py, pz from blueforpositiondataarma where unit_name = '" + blueforUnit + "' order by timestamp asc limit 1;")
    soldier = cursor.fetchone()
    return soldier
    
def initPosRed(opforUnit):
    cursor = connection.cursor()
    cursor.execute("select px, py, pz from opforpositiondataarma where unit_name = '" + opforUnit + "' order by timestamp asc limit 1;")
    soldier = cursor.fetchone()
    return soldier    

def resetHP(unitIndex, side):
    global soldierid
    params = side 
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, command, params)  values ('" + str(soldierid) + "', 'setDamage','" + params + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()


def resetAmmo(sol):
    global soldierid
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command)  values ('" + str(soldierid) + "','" + sol + "', 'setAmmo');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def respawnSol(sol):
    global soldierid
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command)  values ('" + str(soldierid) + "','" + sol + "', 'respawn');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def numOfAlive(side):
    cursor = connection.cursor()
    cursor.execute("select number_alive from UnitCount where side='" +side+ "';")
    count = cursor.fetchone()
    return count[0]

def numOfAlive_v2():
    cursor = connection.cursor()
    cursor.execute("select count(distinct(unit_name)) from positiondata where timestamp > (select max(timestamp) from positiondata where side = 'opfor')  - interval '2 second' and side = 'opfor' and cast(health as integer) > 0 ;")
    count = cursor.fetchone()
    return count[0]

def numOfAlive_v2Blue():
    cursor = connection.cursor()
    cursor.execute("select count(distinct(unit_name)) from positiondata where timestamp > (select max(timestamp) from positiondata where side = 'blufor')  - interval '2 second' and side = 'blufor' and cast(health as integer) > 0 ;")
    count = cursor.fetchone()
    return count[0]

def createUnit(unit_type, X, Y, Z, side):
    global soldierid
    position =  str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z)) 
    params = unit_type + "@" + position + "@" + side
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, command, params)  values ('" + str(soldierid) + "','createUnit','" + params + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()
    
def moveUnit(side, X, Y, Z, unitName):
    global soldierid
    position =  str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z)) 
    params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, command, params)  values ('" + str(soldierid) + "', 'moveUnit','" + params + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()
    
def moveAllUnits(side, positionArray, unitsAlive):
    global soldierid
    #position =  str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z)) 
    print("printing positions sent", positionArray)
    params = str(positionArray) + "@" + side + "@" + str(unitsAlive) 
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommandArma (soldierid, command, params)  values ('" + str(soldierid) + "', 'moveUnit','" + params + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def resetDB():
    cursor = connection.cursor()
    cursor.execute("delete from blueforpositiondataarma;")
    connection.commit()
    cursor.execute("delete from opforpositiondataarma;")
    connection.commit()

#moved to database_connect_ArmaRuns
'''
def armaRunData(runNumber, time, opfor_dead, bluefor_dead, blue_sent_location_x, blue_sent_location_y, percentBuddyTeamVisibleRange, minCover,
                 minConcealment, averageCover, averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, areaLeftUnsearched, distanceMoved):
    cursor = connection.cursor()
    preparedStatement = "insert into armaruns (runNumber, timestamp, opfor_remaining, bluefor_remaining, blue_sent_location_x, blue_sent_location_y, percentBuddyTeamVisibleRange, \
    minCover, minConcealment, averageCover, averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, areaLeftUnsearched, distanceMoved) \
     values ('" + str(runNumber) + "','" + str(time) + "','" + str(opfor_dead) +  "','" + str(bluefor_dead) + "','"+ str(blue_sent_location_x) + "','" + str(blue_sent_location_y) + "','" \
     + str(percentBuddyTeamVisibleRange) +  "','" + str(minCover) + "','" + str(minConcealment) + "','" + str(averageCover) + \
      "','" + str(averageConcealment) + "','" + str(averageVisibleArea) + "','" + str(percentBuddyTeamNotMoving) + \
       "','" + str(largestNumberBuddyTeam30Meters) + "','" + str(areaLeftUnsearched) + "','" + str(distanceMoved) +  "');"
    cursor.execute(preparedStatement)
    connection.commit()
    
def getNumberofRuns():
    cursor = connection.cursor()
    cursor.execute("select count(runNumber) from armaruns;")
    count = cursor.fetchone()
    return int(count[0])

def insertWeights(weight_percentBuddyTeamVisibleRange,
weight_minCover,
weight_minConcealment,
weight_averageCover,
weight_averageConcealment,
weight_averageVisibleArea,
weight_percentBuddyTeamNotMoving, 
weight_largestNumberBuddyTeam30Meters,
weight_areaLeftUnsearched,
weight_distanceMoved ):

    cursor = connection.cursor()
    soldier1Move = "insert into GeneratedWeigths (percentBuddyTeamVisibleRange, minCover, minConcealment, averageCover, \
     averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, \
areaLeftUnsearched, distanceMoved)  values ('" + str(weight_percentBuddyTeamVisibleRange) + "','" + str(weight_minCover) + \
"','" + str(weight_minConcealment) + "','" + str(weight_averageCover) + "','" + str(weight_averageConcealment) + \
"','" + str(weight_averageVisibleArea) + "','" + str(weight_percentBuddyTeamNotMoving) +"','" + str(weight_largestNumberBuddyTeam30Meters) + \
 "','" + str(weight_areaLeftUnsearched) + "','" + str(weight_distanceMoved) + "');"

    cursor.execute(soldier1Move)
    connection.commit()
     
     
def getWeights():
    cursor = connection.cursor()
    cursor.execute("select percentBuddyTeamVisibleRange, minCover, minConcealment, averageCover, \
     averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, \
areaLeftUnsearched, distanceMoved from GeneratedWeigths;")
    weights = cursor.fetchone()
    cursor.execute("delete from GeneratedWeigths;")
    connection.commit()
    return weights
'''
    
    