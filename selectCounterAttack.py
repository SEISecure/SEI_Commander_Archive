import asyncio
import logging
import socket
import sys
import psycopg2
import time
import math
from distutils import command
import torch
import csv
import numpy
from torch import nn
import nest_asyncio

nest_asyncio.apply()


connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")

class ServerProtocol:
    
    def data_received(self, data):
        message = data.decode()
        print('Data received: {}'.format(message))

        print('Send: {}'.format(message))
        
        #print('Close the client socket')
        #self.transport.close()


async def optimalBehavior():
    loop= asyncio.get_running_loop()

    unitArray = ["rightlead","rightgunner","r3","r4", "mlead","mgunner","m3","m4", "leftlead","leftgunner","l3","l4"]
    server = await loop.create_server(
        lambda: ServerProtocol(),
        '127.0.0.1', 10000)
    """
    connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")
    """
    try:
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
        while(True):
            killed = 0.0
            wounded = 0.0
            for unit in unitArray:
                cursor.execute("select unit_health from blufor where unit_name=%s;", [unit]) 
                hp=cursor.fetchall()
                hp=hp[0]
                hp=float(hp[0])                
                if(hp==1.0):
                    killed +=1
                if(hp>0.0 and hp <1.0):
                    wounded +=1
            killedamnt = killed/12
            woundedamnt = wounded/12
            command = 0
            distance = await minDistance()
            
            print(distance)
            print("hi")
            command = deepLearningMode(distance, killedamnt, woundedamnt)
            print("his")
            if(command==1):
                print("assault")
                time.sleep(2)
                await assault()
            if(command==2):
                print("fallback")
                time.sleep(2)
                await fallingback(16400)
            if(command==3):
                print("flank")
                time.sleep(2)
                await flank()
                
            time.sleep(20)    
        """               
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            SystemExit
        """
             
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)  
    

    async with server:
        await server.serve_forever()
async def minDistance():
    mindis = 10000
    unitArray = ["rightlead","rightgunner","r3","r4", "mlead","mgunner","m3","m4", "leftlead","leftgunner","l3","l4"]
    
    for unit in unitArray:
        tempdis = await findClosestEnemyDis(unit)
        if(mindis > tempdis):
            mindis = tempdis
    return mindis        
async def findClosestEnemyDis(currentUnit):
    print("visibleenemies")   
    cursor = connection.cursor()
    cursor.execute("select px,pz,visibleenemies from positiondata where unit_name=%s order by timestamp desc limit 1;", [currentUnit])
    connection.commit()
    thisUnit=cursor.fetchall()
    thisUnit=thisUnit[0]
    #print(thisUnit)
    px = float(thisUnit[0])
    #print(px)
    pz = float(thisUnit[1])
    #print(pz) 
    visibleEnemies = (str(thisUnit[2])[:-1]).split(',')
    #print(visibleEnemies)
    closestEnemyX=px
    closestEnemyZ=pz
    distance = 1000000000
    #print(px,pz,visibleEnemies)
    for enemy in visibleEnemies:
        #print("positiondata")
        #print(enemy)
        cursor.execute("select px,pz from positiondata where unit_name=%s order by timestamp desc limit 1;", [enemy])
        connection.commit()
        enemyVis = cursor.fetchall()
        #print(enemyVis)
        enemyVis = enemyVis[0]
        #print(enemyVis)
        dis = math.sqrt( math.pow(px-float(enemyVis[0]), 2) + math.pow(pz-float(enemyVis[1]), 2))
        #print (dis)
        if(dis<distance) :
            closestEnemyX = float(enemyVis[0])
            closestEnemyZ = float(enemyVis[1])
            distance = dis

    return distance

async def getHealth(currentUnit):   
    cursor = connection.cursor()
    cursor.execute("select unit_health from positiondata where unit_name=%s order by timestamp desc limit 1;", [currentUnit])
    connection.commit()
    thisUnit=cursor.fetchall()
    thisUnit=thisUnit[0]
    hp = float(thisUnit[0])
    #print("printing hp",hp)
    return hp
# this function takes in the distance to cloesest enemy, percentage of blue force dead, percentage of blue force wounded

def deepLearningMode(distanceClosestEnemy, percentageBlueForceDead, percentageBlueForceWounded): #all values should be floats
    
    dtype = torch.float
    device = torch.device("cpu")

    D_in, H_one, H_two, H_three, D_out = 5, 5, 5, 5, 1
    model = torch.nn.Sequential(
    torch.nn.Linear(D_in, H_one),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_one, H_two),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_two, H_three),
    torch.nn.Sigmoid(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_three, D_out),
    )
    #calls the trained model and sets it for evaluation mode
    model.load_state_dict(torch.load('C:/Users/Mo/My Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/Model.pth'))
    model.eval()
    commandOrder = 1
    assaultMatrix =numpy.array([[1,0,distanceClosestEnemy, percentageBlueForceDead,percentageBlueForceWounded]])
    fallbackMatrix =numpy.array([[0,1,distanceClosestEnemy, percentageBlueForceDead,percentageBlueForceWounded]])
    flankMatrix = numpy.array([[0,0,distanceClosestEnemy, percentageBlueForceDead,percentageBlueForceWounded]])

    assaultNode = torch.tensor(assaultMatrix,device=device, dtype=dtype)
    fallbackNode = torch.tensor(fallbackMatrix,device=device, dtype=dtype)
    flankNode = torch.tensor(flankMatrix,device=device, dtype=dtype)

    assaultOutput = model(assaultNode)
    assaultOutput = float(str(assaultOutput[0].item()))
    #print(assaultOutput)


    fallbackOutput = model(fallbackNode)
    fallbackOutput = float(str(fallbackOutput[0].item()))
    #print(fallbackOutput)


    flankOutput = model(flankNode)
    flankOutput = float(str(flankOutput[0].item()))
    #print(flankOutput)

    if fallbackOutput > assaultOutput and fallbackOutput > flankOutput:
        commandOrder = 2
    elif  flankOutput > assaultOutput and flankOutput > fallbackOutput:
        commandOrder = 3   
    print (commandOrder)    
    return 2 #1 = assault, 2 = fallback, 3 = flank order troups to perform action
    
async def fallingback(fallbackPos):
 
    """
    connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")
    """
    try:
        cursor = connection.cursor()
        #print("Falling back")
        moveid=0

                    
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftlead';")
        leftleadposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftgunner';")
        leftgunnerposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l3';")
        l3position = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l4';")
        l4position = cursor.fetchone()
        avgLzPos = 0
        counterL = 0
        if(float(leftleadposition[3]) < 1):
            avgLzPos+=float(leftleadposition[2])
            counterL+=1
            
        if(float(leftgunnerposition[3]) < 1):
            avgLzPos+=float(leftgunnerposition[2])
            counterL+=1
            
        if(float(l3position[3]) < 1):
            avgLzPos+=float(l3position[2])
            counterL+=1
                
        if(float(l4position[3]) < 1):
            avgLzPos+=float(l4position[2])
            counterL+=1
            
        if(counterL >0) :
            avgLzPos= avgLzPos / counterL
            
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mlead';")
        mleadposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mgunner';")
        mgunnerposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m3';")
        m3position = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m4';")
        m4position = cursor.fetchone()
        avgMzPos = 0
        counterM = 0
        if(float(mleadposition[3]) < 1):
            avgMzPos+=float(mleadposition[2])
            counterM+=1
            
        if(float(mgunnerposition[3]) < 1):
            avgMzPos+=float(mgunnerposition[2])
            counterM+=1
            
        if(float(m3position[3]) < 1):
            avgMzPos+=float(m3position[2])
            counterM+=1
                
        if(float(m4position[3]) < 1):
            avgMzPos+=float(m4position[2])
            counterM+=1
            
        if(counterM >0) :
            avgMzPos= avgMzPos / counterM    
            
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightlead';")
        rightleadposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightgunner';")
        rightgunnerposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r3';")
        r3position = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r4';")
        r4position = cursor.fetchone()
        avgRzPos = 0
        counterR = 0
        if(float(rightleadposition[3]) < 1):
            avgRzPos+=float(rightleadposition[2])
            counterR+=1
            
        if(float(rightgunnerposition[3]) < 1):
            avgRzPos+=float(rightgunnerposition[2])
            counterR+=1
            
        if(float(r3position[3]) < 1):
            avgRzPos+=float(r3position[2])
            counterR+=1
                
        if(float(r4position[3]) < 1):
            avgRzPos+=float(r4position[2])
            counterR+=1
            
        if(counterR >0) :
            avgRzPos= avgRzPos / counterR
        #check if all groups are at the fallback position
        #if they are move all groups up 1m and set them to atk  
        #else figure out furthest....
        print("fallback")
        
        
        if(abs(fallbackPos-avgLzPos)< 20 and abs(fallbackPos-avgMzPos) < 20 and abs(fallbackPos-avgRzPos) < 20):
            if(await getHealth('leftlead') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftlead', 0);",(moveid, float(leftleadposition[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('leftgunner') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftgunner', 0);",(moveid, float(leftgunnerposition[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('l3') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l3', 0);",(moveid, float(l3position[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('l4') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l4', 0);",(moveid, float(l4position[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('mlead') < 1) : 
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mlead', 0);",(moveid, float(mleadposition[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('mgunner') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mgunner', 0);",(moveid, float(mgunnerposition[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('m3') < 1) : 
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm3', 0);",(moveid, float(m3position[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('m4') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm4', 0);",(moveid, float(m4position[0]), fallbackPos-1))
                moveid+=1 
            if(await getHealth('rightlead') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightlead', 0);",(moveid, float(rightleadposition[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('rightgunner') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightgunner', 0);",(moveid, float(rightgunnerposition[0]), fallbackPos-1))
                moveid+=1 
            if(await getHealth('r3') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r3', 0);",(moveid, float(r3position[0]), fallbackPos-1))
                moveid+=1
            if(await getHealth('r4') < 1) :
                cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r4', 0);",(moveid, float(r4position[0]), fallbackPos-1))
                moveid+=1 


            connection.commit()               
        else:
            if(abs(fallbackPos-avgLzPos)> abs(fallbackPos-avgMzPos) and abs(fallbackPos-avgLzPos)> abs(fallbackPos-avgRzPos) and counterL >0):
                print("left is furthest")
                moveid+=1
                if(await getHealth('leftlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftlead', 0);",(moveid, float(leftleadposition[0]), avgLzPos+10))
                    moveid+=1                        
                if(await getHealth('leftgunner') < 1) :    
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftgunner', 0);",(moveid, float(leftgunnerposition[0]), avgLzPos+10))
                    moveid+=1
                if(await getHealth('l3') < 1) :    
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l3', 0);",(moveid, float(l3position[0]), avgLzPos+10))
                    moveid+=1
                if(await getHealth('l4') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l4', 0);",(moveid, float(l4position[0]), avgLzPos+10))
                    moveid+=1             
                
                closestEnemyX, closestEnemyZ = await faceEnemy('rightlead')
                if(await getHealth('rightlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('rightgunner')
                if(await getHealth('rightgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1 
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('r3')
                if(await getHealth('r3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r3', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('r4')
                if(await getHealth('r4') < 1) :          
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r4', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
              
                closestEnemyX, closestEnemyZ = await faceEnemy('mlead')
                if(await getHealth('mlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('mgunner')
                if(await getHealth('mgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('m3')            
                if(await getHealth('m3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm3', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('m4')
                if(await getHealth('m4') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm4', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1 
                connection.commit()                 
            elif(abs(fallbackPos-avgRzPos)> abs(fallbackPos-avgMzPos) and abs(fallbackPos-avgRzPos)> abs(fallbackPos-avgLzPos) and counterR >0):
                print("right is furthest")
                moveid+=1
                if(await getHealth('rightlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightlead', 0);",(moveid, float(rightleadposition[0]), avgRzPos+10))
                    moveid+=1
                if(await getHealth('rightgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightgunner', 0);",(moveid, float(rightgunnerposition[0]), avgRzPos+10))
                    moveid+=1 
                if(await getHealth('r3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r3', 0);",(moveid, float(r3position[0]), avgRzPos+10))
                    moveid+=1
                if(await getHealth('r4') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r4', 0);",(moveid, float(r4position[0]), avgRzPos+10))
                    moveid+=1
                
        
                closestEnemyX, closestEnemyZ  =  await faceEnemy('leftlead')
                if(await getHealth('leftlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
            
                closestEnemyX, closestEnemyZ  =  await faceEnemy('leftgunner')
                if(await getHealth('leftgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
            
                closestEnemyX, closestEnemyZ  =  await faceEnemy('l3')
                if(await getHealth('l3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l3', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
            
                closestEnemyX, closestEnemyZ  =  await faceEnemy('l4')
                if(await getHealth('l4') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l4', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('mlead')
                if(await getHealth('mlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('mgunner')
                if(await getHealth('mgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('m3')            
                if(await getHealth('m3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm3', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('m4')
                if(await getHealth('m4') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm4', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1 
                connection.commit()
            elif((abs(fallbackPos-avgMzPos)> abs(fallbackPos-avgLzPos) and abs(fallbackPos-avgMzPos)> abs(fallbackPos-avgRzPos) and counterM >0) 
                 or (counterR == 0 and abs(fallbackPos-avgMzPos)> abs(fallbackPos-avgLzPos))):
                print("mid is furthest")
                moveid+=1
                if(await getHealth('mlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mlead', 0);",(moveid, float(mleadposition[0]), avgMzPos+10))
                    moveid+=1
                if(await getHealth('mgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mgunner', 0);",(moveid, float(mgunnerposition[0]), avgMzPos+10))
                    moveid+=1 
                if(await getHealth('m3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm3', 0);",(moveid, float(m3position[0]), avgMzPos+10))
                    moveid+=1
                if(await getHealth('m4') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm4', 0);",(moveid, float(m4position[0]), avgMzPos+10))
                    moveid+=1 
                
                closestEnemyX, closestEnemyZ  =  await faceEnemy('leftlead')
                if(await getHealth('leftlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
            
                closestEnemyX, closestEnemyZ  =  await faceEnemy('leftgunner')
                if(await getHealth('leftgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
            
                closestEnemyX, closestEnemyZ  =  await faceEnemy('l3')
                if(await getHealth('l3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l3', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
            
                closestEnemyX, closestEnemyZ  =  await faceEnemy('l4')
                if(await getHealth('l4') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l4', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                
                closestEnemyX, closestEnemyZ = await faceEnemy('rightlead')
                if(await getHealth('rightlead') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('rightgunner')
                if(await getHealth('rightgunner') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1 
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('r3')
                if(await getHealth('r3') < 1) :
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r3', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                    
                closestEnemyX, closestEnemyZ = await faceEnemy('r4')
                if(await getHealth('r4') < 1) :          
                    cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r4', 0);",(moveid, closestEnemyX, closestEnemyZ))
                    moveid+=1
                connection.commit()
            #move the furthest group 30m closer to the fallback position 
            #all other groups that are not the furthest group move them 1 meters up and set them to atk
          
         #run every 5 sec 
        
        
    
             
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)  
    

async def assault():
    loop= asyncio.get_running_loop()

    """
    connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")
    """
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    #print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    #print("You are connected to - ", record,"\n")
    moveid=0
    
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftlead';")
    leftleadposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftgunner';")
    leftgunnerposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l3';")
    l3position = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l4';")
    l4position = cursor.fetchone()
    avgLzPos = 0
    counterL = 0
    if(float(leftleadposition[3]) < 1):
        avgLzPos+=float(leftleadposition[2])
        counterL+=1
        
    if(float(leftgunnerposition[3]) < 1):
        avgLzPos+=float(leftgunnerposition[2])
        counterL+=1
        
    if(float(l3position[3]) < 1):
        avgLzPos+=float(l3position[2])
        counterL+=1
            
    if(float(l4position[3]) < 1):
        avgLzPos+=float(l4position[2])
        counterL+=1
        
    if(counterL >0) :
        avgLzPos= avgLzPos / counterL
        
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mlead';")
    mleadposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mgunner';")
    mgunnerposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m3';")
    m3position = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m4';")
    m4position = cursor.fetchone()
    avgMzPos = 0
    counterM = 0
    if(float(mleadposition[3]) < 1):
        avgMzPos+=float(mleadposition[2])
        counterM+=1
        
    if(float(mgunnerposition[3]) < 1):
        avgMzPos+=float(mgunnerposition[2])
        counterM+=1
        
    if(float(m3position[3]) < 1):
        avgMzPos+=float(m3position[2])
        counterM+=1
            
    if(float(m4position[3]) < 1):
        avgMzPos+=float(m4position[2])
        counterM+=1
        
    if(counterM >0) :
        avgMzPos= avgMzPos / counterM    
        
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightlead';")
    rightleadposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightgunner';")
    rightgunnerposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r3';")
    r3position = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r4';")
    r4position = cursor.fetchone()
    avgRzPos = 0
    counterR = 0
    if(float(rightleadposition[3]) < 1):
        avgRzPos+=float(rightleadposition[2])
        counterR+=1
        
    if(float(rightgunnerposition[3]) < 1):
        avgRzPos+=float(rightgunnerposition[2])
        counterR+=1
        
    if(float(r3position[3]) < 1):
        avgRzPos+=float(r3position[2])
        counterR+=1
            
    if(float(r4position[3]) < 1):
        avgRzPos+=float(r4position[2])
        counterR+=1
        
    if(counterR >0) :
        avgRzPos= avgRzPos / counterR
    #check if all groups are at the fallback position
    #if they are move all groups up 1m and set them to atk  
    #else figure out furthest....
    print("inside assault")
    
    
    
    moveid+=1
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('leftlead')
    if(await getHealth('leftlead') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('leftgunner')
    if(await getHealth('leftgunner') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('l3')
    if(await getHealth('l3') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l3', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('l4')
    if(await getHealth('l4') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l4', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1             
    
    closestEnemyX, closestEnemyZ = await findClosestEnemy('rightlead')
    if(await getHealth('rightlead') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('rightgunner')
    if(await getHealth('rightgunner') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1 
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('r3')
    if(await getHealth('r3') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r3', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('r4')
    if(await getHealth('r4') < 1) :          
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r4', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('mlead')
    if(await getHealth('mlead') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mlead', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('mgunner')
    if(await getHealth('mgunner') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'mgunner', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('m3')            
    if(await getHealth('m3') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm3', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('m4')
    if(await getHealth('m4') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'm4', 0);",(moveid, closestEnemyX, closestEnemyZ))
        moveid+=1 
    connection.commit()                 

        #move the furthest group 30m closer to the fallback position 
        #all other groups that are not the furthest group move them 1 meters up and set them to atk
      
     #run every 5 sec 
        
        
async def flank():

    """
    connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")
    """

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    #print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version

    #print("You are connected to - ", record,"\n")
    moveid=0
    
    #if( await isPositionDataEmpty() ==True):
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftlead';")
    leftleadposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftgunner';")
    leftgunnerposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l3';")
    l3position = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l4';")
    l4position = cursor.fetchone()
    avgLzPos = 0
    counterL = 0
    if(float(leftleadposition[3]) < 1):
        avgLzPos+=float(leftleadposition[2])
        counterL+=1
        
    if(float(leftgunnerposition[3]) < 1):
        avgLzPos+=float(leftgunnerposition[2])
        counterL+=1
        
    if(float(l3position[3]) < 1):
        avgLzPos+=float(l3position[2])
        counterL+=1
            
    if(float(l4position[3]) < 1):
        avgLzPos+=float(l4position[2])
        counterL+=1
        
    if(counterL >0) :
        avgLzPos= avgLzPos / counterL
        
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mlead';")
    mleadposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mgunner';")
    mgunnerposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m3';")
    m3position = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m4';")
    m4position = cursor.fetchone()
    avgMzPos = 0
    counterM = 0
    if(float(mleadposition[3]) < 1):
        avgMzPos+=float(mleadposition[2])
        counterM+=1
        
    if(float(mgunnerposition[3]) < 1):
        avgMzPos+=float(mgunnerposition[2])
        counterM+=1
        
    if(float(m3position[3]) < 1):
        avgMzPos+=float(m3position[2])
        counterM+=1
            
    if(float(m4position[3]) < 1):
        avgMzPos+=float(m4position[2])
        counterM+=1
        
    if(counterM >0) :
        avgMzPos= avgMzPos / counterM    
        
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightlead';")
    rightleadposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightgunner';")
    rightgunnerposition = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r3';")
    r3position = cursor.fetchone()
    cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r4';")
    r4position = cursor.fetchone()
    avgRzPos = 0
    counterR = 0
    if(float(rightleadposition[3]) < 1):
        avgRzPos+=float(rightleadposition[2])
        counterR+=1
        
    if(float(rightgunnerposition[3]) < 1):
        avgRzPos+=float(rightgunnerposition[2])
        counterR+=1
        
    if(float(r3position[3]) < 1):
        avgRzPos+=float(r3position[2])
        counterR+=1
            
    if(float(r4position[3]) < 1):
        avgRzPos+=float(r4position[2])
        counterR+=1
        
    if(counterR >0) :
        avgRzPos= avgRzPos / counterR
    #check if all groups are at the fallback position
    #if they are move all groups up 1m and set them to atk  
    #else figure out furthest....
    print("flanks")
    
    
    
    moveid+=1
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('leftlead')
    if(await getHealth('leftlead') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftlead', 0);",(moveid, closestEnemyX-100, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('leftgunner')
    if(await getHealth('leftgunner') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'leftgunner', 0);",(moveid, closestEnemyX-100, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('l3')
    if(await getHealth('l3') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l3', 0);",(moveid, closestEnemyX-100, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ  =  await findClosestEnemy('l4')
    if(await getHealth('l4') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'l4', 0);",(moveid, closestEnemyX-100, closestEnemyZ))
        moveid+=1             
    
    closestEnemyX, closestEnemyZ = await findClosestEnemy('rightlead')
    if(await getHealth('rightlead') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightlead', 0);",(moveid, closestEnemyX+100, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('rightgunner')
    if(await getHealth('rightgunner') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'rightgunner', 0);",(moveid, closestEnemyX+100, closestEnemyZ))
        moveid+=1 
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('r3')
    if(await getHealth('r3') < 1) :
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r3', 0);",(moveid, closestEnemyX+100, closestEnemyZ))
        moveid+=1
        
    closestEnemyX, closestEnemyZ = await findClosestEnemy('r4')
    if(await getHealth('r4') < 1) :          
        cursor.execute("insert into movecommand (moveid, solo, x, y, z, unit1, roe) values (%s, 'yes', %s, 39, %s, 'r4', 0);",(moveid, closestEnemyX+100, closestEnemyZ))
        moveid+=1
    print("yo")  
    connection.commit()                 
 
            #move the furthest group 30m closer to the fallback position 
            #all other groups that are not the furthest group move them 1 meters up and set them to atk
   
     #run every 5 sec 
        
        

        


async def isPositionDataEmpty():
    cursor = connection.cursor()
    cursor.execute("select * from positiondata;")
    connection.commit()
    positionData=cursor.fetchall()
    numberofRows = len(positionData)
    print("number of rows" , numberofRows)
    if(numberofRows >0):
        return True
    return False
        
async def faceEnemy(currentUnit):
    #print("visibleenemies")   
    cursor = connection.cursor()
    cursor.execute("select px,pz,visibleenemies from positiondata where unit_name=%s order by timestamp desc limit 1;", [currentUnit])
    connection.commit()
    thisUnit=cursor.fetchall()
    thisUnit=thisUnit[0]
    #print(thisUnit)
    px = float(thisUnit[0])
    #print(px)
    pz = float(thisUnit[1])
    #print(pz) 
    visibleEnemies = (str(thisUnit[2])[:-1]).split(',')
    #print(visibleEnemies)
    closestEnemyX=px
    closestEnemyZ=pz
    distance = 1000000000
    #print(px,pz,visibleEnemies)
    for enemy in visibleEnemies:
        #print("positiondata")
        #print(enemy)
        cursor.execute("select px,pz from positiondata where unit_name=%s order by timestamp desc limit 1;", [enemy])
        connection.commit()
        enemyVis = cursor.fetchall()
        #print(enemyVis)
        enemyVis = enemyVis[0]
        #print(enemyVis)
        dis = math.sqrt( math.pow(px-float(enemyVis[0]), 2) + math.pow(pz-float(enemyVis[1]), 2))
        if(dis<distance) :
            closestEnemyX = float(enemyVis[0])
            closestEnemyZ = float(enemyVis[1])
            distance = dis
    if(px!=closestEnemyX or pz!=closestEnemyZ):        
        m = (pz-closestEnemyZ)/(px-closestEnemyX)
        b = pz - m*px
        newX = px + (closestEnemyX-px)*0.001
        newZ = m*newX+b
        return newX, newZ     
    return closestEnemyX, closestEnemyZ 
       
async def findClosestEnemy(currentUnit):
    #print("visibleenemies")   
    cursor = connection.cursor()
    cursor.execute("select px,pz,visibleenemies from positiondata where unit_name=%s order by timestamp desc limit 1;", [currentUnit])
    connection.commit()
    thisUnit=cursor.fetchall()
    thisUnit=thisUnit[0]
    #print(thisUnit)
    px = float(thisUnit[0])
    #print(px)
    pz = float(thisUnit[1])
    #print(pz) 
    visibleEnemies = (str(thisUnit[2])[:-1]).split(',')
    #print(visibleEnemies)
    closestEnemyX=px
    closestEnemyZ=pz
    distance = 1000000000
    #print(px,pz,visibleEnemies)
    for enemy in visibleEnemies:
        #print("positiondata")
        #print(enemy)
        cursor.execute("select px,pz from positiondata where unit_name=%s order by timestamp desc limit 1;", [enemy])
        connection.commit()
        enemyVis = cursor.fetchall()
        #print(enemyVis)
        enemyVis = enemyVis[0]
        #print(enemyVis)
        dis = math.sqrt( math.pow(px-float(enemyVis[0]), 2) + math.pow(pz-float(enemyVis[1]), 2))
        if(dis<distance) :
            closestEnemyX = float(enemyVis[0])
            closestEnemyZ = float(enemyVis[1])
            distance = dis
            
       
    return closestEnemyX, closestEnemyZ


async def main():
    task = asyncio.create_task(optimalBehavior())
    
    await task

asyncio.run(main())