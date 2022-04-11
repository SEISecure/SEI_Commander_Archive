#!/usr/bin/env python3

import socket, errno, sys, struct, subprocess, re
import threading
import time
from athena_messages import MobilityTaskRequest, Timestamp, MobilityTask, LLA_Waypoint, MobilityTaskStatus, LocalizationSolution, Detection, Contact_Properties
import psycopg2
import numpy as np
import argparse
import asyncio
import helper


from asyncio import DatagramProtocol
from datetime import datetime


connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")

def DBSaveDetection(TimeStamp, source_id, target_id, longitude, latitude, Z, classification, bearing,
                                estimated_range, confidence, movement, spectrum):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    detectionSQL = "insert into detections (timestamp, unit_name, target_name, target_x, target_y, target_z, \
    classification, bearing, estimated_range, confidence, movement, spectrum) values \
    ('"  + str(TimeStamp) + "','" + str(source_id) + "','" + str(target_id) +  "','" + str(longitude) + "',\
    '" + str(latitude) +  "','" + str(Z) + "','" + classification + "','" + str(bearing) + "', \
    '" + str(estimated_range) +  "','" + str(confidence) +  "','" + str(movement) +  "','" + spectrum + "');"
    cursor.execute(detectionSQL)
    connection.commit()
    
    cursor.execute("RollBACK")
    connection.commit()
    detectionSQL = "insert into longtermdetections (timestamp, unit_name, target_name, target_x, target_y, target_z, \
    classification, bearing, estimated_range, confidence, movement, spectrum) values \
    ('"+str(TimeStamp) + "','" + str(source_id) + "','" + str(target_id) +  "','" + str(longitude) + "',\
    '" + str(latitude) +  "','" + str(Z) + "','" + classification + "','" + str(bearing) + "', \
    '" + str(estimated_range) +  "','" + str(confidence) +  "','" + str(movement) +  "','" + spectrum + "');"
    cursor.execute(detectionSQL)
    connection.commit()
    


class AthenaReceiver(object):

    def __init__(self):
        #self.athena_ip = "127.0.0.1"
        #self.athena_ip = "192.168.1.21"
        #self.athena_ip = "192.168.1.8"
        config = helper.read_config()
        ip = config['AthenaDetections']['ipaddress'] 
        self.athena_ip = ip   #  always us receiver
        #self.athena_ip = "192.168.10.228"   #  always receiver
        #self.athena_port = 3636
        port = config['AthenaDetections']['port'] 
        self.athena_port = port
        messageToSend = ""
        self.set_up_connections()
        #print("in init")

    def set_up_connections(self):
        try:
            """
            Socket for Receiving Protobuff to Athena.
            """
            #print("1")
            self.athena_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #print("4")
            self.athena_socket.bind((self.athena_ip, self.athena_port));
            print("receiving from ",self.athena_ip, self.athena_port)
            self.athena_socket.settimeout(20.0);
            print("receiver set_up_connections socket set up")
        except:
            print('receiver set_up_connections error')

    def receive(self):
        #for socket_instance in self.send_sockets:
        #print("IN receive")
        try:
            #print("1")
            if self.athena_socket != None:
                #print("1a")
                data = self.athena_socket.recv(1024)        
                #print("2")
                #detection_message = MobilityTaskStatus()  #11120
                #detection_message = LocalizationSolution()  # 11111
                #detection_message = MobilityTaskRequest()
                #detection_message = Detection()  
                detection_message = Contact_Properties()  
                #print("3")  
                detection_message.ParseFromString(data)
                #print(detection_message)
                '''
                detection_message.source_id = 7654321
                detection_message.target_id = 1234567
                detection_message.latitude = 37.37
                detection_message.longitude = 123.123
                detection_message.classification = "class_1"
                detection_message.bearing = 11.23
                detection_message.estimated_range = 45.67
                detection_message.confidence = 0.01
                detection_message.movement = True
                detection_message.spectrum = "infrared"
                '''
                # print(detection_message)
                thatime = datetime.now()
                # print("thatime  ", thatime)
                #date_format = "%A, %B, %d, %Y, %I:%M:%S.%f"
                date_format = "%Y-%m-%d %H:%M:%S.%f"
                timeNew = datetime.strptime(str(thatime), date_format).time()
                # print("newtime: ", timeNew)
                print("Saving Detection Message to DB")
                DBSaveDetection(timeNew, detection_message.source_id, detection_message.target_id, 
                                detection_message.longitude, detection_message.latitude, '0', detection_message.classification, detection_message.bearing,
                                detection_message.estimated_range, detection_message.confidence, detection_message.movement, detection_message.spectrum)
                
            else:
                print('No receiving socket')
        except:
            e0 = sys.exc_info()[0]
            e1 = sys.exc_info()[1]
            print('receive error: ', e0, e1)


class AthenaSender(object):

    def __init__(self):
        self.athena_ip = "127.0.0.1"
        #self.athena_ip = "192.168.1.21"
        #self.athena_ip = "192.168.1.8"
        self.athena_port = 3636
        messageToSend = ""
        self.set_up_connections()
        #print("in init")

    def set_up_connections(self):
        try:
            """
            Socket for Sending Protobuff to Athena.
            """
            #print("1")
            self.athena_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #print("2")
            #self.send_sockets.append([self.athena_socket, self.athena_ip, self.athena_port, "athena"])
            print("Send protobuf to Athena socket set up")
        except:
                print('protobuff socket send error')

    def send(self):
        #for socket_instance in self.send_sockets:
        #print("IN send")
        try:
            self.athena_socket.connect((self.athena_ip, self.athena_port));
            print("sending to ",self.athena_ip, self.athena_port)
            # Send data to server
            data = self.messageToSend;
            self.athena_socket.send(data);
        except:
            print('set_up_connections error')



def build_message(longitude, latitude):

    # driver request message
    detection_message = MobilityTaskRequest()
    timestamp  = int(time.time())
    #print(timestamp)
    detection_message.time.sec = timestamp
    detection_message.time.nsec = 0
    detection_message.request = 1  #WAYPOINT 
  
    waypoint =  LLA_Waypoint()
    waypoint.latitude = float(latitude)
    waypoint.longitude = float(longitude)
    detection_message.waypoints.extend([waypoint])
   
    print(detection_message)
    return detection_message.SerializeToString()

def getFromAthena_Asset_Command():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select * from athena_asset_command;")
    athenaCommand = cursor.fetchall()
    #it its one row cursor.fetchone()
    return athenaCommand[0]

def AthenaDetections():
    node = AthenaReceiver()
    while True:
        print("Receiving Detection")
        #node = AthenaReceiver()
        node.receive()
        

    '''
        command  = getFromAthena_Asset_Command()
        print(len(command))
        for i in range(0, len(command) - 1):
            print(i, command[i])
        print("")

        if command[1] == "move":
            print (command[1])
            values = command[2].split(",")
            for i in range(0, len(values)):
                print(i, values[i])

            longitude = values[0]
            latitude = values[1]

            print("Sending message")
            msg = build_message(longitude, latitude)
            print(msg)
            node = AthenaSender()
            node.messageToSend = msg
            node.send()
    '''
        #time.sleep(5)

'''
if __name__ == '__main__':
    asyncio.run(main())
'''