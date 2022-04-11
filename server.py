import asyncio
import logging
import websockets
import socket
import sys
import psycopg2
import time


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
            
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (0, 'hold', 14463, 39, 16000, 'lefttlead', 'leftgunner' , 'l3', 'l4', 'yellow', 'combat');")
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (1, 'hold', 14662, 39, 15930, 'mlead', 'mgunner' , 'm3', 'm4', 'yellow', 'combat');")
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (2, 'hold', 14759, 39, 15930, 'rightlead', 'rightgunner' , 'r3', 'r4', 'yellow', 'combat');")
        connection.commit()
        print("First Set of Waypoints added\n")
        
        inPosition = False
        while(inPosition == False) :
            avgMzPos =0
            counterM =0
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mlead';")
            mleadposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='mgunner';")
            mgunnerposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m3';")
            m3position = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='m4';")
            m4position = cursor.fetchone()

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
            
        
            if (abs(avgRzPos-avgMzPos)) <=50:
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (3, 'hold', 14665, 39, 16000, 'mlead', 'mgunner' , 'm3', 'm4', 'yellow', 'combat');")
                connection.commit()
                print("Middle Group Moving Up\n")
                inPosition=True
            time.sleep(5)
        
        inPosition2 = False
        while(inPosition2 == False) :
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftlead';")
            leftleadposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftgunner';")
            leftgunnerposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l3';")
            l3position = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l4';")
            l4position = cursor.fetchone()
            avgLzPos =0
            counterL =0
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
            
            
            if (abs(avgLzPos-avgMzPos)) <=40:
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (4, 'hold', 14759, 39, 16000, 'rightlead', 'rightgunner' , 'r3', 'r4', 'yellow', 'combat');")
                connection.commit()
                print("Right Group Moving Up\n")
                inPosition2=True
            time.sleep(2)
         
        inPosition3 = False
        while(inPosition3 == False) :          
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftlead';")
            leftleadposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='leftgunner';")
            leftgunnerposition = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l3';")
            l3position = cursor.fetchone()
            cursor.execute("select px,py,pz,unit_health from blufor where unit_name='l4';")
            l4position = cursor.fetchone()
            avgLzPos =0
            counterL =0
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
            
            if (abs(avgRzPos-avgMzPos) <=50) and (abs(avgLzPos-avgMzPos) <=50):
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (5, 'hold', 14611, 39, 16000, 'lefttlead', 'leftgunner' , 'l3', 'l4', 'yellow', 'combat');")
                cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (6, 'hold', 14665, 39, 16000, 'mlead', 'mgunner' , 'm3', 'm4', 'yellow', 'combat');")
                print("Moving Closer\n")
                inPosition3=True
            time.sleep(5)
        time.sleep(20)
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (7, 'hold', 15283, 39, 16257, 'lefttlead', 'leftgunner' , 'l3', 'l4', 'yellow', 'combat');")
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (9, 'hold', 15283, 39, 16257, 'mlead', 'mgunner' , 'm3', 'm4', 'yellow', 'combat');")
        cursor.execute("insert into waypointcommands2 (commandid, command, x, y, z, unit1, unit2, unit3, unit4, combatmode, behavior) values (8, 'hold', 15283, 39, 16257, 'rightlead', 'rightgunner' , 'r3', 'r4', 'yellow', 'combat');")
        print("Going To Town\n")
    
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





    
    
    
