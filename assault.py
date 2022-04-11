import asyncio
import logging
import websockets
import socket
import sys
import psycopg2
import time
import math
from distutils import command

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


async def assault():
    loop= asyncio.get_running_loop()


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
        #print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
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
        
        

             
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)  
    

    async with server:
        await server.serve_forever()
        
        
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
        
async def getHealth(currentUnit):   
    cursor = connection.cursor()
    cursor.execute("select unit_health from positiondata where unit_name=%s order by timestamp desc limit 1;", [currentUnit])
    connection.commit()
    thisUnit=cursor.fetchall()
    thisUnit=thisUnit[0]
    hp = float(thisUnit[0])
    #print("printing hp",hp)
    return hp  
        
async def main():
    task = asyncio.create_task(assault())
    
    await task

asyncio.run(main())