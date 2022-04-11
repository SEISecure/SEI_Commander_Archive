import psycopg2
import numpy as np
import datetime
import glob
import os
from datetime import datetime
import math

#database connection information currently on localhost
connection = ""




soldierid = 0
runId = 0

def setConnection(host):
    global connection
    connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = host,
                                  port = "5432",
                                  database = "units")
    
    
def insertDetections(timestamp, unit_name, enemyPos, enemyName):
    #def insertDetectionData(timestamp, unit_name, enemyPos, enemyName):
    #date_time_obj = datetime.datetime.strptime(timestamp, '%H:%M:%S.%f')
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into detections (timestamp, unit_name, target_name, target_x, target_y, target_z)  values ('" + str(timestamp) + "', '" + unit_name + "', '" + enemyName + "', '" + str(enemyPos[0]) + "', '" + str(enemyPos[1]) + "', '" + str(enemyPos[2]) + "');"
    cursor.execute(soldier1Move)
    connection.commit()

#insert into UAVActions (uav_name, current_action) values ($1, $2) on conflict (uav_name) do update set current_action = excluded.current_action;")

def updateRiskAtLocation(x,z,risk,dis_toGoal, dis_toConceal):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into locationRisk (x_lat, z_long, risk, dis_to_goal, dis_to_concealment)  \
    values ('" + str(x) + "', '" + str(z) + "', '" + str(risk) + "', '" + str(dis_toGoal) + "', '" + str(dis_toConceal) + "') on conflict (x_lat,z_long) do update set risk = excluded.risk,  dis_to_goal = excluded.dis_to_goal, dis_to_concealment = excluded.dis_to_concealment;"
    cursor.execute(soldier1Move)
    connection.commit()

def getRiskDataAtLocation(x,z):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select risk, dis_to_goal, dis_to_concealment from locationRisk where x_lat = '" + str(x) + "'  and z_long = '"+ str(z) + "';")
    riskData = cursor.fetchone()
    return riskData

def insertRiskAtLocation(x,z,risk,dis_toGoal,dis_toConceal):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into locationRisk (x_lat, z_long, risk, dis_to_goal, dis_to_concealment)  values ('" + str(x) + "', '" + str(z) + "', '" + str(risk) + "', '" + str(dis_toGoal) + "', '" + str(dis_toConceal) + "');"
    cursor.execute(soldier1Move)
    connection.commit()


def insertPos(data, side):
    #def insertDetectionData(timestamp, unit_name, enemyPos, enemyName):
    #date_time_obj = datetime.datetime.strptime(timestamp, '%H:%M:%S.%f')
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into positiondata (timestamp, unit_name, px, py, pz, health, side)  values ('" + str(data[5]) + "', '" + data[0] + \
         "', '" + str(data[2]) + "', '" + str(data[3]) + "', '" + str(data[4]) + "' , '" + str(data[1]) + "' , '" + str(side) + "');"
    cursor.execute(soldier1Move)
    connection.commit()

def getOpforBuddyTeam(ft, ftSize):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select unit_name, health, px, pz, vx, vz, timestamp from opforpositiondataarma where unit_name like '" + ft + "%' order by timestamp desc limit "+ str(ftSize) + ";")
    soldiers = cursor.fetchall()
    return soldiers
def getNumberofBlueForceUnits():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select count(distinct unit_name) from blueforpositiondataArma order by timestamp desc limit 1;")
    count = cursor.fetchone()
    return int(count[0])

def getNumberofOpForceUnits():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select count(distinct unit_name) from opforpositiondataArma  order by timestamp desc limit 1;")
    count = cursor.fetchone()
    return int(count[0])


def getFromAthena_Asset_Command():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select * from athena_asset_command;")
    athenaCommand = cursor.fetchall()
    #it its one row cursor.fetchone()
    return athenaCommand[0]

def getTimestampBlue():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select timestamp from blueforpositiondataArma  order by timestamp desc limit 1;")
    time = cursor.fetchone()
    return time[0]
def getTimestampOpfor():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select timestamp from opforpositiondataArma  order by timestamp asc limit 1;")
    time = cursor.fetchone()
    return time[0]

def getAllBlueForceUnits(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select unit_name, health, px, py, pz, timestamp from positiondata  where side = 'blufor' order by timestamp desc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getVBS4threats(unit_name):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select time, enemys_detected from threatsdetected where unit_name = '" + unit_name + "'  order by time desc limit 1;")
    soldiers = cursor.fetchone()
    return soldiers

def getVBS4UAVthreats(unit_name):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select time, enemys_detected from uavthreatsdetected where uav_name = '" + unit_name + "' order by time desc limit 1;")
    soldiers = cursor.fetchone()
    return soldiers

def getAllOpForceUnits(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select unit_name, health, px, py, pz, timestamp from positiondata  where side = 'opfor'  order by timestamp desc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getOpForceFireTeam(numberofUnits, ft):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select unit_name, health, px, py, pz, timestamp from positiondata  where  unit_name like '" + ft + "%' and side = 'opfor'  order by timestamp desc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers


def getOpForceUnitByTimestamp(unit_name, timestamp):
    date_time_obj = datetime.datetime.strptime(timestamp, '%H:%M:%S.%f')
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select px, py, pz from positiondata  where unit_name = '" + unit_name + "' and timestamp  > '" + str(date_time_obj.time()) + "' - interval '5 second';")
    soldiers = cursor.fetchone()
    return soldiers


def getOpForceUnitsByTimestamp(timestamp):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select unit_name, px, py, pz from positiondata  where timestamp  > " + timestamp + "' - interval '2 second';")
    soldiers = cursor.fetchall()
    return soldiers

def getAllBlueForceUnitsASC(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp from positiondata  where side = 'blufor'  order by timestamp asc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getAllOpForceUnitsASC(numberofUnits):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp from positiondata where side = 'opfor'  order by timestamp asc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getInitOpForceUnit(unit_name):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp from positiondata where unit_name = '" + unit_name + "' order by timestamp asc limit 1;")
    soldiers = cursor.fetchone()
    return soldiers

def distanceBetweenPoints(X1,Y1,X2,Y2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Y1- Y2, 2))
    return dis

def getUnitVelocity(unitName, simFlag):
    Y1 = 0
    Y2 = 0
    date_format = "%H:%M:%S.%f"
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp, side from positiondata where unit_name = '" + unitName + "' order by timestamp desc limit 2;")
    soldiers = cursor.fetchall()
    #print(soldiers[0][5])
    time1 = soldiers[0][5]
    time2 = soldiers[1][5]
    time_start = str(time2) 
    time_end = str(time1)  
    elapsedTimed = time_end - time_start  
    #diff = datetime.strptime(time_end, date_format) - datetime.strptime(time_start, date_format)
    #elapsedTimed = diff.total_seconds()
    X1 = soldiers[0][2]
    X2 = soldiers[1][2]
    if "Arma3" in simFlag:
        Y1 = soldiers[0][3]
        Y2 = soldiers[1][3]
    elif "VBS4" in simFlag:
        Y1 =  soldiers[0][4]
        Y2 = soldiers[1][4]   
        
    dis = distanceBetweenPoints(X1,Y1,X2,Y2)
    unitVelocity = dis/elapsedTimed
    
    return unitVelocity

def getCurrentUnit(unit_name):

    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select distinct unit_name, health, px, py, pz, timestamp, side  from positiondata where unit_name = '" + unit_name + "' order by timestamp desc limit 1;")
    soldiers = cursor.fetchone()
    return soldiers

def soldierMoveCommand(sol, X, Y, Z):
    global soldierid
    soldierpositionString = "'" + str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z))  + "'"
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + sol + "', 'move'," + soldierpositionString + ");"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def soldierSetPosCommand(sol, X, Y, Z):
    global soldierid
    soldierpositionString = "'" + str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z))  + "'"
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + sol + "', 'setPos'," + soldierpositionString + ");"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()
    
def Broadcast(side):
    global soldierid
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (command)  values ('broadcast " + side + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()    
    
def getObjects(directory):
    
    
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(".txt")]
    for file in filtered_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)
    
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (command)  values ('getObjects');"
    cursor.execute(soldier1Move)
    connection.commit()  
    
#two new functions to get initial pos

def initPosBlue(blueforUnit):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select px, py, pz from positiondata where unit_name = '" + blueforUnit + "' order by timestamp asc limit 1;")
    soldier = cursor.fetchone()
    return soldier
    
def initPosRed(opforUnit):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select px, py, pz from positiondata where unit_name = '" + opforUnit + "' order by timestamp asc limit 1;")
    soldier = cursor.fetchone()
    return soldier    

def resetHP(unitIndex, side):
    global soldierid
    params = side 
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into soldiercommandArma (soldierid, command, params)  values ('" + str(soldierid) + "', 'setDamage','" + params + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()


def resetAmmo(sol):
    global soldierid
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command)  values ('" + str(soldierid) + "','" + sol + "', 'setAmmo');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def respawnSol(sol):
    global soldierid
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into soldiercommandArma (soldierid, soldier_name, command)  values ('" + str(soldierid) + "','" + sol + "', 'respawn');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def numOfAlive(side):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select number_alive from UnitCount where side='" +side+ "';")
    count = cursor.fetchone()
    return count[0]

def numOfAlive_v2():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select count(distinct(unit_name)) from positiondata where timestamp > (select max(timestamp) from positiondata where side = 'opfor')  - interval '2 second' and side = 'opfor' and cast(health as real) > 0 ;")
    count = cursor.fetchone()
    return count[0]

def numOfAlive_v2Blue():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select count(distinct(unit_name)) from positiondata where timestamp > (select max(timestamp) from positiondata where side = 'blufor')  - interval '2 second' and side = 'blufor' and cast(health as real) > 0 ;")
    count = cursor.fetchone()
    #print(count[0])
    return count[0]

def createUnit(unit_type, X, Y, Z, side):
    global soldierid
    position =  str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z)) 
    params = unit_type +  "@" + side
    cursor = connection.cursor()
    soldier1Move = "insert into athena_asset_command (command, waypoint, opt_param)  values ('createUnit','" + params + "','" + position + "');"
    soldierid+=1
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute(soldier1Move)
    connection.commit()
 
def addWaypointViaSQF(unitName, X, Z): 
    #Note for VBS4 Y = Z amd Z = Y
    global soldierid
    commandid = unitName 
    position =  str(round(X)) + ","  + str(round(Z)) +  ", 3.9, 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, waypoint, behavior, control)  values ('" + commandid + "', 'addWaypoint','" + position + "', 1,1);"
    cursor.execute(soldier1Move)
    connection.commit()    
 
def moveUnitVBS(X, Z, unitName):
    #Note for VBS4 Y = Z amd Z = Y
    global soldierid
    commandid = unitName 
    position =  str(round(X)) + ","  + str(round(Z)) +  ", 3.9, 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, waypoint, behavior, control)  values ('" + commandid + "', 'move','" + position + "', 1,1);"
    cursor.execute(soldier1Move)
    connection.commit()    
    
def moveUnit(X, Y, unitName):
    #Note for VBS4 Y = Z amd Z = Y
    commandid = unitName 
    position =  str(round(X)) + ","  + str(round(Y)) +  "," + str(round(0))  + ", 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, waypoint, behavior, control)  values ('" + commandid + "', 'move','" + position + "', 1,1);"
    cursor.execute(soldier1Move)
    connection.commit()
    
def moveUnitToPos(position, unitName, uuid, delay):
    #Note for VBS4 Y = Z amd Z = Y
    commandid = unitName 
    #position =  str(round(X)) + ","  + str(round(Y)) +  "," + str(round(0))  + ", 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, waypoint, behavior, control, uuid, delay)  values ('" + commandid + "', 'move','" + position + "', 1,1 , '" + uuid + "', '" + delay + "');"
    cursor.execute(soldier1Move)
    connection.commit()
    
def scanArea(position, unitName, control, uuid, delay):
    #Note for VBS4 Y = Z amd Z = Y
    commandid = unitName 
    #position =  str(round(X)) + ","  + str(round(Y)) +  "," + str(round(0))  + ", 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, waypoint, behavior, control, uuid, delay)  values ('" + commandid + "', 'scan','" + position + "', 2,'" + str(control) + "' , '" + uuid + "', '" + delay + "');"
    cursor.execute(soldier1Move)
    connection.commit()
    
def controlOrder(unitName, control, uuid, delay):
    #Note for VBS4 Y = Z amd Z = Y
    commandid = unitName 
    #position =  str(round(X)) + ","  + str(round(Y)) +  "," + str(round(0))  + ", 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, behavior, control, uuid, delay)  values ('" + commandid + "', 'controlorder', 2,'" + str(control) + "', '" + uuid + "', '" + delay + "');"
    cursor.execute(soldier1Move)
    connection.commit()
    
def HoldFire(unitName, delay):    
    commandid = unitName 
    #position =  str(round(X)) + ","  + str(round(Z)) +  "," + str(round(Y))  + ", 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command)  values ('" + commandid + "', 'HoldFire', '" + delay + "');"
    cursor.execute(soldier1Move)
    connection.commit()
    
def OpenFire(unitName, delay):    
    commandid = unitName 
    #position =  str(round(X)) + ","  + str(round(Z)) +  "," + str(round(Y))  + ", 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command)  values ('" + commandid + "', 'OpenFire', '" + delay + "');"
    cursor.execute(soldier1Move)
    connection.commit()
    
def followUnit(unitName, unitToFollow):
    global soldierid
    commandid = unitName 
    #position =  str(round(X)) + ","  + str(round(Z)) +  "," + str(round(Y))  + ", 0"
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, opt_param)  values ('" + commandid + "', 'follow','" + unitToFollow + "');"
    cursor.execute(soldier1Move)
    connection.commit()


def moveUnitW(coordsList, unitName):
    global soldierid
    commandid = unitName 
    waypointCounter = 1
    position = ""
    if(len(coordsList)>1):
        for pos in coordsList:
            if waypointCounter == len(coordsList):
                position +=  str(pos[0]) + "," +  str(pos[2])  + ",0," + str(waypointCounter) 
            else:
                position +=  str(pos[0]) + "," +  str(pos[2])  + ",0," + str(waypointCounter) + "$"
            waypointCounter+=1
    else:
        position +=  pos[0] + "," +  pos[1]  + ", 0," + str(waypointCounter)
    #params = position + "@" + side + "@" + unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command (commandid, command, waypoint, behavior, control)  values ('" + commandid + "', 'move','" + position + "', 1,1);"
    cursor.execute(soldier1Move)
    connection.commit()
    
def moveAllUnits(side, positionArray, unitsAlive):
    global soldierid
    #position =  str(round(X)) + "," +  str(round(Y))  + "," + str(round(Z)) 
    print("printing positions sent", positionArray)
    params = str(positionArray) + "@" + side + "@" + str(unitsAlive) 
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into soldiercommandArma (soldierid, command, params)  values ('" + str(soldierid) + "', 'moveUnit','" + params + "');"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()

def resetDB():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from positiondata;")
    connection.commit()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from detections;")
    connection.commit()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from athena_asset_command;")
    connection.commit()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from squad_command;")
    connection.commit()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from driverstatus;")
    connection.commit()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from longterm_driverstatus;")
    connection.commit()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from longterm_detections;")
    connection.commit()
    
def resetDetection():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from detections;")
    connection.commit()

def getDriverStatus():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select  timestamp, status, uuid from driverstatus order by timestamp desc;")
    soldiers = cursor.fetchall()
    return soldiers

def removeStatusByTimestamp(timestamp):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from driverstatus where timestamp = '" + str(timestamp) + "';")
    connection.commit()


def insertDetectionData(timestamp, unit_name, enemyPos, enemyName):
    date_time_obj = datetime.datetime.strptime(timestamp, '%H:%M:%S.%f')
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into detections (timestamp, unit_name, target_name, target_x, target_y, target_z)  values ('" + str(date_time_obj.time()) + "', '" + unit_name + "', '" + enemyName + "', '" + str(enemyPos[0]) + "', '" + str(enemyPos[1]) + "', '" + str(enemyPos[2]) + "');"
    cursor.execute(soldier1Move)
    connection.commit()

def getRecentDetectionData(unitName):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select timestamp, target_name, target_x, target_y, target_z, bearing, classification from detections where unit_name = '" + unitName + "' order by timestamp desc limit 1;")
    soldier = cursor.fetchone()
    if not soldier:
        return -1
    return soldier 

def getAllDetectionData(unitName):
    u = unitName
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select * from detections order by timestamp desc;")
    soldier = cursor.fetchall()
    return soldier 

def getRecentDetection(unitName):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select target_x, target_y, target_z from detections where unit_name = '" + unitName + "' order by timestamp desc limit 1;")
    
    soldier = cursor.fetchone()
    if not soldier:
        return -1
    return soldier 

def getAllDetection(timeframe):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    currentTime = datetime.datetime.now().time()
    print("Current Time:",str(currentTime))
    cursor.execute("select target_x, target_y, target_z from detections where timestamp > Now() - interval '"+30 +"' second  order by timestamp desc;")
    soldier = cursor.fetchall()
    if not soldier:
        return -1
    return soldier 

def missionStat():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select count(*) FROM missionStatus;")
    count = cursor.fetchone()
    if(count[0] >0):
        message = "select currentStatus from missionStatus  order by timestamp asc limit 1;"
        cursor.execute(message)
        status = cursor.fetchone()
        return status[0]
    return ""


def sendToFileMisssionStatus():
    global runId
    myPath = r'C:\Program Files\Bohemia Interactive Simulations\VBS4 20.1.3 YYMEA_General\mycomponents\ONR_SEI_MissionControl\RunData\positiondata'
    tifCounter = len(glob.glob1(myPath,"*.csv")) +1
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    message = "COPY positiondata TO 'C:\Program Files\Bohemia Interactive Simulations\VBS4 20.1.3 YYMEA_General\mycomponents\ONR_SEI_MissionControl\RunData\positiondata\positiondata_db" + str(tifCounter) + ".csv ' DELIMITER ',' CSV HEADER;"
    #runId+=1
    cursor.execute(message) 
    connection.commit()
    
def sendToFileUAVThreats():
    global runId
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    #message = "COPY uavthreatsdetected TO 'C:\Program Files\Bohemia Interactive Simulations\VBS4 20.1.3 YYMEA_General\mycomponents\ONR_SEI_MissionControl\RunData\UAVThreatData\uavthreatdata_db" + str(runId) + ".csv ' DELIMITER ',' CSV HEADER;"
    message = r"COPY uavthreatsdetected TO 'C:\Program Files\Bohemia Interactive Simulations\VBS4 20.1.3 YYMEA_General\mycomponents\ONR_SEI_MissionControl\RunData\uavthreatdata\uavthreatdata_db" + str(runId) + ".csv ' DELIMITER ',' CSV HEADER;"
    runId+=1
    cursor.execute(message) 
    connection.commit()
    
    
    
def resetMisDB():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from missionStatus;")
    connection.commit()
    
    
def blocking(squadID, waypointLong, waypointLat, zoneRadius=None, targetAreaList=None, inferedDirectionEnemy=None):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    position =  str(round(waypointLong)) + ","  + str(round(waypointLat)) +  "," + str(0)  + ", 0"
    
    
    if zoneRadius != None and targetAreaList != None and inferedDirectionEnemy != None:
        soldier1Move = "insert into squad_command(squadID, command, waypoint, zoneRadius, targetAreaList, inferedDirectionEnemy)  values ('" + squadID + "', 'blocking', \
       '" + position + "','" + zoneRadius + "', '" + targetAreaList + "','" + inferedDirectionEnemy + "');"
    
    if zoneRadius != None and targetAreaList != None:
        soldier1Move = "insert into squad_command(squadID, command, waypoint, zoneRadius, targetAreaList)  values ('" + squadID + "', 'blocking', \
        " + position + "','" + zoneRadius + "', '" + targetAreaList + "');"    
        
    if zoneRadius != None:
        soldier1Move = "insert into squad_command(squadID, command, waypoint, zoneRadius)  values ('" + squadID + "', 'blocking', \
        " + position + "','" + zoneRadius + "');"
        
    cursor.execute(soldier1Move)
    connection.commit()
    

def attackByFire(squadID, waypointLong, waypointLat, unit_name, targetAreaList=None, inferedDirectionEnemy=None):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    position =  str(round(waypointLong)) + ","  + str(round(waypointLat)) +  "," + str(0)  + ", 0"
    
    
    if targetAreaList != None and inferedDirectionEnemy != None:
        soldier1Move = "insert into squad_command(squadID, command, waypoint, unit_name, targetAreaList, inferedDirectionEnemy)  values ('" + squadID + "', 'attack', \
       '" + position + "','" + unit_name + "', '" + targetAreaList + "','" + inferedDirectionEnemy + "');"
    
    elif targetAreaList != None:
        soldier1Move = "insert into squad_command(squadID, command, waypoint, unit_name, targetAreaList)  values ('" + squadID + "', 'attack', \
        " + position + "','" + unit_name + "', '" + targetAreaList + "');"    
        
    else:
        soldier1Move = "insert into squad_command(squadID, command, waypoint, unit_name)  values ('" + squadID + "', 'attack', \
        " + position + "','" + unit_name + "');"  
        
    cursor.execute(soldier1Move)
    connection.commit()


def stopCommand(unit_name, uuid, delay):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    soldier1Move = "insert into athena_asset_command(commandid, command, uuid, delay)  values ('" + unit_name + "', 'stop', '" + uuid + "', '" + delay + "');"
    cursor.execute(soldier1Move)
    connection.commit()
    
def removeSquadCommand(squadID, command, unit_name):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from squad_command where command = '"+ command + "' and squadID = '" + squadID + "' and unit_name = '"+ unit_name + "'  ;")
    connection.commit()
    
def removeAthenaAssetCommand(command, commandid):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("delete from athena_asset_command where command = '"+ command + "' and commandid = '" + commandid + "' ;")
    connection.commit()
    
    

    

def getSquadCommand():
    squadID = None
    command = None
    waypoint = None
    unit_name = None
    targetAreaList = None
    inferedDirectionEnemy = None
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select squadID, command, waypoint, unit_name, targetAreaList, inferedDirectionEnemy, delay from squad_command;")
    squadCommand = cursor.fetchone()
    if squadCommand != None:
        squadID = squadCommand[0]
        command = squadCommand[1]
        waypoint = squadCommand[2]
        unit_name = squadCommand[3]
        targetAreaList = squadCommand[4]
        inferedDirectionEnemy = squadCommand[5]
    
    if (targetAreaList != None or targetAreaList != '') and (inferedDirectionEnemy != None or inferedDirectionEnemy != ''):
        return squadCommand   
    
    if (targetAreaList != None or targetAreaList != '') :
        return squadID, command, waypoint, unit_name, targetAreaList, delay
    
    else:
        return squadID, command, waypoint, unit_name, delay
    
    return None


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
    
    