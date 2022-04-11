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
    cursor.execute("select unit_name, health, px, pz, vx, vz, timestamp from opforpositiondata where unit_name like '" + ft + "%' order by timestamp desc limit "+ str(ftSize) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getNumberofBlueForceUnits():
    cursor = connection.cursor()
    cursor.execute("select count(distinct unit_name) from blueforpositiondata;")
    count = cursor.fetchone()
    return int(count[0])

def getNumberofOpForceUnits():
    cursor = connection.cursor()
    cursor.execute("select count(distinct unit_name) from opforpositiondata;")
    count = cursor.fetchone()
    return int(count[0])

def getAllBlueForceUnits(numberofUnits):
    
    cursor = connection.cursor()
    cursor.execute("select unit_name, health, px, pz, vx, vz, timestamp from blueforpositiondata  order by timestamp desc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getAllOpForceUnits(numberofUnits):
    
    cursor = connection.cursor()
    cursor.execute("select unit_name, health, px, pz, vx, vz, timestamp from opforpositiondata  order by timestamp desc limit "+ str(numberofUnits) + ";")
    soldiers = cursor.fetchall()
    return soldiers

def getBlueforUnit(blueforUnit):
    
    cursor = connection.cursor()
    cursor.execute("select health, px, pz, vx, vz, timestamp from blueforpositiondata where unit_name = '" + blueforUnit + "' order by timestamp desc limit 1;")
    soldier = cursor.fetchone()
    return soldier

def getOpforUnit(opforUnit):
    
    cursor = connection.cursor()
    cursor.execute("select health, px, pz, vx, vz, timestamp from opforpositiondata where unit_name = '" + opforUnit + "' order by timestamp desc limit 1;")
    soldier = cursor.fetchone()
    return soldier

def getOpforHP(opforUnit):
    
    cursor = connection.cursor()
    cursor.execute("select health from opforpositiondata where unit_name = '" + opforUnit + "' order by timestamp desc limit 1;")
    soldier = cursor.fetchone()
    return float(soldier[0])

def getBlueforHP(blueforUnit):
    
    cursor = connection.cursor()
    cursor.execute("select health from blueforpositiondata where unit_name = '" + blueforUnit + "' order by timestamp desc limit 1;")
    soldier = cursor.fetchone()
    return float(soldier[0])

def opForVision(opForUnit):
    cursor = connection.cursor()
    cursor.execute("select seenblufor from enemyVisibility where opfor='"+ opForUnit + "';")
    soldier = cursor.fetchall()
    return soldier

def getOpforSoldierPos(opForUnit):
    cursor = connection.cursor()
    getPos = "select px,pz from opforpositiondata where unit_name='" + opForUnit + "' order by timestamp desc limit 1;"
    cursor.execute(getPos)
    soldierPos = cursor.fetchone()
    return soldierPos

def getBlueforSoldierPos(blueForUnit):
    cursor = connection.cursor()
    getPos = "select px,pz from blueforpositiondata where unit_name='" + blueForUnit + "' order by timestamp desc limit 1;"
    cursor.execute(getPos)
    soldierPos = cursor.fetchone()
    return soldierPos

def soldierMoveCommand(sol, soldierPositionString):
    global soldierid
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + sol + "', 'move'," + soldierPositionString + ");"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()
    
def soldierTeamMoveCommand(fteam, soldierPositionString):
    global soldierid
    cursor = connection.cursor()
    soldier1Move = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','" + fteam + "', 'team_move'," + soldierPositionString + ");"
    soldierid+=1
    cursor.execute(soldier1Move)
    connection.commit()
    
def soldierChangeROE(sol):
    global soldierid
    cursor = connection.cursor()
    soldier1Fire = "insert into soldiercommand (soldierid, soldier_name, command, params)  values ('" + str(soldierid) + "','"  + sol + "', 'change_roe', '0');"
    soldierid+=1
    cursor.execute(soldier1Fire)
    connection.commit()
    
def getMissionType():
    cursor = connection.cursor()
    cursor.execute("select mission_name from missionType;")
    missionType = cursor.fetchone()
    
    return missionType[0]
    
    
    