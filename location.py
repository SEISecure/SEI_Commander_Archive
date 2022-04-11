import asyncio
import logging
import websockets
import socket
import sys
import psycopg2
import time
import math
import csv
from asyncio.tasks import sleep


class ServerProtocol:
    
    def data_received(self, data):
        message = data.decode()
        print('Data received: {}'.format(message))

        print('Send: {}'.format(message))
        
        #print('Close the client socket')
        #self.transport.close()


async def main():
    infilCoverWeight = 1
    infilConcealmentWeight = 2
    insertionTrue = False
    notAtEndPoint = True
    terrainConcealment = [0.0,0.0,1.0,0.5,0]
    terrainCover = [0.0,0.0,1,0.5,0.5]
    landTerritory = []
    for i in range (0, 31):
        temp = []
        for j in range(0, 34):
            temp.append(0)
            landTerritory.append(temp)

   
    
    
    #read in map file
    with open('C:/Users/Mo/My Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/ONR Map.csv') as csvfile:
        mapreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        mapYindex = 0
        for row in mapreader:
           
            mapXindex = 0
            for value in row:
                landTerritory[mapYindex][mapXindex] = int(value)
                mapXindex +=1
            mapYindex += 1
    
    
    loop= asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: ServerProtocol(),
        '127.0.0.1', 10000)
    connection = psycopg2.connect(user = "postgres",
                                      password = "ichigo",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "units")
    previousX = 0
    previousZ = 0
    
    while notAtEndPoint:
        
        try:
            # weight will use for Belman Ford Shortest Path
            pathWeight = []
            for i in range (0, 31):
                temp = []
                for j in range(0, 34):
                    temp.append(10000.0)
                pathWeight.append(temp)
            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print ( connection.get_dsn_parameters(),"\n")
    
            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            #print("You are connected to - ", record,"\n")
            #avg left mid and right groups and set the 
            #take avg of x,y,z of the left group and then order the left grps waypoint to be at the avg 
            #right group will take the avg z of middle grp and and avg x position of where they are
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='RS';")
            rsposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='RS2';")
            rs2position = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='RS3';")
            rs3position = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='RS4';")
            rs4position = cursor.fetchone()
            avgxPos = 0
            avgzPos = 0
            counter = 0
            if(float(rsposition[3]) < 1):
                avgzPos+=float(rsposition[2])
                avgxPos+=float(rsposition[0])
                counter+=1
                
            if(float(rs2position[3]) < 1):
                avgzPos+=float(rs2position[2])
                avgxPos+=float(rs2position[0])
                counter+=1
                
            if(float(rs3position[3]) < 1):
                avgzPos+=float(rs3position[2])
                avgxPos+=float(rs3position[0])
                counter+=1
                
            if(float(rs4position[3]) < 1):
                avgzPos+=float(rs4position[2])
                avgxPos+=float(rs4position[0])
                counter+=1
            
            if(counter >0) :
                    avgzPos= avgzPos / counter    
                    avgxPos= avgxPos / counter
                    
            avgzPos = avgzPos/100
            avgxPos = avgxPos/100
            
            if((math.floor(avgxPos) ==181 and math.ceil(avgzPos) == 150) or insertionTrue == True) :
                endPointIsNotUpdated= True
                timeWithoutChange=0
                if insertionTrue == False:
                    #print("You have reached the insertion point")
                    insertionTrue = True
                #print ("X Value:",math.floor(avgxPos))
                #print ("Z Value:",math.floor(avgzPos))
                print ("$@%%%")
                print(avgxPos)
                print(math.floor(avgxPos))
                print(avgzPos)
                print(math.ceil(avgzPos))
                print ("$@%%%")
                xTerrain = math.floor(avgxPos)-172
                zTerrain = 164 - math.ceil(avgzPos)
               
                pathWeight[zTerrain][xTerrain]=0 #define path
                
                #initalizes weight and update arrays
                xWeightUpdate =[]
                zWeightUpdate = []
                updatedBy =[] 
                xWeightUpdate =[xTerrain]
                zWeightUpdate = [zTerrain]
                updatedBy =[0]
                
                endNodeIndex=0
                EndZ=19
                EndX=16
                print("#^$&")
                print(xTerrain)
                print(zTerrain)
                print("#^$&")
                print (EndX)
                print (EndZ)
                #update weight
                while (endPointIsNotUpdated or timeWithoutChange<10):
                    #print ("*******")
                    if endPointIsNotUpdated == False:
                        timeWithoutChange+=1
                    #print (endPointIsNotUpdated)
                    #print (len(xWeightUpdate))
                    #print (zWeightUpdate)
                    #print (timeWithoutChange)    
                    for i in range(0, len(xWeightUpdate)):
                        x = xWeightUpdate[i]
                        z = zWeightUpdate[i]
                        
                        for t in range (-1, 2):
                            for v in range (-1, 2):
                                if (x+t) >= 0 and (x+t)<34 and (z+v) >= 0 and (z+v)<31 and (abs(t)+abs(v)) != 0: #is the location within the map and not the current patch. You cannot update the distance of the currently selected patch
                                    
                                    distance = math.sqrt( (abs(t) + abs(v))*1.0)
                                    concealmentWeight = infilConcealmentWeight - infilConcealmentWeight*terrainConcealment[landTerritory[z+v][x+t]] 
                                    coverWeight = infilCoverWeight - infilCoverWeight*terrainCover[landTerritory[z+v][x+t]] 
                                    
                                    newWeight = pathWeight[z][x] + distance + concealmentWeight + coverWeight
                                    if newWeight < pathWeight[z+v][x+t] and ( (z+v) != zTerrain or (x+t) !=xTerrain): #did the weight improve and this is not the start node.
                                        pathWeight[z+v][x+t] = newWeight
                                        xWeightUpdate.append(x+t)
                                        zWeightUpdate.append(z+v)
                                        updatedBy.append(i)
                                        if (z+v) == EndZ and (x+t) ==EndX:
                                            endNodeIndex = len(zWeightUpdate)-1
                                            print("******")
                                            endPointIsNotUpdated=False
                                            timeWithoutChange =0
                  
                  
                previousNode = updatedBy[endNodeIndex]
                newX = 0
                newZ = 0
                #print("hi")
                #print(previousX,previousZ)
                #print(xTerrain,zTerrain)
                #print("$$$")
                while previousNode != 0:
                    newX = xWeightUpdate[previousNode] 
                    newZ = zWeightUpdate[previousNode]
                    previousNode = updatedBy[previousNode]
                print("@") 
                print(newX)     
                print(newZ)
                print("@")
                newX = newX+174
                newZ = 164-newZ   
                EndX = 188
                EndZ = 145
                if (abs(newX-EndX) ==1 and abs(newZ-EndZ)==1):
                    newX = EndX
                    newZ = EndZ
                    notAtEndPoint = False 
                newX= newX*100
                newZ= newZ*100
                
                #print (previousX, previousZ)
                if previousX != xTerrain or previousZ != zTerrain:
                    #print ("nolonger at previous location. Executing new waypoint")
                    previousX = xTerrain
                    previousZ = zTerrain
                    
                    #print ("previous location")
                    #print (str(xTerrain) ,"," , str(zTerrain))
                    #print ("new Waypoint destination Location")
                print (str(newX) +"."+ str(newZ))
                cursor.execute("delete from waypointcommands2;")
                connection.commit()
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (3, 'hold', %s, 39, %s, 'RS', 'RS2' , 'RS3', 'RS4', 'yellow', 'combat');",(newX, newZ))
                connection.commit()
                print("***********************")
                time.sleep(20)    
                
            #cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4) values (3, 'hold', 18471, 3.9, 14580, 'rightlead', 'rightgunner' , 'r3', 'r4');")
        
            #closing database connection.
            time.sleep(10)    
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)  
            time.sleep(5)
    if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            SystemExit
                 
    async with server:
        await server.serve_forever()

asyncio.run(main())