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
import uuid




'''
Action Selecter in vehicle Commander
1. What are we orderd to do?
2. if in blocking task and see an enemy, switch to attack by fire
no command sit  still
do keep calling the command, instead call and don't interupt the command
change view angle command to use lat/long
Plot an intercept course for the enemy
velcoity of the enemy
our velocity 
plot intercept course
1st. cut off enemy
2nd. get behind enemy
3rd. get beside enemy 

point Meredith's gun to train on the enemy 
'''


def distanceBetweenPoints(X1,Y1,X2,Y2):
    dis = math.sqrt(math.pow(X1-X2, 2) + math.pow(Y1- Y2, 2))
    return dis

class vehicleCommander(object):
    
    def __init__(self):
        #set connection to local db
        self.terrain = None
        #database_connect_Arma.Broadcast("red")
        self.vehicle = None 
        self.currentOrder = None
        self.visibleEnemy = None
        self.unitName = None
        self.sentPosXLong = None
        self.sentPosYLat = None
        self.simPlatform = None
        self.finalWaypoint = None
        self.side = None
        self.xLongMin = None
        self.xLongMax = None
        self.yLatMin = None
        self.yLatMax = None
        self.orderWaypoint = None
        self.waypointType = None
        self.uuid = None
        self.gunnerSentUUID = None
        self.driverSentUUID = None
        self.recentlyFired = False
        self.timeSinceLastFire = 21
        self.delay = None
        
    def updateVehicleStats(self):
        database_connect_Arma.setConnection("127.0.0.1")
        if  self.simPlatform != None and "Arma3" in self.simPlatform and self.side != None and "red" in self.side: 
            database_connect_Arma.Broadcast("red") 
        elif  self.simPlatform != None and "Arma3" in self.simPlatform and self.side != None and "blue" in self.side: 
            database_connect_Arma.Broadcast("blue")   
        self.vehicle = database_connect_Arma.getCurrentUnit(self.unitName)
            
        
    def blockingTask(self):       
        print("TODO")
    
    def attackByFire(self):
        print("TODO")
    
    def generateUUID(self):
        return uuid.uuid4().hex 

        
    def findVisibleEnemy(self):
        #get detection 
        database_connect_Arma.setConnection("127.0.0.1")
        detections = database_connect_Arma.getAllDetectionData(self.unitName)
        #print("###$$$$$####$$$$####$$$")
        #print(detections)
        self.timeSinceLastFire +=1
        if self.timeSinceLastFire >=3600:
            self.timeSinceLastFire = 21
        if detections != []:
            '''
            print("&&&&&&&&&&&&&&&&&&&&")
            print("are we here", self.timeSinceLastFire)
            print(len(detections))
            print(self.checkIfWithinZone())
            print("&&&&&&&&&&&&&&&&&&&&")
            '''
            if self.timeSinceLastFire >= 20 and self.checkIfWithinZone() == True:
                #send stop command            
                self.driverSentUUID  = self.generateUUID()
                '''
                print("^^^^^^^^^^^^^^^^^^^^^^")
                print("^^^^^^^^^^^^^^^^^^^^^^")
                print(self.driverSentUUID)
                print("^^^^^^^^^^^^^^^^^^^^^^")
                print("^^^^^^^^^^^^^^^^^^^^^^")
                '''
                database_connect_Arma.stopCommand(self.unitName, self.driverSentUUID)
                self.gunnerSentUUID = self.generateUUID()
                database_connect_Arma.controlOrder(self.unitName, 3, self.gunnerSentUUID)
                self.timeSinceLastFire = 0
                self.recentlyFired = True
                '''
                print("###############################")
                print("###############################")
                print("###############################")
                print("sent stop and firing")
                print("###############################")
                print("###############################")
                print("###############################")
                '''
                time.sleep(10)
                self.HoldFire()
            database_connect_Arma.resetDetection()
      
      
            
    def HoldFire(self):
        if "VBS4" in self.simPlatform:
            database_connect_Arma.setConnection("127.0.0.1")
            database_connect_Arma.HoldFire(self.unitName) 
            
        elif "IRL" in self.simPlatform:
            database_connect_Arma.setConnection("127.0.0.1")
            self.gunnerSentUUID = self.generateUUID()
            database_connect_Arma.controlOrder(self.unitName, 1, self.gunnerSentUUID)
      
    def setUnitName(self, name):
        self.unitName = name
    
    
    def checkIfWithinZone(self):
        self.updateVehicleStats()
        if self.vehicle != None:
            if self.currentOrder == 'attack' and "Arma3" in self.simPlatform and (self.vehicle[2] > self.xLongMin and self.vehicle[2] < self.xLongMax) \
            and (self.vehicle[3] > self.yLatMin and self.vehicle[3] < self.yLatMax): 
                
                return True
            elif self.currentOrder == 'attack' and "VBS4" in self.simPlatform and (self.vehicle[2] > self.xLongMin and self.vehicle[2] < self.xLongMax) \
            and (self.vehicle[4] > self.yLatMin and self.vehicle[4] < self.yLatMax): 
                database_connect_Arma.setConnection("127.0.0.1")
                database_connect_Arma.OpenFire(self.unitName)
                return True
            elif self.currentOrder == 'attack' and "IRL" in self.simPlatform and  (self.vehicle[3] > self.xLongMin and self.vehicle[3] < self.xLongMax) \
            and (self.vehicle[2] > self.yLatMin and self.vehicle[2] < self.yLatMax):
                #switch to weapons free
                return True
                
        return False
    
    def getEnemyVelocity(self, enemyName):
        database_connect_Arma.setConnection("127.0.0.1")
        velocity = database_connect_Arma.getUnitVelocity(enemyName, self.simPlatform)
        return velocity
        
    def processTargetAreaList(self, targetAreaList):
        targetAreas = targetAreaList.split('*')    
        targetList = []
        for area in targetAreas:
            pos = area.split(',')
            if "Arma3" in self.simPlatform:
                posString = pos[0] + ","  + pos[1] +  ", 0, 0"
                targetList.append(posString)
            elif "VBS4" in self.simPlatform:
                posString = pos[0] + ", 0"  + pos[1] +  ", 0"
                targetList.append(posString)
        return targetList
    
    
    def processWaypointZone(self, waypointZone):
        if "longlat" in self.waypointType:
            
            bounds = waypointZone.split('*', 4)
            bound1 = bounds[0]
            bound1Coords = bound1.split(',', 4)
            bound1XLong = float(bound1Coords[0])
            bound1YLat = float(bound1Coords[1])
            bound2 = bounds[1]
            bound2Coords = bound2.split(',', 4)
            bound2XLong = float(bound2Coords[0])
            bound2YLat = float(bound2Coords[1])
            bound3 = bounds[2]
            bound3Coords = bound3.split(',', 4)
            bound3XLong = float(bound3Coords[0])
            bound3YLat = float(bound3Coords[1])
            bound4 = bounds[3]
            bound4Coords = bound4.split(',', 4)
            bound4XLong = float(bound4Coords[0])
            bound4YLat = float(bound4Coords[1])
            
            xLongBounds = [bound1XLong, bound2XLong,bound3XLong,bound4XLong]
            yLatBounds = [bound1YLat, bound2YLat,bound3YLat,bound4YLat]
            
            self.xLongMin = min(xLongBounds)
            self.xLongMax = max(xLongBounds)
            self.yLatMin = min(yLatBounds)
            self.yLatMax = max(yLatBounds)
        else:
            bounds = waypointZone.split('*', 4)
            bound1 = bounds[0]
            bound1Coords = bound1.split(',', 4)
            bound1XLong = float(bound1Coords[0])
            bound1YLat = float(bound1Coords[1])
            bound2 = bounds[1]
            bound2Coords = bound2.split(',', 4)
            bound2XLong = float(bound2Coords[0])
            bound2YLat = float(bound2Coords[1])
            bound3 = bounds[2]
            bound3Coords = bound3.split(',', 4)
            bound3XLong = float(bound3Coords[0])
            bound3YLat = float(bound3Coords[1])
            bound4 = bounds[3]
            bound4Coords = bound4.split(',', 4)
            bound4XLong = float(bound4Coords[0])
            bound4YLat = float(bound4Coords[1])
            
            xLongBounds = [bound1XLong, bound2XLong,bound3XLong,bound4XLong]
            yLatBounds = [bound1YLat, bound2YLat,bound3YLat,bound4YLat]
            
            self.xLongMin = min(xLongBounds)
            self.xLongMax = max(xLongBounds)
            self.yLatMin = min(yLatBounds)
            self.yLatMax = max(yLatBounds)
            print("Bounds", self.xLongMin, self.xLongMax, self.yLatMin, self.yLatMax)
            
    def getZoneCenterWaypoint(self):
        xCenter = ( self.xLongMin + self.xLongMax) / 2
        yCenter = (self.yLatMin + self.yLatMax) / 2
        print(xCenter, yCenter)
        if "VBS4" in self.simPlatform:
            self.finalWaypoint = str(xCenter) + ", 0 ,"  + str(yCenter) +  ", 0"
        elif "Arma3" in self.simPlatform:
            self.finalWaypoint = str(xCenter) + ","  + str(yCenter) +  ", 0, 0"
        elif "IRL" in self.simPlatform:
            self.finalWaypoint = str(xCenter) + ","  + str(yCenter) +  ", 0, 0"

    
    def setWaypoint(self, waypoint):
        pos = waypoint.split(',', 4) 
        #self.sentPosX = float(pos[0]) + 10
        #self.sentPosY = float(pos[1]) + 10
        self.sentPosXLong = float(pos[0]) 
        if "VBS4" in self.simPlatform:
            self.sentPosYLat = float(pos[2])
        elif "Arma3" in self.simPlatform:
            self.sentPosYLat = float(pos[1])
        elif "IRL" in self.simPlatform:
            self.sentPosYLat = float(pos[1])    
        '''
        if "VBS4" in self.simPlatform:
            self.finalWaypoint = str(self.sentPosXLong) + "," + str(0) + "," + str(self.sentPosYLat) + "," + str(0)
        elif "Arma3" in self.simPlatform:
            self.finalWaypoint = str(self.sentPosXLong) + "," + str(self.sentPosYLat) + "," + str(0) + "," + str(0)
        '''

    def isNearWaypoint(self):
        self.updateVehicleStats()
        dis = None
        if self.vehicle != None:
            if(self.sentPosXLong !=None and self.sentPosYLat != None):
                if "Arma3" in self.simPlatform: 
                    dis = distanceBetweenPoints(float(self.vehicle[2]), float(self.vehicle[3]),self.sentPosXLong,self.sentPosYLat)
                    if dis <= 5:
                        return True
                    else: 
                        return False
                elif "VBS4" in self.simPlatform: 
                    print("Sent Locations", float(self.vehicle[2]), float(self.vehicle[4]),self.sentPosXLong,self.sentPosYLat)
                    dis = distanceBetweenPoints(float(self.vehicle[2]), float(self.vehicle[4]),self.sentPosXLong,self.sentPosYLat)
                    print("Distance",dis)
                    if dis <= 5:
                        return True
                    else: 
                        return False
                elif "IRL" in self.simPlatform: 
                    dis = distanceBetweenPoints(float(self.vehicle[3]),float(self.vehicle[2]),self.sentPosXLong,self.sentPosYLat)
                    stati = database_connect_Arma.getDriverStatus()
                    for status in stati:
                        #print("**********************")
                        #print("**********************")
                        #print(status[1]) 
                        #print("**********************")
                        #print("**********************")                       
                        if int(status[1]) == 1 and status[2] == self.driverSentUUID :
                            time.sleep(1)
                            return True
                        
                        #elif dis < 0.00009 and int(status[1]) == 4:
                        #    time.sleep(1)
                        #    return True
                        database_connect_Arma.removeStatusByTimestamp(status[0])
                    else:
                        return False
        return False

    def moveToRandoLocInZone(self):
        nearWaypoint = self.isNearWaypoint()
        #print("within area flag",withinZoneFlag)
        #print("**********************")
        #print(self.recentlyFired)
        #print("**********************")
        if nearWaypoint == True or self.recentlyFired == True:
            randoX = random.uniform(self.xLongMin, self.xLongMax)
            randoY = random.uniform(self.yLatMin, self.yLatMax)
            self.recentlyFired = False
            if "VBS4" in self.simPlatform:
                self.finalWaypoint = str(randoX) + "," + str(0) + "," + str(randoY) + "," + str(0)
            elif "Arma3" in self.simPlatform:
                self.finalWaypoint = str(randoX) + "," + str(randoY) + "," + str(0) + "," + str(0)
            elif "IRL" in self.simPlatform:
                self.finalWaypoint = str(randoX) + "," + str(randoY) + "," + str(0) + "," + str(0)
            print("Moving to new Zone")
            self.driverSentUUID  = self.generateUUID()
            database_connect_Arma.moveUnitToPos(self.finalWaypoint, self.unitName, self.driverSentUUID)
            
            
    def movingTask(self):
        if self.finalWaypoint != self.orderWaypoint:
            self.orderWaypoint = self.finalWaypoint
            self.driverSentUUID  = self.generateUUID()
            database_connect_Arma.moveUnitToPos(self.finalWaypoint, self.unitName, self.driverSentUUID, self.delay)
                
    def processSquadCommand(self):
        database_connect_Arma.setConnection("127.0.0.1")
        squadCommand = database_connect_Arma.getSquadCommand()
        self.updateVehicleStats()
        if self.currentOrder == 'blocking' and self.visibleEnemy != None:
            print("Enemy Detected Switching to Attack")
            self.currentOrder = 'attack'
        if squadCommand != None:
            waypointZone = squadCommand[2]
            if len(waypointZone) > 0:
                self.processWaypointZone(waypointZone)
                self.getZoneCenterWaypoint()
                print("center point")
                print(self.finalWaypoint)
                self.setWaypoint(self.finalWaypoint)
            print(self.vehicle)
            
            self.HoldFire()
            #Artemis-126
            #Artemis-135
            #Artemis-141
            if squadCommand[1] == 'attack':
                delay = squadCommand[6]
                self.delay = delay
                print("attacking ", self.unitName)
                self.currentOrder = squadCommand[1]
                self.movingTask()
                database_connect_Arma.removeSquadCommand(squadCommand[0], squadCommand[1], squadCommand[3])
                self.gunnerSentUUID = self.generateUUID()
                print("trying to attack")
                print(squadCommand[4])
                database_connect_Arma.scanArea(squadCommand[4], "Artemis-141", 1, self.gunnerSentUUID, delay)
            elif squadCommand[1] == 'blocking':
                print("blocking ugv1")
                self.currentOrder = squadCommand[1]
            elif squadCommand[1] == 'stop':
                self.HoldFire()
                self.driverSentUUID  = self.generateUUID()
                database_connect_Arma.stopCommand(self.unitName, self.driverSentUUID, self.delay)
            print("Done")
