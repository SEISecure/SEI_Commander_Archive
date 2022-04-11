#!/usr/bin/env python3

import socket, errno, sys, struct, subprocess, re
import threading
from Arthemis.NewCodePy.athena_messages import Waypoint, Principal_Athena_Message, Artemis_Message, Artemis_General_Order, Mars_General_Order, Mars_Message, Scan_Point, Athena_Orders, Nike_Message
import time
import psycopg2
import numpy as np
import argparse
import asyncio
import copy
from asyncio import DatagramProtocol
from datetime import datetime



class AthenaSender(object):

    def __init__(self):
        #self.athena_ip = "127.0.0.1"
        #self.athena_ip = "192.168.1.21"
        config = helper.read_config()
        ip = config['ArthemisSender']['ipaddress'] 
        self.athena_ip = ip 
        #self.athena_ip = "10.1.0.135"
        #self.athena_ip = "127.0.0.1"
        port = config['ArthemisSender']['port'] 
        self.athena_port = port
        messageToSend = ""
        self.set_up_connections()
        print("in init")

    def set_up_connections(self):
        try:
            """
            Socket for Sending Protobuff to Athena.
            """
            print("1")
            self.athena_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("2")
            #self.send_sockets.append([self.athena_socket, self.athena_ip, self.athena_port, "athena"])
            print("Send protobuf to Athena socket set up")
        except:
                print('protobuff socket send error')

    def send(self):
        #for socket_instance in self.send_sockets:
        print("IN send")
        try:
            #time.sleep(delay)
            self.athena_socket.connect((self.athena_ip, self.athena_port));
            print("sending to ",self.athena_ip, self.athena_port)
            # Send data to server
            data = self.messageToSend;
            self.athena_socket.send(data);
        except:
            print('set_up_connections error')



def build_message(control_order,behavior,uuid,scanPoints):
    header_message = Principal_Athena_Message()
    header_message.sender_uuid = "SEI 21351"
    header_message.message_type = "Command"
    header_message.destination_id.append('0')
    time = datetime.utcnow()
    str_time = time.isoformat()
    header_message.timestamp_utc_time = str_time

    order = Athena_Orders()
    order.weapon_control_order = int(control_order) 
    order.behavior = int(behavior) 
    header_message.athena_orders.append(order);


    # Artemis message

    arti_message = Artemis_Message()
    arti_message.uuid = "Artemis-141";  #uuid
    arti_message.current_order_running = "General"
    #status only fields
    '''
    arti_message.ptu_pan = 0
    arti_message.ptu_tilt = 0
    arti_message.latitude = 39.119551
    arti_message.longitude = -87.363750
    arti_message.altitude = 0
    arti_message.heading = 0
    arti_message.zoom = 0
    arti_message.ammo_count = 100000
    '''

    # Message command to Artemis
    current_general_order = Artemis_General_Order()
    current_general_order.trigger = "General"
    current_general_order.weapon_control_order = int(control_order)
    current_general_order.behavior = int(behavior) 
    current_general_order.select_scan_pattern = 1
    #current_general_order.left_aor = 1
    #current_general_order.right_aor = 1
    current_general_order.continuing_order = "General"
    print("Tried sending message###########")
    # ScanPoints
    scanPointNum = 1
    for points in scanPoints:
        longLat = points.split(',')
        scanPoint = Scan_Point()
        scanPoint.point_number  = scanPointNum
        scanPoint.pan = float(longLat[1])
        scanPoint.tilt = float(longLat[0])
        scanPoint.zoom = float(0)
        current_general_order.create_scan_pattern.append(copy.deepcopy(scanPoint))
        scanPointNum+=1
    #scanPoint2 = Scan_Point()
    #scanPoint2.point_number  = 2
    #scanPoint2.pan = float(pan)
    #scanPoint2.tilt = float(tilt)
    #scanPoint2.zoom = float(zoom)
    #current_general_order.create_scan_pattern.append(scanPoint2)

    # ActionPoints
    '''
    action1 = 1
    current_general_order.action_point.append(action1)
    action2 = 2
    current_general_order.action_point.append(action2)
    action3 = 3
    current_general_order.action_point.append(action3)
    '''
    
    arti_message.orders.append(current_general_order)

    header_message.artemis.append(arti_message)

    # mars message
    '''
    mars_message = Mars_Message()
    mars_message.uuid = "kairos"

   
    mars_order = Mars_General_Order()
    mars_order.trigger = "general"
    mars_order.behavior = 1
    mars_order.driving_control_order = 1
    
    waypoint = Waypoint()
    waypoint.point_number = 1
    waypoint.latitude = 34.2413508
    waypoint.longitude = -116.0747637
    waypoint.heading = 90
    mars_order.waypoints.extend([waypoint])
    
    waypoint = Waypoint()
    waypoint.point_number = 2
    waypoint.latitude = 34.2414074
    waypoint.longitude = -116.0748388
    waypoint.heading = 194
    mars_order.waypoints.extend([waypoint])
    
    waypoint = Waypoint()
    waypoint.point_number = 3
    waypoint.latitude = 34.2414340
    waypoint.longitude = -116.0749233
    waypoint.heading = 7
    mars_order.waypoints.extend([waypoint])    
    
    waypoint = Waypoint()
    waypoint.point_number = 4
    waypoint.latitude = 34.2413952
    waypoint.longitude = -116.0749112
    waypoint.heading = 194
    mars_order.waypoints.extend([waypoint])
    
    waypoint = Waypoint()
    waypoint.point_number = 5
    waypoint.latitude = 34.2413686
    waypoint.longitude = -116.0748817
    waypoint.heading = 7
    mars_order.waypoints.extend([waypoint])
    
    waypoint.point_number = 6
    waypoint.latitude = 34.2413508
    waypoint.longitude = -116.0747637
    waypoint.heading = 90
    mars_order.waypoints.extend([waypoint])
    mars_message.orders.append(mars_order)
    header_message.mars.append(mars_message)
    '''
    '''
    # Nike Message example

    nike_message = Nike_Message()
    nike_message.uuid = "nike3"
    nike_message.latitude = 39.119649
    nike_message.longitude = -87.363789
    nike_message.altitude = 32
    header_message.nike.append(nike_message)
    '''
   
    #print(header_message)
    return header_message.SerializeToString()

#database connection information currently on localhost
connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")

def getFromAthena_Asset_Command():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    timestamp  = int(time.time())
    cursor.execute("select * from athena_asset_command where delay <= '" + timestamp + "';")
    athenaCommand = cursor.fetchall()        
    #it its one row cursor.fetchone()
    #new column last column 7th
    return athenaCommand

def removeFromAthena_Asset_Command(command,behavior, control):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    if command != None:
        cursor.execute("delete from athena_asset_command where command = '" + str(command) + "' and  behavior = '" + str(behavior) + "' and control = '" + str(control) + "' ;")
    else:
        cursor.execute("delete from athena_asset_command  where behavior = '" + str(behavior) + "' and  control = '" + str(control) + "' ;")
    connection.commit()


def ArthemisSender():
    
   

    while True:
        """
        print("Receiving message")
        node = AthenaReceiver()
        node.receive()
        """
        
        commands  = getFromAthena_Asset_Command()
        control_order =''
        behavior=''
        uuid=''
        time.sleep(1)

        for command in commands:
            if command != None:
                #print(len(command))
                for i in range(0, len(command) - 1):
                    print(i, command[i])
                #print("")
        
                if command[1] == "scan":
                    print("Got to sca")
                    waypointList = command[2].split("*")
                    #print(waypointList)
                    control_order = command[4]
                    behavior = command[3]
                    uuid = command[0]
                    #print("*******Building Scan Message*********")
                    #print("*******Building Scan Message*********")
                    msg = build_message(control_order,behavior,uuid,waypointList)
                    #print("*******Sending Scan Message*********")
                    #print("*******Sending Scan Message*********")
                    
                    node = AthenaSender()
                    node.messageToSend = msg
                    #t1 = threading.Thread(target=node.send, args = command[7] )
                    #t1.daemon = True
                    #t1.start()
                    node.send()
                    #print("*******Removing Scan Message*********")
                    #print("*******Removing Scan Message*********")
                    removeFromAthena_Asset_Command(command[1], command[3], command[4])
                
                elif command[1] == "controlorder":
                    
                    
                    control_order = command[4]
                    behavior = command[3]
                    uuid = command[0]
                   
                   
                    msg = build_message(control_order,behavior,uuid,[])
                    
                    
                    node = AthenaSender()
                    node.messageToSend = msg
                    node.send()
                    
                    #print("TryingToRemoveCommand")
                    removeFromAthena_Asset_Command(command[1], command[3], command[4])
                    #print("TryingToRemoveCommand")
        #break

'''
if __name__ == '__main__':
    asyncio.run(main())
'''
