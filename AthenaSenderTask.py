#!/usr/bin/env python3

import socket, errno, sys, struct, subprocess, re
import threading
import time
#from athena_messages import MobilityTaskRequest, Timestamp, MobilityTask, LLA_Waypoint
from athena_messages import MobilityTaskRequest, Timestamp, MobilityTask, LLA_Waypoint, MobilityTaskStatus, LocalizationSolution
import psycopg2
import numpy as np
import argparse
import asyncio

import uuid
import database_connect_Arma
from asyncio import DatagramProtocol
from datetime import datetime
import helper


class AthenaSender(object):

    def __init__(self):
        #self.athena_ip = "127.0.0.1"
        #self.athena_ip = "192.168.1.21"
        #self.athena_ip = "192.168.1.8"
        config = helper.read_config()
        ip = config['AthenaSender']['ipaddress'] 
        self.athena_ip = ip
        #self.athena_port = 3636
        port = config['AthenaSender']['port'] 
        self.athena_port = port
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
            #time.sleep(delay)
            self.athena_socket.connect((self.athena_ip, self.athena_port));
            print("sending to ",self.athena_ip, self.athena_port)
            # Send data to server
            data = self.messageToSend;
            self.athena_socket.send(data);
            
        except:
            print('set_up_connections error')



def build_message(longitude, latitude, command, uuid):

    # driver request message
    driver_message = MobilityTaskRequest()
    timestamp  = int(time.time())
    print(timestamp)
    driver_message.time.sec = timestamp
    driver_message.time.nsec = 0
    #driver_message.uuid = uuid.uuid4().hex 
    driver_message.uuid = uuid
    if command == "move":
        print("attempting to move")
        driver_message.request = 1  #WAYPOINT 
        waypoint =  LLA_Waypoint()
        waypoint.latitude = float(latitude)
        waypoint.longitude = float(longitude)
        driver_message.waypoints.extend([waypoint])
    elif command == "stop":
        driver_message.request = 0  #STOP 
  
    print(driver_message)
    return driver_message.SerializeToString()

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

def AthenaRunner():
    while True:
        """
        print("Receiving message")
        node = AthenaReceiver()
        node.receive()
        """
        commands  = getFromAthena_Asset_Command()
        
        for command in commands:
            #for i in range(0, len(command) - 1):
                #print(i, command[i])
            #print("")
            if command[1] == "move" or command[1] == "stop":
                print("@@@@@@@@@@@@@@@@@@@")
                print("@@@@@@@@@@@@@@@@@@@")
                print ("hello    ", command[1])
                print("@@@@@@@@@@@@@@@@@@@")
                print("@@@@@@@@@@@@@@@@@@@")
                longitude = 0
                latitude = 0
                if command[2] != None:
                    values = command[2].split(",")
                    for i in range(0, len(values)):
                        print(i, values[i])
    
                    longitude = values[0]
                    latitude = values[1] 
                uuid = command[6] 
                print("Sending message")
                msg = build_message(longitude, latitude, command[1], uuid)
                print(msg)
                node = AthenaSender()
                node.messageToSend = msg
                #t1 = threading.Thread(target=node.send, args = command[7] )
                #t1.daemon = True
                #t1.start()
                node.send()
                database_connect_Arma.removeAthenaAssetCommand(command[1], command[0])

                
        time.sleep(1)
    

'''
if __name__ == '__main__':
    asyncio.run(main())
'''
