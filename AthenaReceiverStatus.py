﻿#!/usr/bin/env python3

import socket, errno, sys, struct, subprocess, re
import threading
import time
from athena_messages import MobilityTaskRequest, Timestamp, MobilityTask, LLA_Waypoint, MobilityTaskStatus, LocalizationSolution
import psycopg2
import numpy as np
import argparse
import asyncio

import uuid

from asyncio import DatagramProtocol
from datetime import datetime

connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")

def DBSaveStatusData(TimeStamp, Uname, status, uuid):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    positionDataSQL = "insert into driverstatus (timestamp, unit_name, status, uuid) values ('"  + str(TimeStamp) + "','" + Uname + "','"  + status + "', '"  + uuid + "');"
    cursor.execute(positionDataSQL)
    connection.commit()
    cursor.execute("RollBACK")
    connection.commit()
    positionDataSQL2 = "insert into longterm_driverstatus (timestamp, unit_name, status, uuid) values ('"  + str(TimeStamp) + "','" + Uname + "','"  + status + "', '"  + uuid + "');"
    cursor.execute(positionDataSQL2)
    connection.commit()


class AthenaReceiver(object):

    def __init__(self):
        #self.athena_ip = "127.0.0.1"
        #self.athena_ip = "192.168.1.21"
        #self.athena_ip = "192.168.1.8"
        config = helper.read_config()
        ip = config['AthenaStatus']['ipaddress'] 
        self.athena_ip = ip   #  always us receiver
        #self.athena_ip = "192.168.10.228"   #  always receiver
        #self.athena_port = 3636
        port = config['AthenaStatus']['port'] 
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
        print("IN receive")
        try:
            #print("1")
            if self.athena_socket != None:
                #print("1a")
                data = self.athena_socket.recv(1024)        
                #print("2")
                driver_message = MobilityTaskStatus()  #11120
                #driver_message = LocalizationSolution()  # 11111
                #driver_message = MobilityTaskRequest()
                #driver_message.time.sec = 1646687811
                #driver_message.status = 1
                #print("3")  
                driver_message.ParseFromString(data)
                #print("#######################")
                #print(driver_message)
                #print("#######################")
                newtime = driver_message.time.sec
                thatime = datetime.fromtimestamp(newtime).strftime("%A, %B, %d, %Y, %I:%M:%S.%f")
                date_format = "%A, %B, %d, %Y, %I:%M:%S.%f"
                timeNew = datetime.strptime(thatime, date_format).time()
                #print("newtime: ", thatime)
                DBSaveStatusData(timeNew, "SEI", str(driver_message.status), driver_message.uuid)
            else:
                print('No receiving socket')
        except:
            e0 = sys.exc_info()[0]
            e1 = sys.exc_info()[1]
            print('receive error: ', e0, e1)






def build_message(longitude, latitude):

    # driver request message
    driver_message = MobilityTaskRequest()
    timestamp  = int(time.time())
    #print('check time', timestamp)
    driver_message.time.sec = timestamp
    driver_message.time.nsec = 0
    driver_message.request = 1  #WAYPOINT 
  
    waypoint =  LLA_Waypoint()
    waypoint.latitude = float(latitude)
    waypoint.longitude = float(longitude)
    driver_message.waypoints.extend([waypoint])
   
    #print(driver_message)
    return driver_message.SerializeToString()


def getFromAthena_Asset_Command():
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    cursor.execute("select * from athena_asset_command;")
    athenaCommand = cursor.fetchall()
    #it its one row cursor.fetchone()
    return athenaCommand[0]

def AthenaStatus():
    node = AthenaReceiver()
    while True:
        print("Receiving message")
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