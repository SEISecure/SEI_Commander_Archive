import asyncio
import logging
import websockets
import socket
import sys
import psycopg2
import time
from distutils import command


class ServerProtocol:
    
    def data_received(self, data):
        message = data.decode()
        print('Data received: {}'.format(message))

        print('Send: {}'.format(message))
        
        #print('Close the client socket')
        #self.transport.close()


async def main():
    loop= asyncio.get_running_loop()


    server = await loop.create_server(
        lambda: ServerProtocol(),
        '127.0.0.1', 10000)
    connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")

    try:
        

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
        #avg left mid and right groups and set the 
        #take avg of x,y,z of the left group and then order the left grps waypoint to be at the avg 
        #right group will take the avg z of middle grp and and avg x position of where they are
        time.sleep(2)
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftlead';")
        leftleadposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftgunner';")
        leftgunnerposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l3';")
        l3position = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l4';")
        l4position = cursor.fetchone()
        avgLxPos = 0
        avgLzPos = 0
        counterL = 0
        if(float(leftleadposition[3]) < 1):
            avgLzPos+=float(leftleadposition[2])
            avgLxPos+=float(leftleadposition[0])
            counterL+=1
            
        if(float(leftgunnerposition[3]) < 1):
            avgLzPos+=float(leftgunnerposition[2])
            avgLxPos+=float(leftgunnerposition[0])
            counterL+=1
            
        if(float(l3position[3]) < 1):
            avgLzPos+=float(l3position[2])
            avgLxPos+=float(l3position[0])
            counterL+=1
                
        if(float(l4position[3]) < 1):
            avgLzPos+=float(l4position[2])
            avgLxPos+=float(l4position[0])
            counterL+=1
            
        if(counterL >0) :
            avgLzPos= avgLzPos / counterL
            avgLxPos= avgLxPos / counterL       
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mlead';")
        mleadposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mgunner';")
        mgunnerposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m3';")
        m3position = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m4';")
        m4position = cursor.fetchone()
        avgMxPos = 0
        avgMzPos = 0
        counterM = 0
        if(float(mleadposition[3]) < 1):
            avgMzPos+=float(mleadposition[2])
            avgMxPos+=float(mleadposition[0])
            counterM+=1
            
        if(float(mgunnerposition[3]) < 1):
            avgMzPos+=float(mgunnerposition[2])
            avgMxPos+=float(mgunnerposition[0])
            counterM+=1
            
        if(float(m3position[3]) < 1):
            avgMzPos+=float(m3position[2])
            avgMxPos+=float(m3position[0])
            counterM+=1
                
        if(float(m4position[3]) < 1):
            avgMzPos+=float(m4position[2])
            avgMxPos+=float(m4position[0])
            counterM+=1
            
        if(counterM >0) :
            avgMxPos= avgMxPos / counterM
            avgMzPos= avgMzPos / counterM  
            print("Middle team units alive\n", counterM)
        print("workin") 
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightlead';")
        rightleadposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightgunner';")
        rightgunnerposition = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r3';")
        r3position = cursor.fetchone()
        cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r4';")
        r4position = cursor.fetchone()
        avgRxPos =0
        counterR =0
        if(float(rightleadposition[3]) < 1):
            avgRxPos+=float(rightleadposition[0])
            counterR+=1
        
        if(float(rightgunnerposition[3]) < 1):
            avgRxPos+=float(rightgunnerposition[0])
            counterR+=1
            
        if(float(r3position[3]) < 1):
            avgRxPos+=float(r3position[0])
            counterR+=1
            
        if(float(r4position[3]) < 1):
            avgRxPos+=float(r4position[0])
            counterR+=1
        
        if(counterR >0) :
            avgRxPos= avgRxPos / counterR 
            print("Right team units alive\n", counterR)        
        tempRxPos = avgRxPos    
        print("workin") 
        commandid =0
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'lefttlead', 'leftgunner' , 'l3', 'l4', 'yellow', 'combat');",(commandid, avgLxPos, avgLzPos))
        print("left position inserted", avgLxPos, ",", avgLzPos)
        commandid = commandid+1
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'mlead', 'mgunner' , 'm3', 'm4', 'yellow', 'combat');",(commandid, avgMxPos, avgMzPos))
        print("middle position inserted", avgMxPos, ",", avgMzPos)
        commandid = commandid+1
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'rightlead', 'rightgunner' , 'r3', 'r4', 'blue', 'stealth');",(commandid, avgRxPos, avgMzPos))
        print("right position inserted", avgRxPos, ",", avgMzPos)
        connection.commit()
        print("First Set of Waypoints added\n")
        
        inPosition = False
        while(inPosition == False) :
            time.sleep(10)
            #is the avg z of the right grp at the middle grp avg z that was asigned as a waypoint            
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightlead';")
            rightleadposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='rightgunner';")
            rightgunnerposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r3';")
            r3position = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='r4';")
            r4position = cursor.fetchone()
            avgRzPos =0
            counterR =0
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
                      
            print("Difference between right and middle", avgRzPos, avgMzPos)
            if (abs(avgRzPos-avgMzPos)) <=20:
                #current avg z compared to the avg z that we want units to move to
                #get mid grp to move to avg z of left grp
                commandid = commandid+1
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'rightlead', 'rightgunner' , 'r3', 'r4', 'yellow', 'combat');",(commandid, avgRxPos, avgMzPos))
                commandid = commandid+1
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'mlead', 'mgunner' , 'm3', 'm4', 'blue', 'stealth');",(commandid, avgMxPos, 16000))
                connection.commit()
                print("Middle Group Moving Up\n")
                inPosition=True
            if (abs(avgRzPos-avgMzPos)) >20:
                commandid = commandid+1
                print("waypoint reinserted")
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'rightlead', 'rightgunner' , 'r3', 'r4', 'blue', 'stealth');",(commandid, avgRxPos, avgMzPos))
        inPosition2 = False
        while(inPosition2 == False) : 
            time.sleep(10)           
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mlead';")
            mleadposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mgunner';")
            mgunnerposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m3';")
            m3position = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m4';")
            m4position = cursor.fetchone()
            avgMzPos =0
            counterM =0
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
            
            print("Difference between middle and left", avgMzPos, avgLzPos)
            if (abs(avgMzPos-avgLzPos)) <=20 or counterM == 0:
                #is the the z location of the middle grp at the target waypoint
                #right grp moves to the z that we assigned the middle grp to
                commandid = commandid+1
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'mlead', 'mgunner' , 'm3', 'm4', 'yellow', 'combat');",(commandid, avgMxPos, avgLzPos))
                commandid = commandid+1
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'rightlead', 'rightgunner' , 'r3', 'r4', 'blue', 'stealth');",(commandid, tempRxPos, 16000))
                connection.commit()
                print("Right Group Moving Up\n")
                inPosition2=True
            
            if (abs(avgMzPos-avgLzPos)) >20:
                commandid = commandid+1
                print("waypoint reinserted")
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (%s, 'hold', %s, 39, %s, 'mlead', 'mgunner' , 'm3', 'm4', 'blue', 'stealth');",(commandid, avgMxPos, 16000))
        
    
        #cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4) values (3, 'hold', 18471, 3.9, 14580, 'rightlead', 'rightgunner' , 'r3', 'r4');")
    
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            SystemExit
             
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)  
    

    async with server:
        await server.serve_forever()

asyncio.run(main())

